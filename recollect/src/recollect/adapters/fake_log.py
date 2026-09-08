"""
In-memory fake ObservationLogPort for tests (Story 1.3).

Enforces the same append-only invariant as the real adapter so tests
catch violations even without a database.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from uuid import UUID

from recollect.core.entities import (
    Enrolment,
    Gap,
    Interaction,
    Observation,
    Senior,
    Tombstone,
)
from recollect.core.errors import (
    DuplicateInteractionError,
    ImmutableObservationError,
    MissingProvenanceError,
    InactiveEnrolmentError,
)
from recollect.core.ports.log_port import ObservationLogPort


class FakeObservationLog(ObservationLogPort):
    def __init__(self) -> None:
        self._seniors: dict[UUID, Senior] = {}
        self._enrolments: dict[UUID, Enrolment] = {}   # keyed by senior_id
        self._interactions: dict[UUID, Interaction] = {}
        self._idempotency_keys: set[str] = set()
        self._observations: list[Observation] = []      # append-only list
        self._observation_ids: set[UUID] = set()
        self._gaps: dict[UUID, Gap] = {}
        self._tombstones: dict[UUID, Tombstone] = {}  # keyed by senior_id

    # ------------------------------------------------------------------
    # Senior / Enrolment
    # ------------------------------------------------------------------

    async def save_senior(self, senior: Senior) -> None:
        self._seniors[senior.id] = senior

    async def get_enrolment(self, senior_id: UUID) -> Enrolment | None:
        return self._enrolments.get(senior_id)

    async def save_enrolment(self, enrolment: Enrolment) -> None:
        self._enrolments[enrolment.senior_id] = enrolment

    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------

    async def save_interaction(self, interaction: Interaction) -> None:
        if interaction.idempotency_key in self._idempotency_keys:
            raise DuplicateInteractionError(
                f"Interaction idempotency key already seen: {interaction.idempotency_key}"
            )
        self._idempotency_keys.add(interaction.idempotency_key)
        self._interactions[interaction.id] = interaction

    async def get_interaction(self, interaction_id: UUID) -> Interaction | None:
        return self._interactions.get(interaction_id)

    # ------------------------------------------------------------------
    # Observation — append only (AD-1)
    # ------------------------------------------------------------------

    async def append_observation(self, observation: Observation) -> None:
        if observation.provenance is None:
            raise MissingProvenanceError("Observation provenance is required (AD-10).")

        enrolment = await self.get_enrolment(observation.senior_id)
        if enrolment is None or not enrolment.is_active:
            raise InactiveEnrolmentError(
                f"Senior {observation.senior_id} has no active enrolment (AD-4)."
            )

        if observation.id in self._observation_ids:
            raise ImmutableObservationError(
                f"Observation {observation.id} already exists; use a superseding event (AD-1)."
            )

        self._observations.append(observation)
        self._observation_ids.add(observation.id)

    async def get_observation(self, observation_id: UUID) -> Observation | None:
        return next(
            (o for o in self._observations if o.id == observation_id), None
        )

    # ------------------------------------------------------------------
    # Windowed read model — no comparison primitives (AD-3)
    # ------------------------------------------------------------------

    async def get_window(
        self,
        senior_id: UUID,
        from_utc: datetime,
        to_utc: datetime,
    ) -> list[Observation]:
        gap_periods = [
            (g.started_at, g.ended_at)
            for g in self._gaps.values()
            if g.senior_id == senior_id
        ]

        def in_gap(occurred_at: datetime) -> bool:
            for start, end in gap_periods:
                if end is None:
                    if occurred_at >= start:
                        return True
                elif start <= occurred_at <= end:
                    return True
            return False

        return [
            o for o in self._observations
            if (
                o.senior_id == senior_id
                and from_utc <= o.provenance.occurred_at <= to_utc
                and not in_gap(o.provenance.occurred_at)
            )
        ]

    # ------------------------------------------------------------------
    # Gap
    # ------------------------------------------------------------------

    async def append_gap(self, gap: Gap) -> None:
        self._gaps[gap.id] = gap

    async def close_gap(self, gap_id: UUID, ended_at: datetime) -> None:
        existing = self._gaps[gap_id]
        self._gaps[gap_id] = Gap(
            id=existing.id,
            senior_id=existing.senior_id,
            reason=existing.reason,
            started_at=existing.started_at,
            ended_at=ended_at,
        )

    # ------------------------------------------------------------------
    # Tombstone and collection stop (AD-13)
    # ------------------------------------------------------------------

    async def deactivate_enrolment(self, senior_id: UUID, at: datetime) -> None:
        enrolment = self._enrolments.get(senior_id)
        if enrolment is None:
            return
        self._enrolments[senior_id] = replace(enrolment, withdrawn_at=at)

    async def append_tombstone(self, tombstone: Tombstone) -> None:
        self._tombstones[tombstone.senior_id] = tombstone

    async def get_tombstone(self, senior_id: UUID) -> Tombstone | None:
        return self._tombstones.get(senior_id)

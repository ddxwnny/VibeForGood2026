"""
PostgresObservationLog — the real append-only observation log adapter (AD-1).

Implements ObservationLogPort against PostgreSQL via SQLAlchemy async. The
same code runs on SQLite (aiosqlite) in tests. Every rule the fakes enforce is
enforced here against the database:

  - append-only: no update/delete path for observations (AD-1)
  - provenance required, rejected at write (AD-10)
  - consent is a write-path precondition (AD-4)
  - interaction idempotency on idempotency_key (AD-14)
  - windowed read with gap exclusion, no comparison primitives (AD-3)
  - tombstone + collection stop for erasure (AD-13)
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from recollect.adapters.postgres.models import (
    Base,
    EnrolmentRow,
    GapRow,
    InteractionRow,
    ObservationRow,
    SeniorRow,
    TombstoneRow,
)
from recollect.core.entities import (
    ConsentArtifactKind,
    Enrolment,
    ErasureReason,
    Gap,
    GapReason,
    Interaction,
    Observation,
    Provenance,
    Senior,
    SignalType,
    TaskOutcome,
    Tombstone,
)
from recollect.core.errors import (
    DuplicateInteractionError,
    ImmutableObservationError,
    InactiveEnrolmentError,
    MissingProvenanceError,
)
from recollect.core.ports.log_port import ObservationLogPort


def _aware_utc(dt: datetime) -> datetime:
    """Normalise a stored UTC timestamp to timezone-aware (AD-11)."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


# ---------------------------------------------------------------------------
# Row <-> entity mappers
# ---------------------------------------------------------------------------


def _senior_row(senior: Senior) -> SeniorRow:
    return SeniorRow(
        id=senior.id,
        display_name=senior.display_name,
        preferred_language=senior.preferred_language,
        created_at=senior.created_at,
    )


def _enrolment_row(enrolment: Enrolment) -> EnrolmentRow:
    return EnrolmentRow(
        id=enrolment.id,
        senior_id=enrolment.senior_id,
        enrolled_at=enrolment.enrolled_at,
        artefacts=sorted(a.value for a in enrolment.artefacts),
        withdrawn_at=enrolment.withdrawn_at,
    )


def _enrolment_from_row(row: EnrolmentRow) -> Enrolment:
    return Enrolment(
        id=row.id,
        senior_id=row.senior_id,
        enrolled_at=_aware_utc(row.enrolled_at),
        artefacts=frozenset(ConsentArtifactKind(v) for v in (row.artefacts or [])),
        withdrawn_at=_aware_utc(row.withdrawn_at) if row.withdrawn_at else None,
    )


def _observation_row(observation: Observation) -> ObservationRow:
    return ObservationRow(
        id=observation.id,
        senior_id=observation.senior_id,
        interaction_id=observation.provenance.interaction_id,
        occurred_at=observation.provenance.occurred_at,
        signal_type=observation.provenance.signal_type.value,
        item_variant=observation.provenance.item_variant,
        extraction_model_id=observation.provenance.extraction_model_id,
        prompt_version=observation.provenance.prompt_version,
        stt_model_version=observation.provenance.stt_model_version,
        content=observation.content,
        outcome=observation.outcome.value if observation.outcome else None,
        supersedes_id=observation.supersedes_id,
    )


def _observation_from_row(row: ObservationRow) -> Observation:
    return Observation(
        id=row.id,
        senior_id=row.senior_id,
        provenance=Provenance(
            interaction_id=row.interaction_id,
            occurred_at=_aware_utc(row.occurred_at),
            signal_type=SignalType(row.signal_type),
            item_variant=row.item_variant,
            extraction_model_id=row.extraction_model_id,
            prompt_version=row.prompt_version,
            stt_model_version=row.stt_model_version,
        ),
        content=row.content,
        outcome=TaskOutcome(row.outcome) if row.outcome else None,
        supersedes_id=row.supersedes_id,
    )


def _tombstone_from_row(row: TombstoneRow) -> Tombstone:
    return Tombstone(
        id=row.id,
        senior_id=row.senior_id,
        reason=ErasureReason(row.reason),
        shredded_at=_aware_utc(row.shredded_at),
        stores_shredded=frozenset(row.stores_shredded or []),
    )


class PostgresObservationLog(ObservationLogPort):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sessions = session_factory

    # ------------------------------------------------------------------
    # Senior / Enrolment
    # ------------------------------------------------------------------

    async def save_senior(self, senior: Senior) -> None:
        async with self._sessions() as session:
            existing = await session.get(SeniorRow, senior.id)
            if existing is None:
                session.add(_senior_row(senior))
                await session.commit()

    async def get_senior(self, senior_id: UUID) -> Senior | None:
        async with self._sessions() as session:
            row = await session.get(SeniorRow, senior_id)
            if row is None:
                return None
            return Senior(
                id=row.id,
                display_name=row.display_name,
                preferred_language=row.preferred_language,
                created_at=_aware_utc(row.created_at),
            )

    async def list_senior_ids(self) -> list[UUID]:
        async with self._sessions() as session:
            rows = (
                await session.execute(select(SeniorRow.id).order_by(SeniorRow.created_at))
            ).scalars().all()
            return list(rows)

    async def get_enrolment(self, senior_id: UUID) -> Enrolment | None:
        async with self._sessions() as session:
            row = await session.scalar(
                select(EnrolmentRow).where(EnrolmentRow.senior_id == senior_id)
            )
            return _enrolment_from_row(row) if row else None

    async def save_enrolment(self, enrolment: Enrolment) -> None:
        async with self._sessions() as session:
            row = await session.scalar(
                select(EnrolmentRow).where(EnrolmentRow.senior_id == enrolment.senior_id)
            )
            if row is None:
                session.add(_enrolment_row(enrolment))
            else:
                row.enrolled_at = enrolment.enrolled_at
                row.artefacts = sorted(a.value for a in enrolment.artefacts)
                row.withdrawn_at = enrolment.withdrawn_at
            await session.commit()

    # ------------------------------------------------------------------
    # Interaction (AD-14)
    # ------------------------------------------------------------------

    async def save_interaction(self, interaction: Interaction) -> None:
        async with self._sessions() as session:
            existing = await session.scalar(
                select(InteractionRow).where(
                    InteractionRow.idempotency_key == interaction.idempotency_key
                )
            )
            if existing is not None:
                raise DuplicateInteractionError(
                    f"Interaction idempotency key already seen: {interaction.idempotency_key}"
                )
            session.add(
                InteractionRow(
                    id=interaction.id,
                    senior_id=interaction.senior_id,
                    occurred_at=interaction.occurred_at,
                    idempotency_key=interaction.idempotency_key,
                )
            )
            await session.commit()

    async def get_interaction(self, interaction_id: UUID) -> Interaction | None:
        async with self._sessions() as session:
            row = await session.get(InteractionRow, interaction_id)
            if row is None:
                return None
            return Interaction(
                id=row.id,
                senior_id=row.senior_id,
                occurred_at=_aware_utc(row.occurred_at),
                idempotency_key=row.idempotency_key,
            )

    # ------------------------------------------------------------------
    # Observation — append-only (AD-1, AD-10, AD-4)
    # ------------------------------------------------------------------

    async def append_observation(self, observation: Observation) -> None:
        if observation.provenance is None:
            raise MissingProvenanceError("Observation provenance is required (AD-10).")

        async with self._sessions() as session:
            enrolment_row = await session.scalar(
                select(EnrolmentRow).where(EnrolmentRow.senior_id == observation.senior_id)
            )
            enrolment = _enrolment_from_row(enrolment_row) if enrolment_row else None
            if enrolment is None or not enrolment.is_active:
                raise InactiveEnrolmentError(
                    f"Senior {observation.senior_id} has no active enrolment (AD-4)."
                )

            if await session.get(ObservationRow, observation.id) is not None:
                raise ImmutableObservationError(
                    f"Observation {observation.id} already exists; use a superseding event (AD-1)."
                )

            session.add(_observation_row(observation))
            await session.commit()

    async def get_observation(self, observation_id: UUID) -> Observation | None:
        async with self._sessions() as session:
            row = await session.get(ObservationRow, observation_id)
            return _observation_from_row(row) if row else None

    # ------------------------------------------------------------------
    # Windowed read model — no comparison primitives (AD-3)
    # ------------------------------------------------------------------

    async def get_window(
        self,
        senior_id: UUID,
        from_utc: datetime,
        to_utc: datetime,
    ) -> list[Observation]:
        async with self._sessions() as session:
            gap_rows = (
                await session.execute(select(GapRow).where(GapRow.senior_id == senior_id))
            ).scalars().all()
            gap_periods = [(g.started_at, g.ended_at) for g in gap_rows]

            rows = (
                await session.execute(
                    select(ObservationRow)
                    .where(
                        ObservationRow.senior_id == senior_id,
                        ObservationRow.occurred_at >= from_utc,
                        ObservationRow.occurred_at <= to_utc,
                    )
                    .order_by(ObservationRow.id)  # UUIDv7 => insertion order
                )
            ).scalars().all()

            def in_gap(occurred_at: datetime) -> bool:
                at = _aware_utc(occurred_at)
                for start, end in gap_periods:
                    s, e = _aware_utc(start), _aware_utc(end) if end else None
                    if e is None:
                        if at >= s:
                            return True
                    elif s <= at <= e:
                        return True
                return False

            return [_observation_from_row(r) for r in rows if not in_gap(r.occurred_at)]

    # ------------------------------------------------------------------
    # Gap (AD-6)
    # ------------------------------------------------------------------

    async def append_gap(self, gap: Gap) -> None:
        async with self._sessions() as session:
            session.add(
                GapRow(
                    id=gap.id,
                    senior_id=gap.senior_id,
                    reason=gap.reason.value,
                    started_at=gap.started_at,
                    ended_at=gap.ended_at,
                )
            )
            await session.commit()

    async def close_gap(self, gap_id: UUID, ended_at: datetime) -> None:
        async with self._sessions() as session:
            row = await session.get(GapRow, gap_id)
            if row is not None:
                row.ended_at = ended_at
                await session.commit()

    # ------------------------------------------------------------------
    # Tombstone and collection stop (AD-13)
    # ------------------------------------------------------------------

    async def deactivate_enrolment(self, senior_id: UUID, at: datetime) -> None:
        async with self._sessions() as session:
            row = await session.scalar(
                select(EnrolmentRow).where(EnrolmentRow.senior_id == senior_id)
            )
            if row is not None:
                row.withdrawn_at = at
                await session.commit()

    async def append_tombstone(self, tombstone: Tombstone) -> None:
        async with self._sessions() as session:
            session.add(
                TombstoneRow(
                    id=tombstone.id,
                    senior_id=tombstone.senior_id,
                    reason=tombstone.reason.value,
                    shredded_at=tombstone.shredded_at,
                    stores_shredded=sorted(tombstone.stores_shredded),
                )
            )
            await session.commit()

    async def get_tombstone(self, senior_id: UUID) -> Tombstone | None:
        async with self._sessions() as session:
            row = await session.scalar(
                select(TombstoneRow).where(TombstoneRow.senior_id == senior_id)
            )
            return _tombstone_from_row(row) if row else None


__all__ = ["PostgresObservationLog", "Base"]

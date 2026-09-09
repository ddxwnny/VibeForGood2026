"""
Observation log port — the interface the domain owns for writing and reading
the append-only series. Adapters implement this; core imports nothing from adapters.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
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


class ObservationLogPort(ABC):
    """
    Write side: append-only. No update, no delete (AD-1).
    Read side: windowed per senior, no comparison primitives (AD-3, Story 1.2).
    """

    # ------------------------------------------------------------------
    # Senior and enrolment (owned by Enrolment context, AD-7)
    # ------------------------------------------------------------------

    @abstractmethod
    async def save_senior(self, senior: Senior) -> None: ...

    @abstractmethod
    async def get_senior(self, senior_id: UUID) -> Senior | None: ...

    @abstractmethod
    async def list_senior_ids(self) -> list[UUID]:
        """Returns every enrolled senior id, in insertion/enrolment order (AD-7, FR-29)."""
        ...

    @abstractmethod
    async def get_enrolment(self, senior_id: UUID) -> Enrolment | None: ...

    @abstractmethod
    async def save_enrolment(self, enrolment: Enrolment) -> None: ...

    # ------------------------------------------------------------------
    # Interaction (minted by device, AD-14)
    # ------------------------------------------------------------------

    @abstractmethod
    async def save_interaction(self, interaction: Interaction) -> None:
        """Idempotent on interaction.idempotency_key (AD-14)."""
        ...

    @abstractmethod
    async def get_interaction(self, interaction_id: UUID) -> Interaction | None: ...

    # ------------------------------------------------------------------
    # Observation (append-only, provenance required, AD-1, AD-10)
    # ------------------------------------------------------------------

    @abstractmethod
    async def append_observation(self, observation: Observation) -> None:
        """
        Appends an immutable Observation event.
        Raises MissingProvenanceError if provenance is incomplete (AD-10).
        Raises InactiveEnrolmentError if the senior has no active enrolment (AD-4).
        Never updates an existing row.
        """
        ...

    @abstractmethod
    async def get_observation(self, observation_id: UUID) -> Observation | None: ...

    # ------------------------------------------------------------------
    # Windowed read model — no comparison primitives (AD-3, Story 1.2)
    # ------------------------------------------------------------------

    @abstractmethod
    async def get_window(
        self,
        senior_id: UUID,
        from_utc: datetime,
        to_utc: datetime,
    ) -> list[Observation]:
        """
        Returns dated, quotable Observation entries for the window.
        Gap periods are excluded from the result (AD-6, FR-24).
        This method MUST NOT sort, score, aggregate, or compare entries —
        it returns them in insertion order only (AD-3).
        """
        ...

    # ------------------------------------------------------------------
    # Gap (device liveness, AD-6)
    # ------------------------------------------------------------------

    @abstractmethod
    async def append_gap(self, gap: Gap) -> None: ...

    @abstractmethod
    async def close_gap(self, gap_id: UUID, ended_at: datetime) -> None: ...

    # ------------------------------------------------------------------
    # Tombstone and collection stop (erasure, AD-13)
    # ------------------------------------------------------------------

    @abstractmethod
    async def deactivate_enrolment(self, senior_id: UUID, at: datetime) -> None:
        """
        Stops collection for a senior by marking their enrolment withdrawn as
        of ``at``. Covers both withdrawal and death — once a senior is erased,
        the write path (AD-4) rejects further observations.
        """
        ...

    @abstractmethod
    async def append_tombstone(self, tombstone: Tombstone) -> None:
        """
        Appends a Tombstone event. The log is append-only (AD-1); this records
        the erasure without deleting anything. The content is unrecoverable
        because the per-senior key has already been destroyed (AD-13).
        """
        ...

    @abstractmethod
    async def get_tombstone(self, senior_id: UUID) -> Tombstone | None:
        """Returns the senior's Tombstone if one exists — verifies erasure."""

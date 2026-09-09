"""
Raw audio port — the transient buffer holding interaction audio before it is
extracted, plus the discard and shred operations that guarantee it never lingers.

AD-2: raw audio is never durable. It exists only in memory, only for the
duration of one turn's transcription. This port models that transient buffer
so the retention sweep (Story 7.1) and the erasure path (Story 7.2, AD-13
reach) both have a seam to enforce the guarantee through.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class RawAudioRecord:
    """Metadata for a buffered, not-yet-discarded raw audio segment."""
    interaction_id: UUID
    senior_id: UUID
    recorded_at: datetime  # UTC


class RawAudioPort(ABC):
    @abstractmethod
    async def store_raw_audio(
        self,
        senior_id: UUID,
        interaction_id: UUID,
        audio_bytes: bytes,
        recorded_at: datetime,
    ) -> None:
        """Buffers a raw audio segment for one turn's transcription (transient)."""
        ...

    @abstractmethod
    async def list_raw_audio(self, senior_id: UUID) -> list[RawAudioRecord]:
        """Returns buffered raw audio for a senior, for inspection and tests."""
        ...

    @abstractmethod
    async def discard_before(self, cutoff: datetime) -> int:
        """
        Discards every segment recorded before ``cutoff`` and returns the
        number discarded. Used by the retention sweep (Story 7.1).
        """
        ...

    @abstractmethod
    async def shred_senior(self, senior_id: UUID) -> None:
        """Removes all buffered raw audio for a senior (erasure reach, AD-13)."""
        ...

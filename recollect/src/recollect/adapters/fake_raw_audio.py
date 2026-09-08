"""In-memory fake RawAudioPort for tests (Story 7.1 / Story 1.3)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from recollect.core.ports.raw_audio_port import RawAudioPort, RawAudioRecord


class FakeRawAudio(RawAudioPort):
    def __init__(self) -> None:
        self._records: list[RawAudioRecord] = []
        self._audio: dict[UUID, bytes] = {}  # interaction_id -> bytes

    async def store_raw_audio(
        self,
        senior_id: UUID,
        interaction_id: UUID,
        audio_bytes: bytes,
        recorded_at: datetime,
    ) -> None:
        self._records.append(
            RawAudioRecord(
                interaction_id=interaction_id,
                senior_id=senior_id,
                recorded_at=recorded_at,
            )
        )
        self._audio[interaction_id] = audio_bytes

    async def list_raw_audio(self, senior_id: UUID) -> list[RawAudioRecord]:
        return [r for r in self._records if r.senior_id == senior_id]

    async def discard_before(self, cutoff: datetime) -> int:
        removed = 0
        keep: list[RawAudioRecord] = []
        for r in self._records:
            if r.recorded_at < cutoff:
                self._audio.pop(r.interaction_id, None)
                removed += 1
            else:
                keep.append(r)
        self._records = keep
        return removed

    async def shred_senior(self, senior_id: UUID) -> None:
        keep: list[RawAudioRecord] = []
        for r in self._records:
            if r.senior_id == senior_id:
                self._audio.pop(r.interaction_id, None)
            else:
                keep.append(r)
        self._records = keep

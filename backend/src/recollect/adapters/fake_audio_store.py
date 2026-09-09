"""In-memory fake AudioStorePort for tests (Story 2.3 / Story 1.3)."""

from __future__ import annotations

import uuid

from recollect.core.ports.audio_store_port import AudioStorePort


class FakeAudioStore(AudioStorePort):
    def __init__(self) -> None:
        self._store: dict[str, bytes] = {}

    async def store_consent_audio(self, senior_id_str: str, audio_bytes: bytes) -> str:
        ref = f"consent-audio/{senior_id_str}/{uuid.uuid4()}"
        self._store[ref] = audio_bytes
        return ref

    async def get_consent_audio(self, audio_ref: str) -> bytes:
        return self._store[audio_ref]

    async def shred_senior(self, senior_id_str: str) -> None:
        prefix = f"consent-audio/{senior_id_str}/"
        for ref in [r for r in self._store if r.startswith(prefix)]:
            del self._store[ref]

"""TTS port — text-to-speech interface. ElevenLabs assumed (Architecture Spine, [ASSUMPTION])."""

from __future__ import annotations

from abc import ABC, abstractmethod


class TTSPort(ABC):
    @abstractmethod
    async def synthesise(self, text: str, language_tag: str) -> bytes:
        """Returns audio bytes for playback. Never persisted (AD-2)."""
        ...

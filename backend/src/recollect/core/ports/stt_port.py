"""STT port — speech-to-text interface. Vendor undecided (Architecture Spine Deferred).
Audio bytes are never persisted; the port receives them in-memory and returns text (AD-2)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class STTResult:
    transcript: str
    language_tag: str   # IETF BCP-47
    model_version: str  # recorded on every Observation (AD-15)
    confidence: float | None = None


class STTPort(ABC):
    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, language_hint: str) -> STTResult:
        """
        audio_bytes exist only for the duration of this call and are never
        written to storage inside this method (AD-2).
        """
        ...

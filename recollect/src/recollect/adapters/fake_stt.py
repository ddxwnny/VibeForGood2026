"""Fake STTPort for tests and dev defaults."""

from __future__ import annotations

from recollect.core.ports.stt_port import STTPort, STTResult


class FakeSTT(STTPort):
    def __init__(
        self,
        transcript: str = "Good morning aunty, took my medication.",
        language_tag: str = "zh-cmn-Hans-SG",
        model_version: str = "fake-stt-v1",
        confidence: float = 0.99,
    ) -> None:
        self.transcript = transcript
        self.language_tag = language_tag
        self.model_version = model_version
        self.confidence = confidence
        self.calls: list[tuple[bytes, str]] = []

    async def transcribe(self, audio_bytes: bytes, language_hint: str) -> STTResult:
        self.calls.append((audio_bytes, language_hint))
        return STTResult(
            transcript=self.transcript,
            language_tag=language_hint or self.language_tag,
            model_version=self.model_version,
            confidence=self.confidence,
        )

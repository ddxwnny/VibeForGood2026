"""
Deepgram STT adapter — implementation of STTPort using Deepgram's API.

Audio bytes exist only for the duration of this call and are never written to
storage inside it (AD-2). Deepgram's API is invoked via HTTP POST with in-memory
audio bytes.
"""

from __future__ import annotations

import httpx

from recollect.core.ports.stt_port import STTPort, STTResult


class DeepgramSTT(STTPort):
    """
    STTPort adapter talking to Deepgram's /v1/listen endpoint.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.deepgram.com",
        model: str = "nova-3",
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._client = client or httpx.AsyncClient(base_url=base_url, timeout=60.0)

    async def transcribe(self, audio_bytes: bytes, language_hint: str) -> STTResult:
        headers = {
            "Authorization": f"Token {self._api_key}",
            "Content-Type": "audio/*",
        }
        params: dict[str, str] = {
            "model": self._model,
            "smart_format": "true",
        }
        if language_hint:
            params["language"] = language_hint

        resp = await self._client.post(
            "/v1/listen",
            content=audio_bytes,
            params=params,
            headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()

        # Parse Deepgram response schema:
        # results -> channels[0] -> alternatives[0] -> transcript
        try:
            channel = data["results"]["channels"][0]
            alt = channel["alternatives"][0]
            transcript = alt.get("transcript", "")
            confidence = alt.get("confidence")
            detected_language = channel.get("detected_language") or language_hint
        except (KeyError, IndexError, TypeError):
            transcript = ""
            confidence = None
            detected_language = language_hint

        model_version = f"deepgram-{self._model}"
        return STTResult(
            transcript=transcript,
            language_tag=detected_language or "en",
            model_version=model_version,
            confidence=confidence,
        )

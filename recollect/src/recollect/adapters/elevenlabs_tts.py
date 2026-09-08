"""
ElevenLabs TTS adapter — real implementation of TTSPort (assumed vendor).

Synthesises speech from text and returns audio bytes. The bytes are returned
in-memory only and never persisted (AD-2). The adapter owns nothing about
policy — it just speaks the text it is given.
"""

from __future__ import annotations

import httpx

from recollect.core.ports.tts_port import TTSPort

DEFAULT_BASE_URL = "https://api.elevenlabs.io"
MODEL_ID = "eleven_multilingual_v2"


class ElevenLabsTTS(TTSPort):
    def __init__(
        self,
        api_key: str,
        voice_id: str,
        client: httpx.AsyncClient | None = None,
        base_url: str = DEFAULT_BASE_URL,
    ) -> None:
        self._api_key = api_key
        self._voice_id = voice_id
        self._client = client or httpx.AsyncClient(base_url=base_url, timeout=60.0)

    async def synthesise(self, text: str, language_tag: str) -> bytes:
        resp = await self._client.post(
            f"/v1/text-to-speech/{self._voice_id}",
            json={"text": text, "model_id": MODEL_ID},
            headers={"xi-api-key": self._api_key, "content-type": "application/json"},
        )
        resp.raise_for_status()
        return resp.content

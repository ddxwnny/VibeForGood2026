"""
STT adapter — real implementation of STTPort behind a configurable HTTP
provider.

The STT vendor is UNDECIDED (Architecture Spine "Deferred"): Deepgram was
removed (cannot transcribe the target languages) and no replacement has been
selected pending a bake-off. This adapter is the integration seam: it posts the
in-memory audio bytes to the configured provider and maps the response to the
STTResult contract. When a vendor is chosen, only the request/response mapping
here changes — the port and the rest of the pipeline do not.

Audio bytes exist only for the duration of this call and are never written to
storage inside it (AD-2).
"""

from __future__ import annotations

import httpx

from recollect.core.ports.stt_port import STTPort, STTResult


class HttpSTT(STTPort):
    def __init__(
        self,
        base_url: str,
        api_key: str = "",
        client: httpx.AsyncClient | None = None,
        transcribe_path: str = "/transcribe",
    ) -> None:
        self._api_key = api_key
        self._transcribe_path = transcribe_path
        self._client = client or httpx.AsyncClient(base_url=base_url, timeout=60.0)

    async def transcribe(self, audio_bytes: bytes, language_hint: str) -> STTResult:
        headers = {"content-type": "application/octet-stream"}
        if self._api_key:
            headers["authorization"] = f"Bearer {self._api_key}"

        resp = await self._client.post(
            self._transcribe_path,
            content=audio_bytes,
            params={"language": language_hint},
            headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()
        return STTResult(
            transcript=data["transcript"],
            language_tag=data.get("language_tag", language_hint),
            model_version=data.get("model_version", "unknown"),
            confidence=data.get("confidence"),
        )

"""Tests for the ElevenLabs TTS adapter (mocked HTTP transport)."""

import httpx
import pytest

from recollect.adapters.elevenlabs_tts import ElevenLabsTTS


@pytest.mark.asyncio
async def test_synthesise_returns_audio_bytes() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, content=b"\x00fake-audio")

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://api.elevenlabs.io")
    tts = ElevenLabsTTS(api_key="k", voice_id="voice-1", client=client)

    audio = await tts.synthesise("hello", "en-SG")

    assert audio == b"\x00fake-audio"
    req = captured[0]
    assert req.url.path == "/v1/text-to-speech/voice-1"
    assert req.headers["xi-api-key"] == "k"

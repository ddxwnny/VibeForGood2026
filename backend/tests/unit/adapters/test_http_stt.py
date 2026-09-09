"""Tests for the HTTP STT adapter (mocked HTTP transport)."""

import httpx
import pytest

from recollect.adapters.http_stt import HttpSTT


@pytest.mark.asyncio
async def test_transcribe_maps_response() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            200,
            json={"transcript": "took my dose", "language_tag": "zh-cmn-Hans-SG", "model_version": "stt-v1"},
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://stt.example")
    stt = HttpSTT(base_url="https://stt.example", api_key="k", client=client)

    result = await stt.transcribe(b"\x00audio", "zh-cmn-Hans-SG")

    assert result.transcript == "took my dose"
    assert result.language_tag == "zh-cmn-Hans-SG"
    assert result.model_version == "stt-v1"

    req = captured[0]
    assert req.url.path == "/transcribe"
    assert req.content == b"\x00audio"
    assert req.headers["authorization"] == "Bearer k"


@pytest.mark.asyncio
async def test_deepgram_transcribe_maps_response() -> None:
    from recollect.adapters.deepgram_stt import DeepgramSTT

    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            200,
            json={
                "results": {
                    "channels": [
                        {
                            "alternatives": [
                                {
                                    "transcript": "hello aunty how are you",
                                    "confidence": 0.98,
                                }
                            ],
                            "detected_language": "en-SG",
                        }
                    ]
                }
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://api.deepgram.com")
    stt = DeepgramSTT(api_key="test-dg-key", client=client, model="nova-3")

    result = await stt.transcribe(b"\x00audiobytes", "en-SG")

    assert result.transcript == "hello aunty how are you"
    assert result.language_tag == "en-SG"
    assert result.model_version == "deepgram-nova-3"
    assert result.confidence == 0.98

    req = captured[0]
    assert req.url.path == "/v1/listen"
    assert req.content == b"\x00audiobytes"
    assert req.headers["authorization"] == "Token test-dg-key"
    assert req.headers["content-type"] == "audio/*"
    assert "model=nova-3" in str(req.url)
    assert "smart_format=true" in str(req.url)
    assert "language=en-SG" in str(req.url)

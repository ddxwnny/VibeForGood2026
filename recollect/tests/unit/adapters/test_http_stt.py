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

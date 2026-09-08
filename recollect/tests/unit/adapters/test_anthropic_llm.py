"""Tests for the Anthropic LLM adapter (mocked HTTP transport)."""

import httpx
import pytest

from recollect.adapters.anthropic_llm import AnthropicLLM
from recollect.core.ports.llm_port import LLMRequest


@pytest.mark.asyncio
async def test_complete_maps_messages_api() -> None:
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            200,
            json={"model": "claude-sonnet-5", "content": [{"type": "text", "text": "hello there"}]},
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://api.anthropic.com")
    llm = AnthropicLLM(api_key="k", model_id="claude-sonnet-5", client=client)

    resp = await llm.complete(
        LLMRequest(system_prompt="sys", user_message="hi", model_id="claude-sonnet-5", prompt_version="v1")
    )

    assert resp.content == "hello there"
    assert resp.model_id == "claude-sonnet-5"
    assert resp.prompt_version == "v1"

    req = captured[0]
    assert req.url.path == "/v1/messages"
    assert req.headers["x-api-key"] == "k"
    body = req.read().decode()
    assert '"model":"claude-sonnet-5"' in body
    assert '"messages"' in body


@pytest.mark.asyncio
async def test_complete_uses_default_model_when_request_omits_it() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"model": "claude-sonnet-5", "content": [{"type": "text", "text": "x"}]})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://api.anthropic.com")
    llm = AnthropicLLM(api_key="k", model_id="claude-sonnet-5", client=client)

    resp = await llm.complete(LLMRequest(system_prompt="s", user_message="u", model_id="", prompt_version="v1"))
    assert resp.content == "x"

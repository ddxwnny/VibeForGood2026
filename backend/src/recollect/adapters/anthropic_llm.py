"""
Anthropic LLM adapter — real implementation of LLMPort (decided vendor, AD-12).

Calls the Anthropic Messages API. The model id is pinned per request (AD-15);
the prompt version is carried through to the response so it lands on every
Observation. The model is an adapter, never the policy (AD-12).
"""

from __future__ import annotations

import httpx

from recollect.core.ports.llm_port import LLMPort, LLMRequest, LLMResponse

ANTHROPIC_VERSION = "2023-06-01"
DEFAULT_BASE_URL = "https://api.anthropic.com"


class AnthropicLLM(LLMPort):
    def __init__(
        self,
        api_key: str,
        model_id: str,
        client: httpx.AsyncClient | None = None,
        base_url: str = DEFAULT_BASE_URL,
        max_tokens: int = 1024,
    ) -> None:
        self._api_key = api_key
        self._model_id = model_id
        self._max_tokens = max_tokens
        self._client = client or httpx.AsyncClient(base_url=base_url, timeout=60.0)

    async def complete(self, request: LLMRequest) -> LLMResponse:
        payload = {
            "model": request.model_id or self._model_id,
            "max_tokens": self._max_tokens,
            "system": request.system_prompt,
            "messages": [{"role": "user", "content": request.user_message}],
        }
        resp = await self._client.post(
            "/v1/messages",
            json=payload,
            headers={
                "x-api-key": self._api_key,
                "anthropic-version": ANTHROPIC_VERSION,
                "content-type": "application/json",
            },
        )
        resp.raise_for_status()
        data = resp.json()
        content = "".join(
            block.get("text", "")
            for block in data.get("content", [])
            if block.get("type") == "text"
        )
        return LLMResponse(
            content=content,
            model_id=data.get("model", request.model_id),
            prompt_version=request.prompt_version,
        )

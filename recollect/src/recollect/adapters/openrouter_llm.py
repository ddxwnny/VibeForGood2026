"""
OpenRouter LLM adapter — implementation of LLMPort for OpenRouter API.

Supports free and low-cost hosted models for testing (e.g. meta-llama/llama-3.3-70b-instruct:free).
The model is an adapter, never the policy (AD-12).
"""

from __future__ import annotations

import httpx

from recollect.core.ports.llm_port import LLMPort, LLMRequest, LLMResponse

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class OpenRouterLLM(LLMPort):
    def __init__(
        self,
        api_key: str,
        model_id: str = "meta-llama/llama-3.3-70b-instruct:free",
        client: httpx.AsyncClient | None = None,
        base_url: str = OPENROUTER_BASE_URL,
        max_tokens: int = 150,
        timeout: float = 6.0,
    ) -> None:
        self._api_key = api_key
        self._model_id = model_id
        self._max_tokens = max_tokens
        self._client = client or httpx.AsyncClient(base_url=base_url, timeout=timeout)

    async def complete(self, request: LLMRequest) -> LLMResponse:
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.user_message})

        payload = {
            "model": request.model_id or self._model_id,
            "max_tokens": self._max_tokens,
            "messages": messages,
            "reasoning": {"effort": "none"},
        }
        resp = await self._client.post(
            "/chat/completions",
            json=payload,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Recollect",
            },
        )
        resp.raise_for_status()
        data = resp.json()
        choices = data.get("choices", [])
        content = ""
        if choices:
            msg = choices[0].get("message", {})
            content = msg.get("content") or ""
            if not content:
                content = msg.get("reasoning") or ""
            if "<think>" in content:
                import re
                content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

        return LLMResponse(
            content=content,
            model_id=data.get("model", request.model_id or self._model_id),
            prompt_version=request.prompt_version,
        )

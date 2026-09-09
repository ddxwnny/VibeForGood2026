"""
Groq LLM adapter — implementation of LLMPort for Groq Cloud API.

Ultra-low latency, generous free tier (thousands of requests per day).
The model is an adapter, never the policy (AD-12).
"""

from __future__ import annotations

import re
import httpx

from recollect.core.ports.llm_port import LLMPort, LLMRequest, LLMResponse

GROQ_BASE_URL = "https://api.groq.com/openai/v1"


class GroqLLM(LLMPort):
    def __init__(
        self,
        api_key: str,
        model_id: str = "qwen/qwen3.8-27b",
        client: httpx.AsyncClient | None = None,
        base_url: str = GROQ_BASE_URL,
        max_tokens: int = 150,
        timeout: float = 8.0,
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
            "temperature": 0.6,
        }
        resp = await self._client.post(
            "/chat/completions",
            json=payload,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
        )
        resp.raise_for_status()
        data = resp.json()
        choices = data.get("choices", [])
        content = ""
        if choices:
            msg = choices[0].get("message", {})
            content = msg.get("content") or ""
            if "<think>" in content:
                content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

        return LLMResponse(
            content=content,
            model_id=data.get("model", request.model_id or self._model_id),
            prompt_version=request.prompt_version,
        )


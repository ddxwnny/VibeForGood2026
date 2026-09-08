"""LLM port — the domain's interface for language model calls.
The model is an adapter, never the policy (AD-12)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMRequest:
    system_prompt: str
    user_message: str
    model_id: str       # pinned, never a floating alias (AD-15)
    prompt_version: str # recorded on every Observation (AD-15)


@dataclass(frozen=True)
class LLMResponse:
    content: str
    model_id: str
    prompt_version: str


class LLMPort(ABC):
    @abstractmethod
    async def complete(self, request: LLMRequest) -> LLMResponse: ...

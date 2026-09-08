"""Domain ports (interfaces the domain owns).

Adapters implement these; core depends only on these, never on a concrete adapter.
Story 1.3 fills in the full set (LLM, STT, TTS, ObservationLog). The Clock port is
defined now because it is stable and load-bearing for AD-11 (UTC storage, injectable time).
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    """A source of the current instant, injected so time is testable (AD-11)."""

    def now(self) -> datetime: ...

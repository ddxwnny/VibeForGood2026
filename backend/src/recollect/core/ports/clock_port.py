"""Clock port — lets core request the current UTC time without importing datetime directly.
Swappable for a fake in tests (Story 1.3)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone


class ClockPort(ABC):
    @abstractmethod
    def utc_now(self) -> datetime: ...


class SystemClock(ClockPort):
    def utc_now(self) -> datetime:
        return datetime.now(timezone.utc)

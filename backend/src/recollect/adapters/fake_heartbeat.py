"""Fake HeartbeatPort for tests."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from recollect.core.ports.heartbeat_port import HeartbeatPort


class FakeHeartbeat(HeartbeatPort):
    def __init__(self, beats: dict[UUID, datetime] | None = None) -> None:
        self._beats: dict[UUID, datetime] = beats or {}

    def set_heartbeat(self, senior_id: UUID, at: datetime) -> None:
        self._beats[senior_id] = at

    async def record_heartbeat(self, senior_id: UUID, at: datetime) -> None:
        self._beats[senior_id] = at

    async def last_heartbeat_at(self, senior_id: UUID) -> datetime | None:
        return self._beats.get(senior_id)

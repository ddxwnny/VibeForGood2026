"""PostgresHeartbeat — real heartbeat adapter (AD-6)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from uuid_extensions import uuid7

from recollect.adapters.postgres.models import HeartbeatRow
from recollect.core.ports.heartbeat_port import HeartbeatPort


class PostgresHeartbeat(HeartbeatPort):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sessions = session_factory

    async def record_heartbeat(self, senior_id: UUID, at: datetime) -> None:
        async with self._sessions() as session:
            session.add(HeartbeatRow(id=uuid7(), senior_id=senior_id, at=at))
            await session.commit()

    async def last_heartbeat_at(self, senior_id: UUID) -> datetime | None:
        async with self._sessions() as session:
            result = await session.scalar(
                select(func.max(HeartbeatRow.at)).where(HeartbeatRow.senior_id == senior_id)
            )
            return result

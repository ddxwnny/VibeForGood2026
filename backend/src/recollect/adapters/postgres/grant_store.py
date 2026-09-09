"""PostgresGrantStore — real grant adapter (AD-7, AD-16/NFR-15)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from recollect.adapters.postgres.models import GrantRow
from recollect.core.entities import Grant, GrantRole, GrantScope
from recollect.core.ports.grant_store_port import GrantCredential, GrantStorePort


class _GrantNotFound(Exception):
    pass


class PostgresGrantStore(GrantStorePort):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sessions = session_factory

    async def save_grant(self, grant: Grant, api_key_hash: str) -> None:
        async with self._sessions() as session:
            session.add(
                GrantRow(
                    id=grant.id,
                    senior_id=grant.senior_id,
                    role=grant.role.value,
                    scope=grant.scope.value,
                    api_key_hash=api_key_hash,
                    granted_at=grant.granted_at,
                    revoked_at=grant.revoked_at,
                )
            )
            await session.commit()

    async def get_grant_by_key_hash(self, api_key_hash: str) -> list[GrantCredential]:
        async with self._sessions() as session:
            rows = (
                await session.execute(
                    select(GrantRow).where(GrantRow.api_key_hash == api_key_hash)
                )
            ).scalars().all()

        return [
            GrantCredential(
                grant_id=row.id,
                senior_id=row.senior_id,
                role=GrantRole(row.role),
                scope=GrantScope(row.scope),
                is_active=row.revoked_at is None,
            )
            for row in rows
        ]

    async def revoke_grant(self, grant_id: UUID, at: datetime) -> None:
        async with self._sessions() as session:
            row = await session.get(GrantRow, grant_id)
            if row is None:
                raise _GrantNotFound(f"Grant {grant_id} does not exist.")
            row.revoked_at = at
            await session.commit()

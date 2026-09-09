"""In-memory fake GrantStorePort for tests (AD-7, Story 1.3)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from recollect.core.entities import Grant
from recollect.core.ports.grant_store_port import GrantCredential, GrantStorePort


class FakeGrantStore(GrantStorePort):
    def __init__(self) -> None:
        self._grants: dict[UUID, tuple[Grant, str]] = {}   # grant_id -> (grant, key_hash)

    async def save_grant(self, grant: Grant, api_key_hash: str) -> None:
        self._grants[grant.id] = (grant, api_key_hash)

    async def get_grant_by_key_hash(self, api_key_hash: str) -> list[GrantCredential]:
        result: list[GrantCredential] = []
        for grant, key_hash in self._grants.values():
            if key_hash == api_key_hash:
                result.append(GrantCredential(
                    grant_id=grant.id,
                    senior_id=grant.senior_id,
                    role=grant.role,
                    scope=grant.scope,
                    is_active=grant.is_active,
                ))
        return result

    async def revoke_grant(self, grant_id: UUID, at: datetime) -> None:
        if grant_id in self._grants:
            grant, key_hash = self._grants[grant_id]
            self._grants[grant_id] = (
                Grant(
                    id=grant.id,
                    senior_id=grant.senior_id,
                    role=grant.role,
                    scope=grant.scope,
                    granted_at=grant.granted_at,
                    revoked_at=at,
                ),
                key_hash,
            )

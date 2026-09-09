"""
Grant store port — authorises a person (by role) against a senior's data.

AD-7: family members and care workers are Grants, not entities of their own.
AD-16/NFR-15: care worker and family authenticate on the phone surface; the
senior never authenticates. This port lets the delivery layer resolve an
incoming credential (an API key) to an active Grant and check its scope
against a senior — without core knowing anything about HTTP or secrets.

The credential itself is never stored in the clear: callers hand this port a
one-way hash, and the adapter compares hashes. Nothing that reaches a backup
holds a live secret.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from recollect.core.entities import Grant, GrantRole, GrantScope


@dataclass(frozen=True)
class GrantCredential:
    """A resolved credential presented by a human-surface caller."""
    grant_id: UUID
    senior_id: UUID
    role: GrantRole
    scope: GrantScope
    is_active: bool


class GrantStorePort(ABC):
    @abstractmethod
    async def save_grant(self, grant: Grant, api_key_hash: str) -> None:
        """Persists a Grant with a hashed credential. AD-7: one owner, scoped access."""
        ...

    @abstractmethod
    async def get_grant_by_key_hash(self, api_key_hash: str) -> list[GrantCredential]:
        """
        Resolves a credential to its active Grant credentials. An API key may
        authorise more than one senior (e.g. a care worker's caseload).
        """
        ...

    @abstractmethod
    async def revoke_grant(self, grant_id: UUID, at: datetime) -> None:
        """Revokes a Grant so its credential no longer authorises access."""
        ...

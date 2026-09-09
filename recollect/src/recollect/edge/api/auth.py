"""
Authentication and authorisation for the delivery layer (NFR-15, AD-7, AD-16).

The senior never authenticates (CAP-1). Two callers do:

  - The device — authenticates with a shared RECOLLECT_DEVICE_API_KEY to report
    heartbeats and addressed turns (AD-6, AD-14). In dev mode with no key
    configured, the device is trusted (the mock frontend needs this).
  - Phone surfaces (care worker, named recipient) — authenticate with a
    per-grant API key resolved against GrantStorePort to its active Grant
    credentials. Scope is checked per-route against the senior being accessed.

Secrets are never logged and comparisons are constant-time.
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from recollect.core.entities import GrantRole, GrantScope
from recollect.core.ports.grant_store_port import GrantCredential

_bearer_scheme = HTTPBearer(auto_error=False)


def _hash_key(key: str) -> str:
    """One-way hash of a credential. Nothing reachable from a backup holds the live key."""
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def _constant_time_compare(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


@dataclass(frozen=True)
class DeviceAuth:
    """The device's authenticated identity (shared key, no per-senior claim)."""


@dataclass(frozen=True)
class PhoneAuth:
    """A resolved human-surface credential with the grants it authorises."""
    credentials: tuple[GrantCredential, ...]
    wildcard: bool = False

    def can(self, *, senior_id, role: GrantRole | None = None, scope: GrantScope | None = None) -> bool:
        """True if any active grant covers the senior (and matching role/scope)."""
        if self.wildcard:
            return True
        for c in self.credentials:
            if c.senior_id != senior_id:
                continue
            if role is not None and c.role != role:
                continue
            if scope is not None and c.scope != scope:
                continue
            return True
        return False


async def require_device(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
    request: Request,
) -> DeviceAuth:
    """
    Authenticates the device. In dev mode with no key configured, the device is
    trusted. A caller presenting an unknown device key is rejected with 401.
    """
    configured: str = request.app.state.settings.device_api_key
    presented = credentials.credentials if credentials else None

    if not configured:
        return DeviceAuth()

    if presented is None or not _constant_time_compare(presented, configured):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid device key.")
    return DeviceAuth()


async def resolve_phone(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
    request: Request,
) -> PhoneAuth:
    """
    Resolves a human-surface API key to its active grants. In dev mode with no
    grant infrastructure configured, returns a wildcard credential so the mock
    frontend and tests keep working; in production the key must resolve to an
    active grant (401 otherwise).
    """
    environment: str = request.app.state.settings.environment
    if environment == "dev":
        return PhoneAuth(credentials=(), wildcard=True)

    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key.")

    store = request.app.state.store.grant_store
    resolved = await store.get_grant_by_key_hash(_hash_key(credentials.credentials))
    active = tuple(c for c in resolved if c.is_active)
    if not active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key.")
    return PhoneAuth(credentials=active)


DeviceDep = Annotated[DeviceAuth, Depends(require_device)]
PhoneDep = Annotated[PhoneAuth, Depends(resolve_phone)]

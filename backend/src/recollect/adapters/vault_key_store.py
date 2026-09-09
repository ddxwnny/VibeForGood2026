"""
Vault key-store adapter — real implementation of KeyStorePort via HashiCorp
Vault's Transit engine.

Keys live in a dedicated key-management service, never in the application
database (AD-13 custody). Shredding deletes the Transit key; content encrypted
under it becomes unrecoverable. Shredding an already-deleted key is treated as
success so the erasure path stays idempotent.

Note: the custody/hosting decision (which KMS, which region) is still deferred
in the Architecture Spine; this adapter is written to the Vault Transit contract
so the decision is a configuration change, not a code change.
"""

from __future__ import annotations

from uuid import UUID

import httpx

from recollect.core.ports.key_store_port import KeyStorePort


class VaultKeyStore(KeyStorePort):
    def __init__(
        self,
        vault_url: str,
        vault_token: str,
        client: httpx.AsyncClient | None = None,
        mount: str = "transit",
    ) -> None:
        self._mount = mount
        self._client = client or httpx.AsyncClient(base_url=vault_url, timeout=30.0)
        self._headers = {"X-Vault-Token": vault_token}

    def _name(self, senior_id: UUID) -> str:
        return f"senior-{senior_id}"

    async def create_key(self, senior_id: UUID) -> None:
        resp = await self._client.post(
            f"/v1/{self._mount}/keys/{self._name(senior_id)}", headers=self._headers
        )
        resp.raise_for_status()

    async def shred_key(self, senior_id: UUID) -> None:
        resp = await self._client.delete(
            f"/v1/{self._mount}/keys/{self._name(senior_id)}", headers=self._headers
        )
        # 404 = key already gone; shredding is idempotent (AD-13).
        if resp.status_code == 404:
            return
        resp.raise_for_status()

    async def has_key(self, senior_id: UUID) -> bool:
        resp = await self._client.get(
            f"/v1/{self._mount}/keys/{self._name(senior_id)}", headers=self._headers
        )
        if resp.status_code == 404:
            return False
        resp.raise_for_status()
        return True

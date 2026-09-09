"""Tests for the Vault key-store adapter (mocked HTTP transport)."""

import httpx
import pytest
from uuid_extensions import uuid7

from recollect.adapters.vault_key_store import VaultKeyStore


@pytest.mark.asyncio
async def test_create_shred_has_key_cycle() -> None:
    senior_id = uuid7()
    key_name = f"senior-{senior_id}"
    exists = True

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal exists
        if request.method == "POST":
            exists = True
            return httpx.Response(204)
        if request.method == "DELETE":
            exists = False
            return httpx.Response(204)
        if request.method == "GET":
            return httpx.Response(200) if exists else httpx.Response(404)
        return httpx.Response(405)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://vault.example")
    store = VaultKeyStore(vault_url="https://vault.example", vault_token="t", client=client)

    await store.create_key(senior_id)
    assert await store.has_key(senior_id) is True

    await store.shred_key(senior_id)
    assert await store.has_key(senior_id) is False


@pytest.mark.asyncio
async def test_shred_is_idempotent() -> None:
    senior_id = uuid7()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)  # already gone

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://vault.example")
    store = VaultKeyStore(vault_url="https://vault.example", vault_token="t", client=client)

    # Must not raise even though the key does not exist.
    await store.shred_key(senior_id)

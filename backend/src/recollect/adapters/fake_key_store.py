"""In-memory fake KeyStorePort for tests (Story 7.2 / Story 1.3)."""

from __future__ import annotations

from uuid import UUID

from recollect.core.ports.key_store_port import KeyStorePort


class FakeKeyStore(KeyStorePort):
    def __init__(self) -> None:
        self._keys: set[UUID] = set()
        self.shredded: list[UUID] = []  # for inspection/verification

    async def create_key(self, senior_id: UUID) -> None:
        self._keys.add(senior_id)

    async def shred_key(self, senior_id: UUID) -> None:
        if senior_id in self._keys:
            self._keys.discard(senior_id)
            self.shredded.append(senior_id)

    async def has_key(self, senior_id: UUID) -> bool:
        return senior_id in self._keys

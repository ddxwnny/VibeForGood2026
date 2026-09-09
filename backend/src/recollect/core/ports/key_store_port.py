"""
Key store port — custody of the per-senior encryption key (AD-13).

Keys live in a dedicated key-management service, never in the application
database and never in any artefact that reaches a backup. The observation
log's payloads are encrypted under each senior's key; destroying the key is
what makes erasure real rather than cosmetic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID


class KeyStorePort(ABC):
    @abstractmethod
    async def create_key(self, senior_id: UUID) -> None:
        """Mints a per-senior key at enrolment. No-op if one already exists."""
        ...

    @abstractmethod
    async def shred_key(self, senior_id: UUID) -> None:
        """
        Destroys the senior's key. Idempotent — shredding a key that is
        already gone is not an error (AD-13).
        """
        ...

    @abstractmethod
    async def has_key(self, senior_id: UUID) -> bool:
        """True if a live key exists for the senior — used to verify erasure."""
        ...

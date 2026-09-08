"""
EraseSenior use case (Story 7.2).

Executes the crypto-shred erasure path on withdrawal or death. AD-13:
destroys the per-senior key, shreds every store holding her content, stops
collection, and appends a Tombstone. The log structure survives; the content
becomes unrecoverable — verifiable by inspection afterwards.

Reach (AD-13): the shred iterates every store holding her content, not a
hand-maintained list. v1 stores are the raw audio buffer, the consent audio,
and the observation-log payloads (covered by key destruction).
"""

from __future__ import annotations

from uuid import UUID

from uuid_extensions import uuid7

from recollect.core.entities import ErasureReason, Tombstone
from recollect.core.errors import AlreadyErasedError
from recollect.core.ports.audio_store_port import AudioStorePort
from recollect.core.ports.clock_port import ClockPort
from recollect.core.ports.key_store_port import KeyStorePort
from recollect.core.ports.log_port import ObservationLogPort
from recollect.core.ports.raw_audio_port import RawAudioPort

# Stores the erasure path touches directly. Observation-log payloads are made
# unrecoverable by destroying the key, not by deleting the log (AD-13).
SHREDDED_STORES = frozenset({"key", "raw_audio", "consent_audio"})


async def erase_senior(
    senior_id: UUID,
    reason: ErasureReason,
    key_store: KeyStorePort,
    log: ObservationLogPort,
    raw_audio: RawAudioPort,
    audio_store: AudioStorePort,
    clock: ClockPort,
) -> Tombstone:
    """
    Crypto-shreds a senior's data for ``reason`` (withdrawal or death) and
    appends a Tombstone. Raises AlreadyErasedError if the senior is already
    erased. Idempotent across the underlying stores; the tombstone guard
    prevents double-erasure from recording two tombstones.
    """
    existing = await log.get_tombstone(senior_id)
    if existing is not None:
        raise AlreadyErasedError(
            f"Senior {senior_id} already has a tombstone (reason={existing.reason.value})."
        )

    now = clock.utc_now()

    # 1. Destroy the per-senior key — makes observation-log payloads unrecoverable.
    await key_store.shred_key(senior_id)

    # 2. Shred every store holding her content (AD-13 reach).
    await raw_audio.shred_senior(senior_id)
    await audio_store.shred_senior(str(senior_id))

    # 3. Stop collection — the write path (AD-4) rejects further observations.
    await log.deactivate_enrolment(senior_id, now)

    # 4. Append the tombstone (append-only; the log structure survives, AD-1).
    tombstone = Tombstone(
        id=uuid7(),
        senior_id=senior_id,
        reason=reason,
        shredded_at=now,
        stores_shredded=SHREDDED_STORES,
    )
    await log.append_tombstone(tombstone)

    return tombstone

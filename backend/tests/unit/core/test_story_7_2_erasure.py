"""
Tests for Epic 7 — Story 7.2: Retention and erasure paths.

AC1: Given a withdrawal request, when it executes, then the crypto-shred path
     runs and is verifiable by inspection afterwards.
AC2: Every stored item has a defined retention, access boundary, and end-of-life
     path covering withdrawal and death.
"""

from datetime import datetime, timezone

import pytest
from uuid_extensions import uuid7

from recollect.adapters.fake_audio_store import FakeAudioStore
from recollect.adapters.fake_key_store import FakeKeyStore
from recollect.adapters.fake_log import FakeObservationLog
from recollect.adapters.fake_raw_audio import FakeRawAudio
from recollect.app.append_observation import append_observation
from recollect.app.erase_senior import SHREDDED_STORES, erase_senior
from recollect.core.entities import (
    ConsentArtifactKind,
    Enrolment,
    ErasureReason,
    Observation,
    Provenance,
    Senior,
    SignalType,
    TaskOutcome,
)
from recollect.core.errors import AlreadyErasedError, InactiveEnrolmentError
from recollect.core.ports.clock_port import ClockPort
from recollect.core.retention import RETENTION_CATALOG, retention_policy_for


def _utc(ts: str) -> datetime:
    return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)


NOW = _utc("2026-09-09T12:00:00")


class FakeClock(ClockPort):
    def __init__(self, now: datetime) -> None:
        self._now = now

    def utc_now(self) -> datetime:
        return self._now


@pytest.fixture
def log() -> FakeObservationLog:
    return FakeObservationLog()


@pytest.fixture
def key_store() -> FakeKeyStore:
    return FakeKeyStore()


@pytest.fixture
def raw_audio() -> FakeRawAudio:
    return FakeRawAudio()


@pytest.fixture
def audio_store() -> FakeAudioStore:
    return FakeAudioStore()


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock(NOW)


def _senior() -> Senior:
    return Senior(
        id=uuid7(),
        display_name="Mrs Tan",
        preferred_language="zh-cmn-Hans-SG",
        created_at=NOW,
    )


async def _enrol(log: FakeObservationLog, audio_store: FakeAudioStore, senior: Senior) -> str:
    """Creates an active enrolment with stored consent audio; returns the audio ref."""
    await log.save_senior(senior)
    await log.save_enrolment(Enrolment(
        id=uuid7(),
        senior_id=senior.id,
        enrolled_at=NOW,
        artefacts=ConsentArtifactKind.required_set(),
    ))
    ref = await audio_store.store_consent_audio(str(senior.id), b"own-voice-ulysses")
    return ref


def _observation(senior_id, occurred_at=None) -> Observation:
    return Observation(
        id=uuid7(),
        senior_id=senior_id,
        provenance=Provenance(
            interaction_id=uuid7(),
            occurred_at=occurred_at or NOW,
            signal_type=SignalType.ROUTINE,
            extraction_model_id="claude-sonnet-5",
            prompt_version="v1.0.0",
            stt_model_version="stt-v1",
        ),
        content="routine done",
        outcome=TaskOutcome.COMPLETED,
    )


# ===========================================================================
# Story 7.2 AC1: withdrawal executes the crypto-shred path, verifiable
# ===========================================================================

@pytest.mark.asyncio
async def test_withdrawal_shreds_key(
    log, key_store, raw_audio, audio_store, clock
) -> None:
    senior = _senior()
    await _enrol(log, audio_store, senior)
    await key_store.create_key(senior.id)

    await erase_senior(
        senior.id, ErasureReason.WITHDRAWAL, key_store, log, raw_audio, audio_store, clock
    )

    assert await key_store.has_key(senior.id) is False
    assert senior.id in key_store.shredded


@pytest.mark.asyncio
async def test_withdrawal_shreds_all_stores(
    log, key_store, raw_audio, audio_store, clock
) -> None:
    senior = _senior()
    await _enrol(log, audio_store, senior)
    await key_store.create_key(senior.id)
    await raw_audio.store_raw_audio(senior.id, uuid7(), b"raw", NOW)

    await erase_senior(
        senior.id, ErasureReason.WITHDRAWAL, key_store, log, raw_audio, audio_store, clock
    )

    assert await raw_audio.list_raw_audio(senior.id) == []
    # consent audio is gone: nothing under the senior's prefix remains
    remaining = [r for r in audio_store._store if r.startswith(f"consent-audio/{senior.id}/")]
    assert remaining == []


@pytest.mark.asyncio
async def test_withdrawal_appends_tombstone_verifiable(
    log, key_store, raw_audio, audio_store, clock
) -> None:
    senior = _senior()
    await _enrol(log, audio_store, senior)
    await key_store.create_key(senior.id)

    tombstone = await erase_senior(
        senior.id, ErasureReason.WITHDRAWAL, key_store, log, raw_audio, audio_store, clock
    )

    assert tombstone.reason == ErasureReason.WITHDRAWAL
    assert tombstone.senior_id == senior.id
    assert tombstone.stores_shredded == SHREDDED_STORES

    # Verifiable by inspection: tombstone recorded, key gone.
    recorded = await log.get_tombstone(senior.id)
    assert recorded is not None
    assert recorded.reason == ErasureReason.WITHDRAWAL
    assert await key_store.has_key(senior.id) is False


@pytest.mark.asyncio
async def test_collection_stops_after_erasure(
    log, key_store, raw_audio, audio_store, clock
) -> None:
    senior = _senior()
    await _enrol(log, audio_store, senior)
    await key_store.create_key(senior.id)

    await erase_senior(
        senior.id, ErasureReason.WITHDRAWAL, key_store, log, raw_audio, audio_store, clock
    )

    with pytest.raises(InactiveEnrolmentError):
        await append_observation(_observation(senior.id), log)


@pytest.mark.asyncio
async def test_death_executes_erasure_path(
    log, key_store, raw_audio, audio_store, clock
) -> None:
    senior = _senior()
    await _enrol(log, audio_store, senior)
    await key_store.create_key(senior.id)

    tombstone = await erase_senior(
        senior.id, ErasureReason.DEATH, key_store, log, raw_audio, audio_store, clock
    )

    assert tombstone.reason == ErasureReason.DEATH
    assert await key_store.has_key(senior.id) is False
    assert await log.get_tombstone(senior.id) is not None


@pytest.mark.asyncio
async def test_double_erasure_rejected(
    log, key_store, raw_audio, audio_store, clock
) -> None:
    senior = _senior()
    await _enrol(log, audio_store, senior)
    await key_store.create_key(senior.id)

    await erase_senior(
        senior.id, ErasureReason.WITHDRAWAL, key_store, log, raw_audio, audio_store, clock
    )

    with pytest.raises(AlreadyErasedError):
        await erase_senior(
            senior.id, ErasureReason.DEATH, key_store, log, raw_audio, audio_store, clock
        )


# ===========================================================================
# Story 7.2 AC2: every stored item has retention / access / end-of-life
# ===========================================================================

def test_every_catalogued_store_has_defined_policy() -> None:
    """FR-27: every store has a defined retention, access boundary, and EOL path."""
    assert RETENTION_CATALOG

    for policy in RETENTION_CATALOG:
        assert policy.store
        assert policy.retention
        assert policy.access_boundary
        assert policy.end_of_life


def test_catalogue_covers_erasure_reach_stores() -> None:
    """The stores the erasure path reaches are catalogued (AD-13 reach)."""
    for store in ("raw_audio", "consent_audio", "observation_log_payloads"):
        assert retention_policy_for(store) is not None, f"{store} missing from catalog"

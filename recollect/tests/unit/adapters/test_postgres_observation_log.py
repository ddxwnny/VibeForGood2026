"""
Tests for PostgresObservationLog against SQLite (aiosqlite).

The same adapter runs on PostgreSQL in production; here it exercises the full
ObservationLogPort contract against a real SQL database to prove the append-only,
consent, idempotency, windowing, and erasure invariants hold at the storage
boundary — not just in the in-memory fake.
"""

from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from uuid_extensions import uuid7

from recollect.adapters.postgres.models import Base
from recollect.adapters.postgres.observation_log import PostgresObservationLog
from recollect.core.entities import (
    ConsentArtifactKind,
    Enrolment,
    ErasureReason,
    Gap,
    GapReason,
    Interaction,
    Observation,
    Provenance,
    Senior,
    SignalType,
    TaskOutcome,
    Tombstone,
)
from recollect.core.errors import DuplicateInteractionError, ImmutableObservationError, InactiveEnrolmentError


def _utc(ts: str) -> datetime:
    return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)


NOW = _utc("2026-09-09T12:00:00")


@pytest.fixture
async def log():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    yield PostgresObservationLog(factory)
    await engine.dispose()


def _senior() -> Senior:
    return Senior(id=uuid7(), display_name="Mrs Tan", preferred_language="zh-cmn-Hans-SG", created_at=NOW)


def _active_enrolment(senior_id) -> Enrolment:
    return Enrolment(
        id=uuid7(), senior_id=senior_id, enrolled_at=NOW, artefacts=ConsentArtifactKind.required_set()
    )


def _observation(senior_id, occurred_at=None, signal_type=SignalType.ROUTINE) -> Observation:
    return Observation(
        id=uuid7(),
        senior_id=senior_id,
        provenance=Provenance(
            interaction_id=uuid7(),
            occurred_at=occurred_at or NOW,
            signal_type=signal_type,
            extraction_model_id="claude-sonnet-5",
            prompt_version="v1.0.0",
            stt_model_version="stt-v1",
        ),
        content="routine done",
        outcome=TaskOutcome.COMPLETED,
    )


@pytest.mark.asyncio
async def test_enrolment_roundtrip_is_active(log) -> None:
    senior = _senior()
    await log.save_senior(senior)
    await log.save_enrolment(_active_enrolment(senior.id))

    enrolment = await log.get_enrolment(senior.id)
    assert enrolment is not None
    assert enrolment.is_active is True
    assert enrolment.artefacts == ConsentArtifactKind.required_set()


@pytest.mark.asyncio
async def test_observation_window_roundtrip_preserves_provenance(log) -> None:
    senior = _senior()
    await log.save_senior(senior)
    await log.save_enrolment(_active_enrolment(senior.id))

    obs = _observation(senior.id)
    await log.append_observation(obs)

    window = await log.get_window(
        senior.id, from_utc=_utc("2026-09-08T00:00:00"), to_utc=_utc("2026-09-10T00:00:00")
    )
    assert len(window) == 1
    got = window[0]
    assert got.id == obs.id
    assert got.provenance.signal_type == SignalType.ROUTINE
    assert got.provenance.occurred_at.tzinfo is not None  # normalised to aware UTC (AD-11)
    assert got.content == "routine done"


@pytest.mark.asyncio
async def test_append_observation_rejects_without_active_enrolment(log) -> None:
    senior = _senior()
    await log.save_senior(senior)

    with pytest.raises(InactiveEnrolmentError):
        await log.append_observation(_observation(senior.id))


@pytest.mark.asyncio
async def test_interaction_idempotency_rejects_duplicate(log) -> None:
    senior = _senior()
    await log.save_senior(senior)

    interaction = Interaction(id=uuid7(), senior_id=senior.id, occurred_at=NOW, idempotency_key="key-1")
    await log.save_interaction(interaction)

    with pytest.raises(DuplicateInteractionError):
        await log.save_interaction(
            Interaction(id=uuid7(), senior_id=senior.id, occurred_at=NOW, idempotency_key="key-1")
        )


@pytest.mark.asyncio
async def test_observation_is_immutable(log) -> None:
    senior = _senior()
    await log.save_senior(senior)
    await log.save_enrolment(_active_enrolment(senior.id))

    obs = _observation(senior.id)
    await log.append_observation(obs)

    with pytest.raises(ImmutableObservationError):
        await log.append_observation(obs)


@pytest.mark.asyncio
async def test_window_excludes_gap_periods(log) -> None:
    senior = _senior()
    await log.save_senior(senior)
    await log.save_enrolment(_active_enrolment(senior.id))

    await log.append_gap(
        Gap(
            id=uuid7(),
            senior_id=senior.id,
            reason=GapReason.DEVICE_UNREACHABLE,
            started_at=_utc("2026-09-09T06:00:00"),
            ended_at=_utc("2026-09-09T10:00:00"),
        )
    )

    in_gap = _observation(senior.id, occurred_at=_utc("2026-09-09T08:00:00"))
    outside = _observation(senior.id, occurred_at=_utc("2026-09-09T14:00:00"))
    await log.append_observation(in_gap)
    await log.append_observation(outside)

    window = await log.get_window(
        senior.id, from_utc=_utc("2026-09-09T00:00:00"), to_utc=_utc("2026-09-09T23:59:59")
    )
    ids = {o.id for o in window}
    assert in_gap.id not in ids
    assert outside.id in ids


@pytest.mark.asyncio
async def test_deactivate_stops_collection(log) -> None:
    senior = _senior()
    await log.save_senior(senior)
    await log.save_enrolment(_active_enrolment(senior.id))

    await log.deactivate_enrolment(senior.id, NOW)

    enrolment = await log.get_enrolment(senior.id)
    assert enrolment.is_active is False

    with pytest.raises(InactiveEnrolmentError):
        await log.append_observation(_observation(senior.id))


@pytest.mark.asyncio
async def test_tombstone_roundtrip(log) -> None:
    senior = _senior()
    await log.save_senior(senior)

    tombstone = Tombstone(
        id=uuid7(),
        senior_id=senior.id,
        reason=ErasureReason.WITHDRAWAL,
        shredded_at=NOW,
        stores_shredded=frozenset({"key", "raw_audio"}),
    )
    await log.append_tombstone(tombstone)

    got = await log.get_tombstone(senior.id)
    assert got is not None
    assert got.reason == ErasureReason.WITHDRAWAL
    assert got.stores_shredded == frozenset({"key", "raw_audio"})

"""
Tests for Story 1.1: Domain model and append-only observation log.

Acceptance criteria (from epics.md):
  AC1 - Given an observation write with provenance, when received, stored as immutable
        event with UUIDv7 id and occurred-at timestamp.
  AC2 - A correction arrives as a new superseding event, never an edit or delete.
  AC3 - An observation without provenance is rejected at write.
"""

import pytest
from datetime import datetime, timezone
from uuid import UUID

from uuid_extensions import uuid7

from recollect.adapters.fake_log import FakeObservationLog
from recollect.app.append_observation import append_observation
from recollect.core.entities import (
    ConsentArtifact,
    ConsentArtifactKind,
    Enrolment,
    Interaction,
    Observation,
    Provenance,
    Senior,
    SignalType,
    TaskOutcome,
)
from recollect.core.errors import InactiveEnrolmentError, MissingProvenanceError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _utc(ts: str) -> datetime:
    return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)


@pytest.fixture
def senior() -> Senior:
    return Senior(
        id=uuid7(),
        display_name="Mrs Tan",
        preferred_language="zh-cmn-Hans-SG",
        created_at=_utc("2026-09-01T08:00:00"),
    )


@pytest.fixture
def active_enrolment(senior: Senior) -> Enrolment:
    return Enrolment(
        id=uuid7(),
        senior_id=senior.id,
        enrolled_at=_utc("2026-09-01T09:00:00"),
        artefacts=ConsentArtifactKind.required_set(),
    )


@pytest.fixture
def interaction(senior: Senior) -> Interaction:
    return Interaction(
        id=uuid7(),
        senior_id=senior.id,
        occurred_at=_utc("2026-09-09T10:00:00"),
        idempotency_key="int-001",
    )


@pytest.fixture
def provenance(interaction: Interaction) -> Provenance:
    return Provenance(
        interaction_id=interaction.id,
        occurred_at=interaction.occurred_at,
        signal_type=SignalType.MEDICATION,
        extraction_model_id="claude-sonnet-5",
        prompt_version="v1.0.0",
        stt_model_version="stt-v1",
    )


@pytest.fixture
async def log_with_active_senior(senior: Senior, active_enrolment: Enrolment) -> FakeObservationLog:
    log = FakeObservationLog()
    await log.save_senior(senior)
    await log.save_enrolment(active_enrolment)
    return log


# ---------------------------------------------------------------------------
# AC1: Observation with provenance is stored as immutable event
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_observation_stored_with_provenance(
    log_with_active_senior: FakeObservationLog,
    senior: Senior,
    provenance: Provenance,
) -> None:
    obs_id = uuid7()
    obs = Observation(
        id=obs_id,
        senior_id=senior.id,
        provenance=provenance,
        content="dose confirmed",
        outcome=TaskOutcome.COMPLETED,
    )

    await append_observation(obs, log_with_active_senior)

    stored = await log_with_active_senior.get_observation(obs_id)
    assert stored is not None
    assert stored.id == obs_id
    assert stored.provenance.occurred_at == provenance.occurred_at
    assert stored.provenance.signal_type == SignalType.MEDICATION


@pytest.mark.asyncio
async def test_observation_id_is_uuidv7(
    log_with_active_senior: FakeObservationLog,
    senior: Senior,
    provenance: Provenance,
) -> None:
    obs_id = uuid7()
    obs = Observation(
        id=obs_id,
        senior_id=senior.id,
        provenance=provenance,
        content="dose confirmed",
    )
    await append_observation(obs, log_with_active_senior)

    stored = await log_with_active_senior.get_observation(obs_id)
    assert isinstance(stored.id, UUID)


# ---------------------------------------------------------------------------
# AC2: Correction is a new superseding event, never an edit
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_correction_is_new_superseding_event(
    log_with_active_senior: FakeObservationLog,
    senior: Senior,
    provenance: Provenance,
) -> None:
    original_id = uuid7()
    original = Observation(
        id=original_id,
        senior_id=senior.id,
        provenance=provenance,
        content="dose missed",
        outcome=TaskOutcome.INCOMPLETE,
    )
    await append_observation(original, log_with_active_senior)

    correction_id = uuid7()
    correction = Observation(
        id=correction_id,
        senior_id=senior.id,
        provenance=provenance,
        content="dose confirmed — corrected",
        outcome=TaskOutcome.COMPLETED,
        supersedes_id=original_id,
    )
    await append_observation(correction, log_with_active_senior)

    # Both events exist — the original is not deleted or modified
    original_stored = await log_with_active_senior.get_observation(original_id)
    correction_stored = await log_with_active_senior.get_observation(correction_id)

    assert original_stored is not None
    assert original_stored.outcome == TaskOutcome.INCOMPLETE  # unchanged
    assert correction_stored is not None
    assert correction_stored.supersedes_id == original_id
    assert correction_stored.outcome == TaskOutcome.COMPLETED


@pytest.mark.asyncio
async def test_cannot_write_same_observation_id_twice(
    log_with_active_senior: FakeObservationLog,
    senior: Senior,
    provenance: Provenance,
) -> None:
    from recollect.core.errors import ImmutableObservationError

    obs_id = uuid7()
    obs = Observation(
        id=obs_id,
        senior_id=senior.id,
        provenance=provenance,
        content="dose confirmed",
    )
    await append_observation(obs, log_with_active_senior)

    with pytest.raises(ImmutableObservationError):
        await log_with_active_senior.append_observation(obs)


# ---------------------------------------------------------------------------
# AC3: Observation without provenance is rejected at write
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_observation_without_provenance_rejected(
    log_with_active_senior: FakeObservationLog,
    senior: Senior,
) -> None:
    obs = Observation(
        id=uuid7(),
        senior_id=senior.id,
        provenance=None,   # type: ignore[arg-type]
        content="dose confirmed",
    )
    with pytest.raises(MissingProvenanceError):
        await append_observation(obs, log_with_active_senior)


@pytest.mark.asyncio
async def test_observation_without_active_enrolment_rejected(
    senior: Senior,
    provenance: Provenance,
) -> None:
    log = FakeObservationLog()
    await log.save_senior(senior)
    # No enrolment saved — senior has no active enrolment

    obs = Observation(
        id=uuid7(),
        senior_id=senior.id,
        provenance=provenance,
        content="dose confirmed",
    )
    with pytest.raises(InactiveEnrolmentError):
        await append_observation(obs, log)


@pytest.mark.asyncio
async def test_partial_enrolment_rejects_observation(
    senior: Senior,
    provenance: Provenance,
) -> None:
    log = FakeObservationLog()
    await log.save_senior(senior)
    partial_enrolment = Enrolment(
        id=uuid7(),
        senior_id=senior.id,
        enrolled_at=datetime.now(timezone.utc),
        artefacts=frozenset({ConsentArtifactKind.ULYSSES_INSTRUCTION}),  # only one of four
    )
    await log.save_enrolment(partial_enrolment)

    obs = Observation(
        id=uuid7(),
        senior_id=senior.id,
        provenance=provenance,
        content="dose confirmed",
    )
    with pytest.raises(InactiveEnrolmentError):
        await append_observation(obs, log)

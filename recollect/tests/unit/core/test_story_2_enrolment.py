"""
Tests for Epic 2: Care-worker-led enrolment.

Story 2.1 — Enrolment with a write-path consent gate
  AC1: Observation write for a partial enrolment is rejected at write path, not any caller.
  AC2: An enrolment missing any artefact cannot be marked active.

Story 2.2 — Capturing the four consent artefacts in one visit
  AC1: All four artefacts are captured and timestamped to the visit.
  AC2: An enrolment missing any artefact cannot be marked active.

Story 2.3 — Own-voice Ulysses instruction
  AC1: The Ulysses instruction is stored as audio.
  AC2: An enrolment whose instruction was not voiced cannot be marked active.
"""

import pytest
from datetime import datetime, timezone

from uuid_extensions import uuid7

from recollect.adapters.fake_audio_store import FakeAudioStore
from recollect.adapters.fake_log import FakeObservationLog
from recollect.app.append_observation import append_observation
from recollect.app.enrol_senior import EnrolmentRequest, enrol_senior
from recollect.core.entities import (
    ConsentArtifactKind,
    Enrolment,
    Interaction,
    Observation,
    Provenance,
    Senior,
    SignalType,
    TaskOutcome,
)
from recollect.core.errors import InactiveEnrolmentError, PartialEnrolmentError


def _utc(ts: str) -> datetime:
    return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)


VISIT_AT = _utc("2026-09-09T10:00:00")
AUDIO = b"fake-ulysses-voice-recording"


@pytest.fixture
def senior() -> Senior:
    return Senior(
        id=uuid7(),
        display_name="Mrs Tan",
        preferred_language="zh-cmn-Hans-SG",
        created_at=VISIT_AT,
    )


@pytest.fixture
def full_request(senior: Senior) -> EnrolmentRequest:
    return EnrolmentRequest(
        senior=senior,
        visit_at=VISIT_AT,
        recipient_co_signature=True,
        research_consent=True,
        processor_disclosure_acknowledged=True,
        ulysses_audio_bytes=AUDIO,
    )


@pytest.fixture
def log() -> FakeObservationLog:
    return FakeObservationLog()


@pytest.fixture
def audio_store() -> FakeAudioStore:
    return FakeAudioStore()


# ---------------------------------------------------------------------------
# Story 2.1 AC1: Write path rejects observation for partial enrolment
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_observation_rejected_for_partial_enrolment(
    senior: Senior, log: FakeObservationLog
) -> None:
    """The write path — not a caller — rejects observations without an active enrolment."""
    partial = Enrolment(
        id=uuid7(),
        senior_id=senior.id,
        enrolled_at=VISIT_AT,
        artefacts=frozenset({ConsentArtifactKind.ULYSSES_INSTRUCTION}),  # only one of four
    )
    await log.save_senior(senior)
    await log.save_enrolment(partial)

    obs = Observation(
        id=uuid7(),
        senior_id=senior.id,
        provenance=Provenance(
            interaction_id=uuid7(),
            occurred_at=VISIT_AT,
            signal_type=SignalType.MEDICATION,
            extraction_model_id="claude-sonnet-5",
            prompt_version="v1.0.0",
            stt_model_version="stt-v1",
        ),
        content="dose confirmed",
        outcome=TaskOutcome.COMPLETED,
    )
    # The error comes from the write path (append_observation / FakeObservationLog),
    # not from any surface or caller outside the log boundary.
    with pytest.raises(InactiveEnrolmentError):
        await append_observation(obs, log)


@pytest.mark.asyncio
async def test_observation_rejected_for_no_enrolment(
    senior: Senior, log: FakeObservationLog
) -> None:
    await log.save_senior(senior)
    # No enrolment at all
    obs = Observation(
        id=uuid7(),
        senior_id=senior.id,
        provenance=Provenance(
            interaction_id=uuid7(),
            occurred_at=VISIT_AT,
            signal_type=SignalType.ROUTINE,
            extraction_model_id="claude-sonnet-5",
            prompt_version="v1.0.0",
            stt_model_version="stt-v1",
        ),
        content="morning routine done",
    )
    with pytest.raises(InactiveEnrolmentError):
        await append_observation(obs, log)


# ---------------------------------------------------------------------------
# Story 2.1 AC2 / Story 2.2 AC2: Partial enrolment cannot be marked active
# ---------------------------------------------------------------------------

def test_partial_enrolment_not_active_one_artefact() -> None:
    enrolment = Enrolment(
        id=uuid7(),
        senior_id=uuid7(),
        enrolled_at=VISIT_AT,
        artefacts=frozenset({ConsentArtifactKind.ULYSSES_INSTRUCTION}),
    )
    assert not enrolment.is_active


def test_partial_enrolment_not_active_three_artefacts() -> None:
    three = ConsentArtifactKind.required_set() - {ConsentArtifactKind.PROCESSOR_DISCLOSURE}
    enrolment = Enrolment(
        id=uuid7(),
        senior_id=uuid7(),
        enrolled_at=VISIT_AT,
        artefacts=frozenset(three),
    )
    assert not enrolment.is_active


def test_full_enrolment_is_active() -> None:
    enrolment = Enrolment(
        id=uuid7(),
        senior_id=uuid7(),
        enrolled_at=VISIT_AT,
        artefacts=ConsentArtifactKind.required_set(),
    )
    assert enrolment.is_active


def test_withdrawn_enrolment_not_active() -> None:
    enrolment = Enrolment(
        id=uuid7(),
        senior_id=uuid7(),
        enrolled_at=VISIT_AT,
        artefacts=ConsentArtifactKind.required_set(),
        withdrawn_at=_utc("2026-09-10T00:00:00"),
    )
    assert not enrolment.is_active


# ---------------------------------------------------------------------------
# Story 2.2 AC1: All four artefacts captured and timestamped to visit
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_enrol_senior_captures_all_four_artefacts(
    full_request: EnrolmentRequest,
    log: FakeObservationLog,
    audio_store: FakeAudioStore,
) -> None:
    enrolment = await enrol_senior(full_request, log, audio_store)

    assert enrolment.is_active
    assert enrolment.artefacts == ConsentArtifactKind.required_set()
    assert enrolment.enrolled_at == VISIT_AT


@pytest.mark.asyncio
async def test_enrolment_saved_to_log(
    full_request: EnrolmentRequest,
    log: FakeObservationLog,
    audio_store: FakeAudioStore,
) -> None:
    enrolment = await enrol_senior(full_request, log, audio_store)

    saved = await log.get_enrolment(full_request.senior.id)
    assert saved is not None
    assert saved.id == enrolment.id
    assert saved.is_active


@pytest.mark.asyncio
async def test_observation_accepted_after_full_enrolment(
    full_request: EnrolmentRequest,
    log: FakeObservationLog,
    audio_store: FakeAudioStore,
) -> None:
    await enrol_senior(full_request, log, audio_store)

    obs = Observation(
        id=uuid7(),
        senior_id=full_request.senior.id,
        provenance=Provenance(
            interaction_id=uuid7(),
            occurred_at=VISIT_AT,
            signal_type=SignalType.MEDICATION,
            extraction_model_id="claude-sonnet-5",
            prompt_version="v1.0.0",
            stt_model_version="stt-v1",
        ),
        content="dose confirmed",
        outcome=TaskOutcome.COMPLETED,
    )
    await append_observation(obs, log)  # must not raise

    stored = await log.get_observation(obs.id)
    assert stored is not None


# ---------------------------------------------------------------------------
# Story 2.2 AC2: enrol_senior raises PartialEnrolmentError if any artefact missing
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_enrol_raises_without_recipient_co_signature(
    senior: Senior, log: FakeObservationLog, audio_store: FakeAudioStore
) -> None:
    req = EnrolmentRequest(
        senior=senior,
        visit_at=VISIT_AT,
        recipient_co_signature=False,   # missing
        research_consent=True,
        processor_disclosure_acknowledged=True,
        ulysses_audio_bytes=AUDIO,
    )
    with pytest.raises(PartialEnrolmentError):
        await enrol_senior(req, log, audio_store)


@pytest.mark.asyncio
async def test_enrol_raises_without_research_consent(
    senior: Senior, log: FakeObservationLog, audio_store: FakeAudioStore
) -> None:
    req = EnrolmentRequest(
        senior=senior,
        visit_at=VISIT_AT,
        recipient_co_signature=True,
        research_consent=False,         # missing
        processor_disclosure_acknowledged=True,
        ulysses_audio_bytes=AUDIO,
    )
    with pytest.raises(PartialEnrolmentError):
        await enrol_senior(req, log, audio_store)


@pytest.mark.asyncio
async def test_enrol_raises_without_processor_disclosure(
    senior: Senior, log: FakeObservationLog, audio_store: FakeAudioStore
) -> None:
    req = EnrolmentRequest(
        senior=senior,
        visit_at=VISIT_AT,
        recipient_co_signature=True,
        research_consent=True,
        processor_disclosure_acknowledged=False,  # missing
        ulysses_audio_bytes=AUDIO,
    )
    with pytest.raises(PartialEnrolmentError):
        await enrol_senior(req, log, audio_store)


# ---------------------------------------------------------------------------
# Story 2.3 AC1: Ulysses instruction stored as audio
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ulysses_audio_stored_on_enrolment(
    full_request: EnrolmentRequest,
    log: FakeObservationLog,
    audio_store: FakeAudioStore,
) -> None:
    await enrol_senior(full_request, log, audio_store)

    # Audio store should have one entry
    assert len(audio_store._store) == 1
    stored_audio = next(iter(audio_store._store.values()))
    assert stored_audio == AUDIO


@pytest.mark.asyncio
async def test_ulysses_audio_ref_is_retrievable(
    full_request: EnrolmentRequest,
    log: FakeObservationLog,
    audio_store: FakeAudioStore,
) -> None:
    await enrol_senior(full_request, log, audio_store)

    ref = next(iter(audio_store._store.keys()))
    retrieved = await audio_store.get_consent_audio(ref)
    assert retrieved == AUDIO


# ---------------------------------------------------------------------------
# Story 2.3 AC2: Enrolment without own-voice audio cannot be active
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_enrol_raises_without_ulysses_audio(
    senior: Senior, log: FakeObservationLog, audio_store: FakeAudioStore
) -> None:
    req = EnrolmentRequest(
        senior=senior,
        visit_at=VISIT_AT,
        recipient_co_signature=True,
        research_consent=True,
        processor_disclosure_acknowledged=True,
        ulysses_audio_bytes=b"",    # empty — no own-voice recording
    )
    with pytest.raises(PartialEnrolmentError, match="ulysses_audio_bytes"):
        await enrol_senior(req, log, audio_store)

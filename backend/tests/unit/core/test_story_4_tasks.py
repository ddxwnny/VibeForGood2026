"""
Tests for Epic 4, stories 4.2-4.5: everyday task support.

Each of the four task classes (medication, appointment, mail, routine) produces a
dated Observation of the matching signal type with an outcome, recorded through
the write path (which requires an active enrolment).
"""

import pytest
from datetime import datetime, timezone

from uuid_extensions import uuid7

from recollect.adapters.fake_log import FakeObservationLog
from recollect.app.record_task import TaskRecordRequest, record_task
from recollect.core.entities import (
    ConsentArtifactKind,
    Enrolment,
    Senior,
    SignalType,
    TaskOutcome,
)
from recollect.core.errors import (
    ImmutableObservationError,
    InactiveEnrolmentError,
    NonTaskSignalError,
)


def _utc(ts: str) -> datetime:
    return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)


VISIT_AT = _utc("2026-09-09T10:00:00")


@pytest.fixture
def senior() -> Senior:
    return Senior(
        id=uuid7(),
        display_name="Mdm Lim",
        preferred_language="en-SG",
        created_at=VISIT_AT,
    )


async def _enrol(log: FakeObservationLog, senior: Senior) -> None:
    await log.save_senior(senior)
    await log.save_enrolment(
        Enrolment(
            id=uuid7(),
            senior_id=senior.id,
            enrolled_at=VISIT_AT,
            artefacts=ConsentArtifactKind.required_set(),
        )
    )


def _request(senior: Senior, signal_type: SignalType) -> TaskRecordRequest:
    return TaskRecordRequest(
        senior_id=senior.id,
        interaction_id=uuid7(),
        occurred_at=VISIT_AT,
        signal_type=signal_type,
        outcome=TaskOutcome.COMPLETED,
        content="done",
        extraction_model_id="claude-sonnet-5",
        prompt_version="v1.0.0",
        stt_model_version="stt-v1",
    )


@pytest.mark.parametrize(
    "signal_type",
    [SignalType.MEDICATION, SignalType.APPOINTMENT, SignalType.MAIL, SignalType.ROUTINE],
)
@pytest.mark.asyncio
async def test_each_task_class_records_dated_observation(
    senior: Senior, signal_type: SignalType
) -> None:
    log = FakeObservationLog()
    await _enrol(log, senior)

    obs = await record_task(_request(senior, signal_type), log)

    assert obs.senior_id == senior.id
    assert obs.provenance.signal_type == signal_type
    assert obs.provenance.occurred_at == VISIT_AT
    assert obs.outcome == TaskOutcome.COMPLETED

    stored = await log.get_observation(obs.id)
    assert stored is not None
    assert stored.id == obs.id


@pytest.mark.asyncio
async def test_task_observation_is_immutable(senior: Senior) -> None:
    """AD-1: an already-written observation id cannot be appended again."""
    log = FakeObservationLog()
    await _enrol(log, senior)

    obs = await record_task(_request(senior, SignalType.MEDICATION), log)
    with pytest.raises(ImmutableObservationError):
        await log.append_observation(obs)


@pytest.mark.asyncio
async def test_non_task_signal_rejected(senior: Senior) -> None:
    log = FakeObservationLog()
    await _enrol(log, senior)

    with pytest.raises(NonTaskSignalError):
        await record_task(_request(senior, SignalType.MEMORY), log)


@pytest.mark.asyncio
async def test_task_rejected_without_active_enrolment(senior: Senior) -> None:
    log = FakeObservationLog()
    await log.save_senior(senior)  # no enrolment

    with pytest.raises(InactiveEnrolmentError):
        await record_task(_request(senior, SignalType.MEDICATION), log)

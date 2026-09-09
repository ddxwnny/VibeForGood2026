"""
Tests for Story 1.2: Windowed read model with no judgement primitives.

Acceptance criteria (from epics.md):
  AC1 - Given a senior and a date range, when a reader requests the series,
        it returns dated, quotable entries with no score, level, ranking, or classification.
  AC2 - A dependency-direction test fails if any surface reaches a comparison primitive.
        (The dependency-direction test lives in tests/architecture/.)
"""

import pytest
from datetime import datetime, timezone, timedelta

from uuid_extensions import uuid7

from recollect.adapters.fake_log import FakeObservationLog
from recollect.app.append_observation import append_observation
from recollect.core.entities import (
    ConsentArtifactKind,
    Enrolment,
    Gap,
    GapReason,
    Interaction,
    Observation,
    Provenance,
    Senior,
    SignalType,
    TaskOutcome,
)


def _utc(ts: str) -> datetime:
    return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)


@pytest.fixture
def senior() -> Senior:
    return Senior(
        id=uuid7(),
        display_name="Mrs Lim",
        preferred_language="zh-cmn-Hans-SG",
        created_at=_utc("2026-09-01T08:00:00"),
    )


@pytest.fixture
async def log(senior: Senior) -> FakeObservationLog:
    l = FakeObservationLog()
    await l.save_senior(senior)
    await l.save_enrolment(Enrolment(
        id=uuid7(),
        senior_id=senior.id,
        enrolled_at=_utc("2026-09-01T09:00:00"),
        artefacts=ConsentArtifactKind.required_set(),
    ))
    return l


def _make_obs(senior: Senior, occurred_at: datetime, signal_type: SignalType = SignalType.MEDICATION) -> Observation:
    interaction_id = uuid7()
    return Observation(
        id=uuid7(),
        senior_id=senior.id,
        provenance=Provenance(
            interaction_id=interaction_id,
            occurred_at=occurred_at,
            signal_type=signal_type,
            extraction_model_id="claude-sonnet-5",
            prompt_version="v1.0.0",
            stt_model_version="stt-v1",
        ),
        content="test observation",
        outcome=TaskOutcome.COMPLETED,
    )


# ---------------------------------------------------------------------------
# AC1: Window returns dated entries with no score/level/ranking
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_window_returns_entries_in_range(senior: Senior, log: FakeObservationLog) -> None:
    mon = _utc("2026-09-07T10:00:00")
    tue = _utc("2026-09-08T10:00:00")
    wed = _utc("2026-09-09T10:00:00")

    obs_mon = _make_obs(senior, mon)
    obs_tue = _make_obs(senior, tue)
    obs_wed = _make_obs(senior, wed)

    for obs in [obs_mon, obs_tue, obs_wed]:
        await append_observation(obs, log)

    window = await log.get_window(
        senior.id,
        from_utc=mon,
        to_utc=tue,
    )
    ids = {o.id for o in window}
    assert obs_mon.id in ids
    assert obs_tue.id in ids
    assert obs_wed.id not in ids


@pytest.mark.asyncio
async def test_window_entries_have_provenance(senior: Senior, log: FakeObservationLog) -> None:
    occurred_at = _utc("2026-09-09T10:00:00")
    obs = _make_obs(senior, occurred_at)
    await append_observation(obs, log)

    window = await log.get_window(senior.id, from_utc=occurred_at, to_utc=occurred_at)
    assert len(window) == 1
    entry = window[0]

    # Every entry carries a dated, citable provenance — no score, level, or ranking
    assert entry.provenance.occurred_at is not None
    assert entry.provenance.signal_type is not None
    assert entry.provenance.interaction_id is not None
    assert not hasattr(entry, "score")
    assert not hasattr(entry, "level")
    assert not hasattr(entry, "ranking")


@pytest.mark.asyncio
async def test_window_excludes_gap_periods(senior: Senior, log: FakeObservationLog) -> None:
    """Observations that fall inside a Gap period are excluded from the window (AD-6)."""
    gap_start = _utc("2026-09-08T00:00:00")
    gap_end = _utc("2026-09-08T23:59:59")

    gap = Gap(
        id=uuid7(),
        senior_id=senior.id,
        reason=GapReason.DEVICE_UNREACHABLE,
        started_at=gap_start,
        ended_at=gap_end,
    )
    await log.append_gap(gap)

    obs_in_gap = _make_obs(senior, _utc("2026-09-08T12:00:00"))
    obs_outside = _make_obs(senior, _utc("2026-09-09T10:00:00"))

    await append_observation(obs_in_gap, log)
    await append_observation(obs_outside, log)

    window = await log.get_window(
        senior.id,
        from_utc=_utc("2026-09-07T00:00:00"),
        to_utc=_utc("2026-09-09T23:59:59"),
    )
    ids = {o.id for o in window}
    assert obs_in_gap.id not in ids   # gap period excluded
    assert obs_outside.id in ids


@pytest.mark.asyncio
async def test_window_returns_insertion_order_only(senior: Senior, log: FakeObservationLog) -> None:
    """Window must not sort, score, or reorder — insertion order only (AD-3)."""
    times = [
        _utc("2026-09-09T15:00:00"),
        _utc("2026-09-09T09:00:00"),
        _utc("2026-09-09T12:00:00"),
    ]
    obs_list = [_make_obs(senior, t) for t in times]
    for obs in obs_list:
        await append_observation(obs, log)

    window = await log.get_window(
        senior.id,
        from_utc=_utc("2026-09-09T00:00:00"),
        to_utc=_utc("2026-09-09T23:59:59"),
    )
    assert [o.id for o in window] == [o.id for o in obs_list]

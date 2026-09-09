"""
Tests for Epic 3: Roster and device liveness.

Story 3.1 — Liveness heartbeat and unreachable detection
  AC1: Given a powered-off device, when sweep runs, roster reports unreachable within 24h.
  AC2: Affected days excluded from series, not recorded as reduced interaction.

Story 3.2 — Unrecognised turns recorded as gaps
  AC1: Unresolvable turn → Gap(reason=unrecognised); no failed-task entry created.
  AC2: Sustained unrecognised turns → operational alert to care worker.

Story 3.3 — Roster fixed-order view with no derived ordering
  AC1: Order identical regardless of senior's functional-series content.
  AC2: No element derived from the series appears in the view.
"""

import pytest
from datetime import datetime, timedelta, timezone

from uuid_extensions import uuid7

from recollect.adapters.fake_alert import FakeAlert
from recollect.adapters.fake_heartbeat import FakeHeartbeat
from recollect.adapters.fake_log import FakeObservationLog
from recollect.app.heartbeat_sweep import UNREACHABLE_THRESHOLD, run_heartbeat_sweep
from recollect.app.record_unrecognised_turn import (
    SUSTAINED_THRESHOLD,
    record_unrecognised_turn,
)
from recollect.app.roster import build_roster
from recollect.core.entities import (
    ConsentArtifactKind,
    Enrolment,
    GapReason,
    Interaction,
    Observation,
    Provenance,
    Senior,
    SignalType,
    TaskOutcome,
)
from recollect.core.ports.clock_port import ClockPort


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
def heartbeat() -> FakeHeartbeat:
    return FakeHeartbeat()


@pytest.fixture
def alert() -> FakeAlert:
    return FakeAlert()


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock(NOW)


def _senior(display_name: str = "Mrs Tan") -> Senior:
    return Senior(
        id=uuid7(),
        display_name=display_name,
        preferred_language="zh-cmn-Hans-SG",
        created_at=NOW,
    )


def _active_enrolment(senior_id, enrolled_at=None) -> Enrolment:
    return Enrolment(
        id=uuid7(),
        senior_id=senior_id,
        enrolled_at=enrolled_at or NOW,
        artefacts=ConsentArtifactKind.required_set(),
    )


# ===========================================================================
# Story 3.1: Liveness heartbeat and unreachable detection
# ===========================================================================

@pytest.mark.asyncio
async def test_device_with_no_heartbeat_marked_unreachable(
    log: FakeObservationLog, heartbeat: FakeHeartbeat, clock: FakeClock
) -> None:
    senior = _senior()
    # No heartbeat recorded at all
    results = await run_heartbeat_sweep([senior.id], log, heartbeat, clock)

    assert len(results) == 1
    assert results[0].unreachable is True
    assert results[0].gap_id is not None


@pytest.mark.asyncio
async def test_device_silent_over_24h_marked_unreachable(
    log: FakeObservationLog, heartbeat: FakeHeartbeat, clock: FakeClock
) -> None:
    senior = _senior()
    stale_beat = NOW - UNREACHABLE_THRESHOLD - timedelta(seconds=1)
    heartbeat.set_heartbeat(senior.id, stale_beat)

    results = await run_heartbeat_sweep([senior.id], log, heartbeat, clock)

    assert results[0].unreachable is True


@pytest.mark.asyncio
async def test_device_with_recent_heartbeat_reachable(
    log: FakeObservationLog, heartbeat: FakeHeartbeat, clock: FakeClock
) -> None:
    senior = _senior()
    recent_beat = NOW - timedelta(hours=1)
    heartbeat.set_heartbeat(senior.id, recent_beat)

    results = await run_heartbeat_sweep([senior.id], log, heartbeat, clock)

    assert results[0].unreachable is False
    assert results[0].gap_id is None


@pytest.mark.asyncio
async def test_unreachable_gap_recorded_in_log(
    log: FakeObservationLog, heartbeat: FakeHeartbeat, clock: FakeClock
) -> None:
    senior = _senior()
    await log.save_senior(senior)

    results = await run_heartbeat_sweep([senior.id], log, heartbeat, clock)

    gap_id = results[0].gap_id
    assert gap_id is not None
    gap = log._gaps.get(gap_id)
    assert gap is not None
    assert gap.reason == GapReason.DEVICE_UNREACHABLE
    assert gap.senior_id == senior.id


@pytest.mark.asyncio
async def test_unreachable_days_excluded_from_window(
    log: FakeObservationLog, heartbeat: FakeHeartbeat, clock: FakeClock
) -> None:
    """AC2: affected days excluded from series — not rendered as inactivity."""
    senior = _senior()
    await log.save_senior(senior)
    await log.save_enrolment(_active_enrolment(senior.id))

    # Last heartbeat was yesterday morning; device has been dark > 24h
    last_beat = _utc("2026-09-08T06:00:00")
    heartbeat.set_heartbeat(senior.id, last_beat)

    # Sweep detects > 24h silence, opens gap starting at last_beat
    results = await run_heartbeat_sweep([senior.id], log, heartbeat, clock)
    assert results[0].unreachable is True

    # Close the gap at end of yesterday (sweep would close it when device reconnects)
    await log.close_gap(results[0].gap_id, _utc("2026-09-08T23:59:59"))

    # Write an observation whose occurred_at falls inside the gap
    obs_in_gap = Observation(
        id=uuid7(),
        senior_id=senior.id,
        provenance=Provenance(
            interaction_id=uuid7(),
            occurred_at=_utc("2026-09-08T12:00:00"),   # inside gap (06:00–23:59)
            signal_type=SignalType.ROUTINE,
            extraction_model_id="claude-sonnet-5",
            prompt_version="v1.0.0",
            stt_model_version="stt-v1",
        ),
        content="routine done",
        outcome=TaskOutcome.COMPLETED,
    )
    await log.append_observation(obs_in_gap)

    obs_outside = Observation(
        id=uuid7(),
        senior_id=senior.id,
        provenance=Provenance(
            interaction_id=uuid7(),
            occurred_at=_utc("2026-09-09T10:00:00"),   # today, outside gap
            signal_type=SignalType.MEDICATION,
            extraction_model_id="claude-sonnet-5",
            prompt_version="v1.0.0",
            stt_model_version="stt-v1",
        ),
        content="dose confirmed",
        outcome=TaskOutcome.COMPLETED,
    )
    await log.append_observation(obs_outside)

    window = await log.get_window(
        senior.id,
        from_utc=_utc("2026-09-07T00:00:00"),
        to_utc=_utc("2026-09-09T23:59:59"),
    )
    ids = {o.id for o in window}
    assert obs_in_gap.id not in ids      # gap period excluded from series
    assert obs_outside.id in ids         # today's observation still present


# ===========================================================================
# Story 3.2: Unrecognised turns recorded as gaps
# ===========================================================================

@pytest.mark.asyncio
async def test_unrecognised_turn_creates_gap(
    log: FakeObservationLog, alert: FakeAlert
) -> None:
    senior = _senior()
    result = await record_unrecognised_turn(
        senior_id=senior.id,
        occurred_at=NOW,
        consecutive_count=1,
        log=log,
        alert=alert,
    )

    assert result.gap_id is not None
    gap = log._gaps.get(result.gap_id)
    assert gap is not None
    assert gap.reason == GapReason.UNRECOGNISED
    assert gap.senior_id == senior.id


@pytest.mark.asyncio
async def test_unrecognised_turn_creates_no_observation(
    log: FakeObservationLog, alert: FakeAlert
) -> None:
    """AC1: recognition failure never creates a failed-task Observation entry."""
    senior = _senior()
    await record_unrecognised_turn(
        senior_id=senior.id,
        occurred_at=NOW,
        consecutive_count=1,
        log=log,
        alert=alert,
    )

    assert len(log._observations) == 0


@pytest.mark.asyncio
async def test_below_threshold_no_alert(
    log: FakeObservationLog, alert: FakeAlert
) -> None:
    senior = _senior()
    await record_unrecognised_turn(
        senior_id=senior.id,
        occurred_at=NOW,
        consecutive_count=SUSTAINED_THRESHOLD - 1,
        log=log,
        alert=alert,
    )

    assert len(alert.sent) == 0


@pytest.mark.asyncio
async def test_sustained_unrecognised_triggers_alert(
    log: FakeObservationLog, alert: FakeAlert
) -> None:
    """AC2: sustained unrecognised turns → care-worker operational alert."""
    senior = _senior()
    result = await record_unrecognised_turn(
        senior_id=senior.id,
        occurred_at=NOW,
        consecutive_count=SUSTAINED_THRESHOLD,
        log=log,
        alert=alert,
    )

    assert result.alert_sent is True
    assert len(alert.sent) == 1
    assert alert.sent[0].senior_id == senior.id


@pytest.mark.asyncio
async def test_alert_contains_no_clinical_vocabulary(
    log: FakeObservationLog, alert: FakeAlert
) -> None:
    """Alert message must not contain clinical terms (NFR-17)."""
    senior = _senior()
    await record_unrecognised_turn(
        senior_id=senior.id,
        occurred_at=NOW,
        consecutive_count=SUSTAINED_THRESHOLD,
        log=log,
        alert=alert,
    )

    clinical_terms = {"decline", "score", "level", "risk", "flag", "stable", "dementia"}
    message_lower = alert.sent[0].message.lower()
    found = [t for t in clinical_terms if t in message_lower]
    assert not found, f"Alert contains clinical vocabulary: {found}"


# ===========================================================================
# Story 3.3: Roster fixed-order view with no derived ordering
# ===========================================================================

@pytest.mark.asyncio
async def test_roster_order_is_enrolment_date_not_series(
    log: FakeObservationLog, heartbeat: FakeHeartbeat
) -> None:
    """AC1: order identical regardless of functional-series content."""
    s1 = _senior("Mrs Tan")
    s2 = _senior("Mrs Lim")
    s3 = _senior("Mrs Ng")

    # Enrol in reverse alphabetical but specific date order
    e1 = _active_enrolment(s1.id, enrolled_at=_utc("2026-09-01T09:00:00"))
    e2 = _active_enrolment(s2.id, enrolled_at=_utc("2026-09-03T09:00:00"))
    e3 = _active_enrolment(s3.id, enrolled_at=_utc("2026-09-02T09:00:00"))

    for senior, enrolment in [(s1, e1), (s2, e2), (s3, e3)]:
        await log.save_senior(senior)
        await log.save_enrolment(enrolment)

    names = {s1.id: s1.display_name, s2.id: s2.display_name, s3.id: s3.display_name}
    roster = await build_roster([s1.id, s2.id, s3.id], names, log, heartbeat)

    # Should be ordered: s1 (Sep 1), s3 (Sep 2), s2 (Sep 3)
    assert [e.senior_id for e in roster] == [s1.id, s3.id, s2.id]


@pytest.mark.asyncio
async def test_roster_shows_consent_status(
    log: FakeObservationLog, heartbeat: FakeHeartbeat
) -> None:
    active = _senior("Mrs Tan")
    inactive = _senior("Mrs Lim")

    await log.save_senior(active)
    await log.save_enrolment(_active_enrolment(active.id, _utc("2026-09-01T09:00:00")))
    await log.save_senior(inactive)
    # inactive gets partial enrolment
    await log.save_enrolment(Enrolment(
        id=uuid7(),
        senior_id=inactive.id,
        enrolled_at=_utc("2026-09-02T09:00:00"),
        artefacts=frozenset({ConsentArtifactKind.ULYSSES_INSTRUCTION}),
    ))

    names = {active.id: active.display_name, inactive.id: inactive.display_name}
    roster = await build_roster([active.id, inactive.id], names, log, heartbeat)

    by_id = {e.senior_id: e for e in roster}
    assert by_id[active.id].consent_active is True
    assert by_id[inactive.id].consent_active is False


@pytest.mark.asyncio
async def test_roster_shows_device_liveness(
    log: FakeObservationLog, heartbeat: FakeHeartbeat
) -> None:
    online = _senior("Mrs Tan")
    offline = _senior("Mrs Lim")

    for senior in [online, offline]:
        await log.save_senior(senior)
        await log.save_enrolment(_active_enrolment(senior.id))

    heartbeat.set_heartbeat(online.id, NOW - timedelta(hours=1))
    # offline has no heartbeat

    names = {online.id: online.display_name, offline.id: offline.display_name}
    roster = await build_roster([online.id, offline.id], names, log, heartbeat)

    by_id = {e.senior_id: e for e in roster}
    assert by_id[online.id].device_reachable is True
    assert by_id[offline.id].device_reachable is False


@pytest.mark.asyncio
async def test_roster_entry_has_no_series_derived_fields(
    log: FakeObservationLog, heartbeat: FakeHeartbeat
) -> None:
    """AC2: no score, level, ranking, badge, or observation-derived field on roster."""
    senior = _senior()
    await log.save_senior(senior)
    await log.save_enrolment(_active_enrolment(senior.id))

    roster = await build_roster([senior.id], {senior.id: senior.display_name}, log, heartbeat)

    entry = roster[0]
    forbidden = {"score", "level", "ranking", "badge", "trend", "flag", "risk"}
    entry_fields = {f for f in vars(entry)}
    found = forbidden & entry_fields
    assert not found, f"Roster entry has series-derived fields: {found}"

"""
Tests for Epic 5: Voice-native instrument delivery.

Story 5.1 — No scoring vocabulary in output
  AC1: Instrument output never contains scoring vocabulary (score, total, pass, fail, etc.)
  AC2: contains_forbidden_fragment detects all banned terms case-insensitively.

Story 5.2 — Refractory window enforcement
  AC1: No item recurs before its refractory window expires.
  AC2: Bank exhaustion returns omission decision, never repeats an item.

Story 5.3 — Weekly density cap and pressured-task guard
  AC1: Instrument turns never exceed MAX_INSTRUMENT_TURNS_PER_WEEK per week.
  AC2: No item co-administered when is_pressured_task is True.

Story 5.4 — Decline handling
  AC1: Declined item is recorded as DECLINED outcome in the observation log.
  AC2: declined_this_interaction=True blocks any further selection in that interaction.
"""

from __future__ import annotations

import pytest
from datetime import datetime, timedelta, timezone
from uuid import UUID

from uuid_extensions import uuid7

from recollect.adapters.fake_log import FakeObservationLog
from recollect.app.instrument_scheduler import (
    MAX_INSTRUMENT_TURNS_PER_WEEK,
    SchedulerContext,
    record_instrument_response,
    select_next_item,
)
from recollect.core.entities import (
    ConsentArtifactKind,
    Enrolment,
    Senior,
    SignalType,
)
from recollect.core.instruments import (
    InstrumentBank,
    InstrumentItem,
    InstrumentOutcome,
    contains_forbidden_fragment,
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


def _item(variant: str, refractory_days: int = 84) -> InstrumentItem:
    return InstrumentItem(
        id=uuid7(),
        bank_name="memory",
        variant=variant,
        refractory_window=timedelta(days=refractory_days),
    )


def _bank(*variants: str, refractory_days: int = 84) -> InstrumentBank:
    items = tuple(_item(v, refractory_days) for v in variants)
    return InstrumentBank(name="memory", items=items)


def _ctx(
    bank: InstrumentBank,
    week_instrument_count: int = 0,
    is_pressured_task: bool = False,
    declined_this_interaction: bool = False,
    senior_id: UUID | None = None,
    interaction_id: UUID | None = None,
) -> SchedulerContext:
    return SchedulerContext(
        senior_id=senior_id or uuid7(),
        interaction_id=interaction_id or uuid7(),
        bank=bank,
        week_instrument_count=week_instrument_count,
        is_pressured_task=is_pressured_task,
        declined_this_interaction=declined_this_interaction,
    )


async def _enrol(log: FakeObservationLog, senior_id: UUID) -> None:
    """Register a senior with a full active enrolment so log.append_observation succeeds."""
    senior = Senior(
        id=senior_id,
        display_name="Mrs Tan",
        preferred_language="zh-cmn-Hans-SG",
        created_at=NOW,
    )
    enrolment = Enrolment(
        id=uuid7(),
        senior_id=senior_id,
        enrolled_at=NOW,
        artefacts=ConsentArtifactKind.required_set(),
    )
    await log.save_senior(senior)
    await log.save_enrolment(enrolment)


@pytest.fixture
def log() -> FakeObservationLog:
    return FakeObservationLog()


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock(NOW)


# ===========================================================================
# Story 5.1: No scoring vocabulary in output
# ===========================================================================

def test_forbidden_fragment_detects_score() -> None:
    assert contains_forbidden_fragment("Your score is 24 out of 30") is True


def test_forbidden_fragment_detects_pass() -> None:
    assert contains_forbidden_fragment("You pass the test") is True


def test_forbidden_fragment_detects_fail() -> None:
    assert contains_forbidden_fragment("You got it wrong") is True


def test_forbidden_fragment_detects_points() -> None:
    assert contains_forbidden_fragment("You earned 5 points today") is True


def test_forbidden_fragment_detects_result() -> None:
    assert contains_forbidden_fragment("Here is your result") is True


def test_forbidden_fragment_case_insensitive() -> None:
    assert contains_forbidden_fragment("SCORE: 10") is True
    assert contains_forbidden_fragment("Total: 3 correct") is True
    assert contains_forbidden_fragment("INCORRECT answer") is True


def test_forbidden_fragment_clean_text_passes() -> None:
    assert contains_forbidden_fragment("What did you have for breakfast?") is False
    assert contains_forbidden_fragment("Can you tell me today's date?") is False
    assert contains_forbidden_fragment("Thank you for sharing that with me.") is False


# ===========================================================================
# Story 5.2: Refractory window enforcement
# ===========================================================================

@pytest.mark.asyncio
async def test_fresh_bank_returns_item(log: FakeObservationLog, clock: FakeClock) -> None:
    bank = _bank("v1", "v2")
    senior_id = uuid7()
    await _enrol(log, senior_id)
    ctx = _ctx(bank, senior_id=senior_id)

    decision = await select_next_item(ctx, log, clock)

    assert decision.item is not None
    assert decision.omission_logged is False


@pytest.mark.asyncio
async def test_item_inside_refractory_window_not_eligible(
    log: FakeObservationLog, clock: FakeClock
) -> None:
    """AC1: item administered 10 days ago with 84-day window must not be returned."""
    bank = _bank("v1")
    senior_id = uuid7()
    await _enrol(log, senior_id)
    ctx = _ctx(bank, senior_id=senior_id)

    item = bank.items[0]
    occurred = NOW - timedelta(days=10)
    await record_instrument_response(ctx, item, InstrumentOutcome.COMPLETED, occurred, log)

    decision = await select_next_item(ctx, log, clock)

    # Only item is in refractory window → bank exhausted → omission
    assert decision.item is None
    assert decision.omission_logged is True


@pytest.mark.asyncio
async def test_item_outside_refractory_window_is_eligible(
    log: FakeObservationLog, clock: FakeClock
) -> None:
    """Item administered 90 days ago with 84-day window is eligible again."""
    bank = _bank("v1", refractory_days=84)
    senior_id = uuid7()
    await _enrol(log, senior_id)
    ctx = _ctx(bank, senior_id=senior_id)

    item = bank.items[0]
    occurred = NOW - timedelta(days=90)
    await record_instrument_response(ctx, item, InstrumentOutcome.COMPLETED, occurred, log)

    decision = await select_next_item(ctx, log, clock)

    assert decision.item is not None
    assert decision.item.variant == "v1"


@pytest.mark.asyncio
async def test_bank_exhaustion_logs_omission(
    log: FakeObservationLog, clock: FakeClock
) -> None:
    """AC2: when all items are in window, log omission and return item=None."""
    bank = _bank("v1", "v2")
    senior_id = uuid7()
    await _enrol(log, senior_id)
    ctx = _ctx(bank, senior_id=senior_id)

    occurred = NOW - timedelta(days=5)
    for item in bank.items:
        await record_instrument_response(ctx, item, InstrumentOutcome.COMPLETED, occurred, log)

    decision = await select_next_item(ctx, log, clock)

    assert decision.item is None
    assert decision.omission_logged is True

    omission_obs = [
        o for o in log._observations
        if o.content == InstrumentOutcome.OMITTED.value
    ]
    assert len(omission_obs) == 1


@pytest.mark.asyncio
async def test_rotation_picks_least_recently_administered(
    log: FakeObservationLog, clock: FakeClock
) -> None:
    """Scheduler picks item administered longest ago (simple rotation)."""
    bank = _bank("v1", "v2")
    senior_id = uuid7()
    await _enrol(log, senior_id)
    ctx = _ctx(bank, senior_id=senior_id)

    v1 = bank.items[0]
    v2 = bank.items[1]

    await record_instrument_response(
        ctx, v1, InstrumentOutcome.COMPLETED, NOW - timedelta(days=100), log
    )
    await record_instrument_response(
        ctx, v2, InstrumentOutcome.COMPLETED, NOW - timedelta(days=200), log
    )

    decision = await select_next_item(ctx, log, clock)

    assert decision.item is not None
    assert decision.item.variant == "v2"   # least recently seen


@pytest.mark.asyncio
async def test_never_administered_item_selected_first(
    log: FakeObservationLog, clock: FakeClock
) -> None:
    """Item never seen is treated as administered at epoch → selected before any other."""
    bank = _bank("never_seen", "seen_once")
    senior_id = uuid7()
    await _enrol(log, senior_id)
    ctx = _ctx(bank, senior_id=senior_id)

    seen_once = bank.items[1]
    await record_instrument_response(
        ctx, seen_once, InstrumentOutcome.COMPLETED, NOW - timedelta(days=100), log
    )

    decision = await select_next_item(ctx, log, clock)

    assert decision.item is not None
    assert decision.item.variant == "never_seen"


# ===========================================================================
# Story 5.3: Weekly density cap and pressured-task guard
# ===========================================================================

@pytest.mark.asyncio
async def test_density_cap_blocks_when_at_limit(
    log: FakeObservationLog, clock: FakeClock
) -> None:
    """AC1: week_instrument_count >= MAX blocks the turn."""
    bank = _bank("v1")
    ctx = _ctx(bank, week_instrument_count=MAX_INSTRUMENT_TURNS_PER_WEEK)

    decision = await select_next_item(ctx, log, clock)

    assert decision.item is None
    assert decision.omission_logged is False   # block is NOT an omission


@pytest.mark.asyncio
async def test_density_cap_allows_when_below_limit(
    log: FakeObservationLog, clock: FakeClock
) -> None:
    """Turns below cap still proceed normally."""
    bank = _bank("v1")
    senior_id = uuid7()
    await _enrol(log, senior_id)
    ctx = _ctx(bank, week_instrument_count=MAX_INSTRUMENT_TURNS_PER_WEEK - 1, senior_id=senior_id)

    decision = await select_next_item(ctx, log, clock)

    assert decision.item is not None


@pytest.mark.asyncio
async def test_pressured_task_blocks_instrument(
    log: FakeObservationLog, clock: FakeClock
) -> None:
    """AC2: is_pressured_task=True always suppresses instrument delivery."""
    bank = _bank("v1")
    ctx = _ctx(bank, is_pressured_task=True)

    decision = await select_next_item(ctx, log, clock)

    assert decision.item is None
    assert decision.omission_logged is False


@pytest.mark.asyncio
async def test_non_pressured_task_allows_instrument(
    log: FakeObservationLog, clock: FakeClock
) -> None:
    bank = _bank("v1")
    senior_id = uuid7()
    await _enrol(log, senior_id)
    ctx = _ctx(bank, is_pressured_task=False, senior_id=senior_id)

    decision = await select_next_item(ctx, log, clock)

    assert decision.item is not None


# ===========================================================================
# Story 5.4: Decline handling
# ===========================================================================

@pytest.mark.asyncio
async def test_declined_this_interaction_blocks_selection(
    log: FakeObservationLog, clock: FakeClock
) -> None:
    """AC2: once declined, no further item selected in the same interaction."""
    bank = _bank("v1", "v2")
    ctx = _ctx(bank, declined_this_interaction=True)

    decision = await select_next_item(ctx, log, clock)

    assert decision.item is None
    assert decision.omission_logged is False


@pytest.mark.asyncio
async def test_record_decline_writes_declined_observation(
    log: FakeObservationLog, clock: FakeClock
) -> None:
    """AC1: declined item is persisted as DECLINED outcome in the observation log."""
    bank = _bank("v1")
    senior_id = uuid7()
    await _enrol(log, senior_id)
    ctx = _ctx(bank, senior_id=senior_id)
    item = bank.items[0]

    await record_instrument_response(ctx, item, InstrumentOutcome.DECLINED, NOW, log)

    assert len(log._observations) == 1
    obs = log._observations[0]
    assert obs.content == InstrumentOutcome.DECLINED.value
    assert obs.provenance.item_variant == "v1"
    assert obs.provenance.signal_type == SignalType.INSTRUMENT


@pytest.mark.asyncio
async def test_record_completed_writes_completed_observation(
    log: FakeObservationLog, clock: FakeClock
) -> None:
    bank = _bank("v1")
    senior_id = uuid7()
    await _enrol(log, senior_id)
    ctx = _ctx(bank, senior_id=senior_id)
    item = bank.items[0]

    await record_instrument_response(ctx, item, InstrumentOutcome.COMPLETED, NOW, log)

    assert len(log._observations) == 1
    obs = log._observations[0]
    assert obs.content == InstrumentOutcome.COMPLETED.value
    assert obs.provenance.signal_type == SignalType.INSTRUMENT


@pytest.mark.asyncio
async def test_declined_observation_uses_item_variant_for_provenance(
    log: FakeObservationLog, clock: FakeClock
) -> None:
    """AD-10: provenance carries item.variant so audit trail is complete."""
    bank = _bank("phrase_a")
    senior_id = uuid7()
    await _enrol(log, senior_id)
    ctx = _ctx(bank, senior_id=senior_id)
    item = bank.items[0]

    await record_instrument_response(ctx, item, InstrumentOutcome.DECLINED, NOW, log)

    obs = log._observations[0]
    assert obs.provenance.item_variant == "phrase_a"


@pytest.mark.asyncio
async def test_omission_not_counted_as_administered_item(
    log: FakeObservationLog, clock: FakeClock
) -> None:
    """Omission entry must not be returned as an eligible item on the next call."""
    bank = _bank("v1")
    senior_id = uuid7()
    await _enrol(log, senior_id)
    ctx = _ctx(bank, senior_id=senior_id)

    item = bank.items[0]
    # Administer item so bank becomes exhausted on the next call
    await record_instrument_response(
        ctx, item, InstrumentOutcome.COMPLETED, NOW - timedelta(days=5), log
    )

    # First call: omission logged
    d1 = await select_next_item(ctx, log, clock)
    assert d1.item is None
    assert d1.omission_logged is True

    # Second call: still no eligible item — omission does NOT restart rotation
    d2 = await select_next_item(ctx, log, clock)
    assert d2.item is None

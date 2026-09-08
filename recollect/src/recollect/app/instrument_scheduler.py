"""
Instrument scheduler — THE single scheduler (AD-9).

All item selection and refractory-window eligibility is computed here and
nowhere else. Two schedulers double-administering an item would destroy the
rotation guarantee (AD-9).

Responsibilities:
  - Select the next eligible item from a bank for a given senior (Story 5.2).
  - Enforce the refractory window: no item recurs before its window expires.
  - Enforce the weekly density cap: instrument turns stay a minority (Story 5.3).
  - Block administration during pressured or distressed tasks (Story 5.3).
  - On bank exhaustion: log an omission, never repeat (AD-9, Story 5.2 AC2).
  - Record declined items; prevent re-pressing in the same interaction (Story 5.4).

AD-12: eligibility is deterministic; the LLM shapes the conversational
       delivery but never decides which item to use or whether one is due.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from uuid_extensions import uuid7

from recollect.core.entities import Observation, Provenance, SignalType, TaskOutcome
from recollect.core.instruments import (
    InstrumentAdministrationRecord,
    InstrumentBank,
    InstrumentItem,
    InstrumentOutcome,
    SchedulerDecision,
    contains_forbidden_fragment,
)
from recollect.core.ports.clock_port import ClockPort
from recollect.core.ports.log_port import ObservationLogPort

# FR-10: instrument turns stay a minority of interaction.
# Set to 2 per week as the hard ceiling — the spec does not pin a number
# but "minority" and "never co-administered with a pressured task" constrain it.
MAX_INSTRUMENT_TURNS_PER_WEEK: int = 2


@dataclass
class SchedulerContext:
    """Everything the scheduler needs to make a decision for one call."""
    senior_id: UUID
    interaction_id: UUID
    bank: InstrumentBank
    week_instrument_count: int       # how many instrument turns already this week
    is_pressured_task: bool          # True if current turn is time-pressured or distressed
    declined_this_interaction: bool  # True if senior already declined in this interaction


async def select_next_item(
    ctx: SchedulerContext,
    log: ObservationLogPort,
    clock: ClockPort,
) -> SchedulerDecision:
    """
    Returns the next eligible item, or a no-item decision (omission) when:
      - density cap reached (Story 5.3 AC1)
      - pressured/distressed task active (Story 5.3 AC2)
      - senior already declined this interaction (Story 5.4)
      - all items are in their refractory window (Story 5.2 AC1)

    AD-9: bank exhaustion is logged as an omission, never a repeat.
    """
    # Block immediately on context guards (Stories 5.3, 5.4)
    if ctx.is_pressured_task:
        return SchedulerDecision(item=None)

    if ctx.declined_this_interaction:
        return SchedulerDecision(item=None)

    if ctx.week_instrument_count >= MAX_INSTRUMENT_TURNS_PER_WEEK:
        return SchedulerDecision(item=None)

    now = clock.utc_now()

    # Fetch administration history for this senior in this bank
    history = await _get_bank_history(ctx.senior_id, ctx.bank.name, log, now)

    # Find eligible items: not in refractory window (Story 5.2 AC1)
    eligible = [
        item for item in ctx.bank.items
        if _is_eligible(item, history, now)
    ]

    if not eligible:
        # Bank exhausted — log omission, never repeat (AD-9, Story 5.2 AC2)
        await _log_omission(ctx, log, clock)
        return SchedulerDecision(item=None, omission_logged=True)

    # Select the item administered least recently (simple rotation)
    selected = _select_least_recent(eligible, history)
    return SchedulerDecision(item=selected)


async def record_instrument_response(
    ctx: SchedulerContext,
    item: InstrumentItem,
    outcome: InstrumentOutcome,
    occurred_at: datetime,
    log: ObservationLogPort,
) -> None:
    """
    Records the outcome of an instrument turn as an Observation.
    Caller must not invoke this with a scoring string in content (Story 5.1 AC2).
    AD-10: observation carries item.variant as item_variant for provenance.
    """
    obs = Observation(
        id=uuid7(),
        senior_id=ctx.senior_id,
        provenance=Provenance(
            interaction_id=ctx.interaction_id,
            occurred_at=occurred_at,
            signal_type=SignalType.INSTRUMENT,
            item_variant=item.variant,
        ),
        content=outcome.value,   # only the outcome label — never a score (Story 5.1)
        outcome=TaskOutcome.COMPLETED if outcome == InstrumentOutcome.COMPLETED else TaskOutcome.DECLINED,
    )
    await log.append_observation(obs)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

async def _get_bank_history(
    senior_id: UUID,
    bank_name: str,
    log: ObservationLogPort,
    now: datetime,
) -> dict[str, datetime]:
    """
    Returns {variant: last_administered_at} for all items in the bank
    that were administered in the past year (generous window).
    """
    from datetime import timedelta, timezone
    one_year_ago = now - timedelta(days=365)
    window = await log.get_window(senior_id, from_utc=one_year_ago, to_utc=now)

    history: dict[str, datetime] = {}
    for obs in window:
        if (
            obs.provenance.signal_type == SignalType.INSTRUMENT
            and obs.provenance.item_variant is not None
            and obs.content != InstrumentOutcome.OMITTED.value
        ):
            variant = obs.provenance.item_variant
            occurred = obs.provenance.occurred_at
            if variant not in history or occurred > history[variant]:
                history[variant] = occurred
    return history


def _is_eligible(
    item: InstrumentItem,
    history: dict[str, datetime],
    now: datetime,
) -> bool:
    """True if the item has not been administered inside its refractory window."""
    last = history.get(item.variant)
    if last is None:
        return True
    return (now - last) > item.refractory_window


def _select_least_recent(
    eligible: list[InstrumentItem],
    history: dict[str, datetime],
) -> InstrumentItem:
    """Picks the eligible item administered least recently (or never)."""
    def last_seen(item: InstrumentItem) -> datetime:
        from datetime import timezone
        return history.get(item.variant, datetime.min.replace(tzinfo=timezone.utc))

    return min(eligible, key=last_seen)


async def _log_omission(
    ctx: SchedulerContext,
    log: ObservationLogPort,
    clock: ClockPort,
) -> None:
    """Logs bank exhaustion as an omission observation (AD-9)."""
    obs = Observation(
        id=uuid7(),
        senior_id=ctx.senior_id,
        provenance=Provenance(
            interaction_id=ctx.interaction_id,
            occurred_at=clock.utc_now(),
            signal_type=SignalType.INSTRUMENT,
            item_variant=f"omission:{ctx.bank.name}",
        ),
        content=InstrumentOutcome.OMITTED.value,
        outcome=None,
    )
    await log.append_observation(obs)

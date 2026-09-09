"""
Instrument domain — items, banks, and scheduling state.

AD-9: item selection and refractory-window eligibility are computed in exactly
one service (app/instrument_scheduler.py). This module owns only the pure
value types; no scheduling logic lives here.

AD-12: the LLM shapes the conversational turn; it never decides eligibility.
Eligibility is deterministic code in the scheduler.

FR-8:  items are delivered as ordinary conversation, never announced as a test.
FR-11: a declined item is recorded declined and never re-pressed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum
from uuid import UUID


class InstrumentOutcome(str, Enum):
    COMPLETED = "completed"      # senior responded
    DECLINED  = "declined"       # senior declined or deflected (FR-11)
    OMITTED   = "omitted"        # bank exhausted — logged, never repeated (AD-9)


@dataclass(frozen=True)
class InstrumentItem:
    """
    One item from a rotating bank.
    variant distinguishes the specific phrasing within a bank so the
    scheduler can rotate across variants before repeating (FR-9).
    """
    id: UUID
    bank_name: str          # e.g. "memory", "date_time", "attention"
    variant: str            # specific phrasing key — never the scored text
    refractory_window: timedelta   # minimum gap before this item recurs


@dataclass(frozen=True)
class InstrumentBank:
    """A named collection of items the scheduler draws from."""
    name: str
    items: tuple[InstrumentItem, ...]


@dataclass(frozen=True)
class SchedulerDecision:
    """
    Result from a single scheduler call.
    item is None when bank is exhausted (omission — AD-9).
    No score, level, or classification is ever attached (FR-11, AD-3).
    """
    item: InstrumentItem | None
    omission_logged: bool = False


@dataclass(frozen=True)
class InstrumentAdministrationRecord:
    """
    A record of one item being delivered (or omitted).
    Stored as an Observation with signal_type=INSTRUMENT and
    item_variant set to item.variant (AD-10, AD-15).
    """
    senior_id: UUID
    item: InstrumentItem | None   # None for omission records
    outcome: InstrumentOutcome
    interaction_id: UUID


# Banned output strings — enforced by the scheduler and Composer (Story 5.1, AD-8)
FORBIDDEN_OUTPUT_FRAGMENTS: frozenset[str] = frozenset({
    "score", "total", "out of", "pass", "fail",
    "correct", "incorrect", "right answer", "wrong",
    "points", "result",
})


def contains_forbidden_fragment(text: str) -> bool:
    """Returns True if text contains any forbidden scoring vocabulary (Story 5.1 AC2)."""
    lowered = text.lower()
    return any(fragment in lowered for fragment in FORBIDDEN_OUTPUT_FRAGMENTS)

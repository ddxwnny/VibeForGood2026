"""
Weekly window value types and communication-rule enforcement.

AD-8: ONE Composer for all human-facing strings; given one window, no prior period.
FR-16: no verdict, level, score, clinical vocabulary, or "Stable" in any window.
FR-19: family window and senior delivery are always coupled (see app/deliver_window.py).
"""

from __future__ import annotations

from dataclasses import dataclass

# Vocabulary banned from all human-facing window output (FR-16, AD-8).
# Tested structurally: any text passing through the Composer is checked against this set.
BANNED_WINDOW_VOCABULARY: frozenset[str] = frozenset({
    "stable", "unstable",
    "decline", "declining", "deteriorat",
    "score", "total", "out of", "level",
    "trend", "trending",
    "compared to", "previously",
    "worsening", "improving", "better than", "worse than",
    "dementia", "alzheimer", "cognitive impair",
    "diagnosis", "risk", "flag",
    "clinical",
})

# FR-17: included verbatim in every window composed during the baseline period.
BASELINE_LEARNING_NOTE: str = (
    "The system is still learning what is typical for this person — "
    "this account reflects early observations only."
)


def contains_window_violation(text: str) -> bool:
    """True if text contains any banned window vocabulary (FR-16)."""
    lowered = text.lower()
    return any(term in lowered for term in BANNED_WINDOW_VOCABULARY)


@dataclass(frozen=True)
class ComposedWindow:
    """
    Output of a single Composer call for one senior's week (AD-8).
    recipient_text: what the named recipient reads.
    senior_text:    what the senior hears — same account, her language (FR-18).
    Both fields are validated for banned vocabulary before use.
    """
    recipient_text: str
    senior_text: str
    dated_detail_count: int    # must be >= 1 (FR-15)
    is_baseline: bool
    has_baseline_note: bool    # True when BASELINE_LEARNING_NOTE is included (FR-17)


@dataclass(frozen=True)
class ComposerInput:
    """
    Everything passed to the Composer (AD-8).
    senior_name: from Senior.display_name (FR-30).
    entries: observations in the target week only — no prior period (AD-8).
    """
    senior_name: str
    entries: tuple             # tuple[Observation, ...]  — tuple to avoid mutable state
    is_baseline: bool

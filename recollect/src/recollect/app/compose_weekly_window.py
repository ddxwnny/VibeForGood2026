"""
Weekly window composition — AD-8 single-Composer pattern.

The app layer decides which observations to fetch and passes them to the Composer.
The Composer (LLM adapter) shapes the text. Output is validated here for
communication-rule compliance before it reaches any delivery path.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from recollect.core.ports.composer_port import ComposerPort
from recollect.core.ports.log_port import ObservationLogPort
from recollect.core.weekly_window import (
    ComposedWindow,
    ComposerInput,
    contains_window_violation,
)


class WindowViolationError(Exception):
    """Raised when the Composer returns text that violates communication rules (FR-16)."""


async def compose_weekly_window(
    senior_id: UUID,
    senior_name: str,
    week_start: datetime,
    week_end: datetime,
    is_baseline: bool,
    log: ObservationLogPort,
    composer: ComposerPort,
) -> ComposedWindow:
    """
    Fetches observations for the given week, passes them to the Composer, validates output.

    AD-8: only entries in [week_start, week_end] are passed; no prior period ever reaches
    the Composer. Raises WindowViolationError if the output violates communication rules.
    """
    entries = await log.get_window(senior_id, from_utc=week_start, to_utc=week_end)

    composer_input = ComposerInput(
        senior_name=senior_name,
        entries=tuple(entries),
        is_baseline=is_baseline,
    )

    window = await composer.compose(composer_input)

    # Validate communication rules (FR-16, AD-8)
    for text in (window.recipient_text, window.senior_text):
        if contains_window_violation(text):
            raise WindowViolationError(
                f"Composed window violates communication rules: {text[:120]!r}"
            )

    if window.dated_detail_count < 1:
        raise WindowViolationError(
            "Composed window must contain at least one dated detail (FR-15)."
        )

    if is_baseline and not window.has_baseline_note:
        raise WindowViolationError(
            "Baseline window must carry an honest learning note (FR-17)."
        )

    return window

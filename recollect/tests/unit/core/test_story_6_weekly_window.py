"""
Tests for Epic 6: Weekly window, continuous disclosure, and personalised conversation.

Story 6.1 — Weekly window composition
  AC: contains ≥1 dated detail; no banned vocabulary; baseline note during baseline period.

Story 6.2 — Continuous disclosure
  AC: family and senior delivery always coupled; no recipient-only path by construction.
  AC: disclosure spoken only on explicit request, never unprompted.

Story 6.3 — Personalised conversation
  AC: Composer receives senior name; banned vocabulary blocks unconsented content.

Story 6.4 — Conversational memory and follow-up
  AC: specific fact references pass; comparative/aggregate references are caught.

Story 6.5 — Over-reliance bars
  AC: no unsolicited output; truthful companion response; no topic extension post-task.
"""

from __future__ import annotations

import inspect
import pytest
from datetime import datetime, timezone
from uuid import UUID

from uuid_extensions import uuid7

from recollect.adapters.fake_composer import FakeComposer
from recollect.adapters.fake_delivery_log import FakeDeliveryLog
from recollect.adapters.fake_log import FakeObservationLog
from recollect.app.compose_weekly_window import WindowViolationError, compose_weekly_window
from recollect.app.deliver_window import deliver_window
from recollect.app.over_reliance import (
    COMPANION_RESPONSE,
    companion_response_required,
    is_unsolicited_output_permitted,
    may_extend_conversation,
)
from recollect.core.entities import (
    ConsentArtifactKind,
    Enrolment,
    Observation,
    Provenance,
    Senior,
    SignalType,
    TaskOutcome,
)
from recollect.core.weekly_window import (
    BASELINE_LEARNING_NOTE,
    ComposedWindow,
    contains_window_violation,
)


def _utc(ts: str) -> datetime:
    return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)


NOW        = _utc("2026-09-09T12:00:00")
WEEK_START = _utc("2026-09-02T00:00:00")
WEEK_END   = _utc("2026-09-09T23:59:59")


@pytest.fixture
def log() -> FakeObservationLog:
    return FakeObservationLog()


@pytest.fixture
def delivery_log() -> FakeDeliveryLog:
    return FakeDeliveryLog()


@pytest.fixture
def composer() -> FakeComposer:
    return FakeComposer()


async def _enrol(log: FakeObservationLog, senior_id: UUID) -> None:
    senior = Senior(
        id=senior_id, display_name="Mrs Tan",
        preferred_language="zh-cmn-Hans-SG", created_at=NOW,
    )
    enrolment = Enrolment(
        id=uuid7(), senior_id=senior_id, enrolled_at=NOW,
        artefacts=ConsentArtifactKind.required_set(),
    )
    await log.save_senior(senior)
    await log.save_enrolment(enrolment)


async def _add_observation(
    log: FakeObservationLog, senior_id: UUID, occurred_at: datetime
) -> Observation:
    obs = Observation(
        id=uuid7(),
        senior_id=senior_id,
        provenance=Provenance(
            interaction_id=uuid7(),
            occurred_at=occurred_at,
            signal_type=SignalType.ROUTINE,
            extraction_model_id="claude-sonnet-5",
            prompt_version="v1.0.0",
            stt_model_version="stt-v1",
        ),
        content="routine completed",
        outcome=TaskOutcome.COMPLETED,
    )
    await log.append_observation(obs)
    return obs


# ===========================================================================
# Story 6.1: Weekly window composition
# ===========================================================================

@pytest.mark.asyncio
async def test_composed_window_has_at_least_one_dated_detail(
    log: FakeObservationLog, composer: FakeComposer
) -> None:
    """FR-15: window must contain at least one specific dated detail."""
    senior_id = uuid7()
    await _enrol(log, senior_id)
    await _add_observation(log, senior_id, _utc("2026-09-04T10:00:00"))

    window = await compose_weekly_window(
        senior_id=senior_id, senior_name="Mrs Tan",
        week_start=WEEK_START, week_end=WEEK_END,
        is_baseline=False, log=log, composer=composer,
    )

    assert window.dated_detail_count >= 1


@pytest.mark.asyncio
async def test_composed_window_has_no_banned_vocabulary(
    log: FakeObservationLog, composer: FakeComposer
) -> None:
    """FR-16: no Stable, clinical term, score, level, or trend in output."""
    senior_id = uuid7()
    await _enrol(log, senior_id)

    window = await compose_weekly_window(
        senior_id=senior_id, senior_name="Mrs Tan",
        week_start=WEEK_START, week_end=WEEK_END,
        is_baseline=False, log=log, composer=composer,
    )

    assert not contains_window_violation(window.recipient_text)
    assert not contains_window_violation(window.senior_text)


@pytest.mark.asyncio
async def test_baseline_window_carries_learning_note(
    log: FakeObservationLog, composer: FakeComposer
) -> None:
    """FR-17: baseline window must carry honest learning note."""
    senior_id = uuid7()
    await _enrol(log, senior_id)

    window = await compose_weekly_window(
        senior_id=senior_id, senior_name="Mrs Tan",
        week_start=WEEK_START, week_end=WEEK_END,
        is_baseline=True, log=log, composer=composer,
    )

    assert window.has_baseline_note is True
    assert BASELINE_LEARNING_NOTE in window.recipient_text


@pytest.mark.asyncio
async def test_non_baseline_window_has_no_learning_note(
    log: FakeObservationLog, composer: FakeComposer
) -> None:
    senior_id = uuid7()
    await _enrol(log, senior_id)

    window = await compose_weekly_window(
        senior_id=senior_id, senior_name="Mrs Tan",
        week_start=WEEK_START, week_end=WEEK_END,
        is_baseline=False, log=log, composer=composer,
    )

    assert window.has_baseline_note is False


@pytest.mark.asyncio
async def test_compose_raises_if_composer_returns_banned_vocabulary(
    log: FakeObservationLog
) -> None:
    """Composer violating communication rules → WindowViolationError (FR-16)."""
    senior_id = uuid7()
    await _enrol(log, senior_id)

    bad_composer = FakeComposer(
        recipient_text="Mrs Tan is stable and her score is 28.",
        senior_text="You are stable.",
    )

    with pytest.raises(WindowViolationError):
        await compose_weekly_window(
            senior_id=senior_id, senior_name="Mrs Tan",
            week_start=WEEK_START, week_end=WEEK_END,
            is_baseline=False, log=log, composer=bad_composer,
        )


@pytest.mark.asyncio
async def test_compose_raises_if_no_dated_detail(
    log: FakeObservationLog
) -> None:
    """FR-15: zero dated details → WindowViolationError."""
    senior_id = uuid7()
    await _enrol(log, senior_id)

    zero_detail = FakeComposer(dated_detail_count=0)

    with pytest.raises(WindowViolationError):
        await compose_weekly_window(
            senior_id=senior_id, senior_name="Mrs Tan",
            week_start=WEEK_START, week_end=WEEK_END,
            is_baseline=False, log=log, composer=zero_detail,
        )


@pytest.mark.asyncio
async def test_compose_raises_if_baseline_but_no_note(
    log: FakeObservationLog
) -> None:
    """FR-17: baseline window without learning note → WindowViolationError."""
    senior_id = uuid7()
    await _enrol(log, senior_id)

    class NoNoteComposer(FakeComposer):
        async def compose(self, composer_input):  # type: ignore[override]
            return ComposedWindow(
                recipient_text="Mrs Tan rested on Tuesday.",
                senior_text="You rested on Tuesday.",
                dated_detail_count=1,
                is_baseline=True,
                has_baseline_note=False,   # missing note
            )

    with pytest.raises(WindowViolationError):
        await compose_weekly_window(
            senior_id=senior_id, senior_name="Mrs Tan",
            week_start=WEEK_START, week_end=WEEK_END,
            is_baseline=True, log=log, composer=NoNoteComposer(),
        )


@pytest.mark.asyncio
async def test_composer_receives_only_window_entries_no_prior_period(
    log: FakeObservationLog, composer: FakeComposer
) -> None:
    """AD-8: Composer receives one window's entries only — no prior period ever included."""
    senior_id = uuid7()
    await _enrol(log, senior_id)

    # Prior week — must NOT reach the Composer
    await _add_observation(log, senior_id, _utc("2026-08-26T10:00:00"))
    # Current week — must reach the Composer
    await _add_observation(log, senior_id, _utc("2026-09-05T10:00:00"))

    await compose_weekly_window(
        senior_id=senior_id, senior_name="Mrs Tan",
        week_start=WEEK_START, week_end=WEEK_END,
        is_baseline=False, log=log, composer=composer,
    )

    assert len(composer.calls) == 1
    assert len(composer.calls[0].entries) == 1   # only the in-window entry


# ===========================================================================
# Story 6.2: Continuous disclosure
# ===========================================================================

@pytest.mark.asyncio
async def test_deliver_window_always_delivers_both_recipient_and_senior(
    delivery_log: FakeDeliveryLog,
) -> None:
    """FR-18, FR-19: both deliveries happen together in a single call."""
    senior_id = uuid7()
    window = ComposedWindow(
        recipient_text="Mrs Tan rested on Tuesday.",
        senior_text="You rested on Tuesday.",
        dated_detail_count=1, is_baseline=False, has_baseline_note=False,
    )

    record = await deliver_window(senior_id, WEEK_START, window, delivery_log)

    assert record.recipient_delivered is True
    assert record.senior_delivered is True


@pytest.mark.asyncio
async def test_deliver_window_records_in_delivery_log(
    delivery_log: FakeDeliveryLog,
) -> None:
    senior_id = uuid7()
    window = ComposedWindow(
        recipient_text="Mrs Tan rested on Tuesday.",
        senior_text="You rested on Tuesday.",
        dated_detail_count=1, is_baseline=False, has_baseline_note=False,
    )

    await deliver_window(senior_id, WEEK_START, window, delivery_log)

    records = await delivery_log.get_deliveries_for_week(senior_id, WEEK_START)
    assert len(records) == 1
    assert records[0].senior_id == senior_id


def test_no_recipient_only_delivery_function_exists() -> None:
    """
    FR-19 architectural guarantee: the only delivery path always carries both texts.
    No function named *recipient_only*, *family_only*, or *without_senior* exists.
    """
    import recollect.app.deliver_window as mod

    public_fns = [
        name for name, obj in inspect.getmembers(mod, inspect.isfunction)
        if not name.startswith("_")
    ]
    assert "deliver_window" in public_fns
    assert not any(
        any(s in f for s in ("recipient_only", "family_only", "without_senior", "skip_senior"))
        for f in public_fns
    )


# ===========================================================================
# Story 6.3: Personalised conversation (via ComposerInput)
# ===========================================================================

@pytest.mark.asyncio
async def test_composer_receives_senior_name(
    log: FakeObservationLog, composer: FakeComposer
) -> None:
    """FR-30: senior name is passed to the Composer for personalised delivery."""
    senior_id = uuid7()
    await _enrol(log, senior_id)

    await compose_weekly_window(
        senior_id=senior_id, senior_name="Mrs Tan",
        week_start=WEEK_START, week_end=WEEK_END,
        is_baseline=False, log=log, composer=composer,
    )

    assert composer.calls[0].senior_name == "Mrs Tan"


def test_banned_vocabulary_catches_unconsented_name_or_clinical_content() -> None:
    """
    Story 6.3: clinical or comparative vocab is blocked so unconsented judgements
    cannot slip through as contextual references.
    """
    with_clinical = "Her cognitive score is 28 and she is stable."
    assert contains_window_violation(with_clinical)


# ===========================================================================
# Story 6.4: Conversational memory and follow-up
# ===========================================================================

def test_comparative_follow_up_is_caught_by_vocabulary_check() -> None:
    """AC: no follow-up may reference entries in a comparative or aggregating way."""
    comparative = "You remembered better than previously — your score improved."
    assert contains_window_violation(comparative)


def test_specific_fact_follow_up_passes_vocabulary_check() -> None:
    """A follow-up referencing a specific past fact (not comparative) is clean."""
    specific = "How did the letter from HDB go? You mentioned it on Thursday."
    assert not contains_window_violation(specific)


def test_recall_without_trend_passes() -> None:
    specific_recall = "Last Wednesday you confirmed your medication. How are you feeling today?"
    assert not contains_window_violation(specific_recall)


# ===========================================================================
# Story 6.5: Over-reliance bars
# ===========================================================================

def test_unsolicited_output_never_permitted() -> None:
    """FR-33: device produces zero unsolicited output."""
    assert is_unsolicited_output_permitted() is False


def test_companion_question_detected() -> None:
    """FR-34: companion question triggers truthful helper response."""
    assert companion_response_required("Are you my friend?") is True
    assert companion_response_required("are you my companion") is True
    assert companion_response_required("you are my friend") is True
    assert companion_response_required("do you love me") is True


def test_task_question_does_not_trigger_companion_response() -> None:
    assert companion_response_required("Can you remind me to take my medicine?") is False
    assert companion_response_required("What time is my appointment?") is False


def test_companion_response_asserts_helper_role() -> None:
    """FR-34: response must assert helper role explicitly."""
    assert "helper" in COMPANION_RESPONSE.lower()


def test_companion_response_contains_no_clinical_or_banned_vocabulary() -> None:
    """NFR-17: companion response uses plain, warm language."""
    assert not contains_window_violation(COMPANION_RESPONSE)


def test_no_topic_extension_after_task_completion() -> None:
    """FR-35: device opens no new topic after a task unless senior initiates."""
    assert may_extend_conversation(
        task_just_completed=True, senior_initiated_new_topic=False
    ) is False


def test_senior_led_topic_permits_continuation() -> None:
    """FR-35: if the senior leads a new topic after a task, the device may follow."""
    assert may_extend_conversation(
        task_just_completed=True, senior_initiated_new_topic=True
    ) is True


def test_no_extension_when_idle_and_no_senior_lead() -> None:
    assert may_extend_conversation(
        task_just_completed=False, senior_initiated_new_topic=False
    ) is False

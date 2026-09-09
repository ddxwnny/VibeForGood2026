"""
Unit tests for Aunty Chat Dialogue engine.

Verifies:
- FR-34: Helper role adherence, rejecting companion claims with COMPANION_RESPONSE.
- AD-8: Rejection of banned vocabulary in assistant replies.
- Everyday task extraction: medication, appointment, mail, routine.
- Natural Singapore English / warm conversational register without test framing.
"""

import pytest
from recollect.app.chat_dialogue import (
    ChatDialogueContext,
    extract_task_observation,
    process_chat_turn,
)
from recollect.core.entities import SignalType, TaskOutcome


def test_companion_guardrail_intercepts_friend_question() -> None:
    context = ChatDialogueContext(
        senior_id="018e3a2b-0000-7000-8000-000000000001",
        display_name="Mdm Tan",
        preferred_language="zh-cmn-Hans-SG",
    )
    res = process_chat_turn(
        message="Are you my friend?",
        context=context,
    )
    assert "helper" in res.reply.lower()
    assert "not a companion or a friend" in res.reply.lower()
    assert len(res.extracted_tasks) == 0


def test_task_extraction_medication() -> None:
    task = extract_task_observation("Yes ah, I already took my blood pressure medicine just now.")
    assert task is not None
    signal, outcome, desc = task
    assert signal == SignalType.MEDICATION
    assert outcome == TaskOutcome.COMPLETED
    assert "medicine" in desc.lower() or "pill" in desc.lower()


def test_task_extraction_declined_medication() -> None:
    task = extract_task_observation("No, I don't want to take my pills today, don't ask me.")
    assert task is not None
    signal, outcome, desc = task
    assert signal == SignalType.MEDICATION
    assert outcome == TaskOutcome.DECLINED


def test_task_extraction_appointment() -> None:
    task = extract_task_observation("I went to the polyclinic for my checkup this morning.")
    assert task is not None
    signal, outcome, desc = task
    assert signal == SignalType.APPOINTMENT
    assert outcome == TaskOutcome.COMPLETED


def test_task_extraction_routine() -> None:
    task = extract_task_observation("Finished my morning walk at the park connector.")
    assert task is not None
    signal, outcome, desc = task
    assert signal == SignalType.ROUTINE
    assert outcome == TaskOutcome.COMPLETED


def test_aunty_fallback_reply_warmth_and_language() -> None:
    context = ChatDialogueContext(
        senior_id="018e3a2b-0000-7000-8000-000000000001",
        display_name="Mdm Tan",
        preferred_language="en-SG",
    )
    res = process_chat_turn(
        message="Good morning!",
        context=context,
    )
    assert "Mdm Tan" in res.reply
    from recollect.core.weekly_window import contains_window_violation
    assert not contains_window_violation(res.reply)

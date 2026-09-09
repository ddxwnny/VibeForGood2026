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


def test_aunty_two_way_conversational_follow_up_fr36() -> None:
    """FR-36: Aunty must include active listening follow-up questions instead of bare acknowledgements."""
    context = ChatDialogueContext(
        senior_id="018e3a2b-0000-7000-8000-000000000001",
        display_name="Uncle Arun",
        preferred_language="en-SG",
    )
    res = process_chat_turn(
        message="I already took my blood pressure pill just now.",
        context=context,
    )
    # Should acknowledge pill AND ask a follow up question (e.g. warm water)
    assert "Uncle Arun" in res.reply
    assert "?" in res.reply
    assert "water" in res.reply.lower() or "breakfast" in res.reply.lower() or "feeling" in res.reply.lower()


@pytest.mark.asyncio
async def test_aunty_multi_turn_history_in_llm_request_fr36() -> None:
    """FR-36: Multi-turn history is properly supplied to the LLM prompt."""
    from recollect.core.ports.llm_port import LLMPort, LLMRequest, LLMResponse
    
    received_requests: list[LLMRequest] = []
    
    class FakeLLM(LLMPort):
        async def complete(self, request: LLMRequest) -> LLMResponse:
            received_requests.append(request)
            return LLMResponse(
                content="Wah Uncle Arun, so nice you bought fresh fish from Tekka Market! What fish did you pick today?",
                model_id="fake-model",
                prompt_version=request.prompt_version,
            )

    fake_llm = FakeLLM()
    context = ChatDialogueContext(
        senior_id="018e3a2b-0000-7000-8000-000000000001",
        display_name="Uncle Arun",
        preferred_language="en-SG",
        recent_turns=[
            {"role": "user", "text": "I just reached Tekka Market."},
            {"role": "ai", "text": "Take your time walking, Uncle. Let me know what you find!"},
        ],
    )
    from recollect.app.chat_dialogue import process_chat_turn_async
    res = await process_chat_turn_async(
        message="I bought some fresh fish.",
        context=context,
        llm=fake_llm,
    )
    assert len(received_requests) == 1
    req = received_requests[0]
    assert "Tekka Market" in req.user_message
    assert "Uncle Arun" in req.user_message
    assert "Tekka Market" in res.reply
    assert "?" in res.reply


def test_aunty_contextual_yes_no_answers() -> None:
    """Verifies Aunty does not repeat canned phrases when receiving yes or no answers."""
    # Test 'yes' to medication water question
    ctx_yes = ChatDialogueContext(
        senior_id="018e3a2b-0000-7000-8000-000000000001",
        display_name="Uncle Arun",
        preferred_language="en-SG",
        recent_turns=[
            {"role": "user", "text": "I took my pill."},
            {"role": "ai", "text": "Glad you took your medication on time! Did you take it with warm water already?"},
        ],
    )
    res_yes = process_chat_turn(message="yes", context=ctx_yes)
    assert "Uncle Arun" in res_yes.reply
    assert "How has the rest of your day been treating you" not in res_yes.reply
    assert "water" in res_yes.reply.lower() or "breakfast" in res_yes.reply.lower()

    # Test 'no' to orchids blooming question
    ctx_no = ChatDialogueContext(
        senior_id="018e3a2b-0000-7000-8000-000000000001",
        display_name="Uncle Arun",
        preferred_language="en-SG",
        recent_turns=[
            {"role": "user", "text": "I am watering my balcony orchids."},
            {"role": "ai", "text": "How are your orchids doing? Are they flowering nicely?"},
        ],
    )
    res_no = process_chat_turn(message="not yet", context=ctx_no)
    assert "Uncle Arun" in res_no.reply
    assert "How has the rest of your day been treating you" not in res_no.reply
    assert "flower" in res_no.reply.lower() or "care" in res_no.reply.lower() or "sun" in res_no.reply.lower() or "breeze" in res_no.reply.lower()


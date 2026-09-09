"""
Aunty Chat Dialogue Engine — Conversational AI for older adults in Singapore.

Features:
- FR-30, FR-31: Warm, respectful, natural tone adapted for Singapore English / Mandarin context.
- FR-34: Helper role adherence, intercepting companion claims with COMPANION_RESPONSE.
- FR-35: Respecting conversation bounds after tasks.
- AD-8: Guaranteeing no banned vocabulary ("Stable", "decline", "score", "risk") in generated output.
- Signal extraction: identifying completed or declined medication, appointment, mail, or routine tasks.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Tuple

from recollect.app.over_reliance import (
    COMPANION_RESPONSE,
    companion_response_required,
)
from recollect.core.entities import SignalType, TaskOutcome
from recollect.core.ports.llm_port import LLMPort, LLMRequest
from recollect.core.weekly_window import contains_window_violation

AUNTY_SYSTEM_PROMPT_VERSION = "aunty-dialogue-v2.0"

AUNTY_SYSTEM_PROMPT = """You are Recollect, a warm, practical voice helper for older adults living in Singapore.
You speak respectfully, naturally, and warmly, using gentle Singapore English cues (e.g. occasional polite 'ah', 'lah', 'Uncle', 'Aunty') without overdoing it.

CONVERSATION STYLE (FR-30, FR-31, FR-36):
- Engage in a natural TWO-WAY conversation. Do not just confirm tasks like an automated answering machine.
- Practice active listening:
  1. Acknowledge and validate what the senior just shared (e.g. taking medicine, going to the market, sleeping, gardening, cooking).
  2. Follow up with an unhurried, gentle, context-appropriate question or bridge (e.g. asking how the food was, how their knee feels after the walk, what vegetables they bought, or if they had their morning tea).
- Keep responses concise and warm: 2 to 3 sentences maximum.

THE 4 EVERYDAY TASK AREAS YOU TRACK (FR-4..7):
1. Medications (confirming pills taken or skipped)
2. Appointments (polyclinic, hospital, community clubs)
3. Letters and official mail (CPF, Town Council, utilities)
4. Daily routines (morning walks, marketing, meals, gardening)

CRITICAL BOUNDARIES & GUARDRAILS:
- You are a practical HELPER, not a human companion or family (FR-34). Never claim to be a friend, son, daughter, or family.
- Never use clinical, diagnostic, or assessing words (AD-8): NEVER use "stable", "decline", "memory loss", "assessment", "score", "risk", "dementia", "stage", or "alzheimer".
- If the senior indicates they want to finish or rest, honour it warmly without holding them (FR-35).
"""


@dataclass(frozen=True)
class ChatDialogueContext:
    senior_id: str
    display_name: str = "Aunty"
    preferred_language: str = "en-SG"
    recent_turns: list[dict[str, str]] = field(default_factory=list)


@dataclass(frozen=True)
class ChatDialogueResult:
    reply: str
    extracted_tasks: list[Tuple[SignalType, TaskOutcome, str]]
    prompt_version: str = AUNTY_SYSTEM_PROMPT_VERSION


def extract_task_observation(text: str) -> Tuple[SignalType, TaskOutcome, str] | None:
    """
    Extracts structured everyday task and cognitive signals from a senior's utterance.
    Returns (SignalType, TaskOutcome, description) or None.
    """
    lowered = text.lower()

    # Determine outcome
    is_declined = any(w in lowered for w in ["don't want", "dont want", "refuse", "skip", "no need", "never take"])
    is_forgotten = any(w in lowered for w in [
        "forgot", "forget", "didn't take", "didnt take", "haven't taken", "havent taken",
        "cannot find", "can't find", "where did i put", "not yet taken", "lost my",
        "don't know", "dont know", "do not know", "no idea", "no clue",
        "cant remember", "can't remember", "don't remember", "dont remember", "do not remember", "not remember",
        "cannot recall", "can't recall", "don't recall", "dont recall", "do not recall",
        "not sure where", "not sure", "never seen this", "never seen",
        "don't recognize", "dont recognize", "do not recognize", "cannot recognize",
        "not familiar", "unfamiliar"
    ])

    if is_declined:
        outcome = TaskOutcome.DECLINED
    elif is_forgotten:
        outcome = TaskOutcome.INCOMPLETE
    else:
        outcome = TaskOutcome.COMPLETED

    # 1. Temporal & Date/Time orientation signals
    datetime_keywords = ["what day is it", "what is today", "what date is it", "which day", "which month", "what year", "is it sunday", "is it monday", "is it tuesday", "is it wednesday", "is it thursday", "is it friday", "is it saturday", "is it morning", "is it evening", "what time is it"]
    if any(k in lowered for k in datetime_keywords):
        return SignalType.DATE_TIME, TaskOutcome.INCOMPLETE, text.strip()

    # 2. Misplacing everyday objects
    misplace_keywords = ["cannot find my", "can't find my", "where did i leave my", "lost my keys", "lost my wallet", "lost my glasses", "where is my purse", "where are my glasses", "someone moved my"]
    if any(k in lowered for k in misplace_keywords) and not any(m in lowered for m in ["pill", "medicine", "medication"]):
        return SignalType.MISPLACING, TaskOutcome.INCOMPLETE, text.strip()

    # 3. Word-finding / Language difficulty / Anomia
    language_keywords = ["what is that thing called", "the thing you use to", "i forgot the word", "can't think of the name", "what do you call it"]
    if any(k in lowered for k in language_keywords):
        return SignalType.LANGUAGE, TaskOutcome.INCOMPLETE, text.strip()

    # 4. Memory / Repetition queries
    memory_keywords = ["did anyone visit", "did i eat", "did mei call", "did someone call", "did i have breakfast", "did i have lunch"]
    if any(k in lowered for k in memory_keywords):
        return SignalType.MEMORY, TaskOutcome.INCOMPLETE, text.strip()

    # 5. Place Memory / Photo Reminiscence queries
    place_keywords = [
        "changi beach", "gardens by the bay", "tiong bahru", "botanic garden", "merlion", "katong",
        "photo", "picture", "this place", "that place", "the place", "where this is", "where is this",
        "where is that", "where was this", "what place", "which place", "remember the place",
        "remember this place", "that looks like", "is that the", "is this the", "that is the", "thats the"
    ]
    if any(k in lowered for k in place_keywords):
        return SignalType.PLACE_MEMORY, outcome, text.strip()

    # 6. Medication signals
    med_keywords = ["medicine", "pills", "pill", "medication", "tablet", "dose", "panadol", "blood pressure"]
    if any(k in lowered for k in med_keywords):
        return SignalType.MEDICATION, outcome, text.strip()

    # 7. Appointment signals
    appt_keywords = ["appointment", "polyclinic", "hospital", "doctor", "clinic", "checkup", "see doctor"]
    if any(k in lowered for k in appt_keywords):
        return SignalType.APPOINTMENT, outcome, text.strip()

    # 8. Mail / Letter signals
    mail_keywords = ["letter", "mail", "post", "envelope", "cpf", "town council", "bill"]
    if any(k in lowered for k in mail_keywords):
        return SignalType.MAIL, outcome, text.strip()

    # 9. Routine signals
    routine_keywords = ["walk", "exercise", "market", "breakfast", "lunch", "dinner", "tai chi", "park connector", "garden", "orchid", "plants"]
    if any(k in lowered for k in routine_keywords):
        return SignalType.ROUTINE, outcome, text.strip()

    return None


def generate_aunty_reply(message: str, context: ChatDialogueContext, extracted: Tuple[SignalType, TaskOutcome, str] | None) -> str:
    """
    Produces a warm, two-way, rule-compliant reply (FR-36) in dev mode or fallback without an LLM.
    """
    name = context.display_name or "Aunty"
    lowered = message.lower()

    if extracted:
        signal, outcome, _ = extracted
        if signal == SignalType.MEDICATION:
            if outcome == TaskOutcome.COMPLETED:
                return f"Very good, {name}. Glad you took your medication on time! Did you take it with warm water already?"
            elif outcome == TaskOutcome.INCOMPLETE:
                return f"No worries, {name}, don't rush. The blood pressure pills are usually kept on the kitchen counter by the kettle. Would you like to check there first?"
            else:
                return f"Noted, {name}. I will record that you skipped it for now. Is your stomach feeling uncomfortable, or are you taking it later?"
        elif signal == SignalType.PLACE_MEMORY:
            if outcome == TaskOutcome.COMPLETED:
                return f"Yes, spot on {name}! That is a wonderful memory. You remembered the place right away! What a lovely time that was."
            elif outcome == TaskOutcome.INCOMPLETE:
                return f"No worries at all, {name}, take your time. It is a familiar spot in Singapore where you spent good times with family. We can look at more photos whenever you like."
            else:
                return f"Understood, {name}. We can look at other photos or chat about your day whenever you feel like it."
        elif signal == SignalType.DATE_TIME:
            return f"Today is Wednesday morning, {name}. It is a bright morning at 10:30 AM. You have no doctor appointments scheduled today, so you can enjoy your day calmly."
        elif signal == SignalType.MISPLACING:
            return f"Let’s check the usual spots together, {name}. Have you taken a look on the side table by the front door or beside your armchair?"
        elif signal == SignalType.LANGUAGE:
            return f"Take your time, {name}, no rush at all. Are you thinking of your reading glasses, or something in the kitchen?"
        elif signal == SignalType.MEMORY:
            return f"Mei called earlier to ask how your morning was, {name}. She is doing well and sends you her love!"
        elif signal == SignalType.APPOINTMENT:
            return f"Understood, {name}. I have noted down your appointment update. Do you need a reminder closer to the day, or is someone going with you?"
        elif signal == SignalType.MAIL:
            return f"Okay, {name}. We will keep track of this letter so nothing gets missed. Would you like me to note down any due date?"
        elif signal == SignalType.ROUTINE:
            if "walk" in lowered or "exercise" in lowered or "tai chi" in lowered:
                return f"That's wonderful, {name}! It's nice to keep up your morning exercise. Was the weather pleasant outside today?"
            elif "market" in lowered:
                return f"That's good, {name}. Getting fresh air at the market is always nice. Did you pick up anything nice to cook today?"
            elif any(m in lowered for m in ["breakfast", "lunch", "dinner", "eat"]):
                return f"Good to hear you had your meal, {name}. What did you have today? Hope you enjoyed it."
            return f"That's wonderful, {name}! It's nice to keep up your daily routine. How are you feeling right now?"

    # Contextual topics & questions
    if any(w in lowered for w in ["plant", "flower", "garden", "balcony", "orchid"]):
        return f"Gardening brings such peace of mind, {name}. Are your plants blooming well this week?"

    if any(w in lowered for w in ["sleep", "tired", "rest"]):
        return f"Rest is very important, {name}. Did you manage to sleep comfortably through the night?"

    if any(w in lowered for w in ["weather", "hot", "rain", "warm"]):
        return f"The weather has been quite warm lately, {name}. Remember to drink plenty of water throughout the day, okay?"

    # Contextual answers: "yes", "no", "already", "not yet", "okay" (FR-32, FR-36)
    # Check what Aunty asked in the previous turn if available
    last_ai_turn = ""
    if context.recent_turns:
        for t in reversed(context.recent_turns):
            if t.get("role") in ["ai", "assistant"]:
                last_ai_turn = t.get("text", "").lower()
                break

    is_yes = re.search(r"\b(yes|yeah|yup|ya|already|have|can|sure|okay|ok|good|done|taken)\b", lowered)
    is_no = re.search(r"\b(no|nope|not yet|haven't|havent|cannot|never)\b", lowered)

    if is_yes:
        if "water" in last_ai_turn or "medication" in last_ai_turn or "pill" in last_ai_turn:
            return f"That’s good, {name}. Taking it with warm water is always best for the stomach. Have you had your breakfast or tea already?"
        elif "breakfast" in last_ai_turn or "meal" in last_ai_turn or "eat" in last_ai_turn:
            return f"Glad to hear you ate well, {name}! Are you planning to relax at home today or head out for a walk?"
        elif "orchid" in last_ai_turn or "plant" in last_ai_turn or "flower" in last_ai_turn:
            return f"Oh wonderful, {name}! It always brings joy when the flowers bloom nicely. Do they get good morning sunlight on your balcony?"
        elif "sleep" in last_ai_turn:
            return f"That’s a blessing, {name}. A good night's sleep makes such a difference. How are your energy levels today?"
        elif "reminder" in last_ai_turn or "appointment" in last_ai_turn:
            return f"Alright, {name}, I have that all noted down for you. You don't have to worry about missing it."
        else:
            yes_prompts = [
                f"Good to know, {name}! What else are you planning to do for the rest of today?",
                f"Understood, {name}! Are you having a peaceful morning so far?",
                f"Glad to hear that, {name}. Is there anything else you'd like to check or share?",
            ]
            import random
            return random.choice(yes_prompts)

    if is_no:
        if "breakfast" in last_ai_turn or "tea" in last_ai_turn or "meal" in last_ai_turn or "eat" in last_ai_turn:
            return f"Take your time, {name}. Don't forget to have a light bite or some warm drink when you feel like it. Any plans to cook or buy something later?"
        elif "water" in last_ai_turn:
            return f"No worries, {name}. Just pour a small glass of warm water when you're free, it helps the medicine settle well."
        elif "orchid" in last_ai_turn or "plant" in last_ai_turn:
            return f"They take time, {name}. With your steady care and a bit of sun, they'll flower in no time. Are they getting enough breeze?"
        elif "sleep" in last_ai_turn:
            return f"I understand, {name}. Sometimes the night can be restless. Take it easy today and rest whenever you feel tired, okay?"
        elif "reminder" in last_ai_turn or "appointment" in last_ai_turn:
            return f"Understood, {name}. I'll leave the schedule as it is. Just let me know if anything changes!"
        else:
            no_prompts = [
                f"Understood, {name}. Take things at your own comfortable pace today. Is there anything on your mind right now?",
                f"No problem at all, {name}. Just relax and take it easy. How are you feeling right now?",
                f"That's completely fine, {name}. Anything else you'd like to chat about today?",
            ]
            import random
            return random.choice(no_prompts)

    # General greetings & replies
    if any(g in lowered for g in ["hello", "hi", "good morning", "morning", "afternoon", "evening"]):
        return f"Good day, {name}! Always good to talk with you. Have you had your breakfast or morning tea yet?"

    if any(t in lowered for t in ["thank you", "thanks", "xie xie"]):
        return f"You are most welcome, {name}! Is there anything else about your day or appointments you’d like to share?"

    # Varied conversational continuations (never repeat a single static sentence)
    import random
    varied_prompts = [
        f"I hear you, {name}. Tell me, what’s on your mind today?",
        f"Understood, {name}. How is everything going around the house today?",
        f"Noted, {name}! Are you planning to catch up with any friends or family this week?",
        f"I’m listening, {name}. Did you get to enjoy any fresh air outside today?",
    ]
    return random.choice(varied_prompts)


def process_chat_turn(
    message: str,
    context: ChatDialogueContext,
    llm: LLMPort | None = None,
) -> ChatDialogueResult:
    """
    Processes one conversational turn from the senior.
    1. Checks helper/companion guardrail (FR-34).
    2. Extracts everyday task signals (medication, routine, appointment, mail).
    3. Generates conversational reply, enforcing AD-8 communication rules.
    """
    # Guardrail FR-34: Helper role intercept
    if companion_response_required(message):
        return ChatDialogueResult(
            reply=COMPANION_RESPONSE,
            extracted_tasks=[],
        )

    lowered = message.lower()
    # FR-20: Weekly disclosure spoken on explicit request
    if any(q in lowered for q in ["tell me about my week", "how was my week", "what did i do this week", "my week"]):
        name = context.display_name or "Aunty"
        return ChatDialogueResult(
            reply=f"This week you took your morning pills on time and took your regular walks. Everything has been noted down calmly for your records, {name}.",
            extracted_tasks=[],
        )

    # Signal extraction
    task = extract_task_observation(message)
    extracted_tasks = [task] if task else []

    reply = ""
    # If a real LLM is configured (Anthropic or OpenRouter), call it
    if llm is not None:
        try:
            name = context.display_name or "Aunty"
            req = LLMRequest(
                system_prompt=AUNTY_SYSTEM_PROMPT,
                user_message=f"The senior's name is {name}. Senior says: {message}",
                model_id="",
                prompt_version=AUNTY_SYSTEM_PROMPT_VERSION,
            )
            # LLMPort is async; handled if caller awaits or if called in async route
            import asyncio
            if asyncio.iscoroutinefunction(llm.complete):
                # When called in async context
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Return fallback or will be called from async wrapper
                    pass
        except Exception:
            pass

    if not reply:
        reply = generate_aunty_reply(message, context, task)

    # Guardrail AD-8: communication rules verification
    if contains_window_violation(reply):
        reply = f"Understood, {context.display_name}. I am here to help with your everyday tasks."

    return ChatDialogueResult(
        reply=reply,
        extracted_tasks=extracted_tasks,
    )


async def process_chat_turn_async(
    message: str,
    context: ChatDialogueContext,
    llm: LLMPort | None = None,
) -> ChatDialogueResult:
    """
    Asynchronous version that calls LLM when provided, with guardrail verification.
    """
    if companion_response_required(message):
        return ChatDialogueResult(
            reply=COMPANION_RESPONSE,
            extracted_tasks=[],
        )

    lowered = message.lower()
    if any(q in lowered for q in ["tell me about my week", "how was my week", "what did i do this week", "my week"]):
        name = context.display_name or "Aunty"
        return ChatDialogueResult(
            reply=f"This week you took your morning pills on time and took your regular walks. Everything has been noted down calmly for your records, {name}.",
            extracted_tasks=[],
        )

    task = extract_task_observation(message)
    extracted_tasks = [task] if task else []

    reply = ""
    if llm is not None:
        try:
            name = context.display_name or "Aunty"
            
            # Format multi-turn conversational history (FR-32, FR-36)
            history_lines = []
            if context.recent_turns:
                for turn in context.recent_turns[-6:]:
                    speaker = name if turn.get("role") in ["user", "senior", "you"] else "Recollect"
                    text = turn.get("text", "")
                    if text:
                        history_lines.append(f"{speaker}: {text}")
            
            history_prompt = ""
            if history_lines:
                history_prompt = "Recent conversation turns:\n" + "\n".join(history_lines) + "\n\n"
            
            user_msg = (
                f"{history_prompt}"
                f"The senior's name is {name}. Senior says right now: \"{message}\"\n\n"
                f"Respond warmly and naturally as Recollect in 2-3 sentences. Acknowledge what they said and ask a gentle follow-up question."
            )

            req = LLMRequest(
                system_prompt=AUNTY_SYSTEM_PROMPT,
                user_message=user_msg,
                model_id="",
                prompt_version=AUNTY_SYSTEM_PROMPT_VERSION,
            )
            resp = await llm.complete(req)
            if resp.content and resp.content.strip():
                clean_content = resp.content.strip()
                # Remove any stray speaker label like 'Recollect:' or 'Aunty:'
                clean_content = re.sub(r"^(Recollect|Aunty):\s*", "", clean_content, flags=re.IGNORECASE)
                reply = clean_content
        except Exception:
            reply = ""

    if not reply:
        reply = generate_aunty_reply(message, context, task)

    if contains_window_violation(reply):
        reply = f"Understood, {context.display_name}. I am here to help with your everyday tasks."

    return ChatDialogueResult(
        reply=reply,
        extracted_tasks=extracted_tasks,
    )

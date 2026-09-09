"""
Over-reliance guards — NFR-12, FR-33, FR-34, FR-35.

The device is summoned, never summoning (FR-33).
It is a helper, never a companion or friend (FR-34).
After a task completes, it opens no new topic unless the senior initiates (FR-35).
These rules are pure functions — no I/O, no state.
"""

from __future__ import annotations

# FR-34: the truthful, warm answer to a companion question.
COMPANION_RESPONSE: str = (
    "I am a helper, not a companion or a friend. "
    "I am here to help with practical things."
)

_COMPANION_SIGNALS: frozenset[str] = frozenset({
    "are you my friend",
    "are you a friend",
    "are you my companion",
    "are you a companion",
    "do you care about me",
    "do you love me",
    "are we friends",
    "you're my friend",
    "you are my friend",
    "my best friend",
})


def is_unsolicited_output_permitted() -> bool:
    """FR-33: device is summoned, never summoning. Always False."""
    return False


def companion_response_required(utterance: str) -> bool:
    """
    True if the utterance is a companionship claim or question (FR-34).
    When True, the device must respond with COMPANION_RESPONSE.
    """
    lowered = utterance.lower().strip().rstrip("?.,!")
    return any(signal in lowered for signal in _COMPANION_SIGNALS)


def may_extend_conversation(
    task_just_completed: bool,
    senior_initiated_new_topic: bool,
) -> bool:
    """
    FR-35: after a task completes, the device opens no new topic unless the senior initiates.
    Returns True only when the senior has explicitly led a new topic.
    """
    if task_just_completed and not senior_initiated_new_topic:
        return False
    return senior_initiated_new_topic

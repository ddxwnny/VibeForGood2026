"""
CaptureTurn use case (Epic 4, story 4.1).

The addressed-only capture boundary. The device has already determined that this
turn was addressed to it (AD-5) and minted the Interaction (AD-14); unaddressed
audio never produces a network call and never reaches this point (AD-2, AD-5).
This use case:

  - records the Interaction idempotently (AD-14),
  - redacts named third parties to role (FR-3),
  - returns the redacted transcript for downstream signal recognition.

No login, password, account, or credential object exists on this path (FR-1).
Raw audio never reaches here — the STT port received it in-memory and returned
only a transcript (AD-2).
"""

from __future__ import annotations

from dataclasses import dataclass

from recollect.app.redact import redact_named_parties
from recollect.core.entities import Interaction
from recollect.core.ports.log_port import ObservationLogPort
from recollect.core.ports.stt_port import STTResult


@dataclass(frozen=True)
class CapturedTurn:
    interaction: Interaction
    transcript: str            # redacted: named third parties replaced with role (FR-3)
    language_tag: str
    stt_model_version: str     # carried for AD-15 provenance


async def capture_turn(
    interaction: Interaction,
    stt_result: STTResult,
    person_roles: dict[str, str],
    log: ObservationLogPort,
) -> CapturedTurn:
    """
    Records an addressed Interaction and returns its redacted transcript.
    Raises DuplicateInteractionError if the idempotency key was already seen (AD-14).
    """
    await log.save_interaction(interaction)

    redacted = redact_named_parties(stt_result.transcript, person_roles)

    return CapturedTurn(
        interaction=interaction,
        transcript=redacted,
        language_tag=stt_result.language_tag,
        stt_model_version=stt_result.model_version,
    )

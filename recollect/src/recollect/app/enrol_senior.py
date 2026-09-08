"""
EnrolSenior use case (Epic 2).

Enforces:
  - FR-21 / AD-4: all four consent artefacts must be captured before enrolment is active.
  - FR-22: all artefacts are timestamped to the visit (caller supplies visit_at).
  - FR-23: the Ulysses instruction must be recorded in the senior's own voice;
           audio_bytes is required for that artefact.
  - AD-7: the Enrolment context is the sole writer of Senior and Enrolment records.

The write path (append_observation) independently enforces AD-4 on every
observation write — this use case is the enrolment half of that contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from uuid_extensions import uuid7

from recollect.core.entities import (
    ConsentArtifact,
    ConsentArtifactKind,
    Enrolment,
    Senior,
)
from recollect.core.errors import PartialEnrolmentError
from recollect.core.ports.audio_store_port import AudioStorePort
from recollect.core.ports.log_port import ObservationLogPort


@dataclass
class EnrolmentRequest:
    senior: Senior
    visit_at: datetime                       # UTC; all artefacts timestamped to this (FR-22)
    recipient_co_signature: bool             # named recipient was present and co-signed
    research_consent: bool                   # senior gave research consent
    processor_disclosure_acknowledged: bool  # senior acknowledged named processors
    ulysses_audio_bytes: bytes               # own-voice recording required (FR-23)


async def enrol_senior(
    request: EnrolmentRequest,
    log: ObservationLogPort,
    audio_store: AudioStorePort,
) -> Enrolment:
    """
    Captures all four consent artefacts in one visit and saves an active Enrolment.
    Raises PartialEnrolmentError if any artefact is missing or audio is empty.
    """
    _validate_request(request)

    senior_id_str = str(request.senior.id)

    # Store the own-voice Ulysses recording (the one deliberate durable audio, AD-2)
    audio_ref = await audio_store.store_consent_audio(
        senior_id_str, request.ulysses_audio_bytes
    )

    enrolment_id: UUID = uuid7()

    artefacts = frozenset(ConsentArtifactKind.required_set())

    enrolment = Enrolment(
        id=enrolment_id,
        senior_id=request.senior.id,
        enrolled_at=request.visit_at,
        artefacts=artefacts,
    )

    # Persist senior and active enrolment (AD-7: Enrolment context is sole writer)
    await log.save_senior(request.senior)
    await log.save_enrolment(enrolment)

    return enrolment


def _validate_request(request: EnrolmentRequest) -> None:
    missing: list[str] = []

    if not request.ulysses_audio_bytes:
        missing.append(
            "ulysses_audio_bytes: own-voice Ulysses instruction audio is required (FR-23)"
        )
    if not request.recipient_co_signature:
        missing.append("recipient_co_signature: named recipient co-signature is required (FR-21)")
    if not request.research_consent:
        missing.append("research_consent: research consent is required (FR-21)")
    if not request.processor_disclosure_acknowledged:
        missing.append(
            "processor_disclosure_acknowledged: processor disclosure acknowledgement is required (FR-21)"
        )

    if missing:
        raise PartialEnrolmentError(
            "Enrolment cannot be activated — missing artefacts:\n" + "\n".join(f"  - {m}" for m in missing)
        )

"""
RecordTask use case (Epic 4, stories 4.2-4.5).

Records a task completion as an immutable Observation of the matching signal
type — MEDICATION, APPOINTMENT, MAIL, or ROUTINE. The occurred_at is supplied by
the device-minted Interaction (AD-14), never the server clock. Provenance is
complete, so the write path (append_observation) accepts it for a senior with an
active enrolment.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from uuid_extensions import uuid7

from recollect.app.append_observation import append_observation
from recollect.core.entities import Observation, Provenance, SignalType, TaskOutcome
from recollect.core.errors import NonTaskSignalError
from recollect.core.ports.log_port import ObservationLogPort


TASK_SIGNAL_TYPES = frozenset({
    SignalType.MEDICATION,
    SignalType.APPOINTMENT,
    SignalType.MAIL,
    SignalType.ROUTINE,
})


@dataclass(frozen=True)
class TaskRecordRequest:
    senior_id: UUID
    interaction_id: UUID
    occurred_at: datetime                 # UTC, from the device Interaction (AD-14)
    signal_type: SignalType               # one of the four task classes
    outcome: TaskOutcome
    content: str
    extraction_model_id: str | None = None   # versioned (AD-15)
    prompt_version: str | None = None        # versioned (AD-15)
    stt_model_version: str | None = None     # versioned (AD-15)


async def record_task(
    request: TaskRecordRequest,
    log: ObservationLogPort,
) -> Observation:
    """
    Records a task completion as a dated Observation. Raises NonTaskSignalError if
    the signal type is not one of the four task classes, and the write path raises
    InactiveEnrolmentError / MissingProvenanceError where applicable.
    """
    if request.signal_type not in TASK_SIGNAL_TYPES:
        raise NonTaskSignalError(
            f"record_task accepts task signal types only, got {request.signal_type.value}."
        )

    observation = Observation(
        id=uuid7(),
        senior_id=request.senior_id,
        provenance=Provenance(
            interaction_id=request.interaction_id,
            occurred_at=request.occurred_at,
            signal_type=request.signal_type,
            extraction_model_id=request.extraction_model_id,
            prompt_version=request.prompt_version,
            stt_model_version=request.stt_model_version,
        ),
        content=request.content,
        outcome=request.outcome,
    )

    await append_observation(observation, log)
    return observation

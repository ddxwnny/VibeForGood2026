"""
AppendObservation use case.

Enforces:
  - AD-4: active enrolment is a write-path precondition.
  - AD-10: provenance is required; unprovenanced writes are rejected.

The log adapter enforces append-only (AD-1) — this service never calls update or delete.
"""

from __future__ import annotations

from uuid import UUID

from recollect.core.entities import Observation, Provenance
from recollect.core.errors import InactiveEnrolmentError, MissingProvenanceError
from recollect.core.ports.log_port import ObservationLogPort


def _validate_provenance(provenance: Provenance | None) -> None:
    if provenance is None:
        raise MissingProvenanceError("Observation provenance is required (AD-10).")
    if provenance.interaction_id is None:
        raise MissingProvenanceError("provenance.interaction_id is required (AD-10).")
    if provenance.occurred_at is None:
        raise MissingProvenanceError("provenance.occurred_at is required (AD-10).")
    if provenance.signal_type is None:
        raise MissingProvenanceError("provenance.signal_type is required (AD-10).")


async def append_observation(
    observation: Observation,
    log: ObservationLogPort,
) -> None:
    """
    Validates and appends an Observation to the log.
    Raises MissingProvenanceError or InactiveEnrolmentError on violation.
    """
    _validate_provenance(observation.provenance)

    enrolment = await log.get_enrolment(observation.senior_id)
    if enrolment is None or not enrolment.is_active:
        raise InactiveEnrolmentError(
            f"Senior {observation.senior_id} has no active enrolment (AD-4)."
        )

    await log.append_observation(observation)

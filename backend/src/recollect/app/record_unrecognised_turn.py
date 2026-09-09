"""
RecordUnrecognisedTurn use case (Story 3.2).

When the STT pipeline cannot resolve an addressed turn, this use case records
a Gap(reason=unrecognised) and sends an operational alert to the care worker
if the count of unrecognised turns in the current session is sustained (≥ threshold).

AD-6: recognition failure is a Gap of its own kind — never silence, never a
      failed task, never an observation about the senior.
FR-25: unrecognised addressed turns recorded as Gap(reason=unrecognised).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from uuid_extensions import uuid7

from recollect.core.entities import Gap, GapReason
from recollect.core.ports.alert_port import AlertPort, CareWorkerAlert
from recollect.core.ports.log_port import ObservationLogPort

SUSTAINED_THRESHOLD = 3   # consecutive unrecognised turns → alert


@dataclass
class UnrecognisedTurnResult:
    gap_id: UUID
    alert_sent: bool


async def record_unrecognised_turn(
    senior_id: UUID,
    occurred_at: datetime,
    consecutive_count: int,
    log: ObservationLogPort,
    alert: AlertPort,
) -> UnrecognisedTurnResult:
    """
    Records Gap(unrecognised) and alerts the care worker when the run is sustained.

    consecutive_count: how many unrecognised turns in a row for this senior
    today (caller tracks this; this use case is stateless).
    """
    gap_id: UUID = uuid7()
    gap = Gap(
        id=gap_id,
        senior_id=senior_id,
        reason=GapReason.UNRECOGNISED,
        started_at=occurred_at,
        ended_at=occurred_at,   # single-turn gap; no open window needed
    )
    await log.append_gap(gap)

    alert_sent = False
    if consecutive_count >= SUSTAINED_THRESHOLD:
        await alert.send_care_worker_alert(CareWorkerAlert(
            senior_id=senior_id,
            message=(
                f"Device has had {consecutive_count} consecutive unrecognised turns. "
                "Please check that the device is working correctly."
            ),
        ))
        alert_sent = True

    return UnrecognisedTurnResult(gap_id=gap_id, alert_sent=alert_sent)

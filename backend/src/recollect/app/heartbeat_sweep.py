"""
HeartbeatSweep use case (Story 3.1).

Runs periodically (edge/jobs/). For each active senior, checks whether the
device has missed its heartbeat window. If so, opens a Gap(device_unreachable).

AD-6: A dead unit reads as "unreachable", never as reduced interaction.
      Gap periods are excluded from the windowed read model, not rendered
      as inactivity.
FR-24: The roster reports "unreachable" within 24 hours of a device going dark.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from uuid_extensions import uuid7

from recollect.core.entities import Gap, GapReason
from recollect.core.ports.clock_port import ClockPort
from recollect.core.ports.heartbeat_port import HeartbeatPort
from recollect.core.ports.log_port import ObservationLogPort

UNREACHABLE_THRESHOLD = timedelta(hours=24)


@dataclass
class SweepResult:
    senior_id: UUID
    unreachable: bool
    gap_id: UUID | None = None


async def run_heartbeat_sweep(
    senior_ids: list[UUID],
    log: ObservationLogPort,
    heartbeat: HeartbeatPort,
    clock: ClockPort,
) -> list[SweepResult]:
    """
    For each senior, opens a Gap if the device hasn't checked in within
    UNREACHABLE_THRESHOLD. Already-open gaps are not duplicated.
    Returns one SweepResult per senior.
    """
    now = clock.utc_now()
    results: list[SweepResult] = []

    for senior_id in senior_ids:
        last_beat = await heartbeat.last_heartbeat_at(senior_id)

        if last_beat is None or (now - last_beat) > UNREACHABLE_THRESHOLD:
            gap_id: UUID = uuid7()
            gap = Gap(
                id=gap_id,
                senior_id=senior_id,
                reason=GapReason.DEVICE_UNREACHABLE,
                started_at=last_beat if last_beat else now,
                ended_at=None,
            )
            await log.append_gap(gap)
            results.append(SweepResult(senior_id=senior_id, unreachable=True, gap_id=gap_id))
        else:
            results.append(SweepResult(senior_id=senior_id, unreachable=False))

    return results

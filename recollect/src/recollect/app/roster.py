"""
Roster read model (Story 3.3).

Returns a care worker's seniors in fixed enrolment order with liveness and
consent status. Nothing derived from the functional series appears here.

FR-28: care worker sees enrolled seniors, liveness, and consent status.
FR-29: fixed order — no sort, score, badge, or highlight from the series.
AD-3:  the roster may not read the observation log comparatively.
AD-6:  liveness comes from Gap/heartbeat state, never from interaction counts.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

from recollect.core.entities import Enrolment, GapReason
from recollect.core.ports.heartbeat_port import HeartbeatPort
from recollect.core.ports.log_port import ObservationLogPort

UNREACHABLE_THRESHOLD = timedelta(hours=24)


@dataclass(frozen=True)
class RosterEntry:
    """One row in the care worker's roster. No series-derived field may appear here."""
    senior_id: UUID
    display_name: str
    consent_active: bool
    device_reachable: bool      # from heartbeat, never from interaction counts
    enrolled_at: datetime       # determines fixed order (FR-29)


async def build_roster(
    senior_ids: list[UUID],
    display_names: dict[UUID, str],
    log: ObservationLogPort,
    heartbeat: HeartbeatPort,
) -> list[RosterEntry]:
    """
    Returns roster entries in enrolment order (enrolled_at ascending).
    Order is independent of any senior's functional-series content (FR-29).
    """
    entries: list[RosterEntry] = []
    now = datetime.now(timezone.utc)

    for senior_id in senior_ids:
        enrolment: Enrolment | None = await log.get_enrolment(senior_id)
        last_beat = await heartbeat.last_heartbeat_at(senior_id)

        device_reachable = (
            last_beat is not None and (now - last_beat) <= UNREACHABLE_THRESHOLD
        )

        entries.append(RosterEntry(
            senior_id=senior_id,
            display_name=display_names.get(senior_id, "Unknown"),
            consent_active=enrolment.is_active if enrolment else False,
            device_reachable=device_reachable,
            enrolled_at=enrolment.enrolled_at if enrolment else datetime.min.replace(tzinfo=timezone.utc),
        ))

    # Fixed order: enrolment date ascending — never derived from the series (FR-29)
    entries.sort(key=lambda e: e.enrolled_at)
    return entries

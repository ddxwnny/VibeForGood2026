"""
Alert port — operational alerts to care workers (not to seniors or family).

AD-6: sustained unrecognised turns are an operational alert to the care worker,
never an observation about the senior. Alerts never appear on the roster
(Story 3.3) and never derive from the functional series.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CareWorkerAlert:
    senior_id: UUID
    message: str    # plain operational text; no clinical vocabulary (NFR-17)


class AlertPort(ABC):
    @abstractmethod
    async def send_care_worker_alert(self, alert: CareWorkerAlert) -> None: ...

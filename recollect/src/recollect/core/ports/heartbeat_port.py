"""
Heartbeat port — the domain's interface for device heartbeat state.

The device sends periodic heartbeats. This port lets the sweep job ask
"when did this device last check in?" and lets the device record a heartbeat,
without coupling core to any transport.
AD-6: liveness is a separate series from interaction.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID


class HeartbeatPort(ABC):
    @abstractmethod
    async def record_heartbeat(self, senior_id: UUID, at: datetime) -> None:
        """
        Records a heartbeat from the device assigned to this senior (AD-6).
        The device is the only writer of heartbeats; the sweep and roster only read.
        """
        ...

    @abstractmethod
    async def last_heartbeat_at(self, senior_id: UUID) -> datetime | None:
        """
        Returns the UTC timestamp of the most recent heartbeat from the device
        assigned to this senior, or None if no heartbeat has ever been recorded.
        """
        ...

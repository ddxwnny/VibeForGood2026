"""
Heartbeat port — the domain's interface for querying device heartbeat state.

The device sends periodic heartbeats. This port lets the sweep job ask
"when did this device last check in?" without coupling core to any transport.
AD-6: liveness is a separate series from interaction.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID


class HeartbeatPort(ABC):
    @abstractmethod
    async def last_heartbeat_at(self, senior_id: UUID) -> datetime | None:
        """
        Returns the UTC timestamp of the most recent heartbeat from the device
        assigned to this senior, or None if no heartbeat has ever been recorded.
        """
        ...

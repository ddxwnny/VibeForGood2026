"""
Delivery port — records that a weekly window was delivered.

FR-19: recipient delivery and senior delivery are always coupled.
This port has no partial-delivery method; both texts must be provided together.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class WindowDeliveryRecord:
    senior_id: UUID
    week_start: datetime
    recipient_delivered: bool
    senior_delivered: bool


class DeliveryLogPort(ABC):
    @abstractmethod
    async def record_window_delivery(
        self,
        senior_id: UUID,
        week_start: datetime,
        recipient_text: str,
        senior_text: str,
    ) -> WindowDeliveryRecord:
        """Record delivery of both recipient and senior texts together (FR-19)."""

    @abstractmethod
    async def get_deliveries_for_week(
        self,
        senior_id: UUID,
        week_start: datetime,
    ) -> list[WindowDeliveryRecord]:
        """Returns all delivery records for a given senior's week."""

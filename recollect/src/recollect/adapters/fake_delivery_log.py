"""Fake DeliveryLogPort for tests — captures delivery records for assertion."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from recollect.core.ports.delivery_port import DeliveryLogPort, WindowDeliveryRecord


class FakeDeliveryLog(DeliveryLogPort):
    def __init__(self) -> None:
        self.records: list[WindowDeliveryRecord] = []

    async def record_window_delivery(
        self,
        senior_id: UUID,
        week_start: datetime,
        recipient_text: str,
        senior_text: str,
    ) -> WindowDeliveryRecord:
        record = WindowDeliveryRecord(
            senior_id=senior_id,
            week_start=week_start,
            recipient_delivered=bool(recipient_text),
            senior_delivered=bool(senior_text),
        )
        self.records.append(record)
        return record

    async def get_deliveries_for_week(
        self,
        senior_id: UUID,
        week_start: datetime,
    ) -> list[WindowDeliveryRecord]:
        return [
            r for r in self.records
            if r.senior_id == senior_id and r.week_start == week_start
        ]

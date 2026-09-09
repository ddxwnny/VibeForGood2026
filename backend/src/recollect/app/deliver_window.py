"""
Window delivery — FR-19 architectural guarantee.

The named-recipient window and the senior's own delivery are always sent together.
There is no function in this module that sends one without the other.
Any code path that tried to deliver to the recipient while skipping the senior
would need to call record_window_delivery with an empty senior_text — which
the port is expected to reject or flag.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from recollect.core.ports.delivery_port import DeliveryLogPort, WindowDeliveryRecord
from recollect.core.weekly_window import ComposedWindow


async def deliver_window(
    senior_id: UUID,
    week_start: datetime,
    window: ComposedWindow,
    delivery_log: DeliveryLogPort,
) -> WindowDeliveryRecord:
    """
    Delivers the weekly window to both the named recipient and the senior (FR-18, FR-19).
    Both deliveries happen in a single call; there is no path to suppress one.
    """
    return await delivery_log.record_window_delivery(
        senior_id=senior_id,
        week_start=week_start,
        recipient_text=window.recipient_text,
        senior_text=window.senior_text,
    )

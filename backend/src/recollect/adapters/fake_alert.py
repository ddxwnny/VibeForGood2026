"""Fake AlertPort for tests — captures sent alerts for assertion."""

from __future__ import annotations

from recollect.core.ports.alert_port import AlertPort, CareWorkerAlert


class FakeAlert(AlertPort):
    def __init__(self) -> None:
        self.sent: list[CareWorkerAlert] = []

    async def send_care_worker_alert(self, alert: CareWorkerAlert) -> None:
        self.sent.append(alert)

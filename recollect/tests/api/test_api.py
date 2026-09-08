"""
End-to-end tests for the mock HTTP API.

Exercises every wired feature through the real ASGI app against the in-memory
adapters — proving the use cases work over HTTP, not just at the unit level.
"""

import base64

import pytest
from fastapi.testclient import TestClient

from recollect.edge.api.main import app
from recollect.edge.api.state import AppState


@pytest.fixture
def client() -> TestClient:
    app.state.store = AppState()
    with TestClient(app) as c:
        yield c


def _enrol(client: TestClient, name: str = "Mrs Tan", **overrides) -> dict:
    payload = {
        "display_name": name,
        "preferred_language": "zh-cmn-Hans-SG",
        "recipient_co_signature": True,
        "research_consent": True,
        "processor_disclosure_acknowledged": True,
        "ulysses_audio_base64": base64.b64encode(b"own voice").decode(),
    }
    payload.update(overrides)
    resp = client.post("/api/enrolments", json=payload)
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_health_and_mock_served(client: TestClient) -> None:
    assert client.get("/api/health").json() == {"status": "ok"}
    assert "Recollect" in client.get("/").text


def test_enrol_then_roster(client: TestClient) -> None:
    data = _enrol(client, name="Mrs Tan")
    senior_id = data["senior_id"]

    roster = client.get("/api/roster").json()["roster"]
    assert len(roster) == 1
    assert roster[0]["senior_id"] == senior_id
    assert roster[0]["consent_active"] is True


def test_record_and_read_observation(client: TestClient) -> None:
    senior_id = _enrol(client)["senior_id"]

    resp = client.post(
        f"/api/seniors/{senior_id}/observations",
        json={"signal_type": "medication", "outcome": "completed", "content": "took morning dose"},
    )
    assert resp.status_code == 200, resp.text

    series = client.get(f"/api/seniors/{senior_id}/observations").json()["observations"]
    assert len(series) == 1
    assert series[0]["signal_type"] == "medication"
    assert series[0]["outcome"] == "completed"


def test_observation_rejected_without_active_enrolment(client: TestClient) -> None:
    resp = client.post(
        "/api/seniors/00000000-0000-0000-0000-000000000000/observations",
        json={"signal_type": "medication", "outcome": "completed", "content": "x"},
    )
    assert resp.status_code == 400


def test_enrolment_rejected_when_consent_missing(client: TestClient) -> None:
    resp = client.post(
        "/api/enrolments",
        json={
            "display_name": "Mrs Lim",
            "recipient_co_signature": False,  # missing artefact
            "research_consent": True,
            "processor_disclosure_acknowledged": True,
            "ulysses_audio_base64": base64.b64encode(b"own voice").decode(),
        },
    )
    assert resp.status_code == 400


def test_weekly_window_composes_and_delivers(client: TestClient) -> None:
    senior_id = _enrol(client)["senior_id"]
    client.post(
        f"/api/seniors/{senior_id}/observations",
        json={"signal_type": "routine", "outcome": "completed", "content": "walked"},
    )

    resp = client.post(f"/api/seniors/{senior_id}/window", params={"baseline": "true"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["recipient_text"]
    assert body["senior_text"]
    assert body["recipient_delivered"] is True
    assert body["senior_delivered"] is True


def test_erase_shreds_and_stops_collection(client: TestClient) -> None:
    senior_id = _enrol(client)["senior_id"]
    client.post(
        f"/api/seniors/{senior_id}/observations",
        json={"signal_type": "medication", "outcome": "completed", "content": "dose"},
    )

    resp = client.post(f"/api/seniors/{senior_id}/erase", json={"reason": "withdrawal"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["reason"] == "withdrawal"
    assert "key" in body["stores_shredded"]

    # Collection has stopped — further writes are rejected.
    resp2 = client.post(
        f"/api/seniors/{senior_id}/observations",
        json={"signal_type": "medication", "outcome": "completed", "content": "dose"},
    )
    assert resp2.status_code == 400


def test_retention_sweep(client: TestClient) -> None:
    resp = client.post("/api/jobs/retention-sweep")
    assert resp.status_code == 200
    assert resp.json()["discarded"] == 0

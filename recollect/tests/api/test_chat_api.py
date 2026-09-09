"""
End-to-end API tests for the conversational Aunty chatbot endpoint:
POST /v1/seniors/{senior_id}/chat
"""

import base64
import pytest
from fastapi.testclient import TestClient

from recollect.edge.api.main import app
from recollect.edge.api.settings import Settings
from recollect.edge.api.state import AppState


@pytest.fixture
def client() -> TestClient:
    app.state.settings = Settings(environment="dev")
    app.state.store = AppState()
    with TestClient(app) as c:
        yield c


def _enrol(client: TestClient, name: str = "Mdm Tan") -> dict:
    payload = {
        "display_name": name,
        "preferred_language": "zh-cmn-Hans-SG",
        "recipient_co_signature": True,
        "research_consent": True,
        "processor_disclosure_acknowledged": True,
        "ulysses_audio_base64": base64.b64encode(b"own voice").decode(),
    }
    resp = client.post("/v1/enrolments", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_chat_requires_active_enrolment(client: TestClient) -> None:
    resp = client.post(
        "/v1/seniors/00000000-0000-0000-0000-000000000000/chat",
        json={"message": "Good morning!"},
    )
    assert resp.status_code == 400


def test_chat_normal_conversation(client: TestClient) -> None:
    senior_id = _enrol(client)["senior_id"]
    resp = client.post(
        f"/v1/seniors/{senior_id}/chat",
        json={"message": "Hello!"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "reply" in data
    assert "Mdm Tan" in data["reply"]
    assert len(data["observations_recorded"]) == 0


def test_chat_medication_auto_records_observation(client: TestClient) -> None:
    senior_id = _enrol(client)["senior_id"]
    resp = client.post(
        f"/v1/seniors/{senior_id}/chat",
        json={"message": "I already swallowed my morning pills with water."},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data["observations_recorded"]) == 1
    assert data["observations_recorded"][0]["signal_type"] == "medication"
    assert data["observations_recorded"][0]["outcome"] == "completed"

    # Verify persisted in functional series
    series_resp = client.get(f"/v1/seniors/{senior_id}/observations")
    assert series_resp.status_code == 200
    obs = series_resp.json()["observations"]
    assert len(obs) == 1
    assert obs[0]["signal_type"] == "medication"


def test_chat_friend_guardrail_per_fr34(client: TestClient) -> None:
    senior_id = _enrol(client)["senior_id"]
    resp = client.post(
        f"/v1/seniors/{senior_id}/chat",
        json={"message": "Are you my friend?"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "helper" in data["reply"].lower()
    assert "not a companion or a friend" in data["reply"].lower()


def test_chat_with_audio_base64_stt_transcription(client: TestClient) -> None:
    senior_id = _enrol(client)["senior_id"]
    # AppState fake STT will transcribe the mock bytes
    fake_audio = base64.b64encode(b"audio stream data").decode("utf-8")
    resp = client.post(
        f"/v1/seniors/{senior_id}/chat",
        json={"audio_base64": fake_audio},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "transcript" in data
    assert "reply" in data
    assert len(data["reply"]) > 0

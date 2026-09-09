"""
Tests for Place Memories and Dementia Reminiscence Cognitive Screening:
- GET /v1/seniors/{senior_id}/places
- POST /v1/seniors/{senior_id}/places
- DELETE /v1/seniors/{senior_id}/places/{place_id}
- Reminiscence dialogue extraction in chat
"""

import base64
import pytest
from fastapi.testclient import TestClient

from recollect.edge.api.main import app
from recollect.edge.api.settings import Settings
from recollect.edge.api.state import AppState
from recollect.core.entities import SignalType, TaskOutcome


@pytest.fixture
def client() -> TestClient:
    from recollect.edge.api.middleware import _limiter
    _limiter.reset()
    app.state.settings = Settings(environment="dev", seed_demo_data=False)
    app.state.store = AppState()
    with TestClient(app) as c:
        yield c


def _enrol(client: TestClient, name: str = "Uncle Arun") -> dict:
    payload = {
        "display_name": name,
        "preferred_language": "en-SG",
        "recipient_co_signature": True,
        "research_consent": True,
        "processor_disclosure_acknowledged": True,
        "ulysses_audio_base64": base64.b64encode(b"voice sample").decode(),
    }
    resp = client.post("/v1/enrolments", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_places_crud_lifecycle(client: TestClient) -> None:
    senior_id = _enrol(client)["senior_id"]

    # 1. List initial places (seeded demo places or empty)
    resp = client.get(f"/v1/seniors/{senior_id}/places")
    assert resp.status_code == 200
    data = resp.json()
    assert "places" in data
    initial_count = len(data["places"])

    # 2. Add a new place
    new_place_payload = {
        "title": "Tiong Bahru Market",
        "description": "Where uncle Arun eats chwee kueh with friends.",
        "image_url": "https://example.com/tiongbahru.jpg",
        "personal_memory": "Ate breakfast here every weekend for 20 years.",
        "recognition_keys": ["tiong bahru", "chwee kueh", "market", "breakfast"],
        "prompt_question": "Do you remember the hawker center where you loved eating chwee kueh?",
    }
    create_resp = client.post(f"/v1/seniors/{senior_id}/places", json=new_place_payload)
    assert create_resp.status_code == 201, create_resp.text
    created_place = create_resp.json()
    assert created_place["title"] == "Tiong Bahru Market"
    assert created_place["senior_id"] == senior_id
    place_id = created_place["id"]

    # 3. Verify in list
    resp = client.get(f"/v1/seniors/{senior_id}/places")
    assert resp.status_code == 200
    places = resp.json()["places"]
    assert len(places) == initial_count + 1
    assert any(p["id"] == place_id for p in places)

    # 4. Delete place
    del_resp = client.delete(f"/v1/seniors/{senior_id}/places/{place_id}")
    assert del_resp.status_code == 200

    # 5. Verify deleted
    resp = client.get(f"/v1/seniors/{senior_id}/places")
    assert resp.status_code == 200
    places = resp.json()["places"]
    assert not any(p["id"] == place_id for p in places)


def test_chat_dialogue_place_memory_recall_completed(client: TestClient) -> None:
    senior_id = _enrol(client)["senior_id"]

    # Senior recalls Changi Beach
    chat_resp = client.post(
        f"/v1/seniors/{senior_id}/chat",
        json={"message": "Oh yes! That's Changi Beach! I used to go cycling there every Sunday."},
    )
    assert chat_resp.status_code == 200
    data = chat_resp.json()
    assert len(data["observations_recorded"]) == 1
    obs = data["observations_recorded"][0]
    assert obs["signal_type"] == "place_memory"
    assert obs["outcome"] == "completed"
    assert "changi beach" in obs["content"].lower()


def test_chat_dialogue_place_memory_recall_incomplete(client: TestClient) -> None:
    senior_id = _enrol(client)["senior_id"]

    # Senior doesn't remember (with exact phrasing "I do not remember this place.")
    chat_resp = client.post(
        f"/v1/seniors/{senior_id}/chat",
        json={"message": "I do not remember this place."},
    )
    assert chat_resp.status_code == 200
    data = chat_resp.json()
    assert len(data["observations_recorded"]) == 1
    obs = data["observations_recorded"][0]
    assert obs["signal_type"] == "place_memory"
    assert obs["outcome"] == "incomplete"


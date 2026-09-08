from fastapi.testclient import TestClient

from recollect.edge.api.main import app

client = TestClient(app)


def test_health_ok():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_mock_frontend_served():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Recollect" in resp.text

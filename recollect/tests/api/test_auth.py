"""
Authentication/authorisation tests (NFR-15, AD-7).

Verifies that in production mode human surfaces must present a valid API key
that resolves to an active Grant, and that senior-specific access is enforced.
Dev mode remains permissive so the mock frontend and tests keep working.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from recollect.core.entities import Grant, GrantRole, GrantScope
from recollect.edge.api.main import app
from recollect.edge.api.settings import Settings
from recollect.edge.api.state import AppState


def _api_key_hash(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def _make_grant(senior_id: UUID, role: GrantRole, scope: GrantScope) -> Grant:
    return Grant(
        id=uuid4(),
        senior_id=senior_id,
        role=role,
        scope=scope,
        granted_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def context():
    key = "secret-care-worker-key"
    senior_id = uuid4()
    grant = _make_grant(senior_id, GrantRole.CARE_WORKER, GrantScope.ROSTER)

    from recollect.adapters.fake_grant_store import FakeGrantStore

    store = AppState()
    seeded = FakeGrantStore()
    seeded._grants[grant.id] = (grant, _api_key_hash(key))
    store.grant_store = seeded

    app.state.settings = Settings(environment="production")
    app.state.store = store
    with TestClient(app) as c:
        yield c, key, senior_id


def test_phone_surface_requires_api_key(context) -> None:
    client, _key, _senior = context
    resp = client.get("/v1/roster")
    assert resp.status_code == 401


def test_phone_surface_accepts_valid_key(context) -> None:
    client, key, _senior = context
    resp = client.get("/v1/roster", headers={"Authorization": f"Bearer {key}"})
    assert resp.status_code == 200


def test_phone_surface_rejects_unknown_key(context) -> None:
    client, _key, _senior = context
    resp = client.get("/v1/roster", headers={"Authorization": "Bearer wrong"})
    assert resp.status_code == 401


def test_senior_specific_scope_enforced(context) -> None:
    client, key, _senior = context
    other = uuid4()
    resp = client.post(
        f"/v1/seniors/{other}/window",
        headers={"Authorization": f"Bearer {key}"},
    )
    assert resp.status_code == 403

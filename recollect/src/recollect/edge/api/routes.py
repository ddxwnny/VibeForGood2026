"""
HTTP routes for the mock API (throwaway delivery layer).

Wires the implemented use cases to in-memory adapters so every feature can be
exercised over HTTP before the real Postgres / vendor adapters and Next.js
surface land. The API contract here is thin — it exists to make the mock
frontend work; production endpoints will carry auth, validation, and the real
adapters.

Errors: domain rule violations (RecollectError) map to HTTP 400 so the write
path's rejections are observable; anything else bubbles up as 500.
"""

from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel
from uuid_extensions import uuid7

from recollect.app.compose_weekly_window import compose_weekly_window
from recollect.app.deliver_window import deliver_window
from recollect.app.enrol_senior import EnrolmentRequest, enrol_senior
from recollect.app.erase_senior import erase_senior
from recollect.app.record_task import TaskRecordRequest, record_task
from recollect.app.retention_sweep import run_retention_sweep
from recollect.app.roster import build_roster
from recollect.core.entities import (
    ErasureReason,
    Senior,
    SignalType,
    TaskOutcome,
)
from recollect.core.errors import RecollectError
from recollect.core.ports.clock_port import SystemClock
from recollect.edge.api.state import AppState

router = APIRouter()
_clock = SystemClock()


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------


class EnrolmentBody(BaseModel):
    display_name: str
    preferred_language: str = "en-SG"
    visit_at: str | None = None
    recipient_co_signature: bool
    research_consent: bool
    processor_disclosure_acknowledged: bool
    ulysses_audio_base64: str


class ObservationBody(BaseModel):
    signal_type: str
    outcome: str
    content: str
    occurred_at: str | None = None


class EraseBody(BaseModel):
    reason: str


def _store(request: Request) -> AppState:
    return request.app.state.store


def _parse_utc(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Enrolment (Epic 2)
# ---------------------------------------------------------------------------


@router.post("/api/enrolments")
async def create_enrolment(body: EnrolmentBody, request: Request) -> dict:
    store = _store(request)
    try:
        audio = base64.b64decode(body.ulysses_audio_base64)
        senior = Senior(
            id=uuid7(),
            display_name=body.display_name,
            preferred_language=body.preferred_language,
            created_at=_parse_utc(body.visit_at) or _clock.utc_now(),
        )
        enrolment = await enrol_senior(
            EnrolmentRequest(
                senior=senior,
                visit_at=_parse_utc(body.visit_at) or _clock.utc_now(),
                recipient_co_signature=body.recipient_co_signature,
                research_consent=body.research_consent,
                processor_disclosure_acknowledged=body.processor_disclosure_acknowledged,
                ulysses_audio_bytes=audio,
            ),
            log=store.log,
            audio_store=store.audio_store,
        )
        await store.key_store.create_key(senior.id)
        store.seniors[senior.id] = senior.display_name
    except RecollectError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"senior_id": str(senior.id), "enrolment_id": str(enrolment.id)}


# ---------------------------------------------------------------------------
# Observations (Epic 1, Epic 4)
# ---------------------------------------------------------------------------


@router.post("/api/seniors/{senior_id}/observations")
async def record_observation(senior_id: str, body: ObservationBody, request: Request) -> dict:
    store = _store(request)
    try:
        senior_uuid = UUID(senior_id)
        signal_type = SignalType(body.signal_type)
        outcome = TaskOutcome(body.outcome)
        observation = await record_task(
            TaskRecordRequest(
                senior_id=senior_uuid,
                interaction_id=uuid7(),
                occurred_at=_parse_utc(body.occurred_at) or _clock.utc_now(),
                signal_type=signal_type,
                outcome=outcome,
                content=body.content,
            ),
            log=store.log,
        )
    except RecollectError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"observation_id": str(observation.id)}


@router.get("/api/seniors/{senior_id}/observations")
async def list_observations(
    senior_id: str,
    request: Request,
    from_utc: str | None = Query(default=None, alias="from"),
    to_utc: str | None = Query(default=None, alias="to"),
) -> dict:
    store = _store(request)
    try:
        senior_uuid = UUID(senior_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    now = _clock.utc_now()
    start = _parse_utc(from_utc) or (now - timedelta(days=7))
    end = _parse_utc(to_utc) or now

    entries = await store.log.get_window(senior_uuid, from_utc=start, to_utc=end)
    return {
        "observations": [
            {
                "id": str(o.id),
                "signal_type": o.provenance.signal_type.value,
                "outcome": o.outcome.value if o.outcome else None,
                "content": o.content,
                "occurred_at": _iso(o.provenance.occurred_at),
                "supersedes_id": str(o.supersedes_id) if o.supersedes_id else None,
            }
            for o in entries
        ]
    }


# ---------------------------------------------------------------------------
# Roster (Epic 3)
# ---------------------------------------------------------------------------


@router.get("/api/roster")
async def roster(request: Request) -> dict:
    store = _store(request)
    senior_ids = list(store.seniors.keys())
    entries = await build_roster(senior_ids, store.seniors, store.log, store.heartbeat)
    return {
        "roster": [
            {
                "senior_id": str(e.senior_id),
                "display_name": e.display_name,
                "consent_active": e.consent_active,
                "device_reachable": e.device_reachable,
                "enrolled_at": _iso(e.enrolled_at),
            }
            for e in entries
        ]
    }


# ---------------------------------------------------------------------------
# Weekly window (Epic 6)
# ---------------------------------------------------------------------------


@router.post("/api/seniors/{senior_id}/window")
async def weekly_window(
    senior_id: str,
    request: Request,
    from_utc: str | None = Query(default=None, alias="from"),
    to_utc: str | None = Query(default=None, alias="to"),
    baseline: bool = Query(default=False),
) -> dict:
    store = _store(request)
    try:
        senior_uuid = UUID(senior_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    now = _clock.utc_now()
    start = _parse_utc(from_utc) or (now - timedelta(days=7))
    end = _parse_utc(to_utc) or now
    name = store.seniors.get(senior_uuid, "Unknown")

    try:
        window = await compose_weekly_window(
            senior_id=senior_uuid,
            senior_name=name,
            week_start=start,
            week_end=end,
            is_baseline=baseline,
            log=store.log,
            composer=store.composer,
        )
        delivery = await deliver_window(
            senior_id=senior_uuid, week_start=start, window=window, delivery_log=store.delivery_log
        )
    except Exception as exc:  # WindowViolationError and friends
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "recipient_text": window.recipient_text,
        "senior_text": window.senior_text,
        "recipient_delivered": delivery.recipient_delivered,
        "senior_delivered": delivery.senior_delivered,
    }


# ---------------------------------------------------------------------------
# Erasure (Epic 7)
# ---------------------------------------------------------------------------


@router.post("/api/seniors/{senior_id}/erase")
async def erase(senior_id: str, body: EraseBody, request: Request) -> dict:
    store = _store(request)
    try:
        senior_uuid = UUID(senior_id)
        reason = ErasureReason(body.reason)
        tombstone = await erase_senior(
            senior_id=senior_uuid,
            reason=reason,
            key_store=store.key_store,
            log=store.log,
            raw_audio=store.raw_audio,
            audio_store=store.audio_store,
            clock=_clock,
        )
    except RecollectError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "senior_id": str(tombstone.senior_id),
        "reason": tombstone.reason.value,
        "shredded_at": _iso(tombstone.shredded_at),
        "stores_shredded": sorted(tombstone.stores_shredded),
    }


# ---------------------------------------------------------------------------
# Jobs (Epic 3, Epic 7)
# ---------------------------------------------------------------------------


@router.post("/api/jobs/retention-sweep")
async def retention_sweep(request: Request) -> dict:
    store = _store(request)
    result = await run_retention_sweep(raw_audio=store.raw_audio, clock=_clock)
    return {"discarded": result.discarded, "cutoff": _iso(result.cutoff)}

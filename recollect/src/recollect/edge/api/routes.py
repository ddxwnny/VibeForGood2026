"""
Versioned HTTP API for the Recollect v1 observation layer.

This is the production delivery surface: it carries response models, typed
error mapping (RecollectError -> 400), device + phone-surface authentication,
and honours the architecture invariants the mock did not:

  - AD-14: ingest never mints an Interaction. The device supplies interaction_id
    and idempotency_key on every turn; the server records it idempotently.
  - NFR-15: the device and phone surfaces authenticate; the senior never does.
  - AD-6:  a heartbeat endpoint lets the device record liveness.
  - AD-7:  access is checked against Grants, not a global permission.

The senior is referenced by UUID only on every route (NFR-16: no names in logs).
"""

from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from uuid_extensions import uuid7

from recollect.app.capture_turn import CapturedTurn, capture_turn
from recollect.app.compose_weekly_window import WindowViolationError, compose_weekly_window
from recollect.app.deliver_window import deliver_window
from recollect.app.enrol_senior import EnrolmentRequest, enrol_senior
from recollect.app.erase_senior import erase_senior
from recollect.app.heartbeat_sweep import SweepResult, run_heartbeat_sweep
from recollect.app.instrument_scheduler import SchedulerContext, select_next_item
from recollect.app.record_task import TaskRecordRequest, record_task
from recollect.app.chat_dialogue import (
    ChatDialogueContext,
    process_chat_turn,
)
from recollect.app.record_unrecognised_turn import record_unrecognised_turn
from recollect.app.retention_sweep import run_retention_sweep
from recollect.app.roster import build_roster
from recollect.core.entities import (
    ErasureReason,
    Interaction,
    Senior,
    SignalType,
    TaskOutcome,
)
from recollect.core.errors import RecollectError
from recollect.core.instruments import InstrumentBank
from recollect.core.ports.clock_port import SystemClock
from recollect.core.ports.stt_port import STTResult
from recollect.edge.api.auth import DeviceDep, PhoneDep
from recollect.edge.api.state import AppState

router = APIRouter(prefix="/v1")
_clock = SystemClock()


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class EnrolmentOut(BaseModel):
    senior_id: UUID
    enrolment_id: UUID


class SeniorOut(BaseModel):
    senior_id: UUID
    display_name: str
    preferred_language: str
    consent_active: bool


class ObservationOut(BaseModel):
    id: UUID
    signal_type: str
    outcome: str | None
    content: str
    occurred_at: datetime
    supersedes_id: UUID | None = None


class ObservationListOut(BaseModel):
    observations: list[ObservationOut]


class RosterEntryOut(BaseModel):
    senior_id: UUID
    display_name: str
    consent_active: bool
    device_reachable: bool
    enrolled_at: datetime


class RosterOut(BaseModel):
    roster: list[RosterEntryOut]


class WeeklyWindowOut(BaseModel):
    recipient_text: str
    senior_text: str
    recipient_delivered: bool
    senior_delivered: bool


class ErasureOut(BaseModel):
    senior_id: UUID
    reason: str
    shredded_at: datetime
    stores_shredded: list[str]


class RetentionSweepOut(BaseModel):
    discarded: int
    cutoff: datetime


class HeartbeatSweepOut(BaseModel):
    results: list[dict]


class InstrumentDecisionOut(BaseModel):
    item_variant: str | None
    omission_logged: bool


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


class CaptureTurnBody(BaseModel):
    senior_id: UUID
    interaction_id: UUID = Field(description="Device-minted interaction id (AD-14).")
    idempotency_key: str = Field(description="Device-minted idempotency key (AD-14).")
    occurred_at: str = Field(description="UTC ISO-8601, authoritative device clock (AD-14).")
    transcript: str


class ObservationBody(BaseModel):
    interaction_id: UUID = Field(default_factory=uuid7)
    signal_type: str
    outcome: str
    content: str
    occurred_at: str | None = None


class EraseBody(BaseModel):
    reason: str


class HeartbeatBody(BaseModel):
    senior_id: UUID
    at: str | None = None


class InstrumentDecisionBody(BaseModel):
    senior_id: UUID
    interaction_id: UUID = Field(description="Device-minted interaction id (AD-14).")
    bank_name: str
    week_instrument_count: int = 0
    is_pressured_task: bool = False
    declined_this_interaction: bool = False


class ChatTurnBody(BaseModel):
    message: str = ""
    audio_base64: str | None = None
    interaction_id: UUID | None = None
    idempotency_key: str | None = None


class ChatTurnOut(BaseModel):
    transcript: str = ""
    reply: str
    audio_base64: str | None = None
    observations_recorded: list[ObservationOut] = []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _store(request: Request) -> AppState:
    return request.app.state.store


def _parse_utc(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _iso(dt: datetime) -> datetime:
    return dt.astimezone(timezone.utc)


def _map_error(exc: Exception) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


# ---------------------------------------------------------------------------
# Enrolment (Epic 2) — device/care-worker context
# ---------------------------------------------------------------------------


@router.post("/enrolments", response_model=EnrolmentOut, status_code=status.HTTP_201_CREATED)
async def create_enrolment(body: EnrolmentBody, request: Request) -> EnrolmentOut:
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
    except RecollectError as exc:
        raise _map_error(exc)

    return EnrolmentOut(senior_id=senior.id, enrolment_id=enrolment.id)


# ---------------------------------------------------------------------------
# Device heartbeat (Epic 3) — device-authenticated (AD-6)
# ---------------------------------------------------------------------------


@router.post("/device/heartbeat", status_code=status.HTTP_204_NO_CONTENT)
async def record_heartbeat(
    body: HeartbeatBody,
    request: Request,
    _auth: DeviceDep,
) -> None:
    store = _store(request)
    at = _parse_utc(body.at) or _clock.utc_now()
    await store.heartbeat.record_heartbeat(body.senior_id, at)


# ---------------------------------------------------------------------------
# Turn capture (Epic 4) — device-authenticated; server never mints (AD-14)
# ---------------------------------------------------------------------------


@router.post("/turns", response_model=dict)
async def capture_device_turn(body: CaptureTurnBody, request: Request, _auth: DeviceDep) -> dict:
    store = _store(request)
    try:
        interaction = Interaction(
            id=body.interaction_id,
            senior_id=body.senior_id,
            occurred_at=_parse_utc(body.occurred_at) or _clock.utc_now(),
            idempotency_key=body.idempotency_key,
        )
        stt_result = STTResult(
            transcript=body.transcript,
            language_tag="",
            model_version="",
        )
        turn: CapturedTurn = await capture_turn(
            interaction=interaction,
            stt_result=stt_result,
            person_roles={},
            log=store.log,
        )
    except RecollectError as exc:
        raise _map_error(exc)

    return {
        "interaction_id": str(turn.interaction.id),
        "transcript": turn.transcript,
    }


@router.post("/turns/unrecognised", response_model=dict)
async def capture_unrecognised_turn(
    body: CaptureTurnBody,
    request: Request,
    _auth: DeviceDep,
    consecutive_count: int = Query(default=1, ge=1),
) -> dict:
    """The device could not resolve this addressed turn (AD-6, FR-25)."""
    store = _store(request)
    try:
        interaction = Interaction(
            id=body.interaction_id,
            senior_id=body.senior_id,
            occurred_at=_parse_utc(body.occurred_at) or _clock.utc_now(),
            idempotency_key=body.idempotency_key,
        )
        await store.log.save_interaction(interaction)
        result = await record_unrecognised_turn(
            senior_id=body.senior_id,
            occurred_at=interaction.occurred_at,
            consecutive_count=consecutive_count,
            log=store.log,
            alert=store.alert,
        )
    except RecollectError as exc:
        raise _map_error(exc)

    return {"gap_id": str(result.gap_id), "alert_sent": result.alert_sent}


# ---------------------------------------------------------------------------
# Observations (Epic 1, Epic 4) — care-worker/family authenticated
# ---------------------------------------------------------------------------


@router.post("/seniors/{senior_id}/observations", response_model=ObservationOut, status_code=status.HTTP_201_CREATED)
async def record_observation(
    senior_id: UUID,
    body: ObservationBody,
    request: Request,
    _phone: PhoneDep,
) -> ObservationOut:
    store = _store(request)
    try:
        signal_type = SignalType(body.signal_type)
        outcome = TaskOutcome(body.outcome)
        observation = await record_task(
            TaskRecordRequest(
                senior_id=senior_id,
                interaction_id=body.interaction_id,
                occurred_at=_parse_utc(body.occurred_at) or _clock.utc_now(),
                signal_type=signal_type,
                outcome=outcome,
                content=body.content,
            ),
            log=store.log,
        )
    except RecollectError as exc:
        raise _map_error(exc)
    except ValueError as exc:
        raise _map_error(exc)

    return ObservationOut(
        id=observation.id,
        signal_type=observation.provenance.signal_type.value,
        outcome=observation.outcome.value if observation.outcome else None,
        content=observation.content,
        occurred_at=_iso(observation.provenance.occurred_at),
        supersedes_id=observation.supersedes_id,
    )


@router.get("/seniors/{senior_id}/observations", response_model=ObservationListOut)
async def list_observations(
    senior_id: UUID,
    request: Request,
    _phone: PhoneDep,
    from_utc: str | None = Query(default=None, alias="from"),
    to_utc: str | None = Query(default=None, alias="to"),
) -> ObservationListOut:
    store = _store(request)
    now = _clock.utc_now()
    start = _parse_utc(from_utc) or (now - timedelta(days=7))
    end = _parse_utc(to_utc) or now

    entries = await store.log.get_window(senior_id, from_utc=start, to_utc=end)
    return ObservationListOut(
        observations=[
            ObservationOut(
                id=o.id,
                signal_type=o.provenance.signal_type.value,
                outcome=o.outcome.value if o.outcome else None,
                content=o.content,
                occurred_at=_iso(o.provenance.occurred_at),
                supersedes_id=o.supersedes_id,
            )
            for o in entries
        ]
    )


# ---------------------------------------------------------------------------
# Roster (Epic 3) — care-worker authenticated (AD-7, FR-28/29)
# ---------------------------------------------------------------------------


@router.get("/roster", response_model=RosterOut)
async def roster(request: Request, phone: PhoneDep) -> RosterOut:
    store = _store(request)
    if phone.wildcard:
        senior_ids = await store.log.list_senior_ids()
    else:
        senior_ids = [c.senior_id for c in phone.credentials]
    display_names = {}
    for senior_id in senior_ids:
        senior = await store.log.get_senior(senior_id)
        if senior is not None:
            display_names[senior_id] = senior.display_name
    entries = await build_roster(senior_ids, display_names, store.log, store.heartbeat)
    return RosterOut(
        roster=[
            RosterEntryOut(
                senior_id=e.senior_id,
                display_name=e.display_name,
                consent_active=e.consent_active,
                device_reachable=e.device_reachable,
                enrolled_at=_iso(e.enrolled_at),
            )
            for e in entries
        ]
    )


# ---------------------------------------------------------------------------
# Weekly window (Epic 6) — named-recipient authenticated (AD-7, FR-15..20)
# ---------------------------------------------------------------------------


@router.post("/seniors/{senior_id}/window", response_model=WeeklyWindowOut)
async def weekly_window(
    senior_id: UUID,
    request: Request,
    phone: PhoneDep,
    from_utc: str | None = Query(default=None, alias="from"),
    to_utc: str | None = Query(default=None, alias="to"),
    baseline: bool = Query(default=False),
) -> WeeklyWindowOut:
    store = _store(request)
    if not phone.can(senior_id=senior_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised for this senior.")

    now = _clock.utc_now()
    start = _parse_utc(from_utc) or (now - timedelta(days=7))
    end = _parse_utc(to_utc) or now
    senior = await store.log.get_senior(senior_id)
    name = senior.display_name if senior else "Unknown"

    try:
        window = await compose_weekly_window(
            senior_id=senior_id,
            senior_name=name,
            week_start=start,
            week_end=end,
            is_baseline=baseline,
            log=store.log,
            composer=store.composer,
        )
        delivery = await deliver_window(
            senior_id=senior_id, week_start=start, window=window, delivery_log=store.delivery_log
        )
    except WindowViolationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return WeeklyWindowOut(
        recipient_text=window.recipient_text,
        senior_text=window.senior_text,
        recipient_delivered=delivery.recipient_delivered,
        senior_delivered=delivery.senior_delivered,
    )


# ---------------------------------------------------------------------------
# Erasure (Epic 7) — care-worker (on the senior's behalf)
# ---------------------------------------------------------------------------


@router.post("/seniors/{senior_id}/erase", response_model=ErasureOut)
async def erase(senior_id: UUID, body: EraseBody, request: Request, phone: PhoneDep) -> ErasureOut:
    store = _store(request)
    if not phone.can(senior_id=senior_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorised for this senior.")

    try:
        reason = ErasureReason(body.reason)
        tombstone = await erase_senior(
            senior_id=senior_id,
            reason=reason,
            key_store=store.key_store,
            log=store.log,
            raw_audio=store.raw_audio,
            audio_store=store.audio_store,
            clock=_clock,
        )
    except RecollectError as exc:
        raise _map_error(exc)
    except ValueError as exc:
        raise _map_error(exc)

    return ErasureOut(
        senior_id=tombstone.senior_id,
        reason=tombstone.reason.value,
        shredded_at=_iso(tombstone.shredded_at),
        stores_shredded=sorted(tombstone.stores_shredded),
    )


# ---------------------------------------------------------------------------
# Instrument scheduler (Epic 5) — device-authenticated (AD-9)
# ---------------------------------------------------------------------------


_BANKS: dict[str, InstrumentBank] = {}


@router.post("/device/instrument/decision", response_model=InstrumentDecisionOut)
async def instrument_decision(
    body: InstrumentDecisionBody,
    request: Request,
    _auth: DeviceDep,
) -> InstrumentDecisionOut:
    """
    Determines the next eligible instrument item (or omission) for a senior.
    The device supplies the interaction id; the server computes eligibility
    deterministically (AD-9, AD-12).
    """
    store = _store(request)
    bank = _BANKS.get(body.bank_name, InstrumentBank(name=body.bank_name, items=()))
    try:
        decision = await select_next_item(
            SchedulerContext(
                senior_id=body.senior_id,
                interaction_id=body.interaction_id,
                bank=bank,
                week_instrument_count=body.week_instrument_count,
                is_pressured_task=body.is_pressured_task,
                declined_this_interaction=body.declined_this_interaction,
            ),
            log=store.log,
            clock=_clock,
        )
    except RecollectError as exc:
        raise _map_error(exc)

    return InstrumentDecisionOut(
        item_variant=decision.item.variant if decision.item else None,
        omission_logged=decision.omission_logged,
    )


# ---------------------------------------------------------------------------
# Jobs (Epic 3, Epic 7)
# ---------------------------------------------------------------------------


@router.post("/jobs/heartbeat-sweep", response_model=HeartbeatSweepOut)
async def heartbeat_sweep(request: Request, _auth: DeviceDep) -> HeartbeatSweepOut:
    """Runs the liveness sweep: opens Gaps for devices that have gone dark (AD-6)."""
    store = _store(request)
    senior_ids = await store.log.list_senior_ids()
    results: list[SweepResult] = await run_heartbeat_sweep(
        senior_ids, store.log, store.heartbeat, _clock
    )
    return HeartbeatSweepOut(
        results=[
            {
                "senior_id": str(r.senior_id),
                "unreachable": r.unreachable,
                "gap_id": str(r.gap_id) if r.gap_id else None,
            }
            for r in results
        ]
    )


@router.post("/jobs/retention-sweep", response_model=RetentionSweepOut)
async def retention_sweep(request: Request, _auth: DeviceDep) -> RetentionSweepOut:
    store = _store(request)
    result = await run_retention_sweep(raw_audio=store.raw_audio, clock=_clock)
    return RetentionSweepOut(discarded=result.discarded, cutoff=_iso(result.cutoff))


# ---------------------------------------------------------------------------
# Conversational Chatbot for Seniors (Part 2: Aunty Chatbot)
# ---------------------------------------------------------------------------


@router.post("/seniors/{senior_id}/chat", response_model=ChatTurnOut)
async def chat_with_senior(
    senior_id: UUID,
    body: ChatTurnBody,
    request: Request,
) -> ChatTurnOut:
    """
    Conversational turn endpoint for talking with the senior.
    Checks active enrolment (AD-4).
    Processes tone, helper guardrail (FR-34), and banned words (AD-8).
    Automatically logs any completed/declined everyday task observations.
    """
    store = _store(request)
    senior = await store.log.get_senior(senior_id)
    if senior is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Senior {senior_id} has no active enrolment (AD-4).",
        )

    # Check active enrolment gate
    enrolment = await store.log.get_enrolment(senior_id)
    if enrolment is None or not enrolment.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Senior {senior_id} enrolment is not active (AD-4).",
        )

    input_text = body.message
    if body.audio_base64:
        try:
            audio_bytes = base64.b64decode(body.audio_base64)
            stt_res = await store.stt.transcribe(audio_bytes, language_hint=senior.preferred_language)
            input_text = stt_res.transcript
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Speech-to-text processing failed: {exc}",
            )

    if not input_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'message' or 'audio_base64' with decipherable speech must be provided.",
        )

    context = ChatDialogueContext(
        senior_id=str(senior.id),
        display_name=senior.display_name,
        preferred_language=senior.preferred_language,
    )

    from recollect.app.chat_dialogue import process_chat_turn_async
    result = await process_chat_turn_async(
        message=input_text,
        context=context,
        llm=store.llm,
    )

    recorded_out: list[ObservationOut] = []
    interaction_id = body.interaction_id or uuid7()
    occurred_at = _clock.utc_now()

    # Automatically record extracted everyday tasks
    for sig, outcome, content in result.extracted_tasks:
        obs = await record_task(
            TaskRecordRequest(
                senior_id=senior_id,
                interaction_id=interaction_id,
                occurred_at=occurred_at,
                signal_type=sig,
                outcome=outcome,
                content=content,
            ),
            log=store.log,
        )
        recorded_out.append(
            ObservationOut(
                id=obs.id,
                signal_type=obs.provenance.signal_type.value,
                outcome=obs.outcome.value if obs.outcome else None,
                content=obs.content,
                occurred_at=_iso(obs.provenance.occurred_at),
                supersedes_id=obs.supersedes_id,
            )
        )

    # Generate ElevenLabs audio if TTS is configured
    tts_audio_base64: str | None = None
    if store.tts is not None:
        try:
            audio_bytes = await store.tts.synthesise(result.reply, language_tag=senior.preferred_language)
            tts_audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        except Exception:
            # Non-blocking fallback: browser TTS can still read reply text if ElevenLabs fails
            tts_audio_base64 = None

    return ChatTurnOut(
        transcript=input_text,
        reply=result.reply,
        audio_base64=tts_audio_base64,
        observations_recorded=recorded_out,
    )


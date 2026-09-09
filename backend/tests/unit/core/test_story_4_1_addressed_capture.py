"""
Tests for Epic 4, story 4.1: addressed-only capture with no login.

  FR-1 (no login): capture_turn needs no credential object — no auth step exists.
  FR-2 (only addressed turns): the device only mints addressed Interactions (AD-5);
       ingest is idempotent on the idempotency key (AD-14).
  FR-3 (redaction): named third parties are redacted to role.
"""

import pytest
from datetime import datetime, timezone

from uuid_extensions import uuid7

from recollect.adapters.fake_log import FakeObservationLog
from recollect.app.capture_turn import capture_turn
from recollect.core.entities import Interaction
from recollect.core.errors import DuplicateInteractionError
from recollect.core.ports.stt_port import STTResult


def _utc(ts: str) -> datetime:
    return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)


NOW = _utc("2026-09-09T10:00:00")
SENIOR_ID = uuid7()


def _interaction(idempotency_key: str = "turn-1") -> Interaction:
    return Interaction(
        id=uuid7(),
        senior_id=SENIOR_ID,
        occurred_at=NOW,
        idempotency_key=idempotency_key,
    )


def _stt(transcript: str = "I saw Mei Lin at the market today.") -> STTResult:
    return STTResult(
        transcript=transcript,
        language_tag="en-SG",
        model_version="stt-v1",
    )


@pytest.mark.asyncio
async def test_capture_requires_no_login() -> None:
    """FR-1: no credential / auth object is ever passed to the capture path."""
    log = FakeObservationLog()
    result = await capture_turn(_interaction(), _stt(), {}, log)
    assert result.transcript is not None


@pytest.mark.asyncio
async def test_interaction_recorded_idempotently() -> None:
    log = FakeObservationLog()
    result = await capture_turn(_interaction("turn-1"), _stt(), {}, log)
    stored = await log.get_interaction(result.interaction.id)
    assert stored is not None
    assert stored.idempotency_key == "turn-1"


@pytest.mark.asyncio
async def test_duplicate_interaction_rejected() -> None:
    """FR-2 / AD-14: the same idempotency key cannot be ingested twice."""
    log = FakeObservationLog()
    await capture_turn(_interaction("turn-dup"), _stt(), {}, log)
    with pytest.raises(DuplicateInteractionError):
        await capture_turn(_interaction("turn-dup"), _stt(), {}, log)


@pytest.mark.asyncio
async def test_third_party_redacted_to_role() -> None:
    """FR-3: a named third party is replaced by role, never stored by name."""
    log = FakeObservationLog()
    roles = {"Mei Lin": "her daughter"}
    result = await capture_turn(_interaction(), _stt(), roles, log)
    assert "Mei Lin" not in result.transcript
    assert "her daughter" in result.transcript


@pytest.mark.asyncio
async def test_senior_own_name_not_redacted() -> None:
    log = FakeObservationLog()
    result = await capture_turn(
        _interaction(),
        _stt("I am Mdm Lim and I took my pills."),
        {"Mei Lin": "her daughter"},
        log,
    )
    assert "Mdm Lim" in result.transcript


@pytest.mark.asyncio
async def test_longest_name_redacted_first() -> None:
    log = FakeObservationLog()
    roles = {"Mei": "someone", "Mei Lin": "her daughter"}
    result = await capture_turn(_interaction(), _stt(), roles, log)
    assert "Mei Lin" not in result.transcript
    assert "her daughter" in result.transcript

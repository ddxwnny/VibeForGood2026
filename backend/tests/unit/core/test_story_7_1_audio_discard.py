"""
Tests for Epic 7 — Story 7.1: Raw audio discard after extraction.

AC: Given an interaction older than the raw-audio retention window, when the
retention sweep runs, then no audio exists in any store or backup.
"""

from datetime import datetime, timedelta, timezone

import pytest
from uuid_extensions import uuid7

from recollect.adapters.fake_raw_audio import FakeRawAudio
from recollect.app.retention_sweep import RAW_AUDIO_RETENTION, run_retention_sweep
from recollect.core.ports.clock_port import ClockPort


def _utc(ts: str) -> datetime:
    return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)


NOW = _utc("2026-09-09T12:00:00")


class FakeClock(ClockPort):
    def __init__(self, now: datetime) -> None:
        self._now = now

    def utc_now(self) -> datetime:
        return self._now


@pytest.fixture
def raw_audio() -> FakeRawAudio:
    return FakeRawAudio()


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock(NOW)


@pytest.mark.asyncio
async def test_audio_older_than_window_discarded(
    raw_audio: FakeRawAudio, clock: FakeClock
) -> None:
    senior_id = uuid7()
    interaction_id = uuid7()
    await raw_audio.store_raw_audio(
        senior_id, interaction_id, b"old-audio", NOW - RAW_AUDIO_RETENTION - timedelta(seconds=1)
    )

    result = await run_retention_sweep(raw_audio, clock)

    assert result.discarded == 1
    assert await raw_audio.list_raw_audio(senior_id) == []
    assert interaction_id not in raw_audio._audio


@pytest.mark.asyncio
async def test_audio_within_window_retained(
    raw_audio: FakeRawAudio, clock: FakeClock
) -> None:
    senior_id = uuid7()
    interaction_id = uuid7()
    await raw_audio.store_raw_audio(
        senior_id, interaction_id, b"recent-audio", NOW - timedelta(minutes=5)
    )

    result = await run_retention_sweep(raw_audio, clock)

    assert result.discarded == 0
    remaining = await raw_audio.list_raw_audio(senior_id)
    assert len(remaining) == 1
    assert interaction_id in raw_audio._audio


@pytest.mark.asyncio
async def test_no_audio_remains_in_any_store_after_sweep(
    raw_audio: FakeRawAudio, clock: FakeClock
) -> None:
    """AC: after the sweep, no audio exists in any store or backup."""
    senior_id = uuid7()

    stale = [uuid7() for _ in range(3)]
    for iid in stale:
        await raw_audio.store_raw_audio(
            senior_id, iid, b"x", NOW - RAW_AUDIO_RETENTION - timedelta(minutes=1)
        )

    fresh = uuid7()
    await raw_audio.store_raw_audio(
        senior_id, fresh, b"y", NOW - timedelta(minutes=1)
    )

    await run_retention_sweep(raw_audio, clock)

    # Every stale segment's bytes and metadata are gone; only fresh remains.
    remaining = await raw_audio.list_raw_audio(senior_id)
    assert [r.interaction_id for r in remaining] == [fresh]
    for iid in stale:
        assert iid not in raw_audio._audio

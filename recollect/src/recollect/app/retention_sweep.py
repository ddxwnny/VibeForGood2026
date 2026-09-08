"""
RetentionSweep use case (Story 7.1).

Runs periodically (edge/jobs/). Discards every raw audio segment older than the
extraction-to-discard window, guaranteeing that no raw audio lingers in any
store or backup past the shortest interval the pipeline supports.

AD-2: audio is never durable. The sweep is the backstop that enforces the
      guarantee even if a turn's per-turn discard was missed.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from recollect.core.ports.clock_port import ClockPort
from recollect.core.ports.raw_audio_port import RawAudioPort

RAW_AUDIO_RETENTION = timedelta(minutes=15)


@dataclass(frozen=True)
class RetentionSweepResult:
    discarded: int
    cutoff: datetime


async def run_retention_sweep(
    raw_audio: RawAudioPort,
    clock: ClockPort,
) -> RetentionSweepResult:
    """
    Discards all raw audio recorded before ``now - RAW_AUDIO_RETENTION``.
    Returns the number of segments discarded and the cutoff used.
    """
    now = clock.utc_now()
    cutoff = now - RAW_AUDIO_RETENTION
    discarded = await raw_audio.discard_before(cutoff)
    return RetentionSweepResult(discarded=discarded, cutoff=cutoff)

"""
Demo data seeder for local development and demonstration.
Ensures all demo seniors exist with active enrolments and sample everyday tasks (FR-4..7).
Strictly complies with PRD:
  - All 4 consent artefacts present (FR-21, FR-22).
  - Everyday tasks: medication, appointment, mail, routine (FR-4..7).
  - No judgement, no scores, no risk levels (FR-13).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID
from uuid_extensions import uuid7

from recollect.app.append_observation import append_observation
from recollect.app.enrol_senior import EnrolmentRequest, enrol_senior
from recollect.core.entities import Observation, Provenance, Senior, SignalType, TaskOutcome
from recollect.edge.api.state import AppState

DEMO_ARUN_ID = UUID("018d0000-0000-7000-8000-000000000001")
DEMO_LILY_ID = UUID("018d0000-0000-7000-8000-000000000002")


async def seed_demo_seniors_if_empty(store: AppState) -> None:
    """Seeds demo seniors and ensures all seniors have observations."""
    now = datetime.now(timezone.utc)
    visit_at = now - timedelta(days=14)

    # 1. Enrol Arun if not enrolled
    if await store.log.get_senior(DEMO_ARUN_ID) is None:
        arun = Senior(
            id=DEMO_ARUN_ID,
            display_name="Arun",
            preferred_language="en-SG",
            created_at=visit_at,
        )
        await enrol_senior(
            EnrolmentRequest(
                senior=arun,
                visit_at=visit_at,
                recipient_co_signature=True,
                research_consent=True,
                processor_disclosure_acknowledged=True,
                ulysses_audio_bytes=b"RIFF....WAVEfmt....data....Ulysses voice instruction for Arun",
            ),
            log=store.log,
            audio_store=store.audio_store,
        )
        await store.key_store.create_key(arun.id)

    # Seed Arun tasks if needed
    arun_obs = await store.log.get_window(DEMO_ARUN_ID, from_utc=now - timedelta(days=30), to_utc=now)
    if len(arun_obs) < 3:
        arun_tasks = [
            (SignalType.MEDICATION, TaskOutcome.INCOMPLETE, "Good morning Aunty. I haven't taken my blood pressure pills today... I forgot where I put the box.", now - timedelta(hours=2)),
            (SignalType.DATE_TIME, TaskOutcome.INCOMPLETE, "Aunty, what day is today? Is it Wednesday or Thursday?", now - timedelta(days=1, hours=4)),
            (SignalType.MEDICATION, TaskOutcome.COMPLETED, "Morning blood pressure medication taken with warm water", now - timedelta(days=2, hours=3)),
            (SignalType.APPOINTMENT, TaskOutcome.COMPLETED, "Confirmed Thursday dental check-up with receptionist", now - timedelta(days=3, hours=4)),
            (SignalType.MAIL, TaskOutcome.COMPLETED, "Read official utility bill letter and noted due date", now - timedelta(days=4, hours=5)),
            (SignalType.ROUTINE, TaskOutcome.COMPLETED, "Watered the balcony plants and took morning walk in garden", now - timedelta(days=5, hours=2)),
        ]
        for sig, outcome, content, dt in arun_tasks:
            obs = Observation(
                id=uuid7(),
                senior_id=DEMO_ARUN_ID,
                provenance=Provenance(interaction_id=uuid7(), occurred_at=dt, signal_type=sig),
                outcome=outcome,
                content=content,
            )
            await append_observation(obs, log=store.log)

    # 2. Enrol Lily if not enrolled
    if await store.log.get_senior(DEMO_LILY_ID) is None:
        lily = Senior(
            id=DEMO_LILY_ID,
            display_name="Lily",
            preferred_language="en-SG",
            created_at=visit_at,
        )
        await enrol_senior(
            EnrolmentRequest(
                senior=lily,
                visit_at=visit_at,
                recipient_co_signature=True,
                research_consent=True,
                processor_disclosure_acknowledged=True,
                ulysses_audio_bytes=b"RIFF....WAVEfmt....data....Ulysses voice instruction for Lily",
            ),
            log=store.log,
            audio_store=store.audio_store,
        )
        await store.key_store.create_key(lily.id)

    # Seed Lily tasks if needed
    lily_obs = await store.log.get_window(DEMO_LILY_ID, from_utc=now - timedelta(days=30), to_utc=now)
    if len(lily_obs) < 3:
        lily_tasks = [
            (SignalType.MEDICATION, TaskOutcome.COMPLETED, "Evening calcium tablet taken with dinner", now - timedelta(days=1, hours=1)),
            (SignalType.ROUTINE, TaskOutcome.COMPLETED, "Watered purple orchids on the balcony and completed morning stretches", now - timedelta(days=2, hours=6)),
            (SignalType.MAIL, TaskOutcome.COMPLETED, "Reviewed community centre newsletter with grandchild photos", now - timedelta(days=4, hours=3)),
            (SignalType.APPOINTMENT, TaskOutcome.COMPLETED, "Scheduled follow-up physiotherapy session for next Tuesday", now - timedelta(days=5, hours=2)),
        ]
        for sig, outcome, content, dt in lily_tasks:
            obs = Observation(
                id=uuid7(),
                senior_id=DEMO_LILY_ID,
                provenance=Provenance(interaction_id=uuid7(), occurred_at=dt, signal_type=sig),
                outcome=outcome,
                content=content,
            )
            await append_observation(obs, log=store.log)

    # 3. Seed tasks for all other enrolled seniors
    senior_ids = await store.log.list_senior_ids()
    for s_id in senior_ids:
        if s_id in (DEMO_ARUN_ID, DEMO_LILY_ID):
            continue
        s_obs = await store.log.get_window(s_id, from_utc=now - timedelta(days=30), to_utc=now)
        if len(s_obs) < 2:
            senior_obj = await store.log.get_senior(s_id)
            name = senior_obj.display_name if senior_obj else "Senior"
            generic_tasks = [
                (SignalType.MEDICATION, TaskOutcome.COMPLETED, f"Morning medication confirmed taken by {name}", now - timedelta(days=1, hours=2)),
                (SignalType.ROUTINE, TaskOutcome.COMPLETED, f"{name} had breakfast and completed morning walk", now - timedelta(days=2, hours=3)),
                (SignalType.APPOINTMENT, TaskOutcome.COMPLETED, f"Polyclinic follow-up appointment confirmed for {name}", now - timedelta(days=3, hours=5)),
            ]
            for sig, outcome, content, dt in generic_tasks:
                obs = Observation(
                    id=uuid7(),
                    senior_id=s_id,
                    provenance=Provenance(interaction_id=uuid7(), occurred_at=dt, signal_type=sig),
                    outcome=outcome,
                    content=content,
                )
                await append_observation(obs, log=store.log)


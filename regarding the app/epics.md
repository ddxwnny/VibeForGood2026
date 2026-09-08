---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - regarding the app/prds/prd-recollect-2026-09-08/prd.md
  - regarding the app/architecture/architecture-recollect-2026-09-08/ARCHITECTURE-SPINE.md
---

# Recollect - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for Recollect, decomposing the requirements from the PRD and the Architecture Spine into implementable stories. Recollect is a voice companion deployed through Singapore community care to seniors living alone: it does real everyday work (medications, appointments, mail, routines) and records a dated, judgement-free functional series. Stack: Python 3.13 / FastAPI / SQLAlchemy / PostgreSQL (backend + device agent), Next.js for the family and care-worker surfaces.

## Requirements Inventory

### Functional Requirements

- **FR-1** — The senior converses with the device with no login, password, account, or app-opening step.
- **FR-2** — The device captures and analyses only speech addressed to it; all other audio is excluded.
- **FR-3** — Co-present third-party speech in an addressed turn is discarded on-device; named third parties are redacted to role.
- **FR-4** — The senior handles medication through the device; each completion recorded with date and outcome.
- **FR-5** — The senior handles appointments through the device; recorded with date and outcome.
- **FR-6** — The senior handles official mail and letters through the device; recorded with date and outcome.
- **FR-7** — The senior handles daily routines through the device; recorded with date and outcome.
- **FR-8** — Instrument items are administered as ordinary conversation, never announced as a test.
- **FR-9** — Item rotation and spacing are enforced; no re-administration inside a refractory window.
- **FR-10** — Instrument turns stay a minority of interaction; never co-administered with a pressured task.
- **FR-11** — The senior is never scored; a declined item is recorded declined and never re-pressed.
- **FR-12** — A dated functional series is maintained per senior: task completions, instrument responses, mood/sleep/appetite mentions.
- **FR-13** — The record makes no judgement: no score, level, ranking, or classification anywhere.
- **FR-14** — Every observation carries provenance (interaction, date, signal type, item variant); unprovenanced rejected at write.
- **FR-15** — The named recipient receives a weekly account plus one conversation opener, with at least one dated detail.
- **FR-16** — The weekly window contains no verdict, level, score, clinical vocabulary, or "Stable".
- **FR-17** — During the baseline period the window carries an honest note on what the system is learning.
- **FR-18** — The senior hears, weekly and in her language, the same account the family receives.
- **FR-19** — Suppressing the senior delivery while sending the family window is unreachable.
- **FR-20** — The disclosure is spoken only on the senior's explicit request, about her life, never third-person.
- **FR-21** — The care worker captures four consent artefacts in one visit (Ulysses instruction, co-signature, research consent, processor disclosure acknowledged).
- **FR-22** — An enrolment missing any of the four artefacts cannot be active; the write path rejects observations without it.
- **FR-23** — The Ulysses instruction is recorded in her own voice, not asserted on her behalf.
- **FR-24** — A powered-off device reports "unreachable" within 24 hours; affected days excluded from the series.
- **FR-25** — Unrecognised addressed turns are recorded as `Gap(reason=unrecognised)`, never silence or a failed task.
- **FR-26** — Raw audio is discarded once features are extracted; no audio persists in any store or backup.
- **FR-27** — Every stored item has a defined retention, access boundary, and end-of-life path (withdrawal and death).
- **FR-28** — The care worker sees their enrolled seniors, each one's liveness and consent status, and the weekly content.
- **FR-29** — The roster renders in a fixed order; no concern level, score, badge, sort, or highlight derived from the series.
- **FR-30** — The device personalises conversation (name, preferences, routine, family by role, never by unconsented name).
- **FR-31** — The device converses in a natural, human-like register; never reads as a scripted test.
- **FR-32** — The device remembers and follows up, recalling a specific prior fact, never a trend or comparison.
- **FR-33** — The device is summoned, not summoning: no proactive outreach beyond task/appointment reminders.
- **FR-34** — The device never presents itself as a companion, friend, or family.
- **FR-35** — The device bounds conversation: no prolonging beyond the task or the senior's lead, no talk-time optimisation.

### NonFunctional Requirements

- **NFR-1** — Addressed-only capture; no ambient or always-on listening.
- **NFR-2** — Raw audio is never persisted anywhere (enrolment consent recording excepted).
- **NFR-3** — No v1 component reads the log comparatively (no aggregate, order, score, threshold).
- **NFR-4** — Every human-facing string is produced by a single Composer enforcing `communication-rules.md`.
- **NFR-5** — Consent is a write-path precondition, not a UI check.
- **NFR-6** — Instrument rotation and refractory-window spacing are computed in one scheduler.
- **NFR-7** — Every observation carries provenance; unprovenanced writes are rejected.
- **NFR-8** — Timestamps stored UTC ISO-8601; all windowing computed in Asia/Singapore.
- **NFR-9** — Erasure is crypto-shredding of a per-senior key plus tombstone events, never deletion.
- **NFR-10** — Only named processors, Singapore-resident, zero-retention, no-training, enumerable for erasure.
- **NFR-11** — Metrics are cohort-level only; never per named senior, never on a human surface.
- **NFR-12** — Over-reliance bars: AI talk-time must never exceed human contact; engagement is never a target.
- **NFR-13** — Liveness is a separate series from interaction; gaps are excluded, not rendered as inactivity.
- **NFR-14** — Extraction is versioned; model/prompt/STT version recorded on each observation.
- **NFR-15** — The senior never authenticates; care worker and family authenticate on the phone surface.
- **NFR-16** — Structured JSON logging; senior referenced by id only; no transcript or observation content in logs.
- **NFR-17** — Warmth and plain language; no clinical vocabulary; older-adult usability (larger type, unhurried).

### Additional Requirements

- **Stack (decided):** Python 3.13 / FastAPI 0.141.1 / SQLAlchemy 2.0.52 / Alembic / asyncpg / PostgreSQL 18.6; Next.js 16.3.4 for surfaces; Raspberry Pi 5 device agent.
- **Architecture:** ports-and-adapters (hexagonal) — `core/ app/ adapters/ edge/` namespaces; `core` depends on nothing.
- **AD-1:** append-only observation log, single source of truth; corrections are superseding events, never edits.
- **AD-2:** audio never durable; network egress allowlist enforced as a tested property.
- **AD-3:** no-judgement by dependency direction, tested at device, ingest, and read model.
- **AD-8:** one Composer for all human-facing text; given one window, no prior period.
- **AD-9:** one instrument scheduler; bank exhaustion logs omission, never repeats.
- **AD-14:** the device mints the Interaction (UUIDv7 id, occurred-at, idempotency key); ingest is idempotent.
- **AD-13:** per-senior encryption key in a dedicated key-management service; shred covers every store.
- **AD-16:** every processor disclosed, contracted, enumerable; controller is the community care organisation.
- **Conventions:** UUIDv7 ids; past-tense events; banned nouns (Patient/Score/Level/Risk/Flag); typed domain errors; no local-time persistence.
- **Deployment:** Singapore-region hosting; mTLS device→API; device heartbeat sweep, weekly composition, retention sweep jobs.

### UX Design Requirements

None — `bmad-ux` has not been run. The superseded demo's DESIGN.md/EXPERIENCE.md is excluded.

### FR Coverage Map

- FR-1: Epic 4 — Addressed-only voice and everyday tasks
- FR-2: Epic 4 — Addressed-only voice and everyday tasks
- FR-3: Epic 4 — Addressed-only voice and everyday tasks
- FR-4: Epic 4 — Addressed-only voice and everyday tasks
- FR-5: Epic 4 — Addressed-only voice and everyday tasks
- FR-6: Epic 4 — Addressed-only voice and everyday tasks
- FR-7: Epic 4 — Addressed-only voice and everyday tasks
- FR-8: Epic 5 — Voice-native instrument delivery
- FR-9: Epic 5 — Voice-native instrument delivery
- FR-10: Epic 5 — Voice-native instrument delivery
- FR-11: Epic 5 — Voice-native instrument delivery
- FR-12: Epic 1 — The functional record
- FR-13: Epic 1 — The functional record
- FR-14: Epic 1 — The functional record
- FR-15: Epic 6 — Weekly window, continuous disclosure, and personalised conversation
- FR-16: Epic 6 — Weekly window, continuous disclosure, and personalised conversation
- FR-17: Epic 6 — Weekly window, continuous disclosure, and personalised conversation
- FR-18: Epic 6 — Weekly window, continuous disclosure, and personalised conversation
- FR-19: Epic 6 — Weekly window, continuous disclosure, and personalised conversation
- FR-20: Epic 6 — Weekly window, continuous disclosure, and personalised conversation
- FR-21: Epic 2 — Care-worker-led enrolment
- FR-22: Epic 2 — Care-worker-led enrolment
- FR-23: Epic 2 — Care-worker-led enrolment
- FR-24: Epic 3 — Roster and device liveness
- FR-25: Epic 3 — Roster and device liveness
- FR-26: Epic 7 — Data lifecycle and erasure
- FR-27: Epic 7 — Data lifecycle and erasure
- FR-28: Epic 3 — Roster and device liveness
- FR-29: Epic 3 — Roster and device liveness
- FR-30: Epic 6 — Weekly window, continuous disclosure, and personalised conversation
- FR-31: Epic 6 — Weekly window, continuous disclosure, and personalised conversation
- FR-32: Epic 6 — Weekly window, continuous disclosure, and personalised conversation
- FR-33: Epic 6 — Weekly window, continuous disclosure, and personalised conversation
- FR-34: Epic 6 — Weekly window, continuous disclosure, and personalised conversation
- FR-35: Epic 6 — Weekly window, continuous disclosure, and personalised conversation

## Epic List

### Epic 1: The functional record
Track: Foundation (shared). A senior's dated, judgement-free record exists and reads back with provenance — the append-only observation log, core entities, ports, and architecture tests.
**FRs covered:** FR-12, FR-13, FR-14

### Epic 2: Care-worker-led enrolment
Track: A (Bread04). A care worker enrols a senior in one visit, capturing the four consent artefacts; the write path rejects data without an active enrolment.
**FRs covered:** FR-21, FR-22, FR-23

### Epic 3: Roster and device liveness
Track: A (Bread04). A care worker sees their seniors, liveness, and consent status in a fixed-order roster; dead devices and unrecognised turns never read as decline.
**FRs covered:** FR-24, FR-25, FR-28, FR-29

### Epic 4: Addressed-only voice and everyday tasks
Track: B (Yan Herng). The senior talks to the device with no login, only addressed speech is captured, and she handles medication, appointments, mail, and routines.
**FRs covered:** FR-1, FR-2, FR-3, FR-4, FR-5, FR-6, FR-7

### Epic 5: Voice-native instrument delivery
Track: B (Yan Herng). Instrument items are delivered as ordinary conversation, rotated and spaced, never scored, never repeated in a refractory window.
**FRs covered:** FR-8, FR-9, FR-10, FR-11

### Epic 6: Weekly window, continuous disclosure, and personalised conversation
Track: B (Yan Herng). The named recipient gets a judgement-free weekly window; the senior hears the same account; conversation is warm and personal, bounded against over-reliance.
**FRs covered:** FR-15, FR-16, FR-17, FR-18, FR-19, FR-20, FR-30, FR-31, FR-32, FR-33, FR-34, FR-35

### Epic 7: Data lifecycle and erasure
Track: A (Bread04). Raw audio is discarded after extraction; withdrawal and death execute crypto-shred erasure, verifiable by inspection.
**FRs covered:** FR-26, FR-27

## Epic 1: The functional record

**Goal:** A senior's dated, judgement-free record exists and reads back with provenance — the append-only observation log, core entities, ports, and architecture tests. *(Track: Foundation — shared.)*

*First dev action: scaffold the FastAPI + PostgreSQL project (Python 3.13, Alembic migrations, `core/ app/ adapters/ edge/` source tree) per the Architecture Spine's Stack and Structural Seed before Story 1.1.*

### Story 1.1: Domain model and append-only observation log

As a system,
I want the core entities (Senior, Observation, Interaction, Gap, Enrolment, Grant, ConsentArtifact) persisted to an append-only observation log,
So that every fact derived from a senior is an immutable, dated, provenance-carrying event that can never be rewritten.

**Acceptance Criteria:**
**Given** an observation write with provenance (interaction id, date, signal type, item variant),
**When** it is received,
**Then** it is stored as an immutable event with a UUIDv7 id and an occurred-at timestamp.
**And** a correction arrives as a new superseding event, never an edit or delete.
**And** an observation without provenance is rejected at write.

### Story 1.2: Windowed read model with no judgement primitives

As a reader surface,
I want a per-senior windowed read model whose API exposes no comparison, ranking, aggregate, or threshold primitive,
So that no v1 component can read the log in a way that compares across entries.

**Acceptance Criteria:**
**Given** a senior and a date range,
**When** a reader requests the series,
**Then** it returns dated, quotable entries with no score, level, ranking, or classification.
**And** a dependency-direction test fails if any surface reaches a comparison primitive.

### Story 1.3: Domain ports and dependency direction

As a developer,
I want the ports (LLM, STT, TTS, clock, log) defined in core/ports/ with adapters depending on core,
So that core depends on nothing and adapters are swappable without touching domain rules.

**Acceptance Criteria:**
**Given** the codebase,
**When** the dependency direction is tested,
**Then** adapters depend on core and core depends on nothing.
**And** a fake adapter can satisfy each port for tests.

## Epic 2: Care-worker-led enrolment

**Goal:** A care worker enrols a senior in one visit, capturing the four consent artefacts; the write path rejects data without an active enrolment. *(Track A — Bread04.)*

### Story 2.1: Enrolment with a write-path consent gate

As a system,
I want enrolment to require all four consent artefacts before any observation is accepted,
So that partial enrolments can never collect data and no caller can bypass the check.

**Acceptance Criteria:**
**Given** a senior with a partial enrolment (fewer than four artefacts),
**When** an observation write is attempted,
**Then** it is rejected at the write path, not in any caller.
**And** an enrolment missing any artefact cannot be marked active.

### Story 2.2: Capturing the four consent artefacts in one visit

As a care worker,
I want to capture the four consent artefacts (own-voice Ulysses instruction, named recipient's co-signature, research consent, processor disclosure acknowledged) in a single visit,
So that enrolment completes without a return trip and every artefact is timestamped to the visit.

**Acceptance Criteria:**
**Given** a care worker on the phone surface with a senior present,
**When** enrolment runs,
**Then** all four artefacts are captured and timestamped to the visit.
**And** an enrolment missing any artefact cannot be marked active.

### Story 2.3: Own-voice Ulysses instruction

As a care worker,
I want the senior's Ulysses instruction recorded in her own voice, not asserted on her behalf,
So that the consent is defensible as her own statement.

**Acceptance Criteria:**
**Given** enrolment,
**When** the instruction is captured,
**Then** it is stored as audio.
**And** an enrolment whose instruction was not voiced by the senior cannot be marked active.

## Epic 3: Roster and device liveness

**Goal:** A care worker sees their seniors, liveness, and consent status in a fixed-order roster; dead devices and unrecognised turns never read as decline. *(Track A — Bread04.)*

### Story 3.1: Liveness heartbeat and unreachable detection

As a care worker,
I want a device that has gone dark reported unreachable within 24 hours,
So that I can distinguish a dead device from a senior who has stopped talking.

**Acceptance Criteria:**
**Given** a powered-off device,
**When** the heartbeat sweep runs,
**Then** the roster reports "unreachable" within 24 hours.
**And** the affected days are excluded from the functional series, not recorded as reduced interaction.

### Story 3.2: Unrecognised turns recorded as gaps

As a system,
I want an addressed turn that STT cannot resolve recorded as Gap(reason=unrecognised),
So that recognition failure never reads as silence or a failed task.

**Acceptance Criteria:**
**Given** an addressed turn STT cannot resolve,
**When** ingest processes it,
**Then** a Gap(reason=unrecognised) is recorded and no failed-task entry is created.
**And** sustained unrecognised turns surface as an operational alert to the care worker.

### Story 3.3: Roster fixed-order view with no derived ordering

As a care worker,
I want to see my enrolled seniors, their liveness, and consent status in a fixed order,
So that no concern level, score, badge, sort, or highlight derived from the series appears.

**Acceptance Criteria:**
**Given** a care worker's roster,
**When** it renders,
**Then** the order is identical regardless of any senior's functional-series content.
**And** no element derived from the series appears in the view.

## Epic 4: Addressed-only voice and everyday tasks

**Goal:** The senior talks to the device with no login, only addressed speech is captured, and she handles medication, appointments, mail, and routines. *(Track B — Yan Herng.)*

### Story 4.1: Addressed-only capture with no login

As a senior,
I want to speak to the device and get a response with no login, account, or app,
So that I can use it without anyone teaching me or any setup step.

**Acceptance Criteria:**
**Given** a powered-on device,
**When** I address it,
**Then** it responds with zero prior setup actions.
**And** in a scripted scene (TV, a visitor, a phone call), only addressed turns reach storage and the series.
**And** a third party named or described by me is redacted to role.

### Story 4.2: Medication task

As a senior,
I want to handle my medication through the device,
So that doses and reminders are managed and each completion is recorded with date and outcome.

**Acceptance Criteria:**
**Given** I address the device about my medication,
**When** I confirm a dose,
**Then** a dated Observation of type `medication` with a confirmed outcome is recorded.

### Story 4.3: Appointment task

As a senior,
I want to create, confirm, and be reminded of appointments through the device,
So that I keep my appointments and each one is recorded with date and outcome.

**Acceptance Criteria:**
**Given** I address the device about an appointment,
**When** I create or confirm it,
**Then** a dated Observation of type `appointment` with its outcome is recorded.

### Story 4.4: Official mail and letters

As a senior,
I want to have official mail and letters read and acted on through the device,
So that I handle my official correspondence and each action is recorded.

**Acceptance Criteria:**
**Given** I address the device about mail or a letter,
**When** it is read and acted on,
**Then** a dated Observation of type `mail` with its outcome is recorded.

### Story 4.5: Daily routines

As a senior,
I want to handle my recurring daily routines through the device,
So that my routines are tracked and each completion is recorded.

**Acceptance Criteria:**
**Given** I address the device about a routine,
**When** I complete it,
**Then** a dated Observation of type `routine` with its outcome is recorded.

## Epic 5: Voice-native instrument delivery

**Goal:** Instrument items are delivered as ordinary conversation, rotated and spaced, never scored, never repeated in a refractory window. *(Track B — Yan Herng.)*

### Story 5.1: Instrument delivery as conversation

As a system,
I want structured instrument items embedded in ordinary conversation with no announcement or score read-back,
So that the senior never perceives a test.

**Acceptance Criteria:**
**Given** an instrument item administered in conversation,
**When** three lay readers review full transcripts,
**Then** they cannot identify the instrument turns above chance.
**And** no utterance contains a score, total, or pass/fail statement.

### Story 5.2: Rotation and refractory scheduler

As a system,
I want a single scheduler that draws items from rotating banks and never re-administers inside a refractory window,
So that practice effects cannot inflate responses.

**Acceptance Criteria:**
**Given** 12 weeks of administration,
**When** the scheduler runs,
**Then** no item recurs inside its refractory window.
**And** bank exhaustion returns "no eligible item" and records the omission, never a repeat.

### Story 5.3: Density cap and pressured-moment avoidance

As a system,
I want instrument turns capped as a minority of interaction and never co-administered with a pressured task,
So that instrument content stays unobtrusive.

**Acceptance Criteria:**
**Given** a senior's interactions,
**When** the scheduler selects items,
**Then** instrument turns never exceed the per-week ceiling.
**And** no item is co-administered with a time-pressured or distressed task.

### Story 5.4: No scoring and declined handling

As a senior,
I want a declined or deflected item recorded as declined and never re-pressed,
So that I am never scored and never pressured.

**Acceptance Criteria:**
**Given** I decline an item,
**When** the system records it,
**Then** a `declined` record is produced and zero further prompts occur that interaction.

## Epic 6: Weekly window, continuous disclosure, and personalised conversation

**Goal:** The named recipient gets a judgement-free weekly window; the senior hears the same account; conversation is warm and personal, bounded against over-reliance. *(Track B — Yan Herng.)*

### Story 6.1: Weekly window composition

As a named recipient,
I want a weekly account of the senior's week plus one conversation opener with at least one dated detail and no verdict,
So that I stay connected with something concrete to ask, without interpreting a score.

**Acceptance Criteria:**
**Given** a senior's week,
**When** the weekly job composes the window,
**Then** it passes communication-rules and contains at least one specific dated detail.
**And** it contains no "Stable", clinical term, score, level, or trend.
**And** during the baseline period it carries an honest learning note.

### Story 6.2: Continuous disclosure

As a senior,
I want to hear, weekly and in my language, the same account my family receives,
So that nothing about me is held back.

**Acceptance Criteria:**
**Given** a family window is sent,
**When** the same week's senior delivery is checked,
**Then** a matching senior-facing delivery is logged in the same week.
**And** a test that sends the family window while suppressing the senior delivery fails by construction.
**And** the disclosure is spoken only on my explicit request, never unprompted.

### Story 6.3: Personalised conversation

As a senior,
I want the device to address me by name and reference my preferences, routine, and family by role,
So that the conversation feels personal without the device ever implying it is a companion.

**Acceptance Criteria:**
**Given** a recorded session,
**When** the device speaks,
**Then** it uses my name and at least one personalised reference from my own prior statements.
**And** it never uses the name of a person who did not consent.

### Story 6.4: Conversational memory and follow-up

As a senior,
I want the device to remember what I said and follow up naturally,
So that conversation feels continuous without the device ever recalling a trend.

**Acceptance Criteria:**
**Given** I recorded a mail task on Wednesday,
**When** I talk to the device on Saturday,
**Then** it can ask "how did the letter go?" without re-asking what the letter was.
**And** no follow-up references any entry in a comparative or aggregating way.

### Story 6.5: Over-reliance bars

As a system,
I want the conversation bounded so the device is summoned, never presents as a companion, and never prolongs talk,
So that engagement never becomes the relationship.

**Acceptance Criteria:**
**Given** a day with no task events or addressed turns,
**When** the device is idle,
**Then** it produces no unsolicited output.
**And** asked "are you my friend?", it answers truthfully that it is a helper.
**And** after a task completes, it opens no new topic unless I initiate.

## Epic 7: Data lifecycle and erasure

**Goal:** Raw audio is discarded after extraction; withdrawal and death execute crypto-shred erasure, verifiable by inspection. *(Track A — Bread04.)*

### Story 7.1: Raw audio discard after extraction

As a system,
I want raw audio discarded once features are extracted,
So that no audio persists in any store or backup.

**Acceptance Criteria:**
**Given** an interaction older than the raw-audio retention window,
**When** the retention sweep runs,
**Then** no audio exists in any store or backup.

### Story 7.2: Retention and erasure paths

As a senior (or a care worker acting on her behalf),
I want a withdrawal request to execute a defined erasure path,
So that my data is removed or de-identified per what I consented to, verifiable afterwards.

**Acceptance Criteria:**
**Given** a withdrawal request,
**When** it executes,
**Then** the crypto-shred path runs and is verifiable by inspection afterwards.
**And** every stored item has a defined retention, access boundary, and end-of-life path covering withdrawal and death.

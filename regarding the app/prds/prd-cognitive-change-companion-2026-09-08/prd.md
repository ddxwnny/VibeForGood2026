---
title: Cognitive-Change Companion — v1 Observation Layer
status: draft
created: 2026-09-08
updated: 2026-09-08
---

# PRD: Cognitive-Change Companion — v1 Observation Layer

## 0. Document Purpose

This PRD is for the product owner, the engineering team, and the downstream workflows it feeds (`bmad-ux`, `bmad-create-epics-and-stories`). It is the people-facing, decision-ready statement of **what** v1 builds and **why**, structured so a reader can act without re-reading the source contract. It builds on — and does not duplicate — two prior artifacts that remain authoritative: the canonical **SPEC** (`regarding the app/specs/spec-cognitive-change-companion/SPEC.md` + its four companions) holds the capabilities, constraints, and success criteria; the **Architecture Spine** (`regarding the app/architecture/architecture-cognitive-change-companion-2026-09-08/ARCHITECTURE-SPINE.md`, AD-1..AD-16) holds the implementation invariants and stack. Where those two decide a technical mechanism, this PRD states the requirement and points at the spine rather than re-deciding it. The Glossary anchors a controlled vocabulary that all downstream artifacts must use verbatim; features group the requirements; assumptions are tagged inline and indexed in §9.

## 1. Vision

In Singapore, dementia detection is symptom-triggered: someone has to notice and raise a concern. For an older adult living alone, no one is there often enough to notice — and anosognosia means the faculty that would raise the concern is the faculty being lost. In the Alzheimer's Society 2025 survey, 28% of people with suspected symptoms put them down to ageing and 16% judged them not severe enough to act on. The people best placed to act, community care workers, meet these seniors on visits already scheduled but leave with no record of what changed since last time.

The opportunity is not another healthcare service; it is the layer before one. A voice helper that does real everyday work for a senior living alone — medications, appointments, official mail, routines — produces, as a by-product of being used, a **dated functional record** no one is currently keeping. This PRD covers the **v1 observation layer only**: it keeps the record and makes no judgement about it. Its deployment is how the evidence for a later, regulated screening layer gets made.

Cheap blood-based biomarkers do not make this redundant — they make it necessary. If testing becomes cheap, the remaining bottleneck is knowing *who* to test, and the person who most needs it never walks into the clinic. This is the who-to-test signal, not a competing test.

## 2. Target User

### 2.1 Jobs To Be Done

- **Senior (lives alone):** keep the everyday machinery of her life running — medications taken, appointments kept, mail handled — through a voice she can use without a login, an app, or anyone to teach her. Functional job, done weekly.
- **Senior (emotional/social):** stay known. Know that her daughter is being told what she's been doing, that nothing about her is held back from her. Continuous disclosure is the dignity contract.
- **Care worker:** enrol a senior in one ordinary home visit, and later see — without a home visit — that the devices she enrolled are alive, whose consent is in order, and what any senior's week held when a family member asks.
- **Named recipient (family):** stay connected to a parent who lives alone, with something concrete to ask about each week, without having to interpret a verdict or a score.
- **Community care organisation (buyer):** hold a dated, per-senior functional record that a regulator could later accept as the evidence base for a screening layer — bought on the ageing-in-place budget line, not the dementia line.

### 2.2 Non-Users (v1)

- **Seniors with engaged, present family** — consumer/direct-to-family sales would systematically reach only seniors who already have help, inverting the targeting. v1 reaches the no-family population through community care.
- **Clinicians or diagnosticians** — v1 makes no judgement and names no condition; it is not a clinical tool for them.
- **The screening layer's end users** — flag recipients, triage desks, referral paths. That is v2, a regulated component, out of scope here.

### 2.3 Key User Journeys

- **UJ-1. Mdm Lim handles her morning medication through the device.**
  - **Persona + context:** Mdm Lim, 78, lives alone in a Housing Board flat; no engaged family nearby; a care worker installed the device and enrolled her last month.
  - **Entry state:** she is at home; the device is always on; no login, no app.
  - **Path:** she addresses the device by name and says she's taking her pills. The device confirms the dose against her routine and records the completion. A TV plays in the background throughout; a neighbour's voice in the room is ignored.
  - **Climax:** the device tells her the medication is done and — noticing she also has an appointment tomorrow — asks if she wants a reminder. She says yes.
  - **Resolution:** two dated entries exist: a medication completion and a reminder set. No score, no judgement.
  - **Edge case:** she addresses the device in Hokkien mid-sentence; if the device cannot resolve the turn, it records a `Gap(reason=unrecognised)` — never a failed task — and the day is not read as decline.

- **UJ-2. Siti, a care worker, enrols Mdm Lim in one visit.**
  - **Persona + context:** Siti visits Mdm Lim monthly as part of a scheduled home-visit routine; enrolment piggybacks on a visit already happening.
  - **Entry state:** Siti is on the phone surface, authenticated; Mdm Lim is present and has capacity.
  - **Path:** Siti reads the enrolment script in Mdm Lim's language. Mdm Lim states, in her own voice, who gets told and whether she is told first. The named recipient (her daughter Rachel) is present and co-signs physically. Siti takes research/validation consent as a separate act. Siti names each processor that will touch Mdm Lim's data; Mdm Lim acknowledges.
  - **Climax:** all four consent artefacts are captured and timestamped to the visit; enrolment is marked active.
  - **Resolution:** Mdm Lim's data is now collectable. The word "dementia" was never said.
  - **Edge case:** the co-signature is missing. Enrolment cannot be marked active; no data is collected; Siti reschedules.

- **UJ-3. Rachel opens the weekly window and calls her mother.**
  - **Persona + context:** Rachel, the named recipient, lives in another estate; she gets a notification each Sunday.
  - **Entry state:** authenticated on the phone surface.
  - **Path:** she opens the window: what her mother did this week — the medication completions, the mail handled — plus one conversation opener. No score, no level, no clinical word.
  - **Climax:** she reads "Mdm Lim finished the letter to the town council on Wednesday" and calls her mother to ask how the letter went.
  - **Resolution:** a genuine, specific conversation happens; Rachel keeps opening the window each week because it is content, not a warning light.
  - **Edge case:** during the baseline period the window carries an honest note that the system is still learning what her week normally looks like.

- **UJ-4. Mdm Lim hears her own weekly disclosure.**
  - **Persona + context:** same week as UJ-3; the account the family saw must reach her too.
  - **Entry state:** she is at home; she asks the device to tell her about her week.
  - **Path:** the device, in her language, briefly recounts what she did — warm, about her life, never a third-person summary of herself.
  - **Climax:** she hears the same content her family heard, delivered as if spoken to her, not about her.
  - **Resolution:** the disclosure is logged in the same week as the family window; nothing about her was held back.
  - **Edge case:** the room holds a visitor; the disclosure is spoken only because she explicitly requested it, never unprompted.

- **UJ-5. Siti sees a device has gone dark.**
  - **Persona + context:** Siti opens her roster to check on her seniors.
  - **Entry state:** authenticated on the phone surface; the roster renders in a fixed order.
  - **Path:** she sees Mdm Lim's device is flagged unreachable. The affected days are excluded from the functional series — shown as a gap, not as reduced activity.
  - **Climax:** Siti schedules a check-in, knowing this is a dead device, not a withdrawn senior.
  - **Resolution:** liveness and interaction are kept distinct; no phantom decline enters the record.
  - **Edge case:** no concern level, badge, sort, or highlight appears anywhere on the roster.

## 3. Glossary

Downstream artifacts and readers must use these terms exactly; FRs, UJs, and SMs use them verbatim.

- **Senior** — the older adult living alone who uses the device; the capture subject. Never "patient."
- **Care worker** — a community care organisation staff member who enrols seniors on a home visit and views the roster.
- **Named recipient** — the person (usually family) the senior designates at enrolment to receive the weekly window. Exists as a Grant against the senior, not as an entity.
- **Community care organisation** — the buyer, the funder's contract partner, and the data controller.
- **Enrolment** — the one-visit act (CAP-7) that makes a senior's data collectable. Not active until all four consent artefacts exist, timestamped to the same visit.
- **Consent artefact** — one of the four required at enrolment: (1) own-voice Ulysses instruction, (2) named recipient's physical co-signature, (3) research/validation consent, (4) processor disclosure acknowledged.
- **Ulysses instruction** — the senior's own-voice statement of who gets told and whether she is told first, taken while clearly able, executed without veto later.
- **Processor disclosure** — the named list of external processors (STT, TTS, LLM) the senior consents to, acknowledged by her at enrolment.
- **Observation** — an immutable, dated, provenance-carrying entry in the functional series: a task completion, an instrument response, or a mood/sleep/appetite mention.
- **Interaction** — the unit of addressed speech the device mints and captures; yields one or more Observations.
- **Functional series** — the per-senior dated series of Observations and Gaps. Synonymous with "functional record."
- **Gap** — an explicit marker of a period without a heartbeat, or of an unrecognised addressed turn. Never rendered as absence of activity.
- **Task** — one of the four everyday job classes: medication, appointment, official mail and letters, routine.
- **Task completion** — the primary metric; a task handled through the device with a date and outcome.
- **Instrument item** — a structured cognitive item from an established battery domain, administered voice-native in conversation, spaced by a refractory window.
- **Item bank** — the set of interchangeable variants per item type.
- **Refractory window** — the minimum interval before an item may be administered again.
- **Weekly window** — the family-facing weekly account: what she did, what she handled, what she mentioned, plus one conversation opener.
- **Weekly disclosure** — the senior-facing voice delivery of the same account, in her language.
- **Baseline period** — the opening ~12 weeks during which the system is "still learning."
- **Named processors** — the external vendors (STT, TTS, LLM) contracted for zero retention and no training use, Singapore-resident, enumerable for erasure.
- **Continuous disclosure** — the rule that she hears weekly what the family sees.
- **Device** — the dedicated always-powered speaker in the home; the senior's only capture surface.
- **Roster** — the care worker's fixed-order view of enrolled seniors, their liveness, and consent status.
- **Liveness** — whether the device is reachable/heartbeating; distinct from interaction.

## 4. Features

Each feature groups the FRs that realise one capability. FRs are numbered globally. Implementation decisions referenced here live in the Architecture Spine (AD-n), not in this document.

### 4.1 Addressed-only voice interaction

**Description:** The senior speaks to the device and it responds, with no login, account, or app to open. The device captures and analyses only speech addressed to it; background audio (TV, a visiting helper, a phone call in the room) is neither stored nor transcribed. This is the first of the two structural guarantees the product sells, and it must be structural, not a convention. Realizes UJ-1, UJ-4. Governed by AD-2, AD-5, AD-14, AD-16.

**Functional Requirements:**

#### FR-1: The senior can converse with the device without any credential step

The senior can address the device and receive a response with no login, password, account, or app-opening step. Realizes UJ-1.

**Consequences (testable):**
- From a powered-on device, an addressed utterance produces a spoken response with zero prior setup actions by the senior.
- No authentication prompt is ever presented on the device surface.

#### FR-2: The device captures only addressed speech

The device captures and analyses only speech addressed to it; all other audio in the room is excluded from storage and from the functional series. Realizes UJ-1.

**Consequences (testable):**
- In a scripted scene (TV audio, a visiting helper, a phone call in the room, then the senior addressing the device), only the addressed turns appear in the stored record and in the functional series.
- No audio from an unaddressed source reaches any store or network destination.

#### FR-3: Co-present speech inside an addressed turn is discarded and third parties are redacted

Within an addressed turn, speech from a non-consenting third party in the room is discarded on-device before egress, and a third party the senior names or describes is redacted to role. Realizes UJ-1.

**Consequences (testable):**
- An addressed turn containing a visitor's voice yields no stored or transcribed third-party speech.
- The record may hold "her daughter," never a named person who did not consent.

**Out of Scope:**
- Always-on or ambient listening of any kind.
- Speaker attribution or speaker verification (biometric) in v1.

### 4.2 Everyday task support

**Description:** The device handles the four task classes — medications, appointments, official mail and letters, and daily routines — such that it is worth keeping switched on for that alone. Task completion carries the primary signal weight because it has no practice effect and IADL decline is already a recognised clinical signal. Realizes UJ-1. Governed by AD-1, AD-10.

**Functional Requirements:**

#### FR-4: The senior can handle medication through the device

The senior can manage doses and reminders through the device, with each completion recorded with its date and outcome. Realizes UJ-1.

**Consequences (testable):**
- A medication completion produces a dated Observation of type `medication` with a confirmed outcome.

#### FR-5: The senior can handle appointments through the device

The senior can create, confirm, and be reminded of appointments through the device, each recorded with date and outcome. Realizes UJ-1.

**Consequences (testable):**
- An appointment interaction produces a dated Observation of type `appointment` with its outcome.

#### FR-6: The senior can handle official mail and letters through the device

The senior can have official mail and letters read and acted on through the device, each recorded with date and outcome. Realizes UJ-1.

**Consequences (testable):**
- A mail-handling interaction produces a dated Observation of type `mail` with its outcome.

#### FR-7: The senior can handle daily routines through the device

The senior can handle recurring daily routines through the device, each recorded with date and outcome. Realizes UJ-1.

**Consequences (testable):**
- A routine interaction produces a dated Observation of type `routine` with its outcome.

**Feature-specific NFRs:**
- Task completion is the primary product metric and must be computable at cohort level only (AD-3 carve-out); never per named senior, never on a human surface.

### 4.3 Voice-native instrument delivery

**Description:** Structured instrument items are administered as part of ordinary conversation rather than as an announced test, drawn from rotating banks on a spaced schedule. Voice is the instrument's native channel — these items were administered aloud long before they were printed. v1 records the response, never a total. Realizes UJ-1. Governed by AD-9, AD-10, AD-12, AD-15.

**Functional Requirements:**

#### FR-8: The system administers instrument items as ordinary conversation

The system delivers structured instrument items embedded in normal conversation, with no announcement, no framing as a check, and no score read back. Realizes UJ-1.

**Consequences (testable):**
- Three lay readers given full transcripts cannot identify which turns were instrument items above chance.

#### FR-9: The system enforces item rotation and spacing

The system draws items from rotating banks and never re-administers an item inside its refractory window. Realizes UJ-1.

**Consequences (testable):**
- Across 12 weeks, no item recurs inside its refractory window.
- Bank exhaustion returns "no eligible item" and the omission is recorded; it never falls back to a repeat.

#### FR-10: The system caps instrument density and avoids pressured moments

The system keeps instrument turns a minority of interaction and never administers an item in the same interaction as a task the senior initiated under time pressure or distress. Realizes UJ-1.

**Consequences (testable):**
- Instrument turns never exceed the configured per-week ceiling.
- No instrument item is co-administered with a time-pressured or distressed task.

#### FR-11: The senior is never scored, and a declined item is not re-pressed

The senior is never told she passed, failed, or scored; a refused or deflected item is recorded as declined and never re-pressed in that interaction. Realizes UJ-1.

**Consequences (testable):**
- No device utterance contains any score, total, or pass/fail statement.
- A declined item produces a `declined` record and zero further prompts that interaction.

**Feature-specific NFRs:**
- Refractory windows are per item type, minimum 90 days for recall items (the most practice-sensitive). [ASSUMPTION: 90-day floor is the instrument-protocol default, not independently validated.]

### 4.4 Longitudinal functional record

**Description:** The system maintains, per senior, a dated series of task completions, instrument responses, and mood/sleep/appetite mentions, each linked to the interaction it came from. It is a record, never a judgement: no entry carries a score, level, ranking, or classification. Realizes UJ-1, UJ-3. Governed by AD-1, AD-3, AD-10, AD-11, AD-14, AD-15.

**Functional Requirements:**

#### FR-12: The system maintains a dated functional series per senior

The system maintains, per senior, a dated series of task completions, instrument responses, and mood/sleep/appetite mentions. Realizes UJ-1, UJ-3.

**Consequences (testable):**
- For any enrolled senior and date range, the system returns the series with every entry traceable to a dated, quotable interaction.

#### FR-13: The record makes no judgement

No entry in the functional series carries a score, level, ranking, or classification. Realizes UJ-1, UJ-3.

**Consequences (testable):**
- No Observation, and no surface rendering of the series, contains a score, level, ranking, classification, concern level, or trend arrow.
- The condition is never named to any user.

#### FR-14: Every observation carries provenance

Each Observation records the interaction it came from, its date, its signal type, and the item-bank variant where one applies. Realizes UJ-3.

**Consequences (testable):**
- An Observation without provenance is rejected at write.

### 4.5 Weekly family window

**Description:** The named recipient receives a weekly account of the senior's week — what she did, what she handled, what she mentioned — plus one concrete thing to ask her about. It is a connection surface with a safety layer, not a warning light with a feed attached. Realizes UJ-3. Governed by AD-3, AD-8, AD-10.

**Functional Requirements:**

#### FR-15: The named recipient receives a weekly account with one conversation opener

The named recipient receives, each week, an account of the senior's week plus one concrete conversation opener, containing at least one specific dated detail. Realizes UJ-3.

**Consequences (testable):**
- Twelve consecutive weekly windows are generated for a senior with no detected change; every one contains at least one specific dated detail.

#### FR-16: The window contains no verdict

The window contains no verdict, level, score, clinical vocabulary, trend, or the word "Stable." Realizes UJ-3.

**Consequences (testable):**
- Every generated window passes the rules in `communication-rules.md`.
- No window text contains "Stable," any clinical term, or any score.

#### FR-17: The window is honest during the baseline period

During the baseline period, the window includes an honest note on what the system is still learning. Realizes UJ-3.

**Consequences (testable):**
- Windows generated within the baseline period contain the learning note.

### 4.6 Continuous disclosure

**Description:** The senior hears, weekly and in her own language, the same account her family receives, so nothing about her is held back from her. Sending the family window while suppressing the senior delivery is not a reachable state. Realizes UJ-4. Governed by AD-8.

**Functional Requirements:**

#### FR-18: The senior hears her weekly disclosure

The senior hears, weekly and in her own language, the same account the family receives. Realizes UJ-4.

**Consequences (testable):**
- Every family window has a matching senior-facing delivery logged in the same week.

#### FR-19: Suppression of the senior delivery is unreachable

Sending the family window while suppressing the senior delivery is not a reachable state. Realizes UJ-4.

**Consequences (testable):**
- A test that attempts to send the family window without the senior delivery fails by construction.

#### FR-20: The disclosure is spoken only on request

The senior-facing disclosure is spoken only on her explicit request, and is delivered about her life, never as a third-person summary. Realizes UJ-4.

**Consequences (testable):**
- No unprompted disclosure is spoken (the room may hold visitors).
- No disclosure reads or is delivered as a summary of her in the third person.

### 4.7 Care-worker-led enrolment

**Description:** A community care worker enrols a senior during an ordinary home visit, capturing in one sitting her Ulysses instruction in her own voice, the named recipient's physical co-signature, separate research/validation consent, and the acknowledged processor disclosure — the four consent artefacts. Realizes UJ-2. Governed by AD-4, AD-7, AD-13, AD-16.

**Functional Requirements:**

#### FR-21: The care worker captures four consent artefacts in one visit

The care worker captures, in a single visit, all four consent artefacts: the own-voice Ulysses instruction, the named recipient's physical co-signature, research/validation consent, and the processor disclosure acknowledged. Realizes UJ-2.

**Consequences (testable):**
- Enrolment completes within a single visit and the record contains all four artefacts timestamped to that visit.

#### FR-22: An enrolment missing any artefact cannot be active

An enrolment missing any of the four artefacts cannot be marked active, and the record's write path rejects observations without an active enrolment. Realizes UJ-2.

**Consequences (testable):**
- A senior with a partial enrolment produces no collected data.
- The consent check is enforced in the write path, not in any caller, with no bypass.

#### FR-23: The Ulysses instruction is recorded in her own voice

The Ulysses instruction — who gets told, and whether she is told first — is recorded in her own voice, not asserted on her behalf. Realizes UJ-2.

**Consequences (testable):**
- The instruction is captured as audio; an enrolment whose instruction was not voiced by the senior cannot be marked active.

### 4.8 Device liveness

**Description:** The system distinguishes a device that has gone dark from a senior who has stopped talking to it. Liveness and interaction are separate series. Realizes UJ-5. Governed by AD-6.

**Functional Requirements:**

#### FR-24: The system reports an unreachable device within 24 hours

With the device powered off, liveness reports "unreachable" to the care worker within 24 hours. Realizes UJ-5.

**Consequences (testable):**
- A powered-off device is reported unreachable within 24 hours.
- The affected days are excluded from the functional series rather than recorded as reduced interaction.

#### FR-25: Unrecognised turns are gaps, never silence or failure

A turn the senior addressed to the device that speech-to-text could not resolve is recorded as `Gap(reason=unrecognised)`, never as silence and never as a failed task. Realizes UJ-5.

**Consequences (testable):**
- An unrecognised addressed turn produces a `Gap(reason=unrecognised)` entry and no failed-task entry.
- Sustained unrecognised turns surface as an operational alert to the care worker, not as an observation about the senior.

### 4.9 Data lifecycle

**Description:** Raw audio is discarded once features are extracted, and every stored item has a defined retention, access boundary, and end-of-life path covering withdrawal and death. Realizes UJ-1, UJ-2. Governed by AD-2, AD-13, AD-16.

**Functional Requirements:**

#### FR-26: Raw audio is discarded after feature extraction

Raw audio is discarded once features are extracted, and no audio exists in any store or backup after the retention window. Realizes UJ-1.

**Consequences (testable):**
- For any interaction older than the raw-audio retention window, no audio exists in any store or backup.

#### FR-27: Every stored item has a defined lifecycle

Every stored item has a defined retention, access boundary, and end-of-life path covering withdrawal and death. Realizes UJ-2.

**Consequences (testable):**
- A withdrawal request executes the crypto-shred path and is verifiable by inspection afterwards.

### 4.10 Care-worker roster

**Description:** A care worker sees the seniors they enrolled, each one's device liveness and consent status, and can reach the weekly content for any of them. The roster renders in a fixed order and carries no concern level, score, badge, sort, or highlight. Realizes UJ-5. Governed by AD-3, AD-7, AD-8, AD-15.

**Functional Requirements:**

#### FR-28: The care worker sees their enrolled seniors, liveness, and consent status

The care worker sees the seniors they enrolled, each one's device liveness and consent status, and can reach the weekly content for any of them. Realizes UJ-5.

**Consequences (testable):**
- A care worker can list their enrolled seniors and open any senior's weekly content.

#### FR-29: The roster renders in a fixed order with no derived ordering

The roster renders in a fixed order that does not vary with any property of the functional series, and no concern level, score, badge, sort, or highlight derived from that series appears anywhere in the view. Realizes UJ-5.

**Consequences (testable):**
- The roster order is identical regardless of the content of any senior's functional series.
- No element derived from the functional series (badge, sort, highlight, colour) appears in the view.

## 5. Non-Goals (Explicit)

v1 is not, and will not be, any of the following:

- **A screening, flagging, or referral system** — no concern levels, urgent lanes, evidence bundles, referral prompts, or ranked caseloads. Sorting is judgement, and judgement is the regulated layer (v2).
- **A diagnostic tool** — no claim about the senior's condition, and the condition is never named to any user.
- **Passive or ambient listening** — no always-on capture; records non-consenting visitors and corrupts the baseline through speaker misattribution.
- **Speech-acoustic analysis** — research-grade, no clinical pathway consumes it, and Singapore's dialect mix and code-switching make the baseline unworkable.
- **Genetics (APOE) or blood/CSF biomarkers** — maximally sensitive, needs counselling, carries family implications she cannot consent away, and says nothing about whether something changed this month.
- **A consumer or direct-to-family product** — systematically reaches only seniors who already have engaged family, inverting the targeting.
- **A companionship product ("AI son")** — gives the real family permission to stay away, manufactures the withdrawal signal being measured, and lands badly against filial piety. Warmth is the texture of delivery, not the job.
- **The phone as the senior's surface** — breaks the no-login constraint; piloting there measures the wrong product.

## 6. MVP Scope

### 6.1 In Scope

- Addressed-only voice interaction (FR-1..3)
- Everyday task support across all four task classes (FR-4..7)
- Voice-native instrument delivery with rotation and spacing (FR-8..11)
- Longitudinal functional record with provenance and no judgement (FR-12..14)
- Weekly family window (FR-15..17)
- Continuous disclosure (FR-18..20)
- Care-worker-led enrolment with four consent artefacts (FR-21..23)
- Device liveness (FR-24..25)
- Data lifecycle with audio discard and crypto-shred erasure (FR-26..27)
- Care-worker roster (FR-28..29)

### 6.2 Out of Scope for MVP

- The screening layer in full (flags, urgent lanes, evidence bundles, referral prompts, concern levels) — deferred to v2, the regulated layer. [NOTE FOR PM: the split-product posture is load-bearing — v1 must not preclude v2, and the pitch must stay staged to match.]
- Cross-person prioritisation across the slow-drift population — unsolved, will be pushed on by funders; out of scope for v1.
- Speaker verification / biometric identification — new biometric data requiring its own consent line; not free.
- Genetics and biomarkers — out of scope entirely.
- Consumer/family-direct distribution.

[NOTE FOR PM: a hackathon deadline is days away, but the demo slice is a sprint-planning call, not a PRD reduction. This PRD stays at full v1 scope; which FRs ship in the demo is decided at `bmad-create-epics-and-stories`, not here.]

## 7. Success Metrics

**Primary**

- **SM-1**: Task completion — each enrolled senior completes all four task classes through the device at least once within a two-week period, each completion recorded with date and outcome. Validates FR-4..7, FR-12.

**Secondary**

- **SM-2**: Weekly window integrity — twelve consecutive weekly windows generated with no detected change, every one passing `communication-rules.md` and containing at least one specific dated detail. Validates FR-15, FR-16.
- **SM-3**: Enrolment completeness — every active enrolment carries all four consent artefacts timestamped to the visit. Validates FR-21, FR-22.
- **SM-4**: Liveness accuracy — every powered-off device reported unreachable within 24 hours, affected days excluded from the functional series. Validates FR-24, FR-25.

**Counter-metrics (do not optimize)**

- **SM-C1**: Real human contact — must not fall. This is a veto: AI talk-time rising while human contact falls is logged as a regression even when task completion rises. Counterbalances SM-1.
- **SM-C2**: Time-talking-to-AI — a diagnostic, never a target. It must never be optimised upward. Counterbalances SM-1.
- **SM-C3**: Engagement / DAU-style growth — not a target. Growth bought in the currency of the product's own validity is a regression.

## 8. Open Questions

1. **Does PDPA s16 override the Ulysses contract?** Singapore's PDPA gives a right to withdraw consent at any time, which a standing instruction taken at enrolment most likely cannot extinguish — directly against the locked "no veto at flag time." Needs Singapore legal advice, and blocks enrolment rather than build.
2. **What HSA medical-device classification will the v2 screening layer fall under, and what PDPA controller/intermediary obligations attach to the community care organisation?**
3. **Which languages and dialects must the voice surface handle** — Mandarin, Hokkien, Cantonese, Malay, Tamil, and code-switching between them — and what happens to a senior whose language is unsupported? No longer only scoping: the leading commercial speech vendor covers ten languages, none of them Singapore's, so this gates vendor feasibility.
4. **Cellular or wifi for the device, and what per-unit cost does that give the funder?** Wifi fails through household changes nobody reports; either way liveness (FR-24) is required.
5. **Do the comparative signal-catalog entries ("repeating a question across days," "increasing reliance") satisfy the functional-record requirement (FR-12) when v1 records only their non-comparative substrate and leaves the comparison to v2?**
6. **Is retention real?** Companion-device deployments for isolated seniors report poor retention. Verify against deployment data rather than assertion.
7. **The enrolment population is already subtly declining by targeting premise, so day one records an already-declined floor as if it were normal.** Does v1 account for this, or is it deferred to v2?
8. **Can the community-care procurement clock be cleared at all?** Right channel, possibly fatal timeline.
9. **How is pitch discipline enforced** given that stating the screening purpose out loud in a funder meeting establishes intended purpose regardless of what v1 ships?
10. **Cross-person prioritisation** across the slow-drift population is unsolved and will be pushed on by funders, even though out of scope for v1.

## 9. Assumptions Index

- **§4.3** — The 90-day refractory floor for recall items is the instrument-protocol default, not independently validated.
- **§2.3 / §4.7** — The senior's surface is a dedicated always-powered voice speaker in the home, procured and installed by the community care organisation.
- **§2.3 / §4.7** — The buyer and operator is a Singapore community care organisation with existing home-visit routines and an ageing-in-place budget line.
- **§2.3 / §4.7** — The senior has capacity at enrolment to give the Ulysses instruction herself; the enrolment path assumes present capacity.
- **§4.5 / §7** — A ~12-week baseline period is long enough to be useful downstream; carried forward from the forge session, not independently validated.
- **§4.1** — Address detection is a purpose-built on-device component; the standard wake-word library (openWakeWord) does only wake-word spotting, not addressed-vs-overheard determination. Choice open.
- **§4.1 / §4.2** — Voice is a three-stage pipeline (STT → LLM → TTS); Anthropic ships no speech or text-to-speech API. STT vendor is undecided pending a real-recordings bake-off; TTS is ElevenLabs.

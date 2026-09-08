---
id: SPEC-cognitive-change-companion
companions:
  - signal-catalog.md
  - instrument-protocol.md
  - consent-and-data-governance.md
  - communication-rules.md
  - ../../architecture/architecture-cognitive-change-companion-2026-09-08/ARCHITECTURE-SPINE.md
sources:
  - ../../forge/cognitive-change-companion/forged-idea.md
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. Source documents listed in frontmatter are for traceability — consult them only if you need narrative rationale or prose color this contract intentionally omits.

# Cognitive-Change Companion — v1 Observation Layer

## Why

A pain, and an opportunity sitting in front of it. In Singapore, dementia detection is symptom-triggered: someone has to notice and raise a concern. For an older adult living alone, no one is there often enough to notice, and anosognosia means the faculty that would raise the concern is the faculty being lost — in the Alzheimer's Society 2025 survey, 28% of people with suspected symptoms put them down to ageing and 16% judged them not severe enough to act on. The people best placed to act, community care workers, meet these seniors on visits already scheduled but leave with no record of what changed since last time. The opportunity is not another healthcare service; it is the layer before one. A voice helper that does real everyday work for a senior living alone produces, as a by-product of being used, a dated functional record no one is currently keeping. This spec covers the **v1 observation layer** only: it keeps the record and makes no judgement about it. Its deployment is how the evidence for a later, regulated screening layer gets made. Cheap blood-based biomarkers do not make this redundant — they make it necessary. If testing becomes cheap, the remaining bottleneck is knowing *who* to test, and the person who most needs it never walks into the clinic. This is the who-to-test signal, not a competing test.

## Capabilities

- **CAP-1 — Addressed-only voice interaction**
  - **intent:** The senior speaks to the device and it responds, with no login or app to open; it captures and analyses only speech addressed to it.
  - **success:** With a scripted household scene (TV audio, a visiting helper, a phone call in the room, then the senior addressing the device), only the addressed turns appear in the stored record; all other audio is absent from storage and from the functional series.

- **CAP-2 — Everyday task support**
  - **intent:** The senior can use the device to handle medications, appointments, official mail and letters, and daily routines, such that it is worth keeping switched on for that alone.
  - **success:** An enrolled senior completes each of the four task classes at least once through the device across a two-week period, and each completion is recorded with its date and outcome.

- **CAP-3 — Voice-native instrument delivery**
  - **intent:** Structured cognitive instrument items are administered as part of ordinary conversation rather than as an announced test, drawn from rotating banks on a spaced schedule.
  - **success:** Across 12 weeks of administration no item recurs inside its refractory window (see `instrument-protocol.md`), and three lay readers given full transcripts cannot identify which turns were instrument items above chance.

- **CAP-4 — Longitudinal functional record**
  - **intent:** The system maintains, per senior, a dated series of task completions, instrument responses, and mentions of mood, sleep and appetite, each linked to the interaction it came from.
  - **success:** For any enrolled senior and date range, the system returns the series with every entry traceable to a dated, quotable interaction, and no entry carries a score, level, ranking, or classification.

- **CAP-5 — Weekly family window**
  - **intent:** The named recipient receives a weekly account of the senior's week — what she did, what she handled, what she mentioned — plus one concrete thing to ask her about.
  - **success:** Twelve consecutive weekly windows are generated for a senior with no detected change; every one passes the rules in `communication-rules.md`, contains at least one specific dated detail, and contains no verdict, level, or clinical vocabulary.

- **CAP-6 — Continuous disclosure to the senior**
  - **intent:** The senior hears, weekly and in her own language, the same account her family receives, so nothing about her is held back from her.
  - **success:** Every family window has a matching senior-facing delivery logged in the same week; sending the family window while suppressing the senior delivery is not a reachable state.

- **CAP-7 — Care-worker-led enrolment**
  - **intent:** A community care worker enrols a senior during an ordinary home visit, capturing in one sitting her Ulysses instruction in her own voice, the named recipient's physical co-signature, separate research/validation consent, and her acknowledgement of the named processors that will touch her data.
  - **success:** Enrolment completes within a single visit and the record contains all four artefacts timestamped to that visit; an enrolment missing any of the four cannot be marked active.

- **CAP-8 — Device liveness**
  - **intent:** The system distinguishes a device that has gone dark from a senior who has stopped talking to it.
  - **success:** With the device powered off, liveness reports "unreachable" to the care worker within 24 hours, and the affected days are excluded from the functional series rather than recorded as reduced interaction.

- **CAP-9 — Data lifecycle**
  - **intent:** Raw audio is discarded once features are extracted, and every stored item has a defined retention, access boundary, and end-of-life path covering withdrawal and death.
  - **success:** For any interaction older than the raw-audio retention window, no audio exists in any store or backup; a withdrawal request executes the path in `consent-and-data-governance.md` and is verifiable by inspection afterwards.

- **CAP-10 — Care-worker roster**
  - **intent:** A care worker sees the seniors they enrolled, each one's device liveness and consent status, and can reach the weekly content for any of them.
  - **success:** The roster renders in a fixed order that does not vary with any property of the functional series, and no concern level, score, badge, sort, or highlight derived from that series appears anywhere in the view.

## Constraints

- Capture is addressed-only. No ambient or always-on listening, and no third party is ever recorded.
- The senior's capture surface is a single dedicated speaker in the home; family and care worker use a phone. She never has a second capture surface — split capture manufactures phantom decline when she merely changes rooms.
- No login, password, account, or app-opening step stands between the senior and the device.
- v1 makes no judgement: no concern levels, sorting, ranking, highlighting, thresholds, or referral prompts, and the condition is never named to any user.
- The word "Stable" is never used. State what the system did, not what is true of her.
- Anything not fit for the senior to hear about herself is not fit to send to anyone.
- Instrument items rotate across banks and are spaced; items are never re-administered inside their refractory window. Practice effects produce false reassurance, which is the most dangerous available failure direction.
- Primary metric is task completion. Real human contact is a counter-metric with veto: AI talk-time rising while human contact falls is logged as a regression even when task completion rises. Time-talking-to-AI is a diagnostic, never a target.
- Research and validation consent is taken at enrolment, in the same sitting as the Ulysses contract. It cannot be retrofitted across a senior cohort later.
- The senior pays nothing; funding is institutional, through the community care organisation.
- v1 is sold on the ageing-in-place / functional-support budget line, never as dementia detection. Stating a screening purpose in a sales or funder meeting establishes that intended purpose regardless of what the product does.
- Every v1 decision must leave the regulated screening layer buildable on the data v1 collects. v1 must not preclude v2.

## Non-goals

- **Screening, flags, urgent lanes, evidence bundles, referral prompts, concern levels** — the regulated layer, on a longer track. Sorting is judgement.
- **Diagnosis, or any claim about the senior's condition** — v1 keeps a record and asserts nothing about what it means.
- **Passive speech-acoustic analysis** — research-grade, no clinical pathway consumes it, and Singapore's dialect mix and code-switching make the baseline unworkable.
- **Ambient / always-on listening** — records non-consenting visitors and corrupts the baseline through speaker misattribution.
- **Genetics (APOE) and blood or CSF biomarkers** — maximally sensitive, needs counselling, carries family implications she cannot consent away, and says nothing about whether something changed this month.
- **A ranked caseload** — cross-person severity cannot be defended, and a wrong ranking gives everyone below the fold a false clean bill.
- **Consumer or direct-to-family sales** — systematically reaches only seniors who already have engaged family, inverting the targeting.
- **Companionship as the product's role ("AI son")** — gives the real family permission to stay away, manufactures the withdrawal signal being measured, and lands badly against filial piety. Warmth is the texture of delivery, not the job.
- **Engagement as a success metric** — growth bought in the currency of the product's own validity.
- **The phone as the senior's surface** — breaks the no-login constraint, and a pilot run there measures the wrong product.

## Success signal

A community care worker enrols a senior who lives alone and has no engaged family, in one visit, without the word "dementia" being said. Twelve weeks later she is still using the device weekly to handle her medications and her mail, her family opens the weekly window, her recorded contact with real people has not fallen, and the organisation holds a dated per-senior functional record — raw audio already discarded, research consent on file — that a regulator could accept as the evidence base for the screening layer.

## Assumptions

- The senior's surface is a dedicated always-powered voice speaker in the home, procured and installed by the community care organisation.
- The buyer and operator is a Singapore community care organisation with existing home-visit routines and an ageing-in-place budget line.
- The senior has capacity at enrolment to give the Ulysses instruction herself; the enrolment path assumes present capacity.
- A ~12-week baseline is long enough to be useful downstream. Carried forward from the forge session, not independently validated.

## Open Questions

- Cellular or wifi for the device, and what per-unit cost does that give the funder? Wifi fails through household changes nobody reports; either way CAP-8 is required.
- **Does PDPA s16 override the Ulysses contract?** Singapore's PDPA gives a right to withdraw consent at any time, which a standing instruction taken at enrolment most likely cannot extinguish — directly against the locked "no veto at flag time" in `consent-and-data-governance.md`. Needs Singapore legal advice, and blocks enrolment rather than build.
- What HSA medical-device classification will the v2 screening layer fall under, and what PDPA controller and intermediary obligations attach to the community care organisation as controller? The input is silent on both.
- Which languages and dialects must the voice surface handle — Mandarin, Hokkien, Cantonese, Malay, Tamil, and code-switching between them — and what happens to a senior whose language is unsupported? No longer only a scoping question: the leading commercial speech vendor covers ten languages, none of them Singapore's, so this now gates vendor feasibility.
- Do the comparative entries in `signal-catalog.md` ("repeating a question across days", "increasing reliance") satisfy CAP-4 when v1 records only their non-comparative substrate and leaves the comparison itself to v2?
- Is retention real? Companion-device deployments for isolated seniors report poor retention. Genuinely unsettled; verify against deployment data rather than assertion.
- The enrolment population is already subtly declining by targeting premise, so day one records an already-declined floor as if it were normal. Does v1 need to account for that, or is it deferred to v2?
- Can the community-care procurement clock be cleared at all? Right channel, possibly fatal timeline.
- How is pitch discipline enforced, given that stating the screening purpose out loud in a funder meeting establishes intended purpose regardless of what v1 ships?
- Cross-person prioritisation across the slow-drift population is unsolved and will be pushed on by funders, even though it is out of scope for v1.

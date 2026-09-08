---
review-of: ../ARCHITECTURE-SPINE.md
spec: ../../../specs/spec-cognitive-change-companion/SPEC.md
type: rubric-walk
reviewer: architecture reviewer
date: '2026-09-08'
---

# Rubric review — ARCHITECTURE-SPINE.md (cognitive-change-companion)

## Verdict

**Conditional pass — strong spine, one self-contradicting invariant.** This is an unusually good artifact for its altitude: thirteen ADs that are mostly enforceable, a paradigm chosen because it makes the two product promises structural rather than cultural, and a Deferred section that argues each deferral instead of just listing it. It is genuinely better than most spines at rubric items 1, 2 and 6.

But the flagship invariant (AD-2, "raw audio never crosses the device boundary") is contradicted by the spine's own deployment diagram and stack, and the mechanism that is supposed to enforce the second flagship invariant (AD-3, "no judgement") does not reach the one component that will actually break it. Both are fixable at this altitude and both must be fixed before epics are cut, because epics built on the current text will build the wrong thing and pass their own architecture tests while doing it.

Findings below are severity-tiered. Counts: **3 critical, 8 high, 7 medium, 4 low**.

---

## Rubric item 1 — Does it fix the real divergence points for epics/stories?

Mostly yes. The spine correctly identifies and fixes the divergences that actually bite: log semantics (AD-1), consent gating location (AD-4), entity ownership (AD-7), text generation ownership (AD-8), scheduler singularity (AD-9), provenance (AD-10), timezone (AD-11), and the model-as-adapter boundary (AD-12). The Consistency Conventions table does real work — the banned-vocabulary-in-code rule and the "rule violations fail the write, never warn" rule are the kind of thing that actually prevents divergence.

The divergence points it **misses** are listed as findings F-04, F-05, F-06, F-08, F-11, F-14, F-15 below.

## Rubric item 2 — Is every AD's Rule enforceable, and does it prevent its stated divergence?

Ten of thirteen are. AD-1, AD-4, AD-7, AD-9, AD-10, AD-11, AD-12 are crisp and testable. AD-5's "no network call of any kind, including telemetry" is a genuinely excellent formulation — it is falsifiable with a packet capture.

Three fail: **AD-2** contradicts its own stack (F-01), **AD-3** is enforced only at the structured-read boundary and not at the prose-composition boundary where the violation will actually occur (F-02), and **AD-6** states a rule without the threshold that makes it computable (F-05).

## Rubric item 3 — Could anything under Deferred let two units diverge?

Three of the eight deferrals are safe and well-argued (screening layer, connectivity, demo slice). Three are conditionally safe (cloud provider, STT/TTS vendor, language coverage) but carry unstated consequences — F-03, F-09, F-12. Two are **not** safe: observability/alerting (F-05) and device provisioning/fleet update (F-08).

## Rubric item 4 — Is named tech verified-current?

Mostly, with two exceptions. See F-13, F-16, F-19. The Anthropic-has-no-STT/TTS claim is **verified correct** — the Messages API surface offers no speech endpoint, so the three-stage pipeline is a real constraint, correctly identified. Model IDs `claude-sonnet-5` and `claude-opus-5` are **verified valid and current**.

## Rubric item 5 — Does it cover CAP-1..CAP-10?

All ten are named in the Capability → Architecture Map, which is more than most spines manage. But three capabilities have success criteria that no AD actually enforces: **CAP-6**'s unreachable-state guarantee (F-04), **CAP-8**'s 24-hour detection criterion (F-05), and **CAP-9**'s "verifiable by inspection" erasure criterion (F-06, F-07). Coverage-by-mapping is not coverage-by-invariant.

## Rubric item 6 — Is every dimension the altitude owns decided, deferred, or open?

The structural dimensions are well covered — the spine has a paradigm, a namespace map, an entity model, a source tree, and a deployment topology. That is more of the operational envelope than most spines at this altitude bother with, and the deployment diagram deserves credit for existing at all.

Two dimensions are nonetheless **silent** — neither decided, nor deferred, nor listed as an open question:

- **Environments and non-production data** (F-11) — nothing at all, in a system whose production data is the most sensitive category it could be.
- **Secrets and key management** (F-06) — silent, while AD-13 makes per-senior keys the entire erasure mechanism.

And one dimension is silent in a way that matters more than either: the **counter-metric** (F-10), a hard SPEC constraint that appears nowhere in the spine and structurally conflicts with AD-3.

---

# Findings

## CRITICAL

### F-01 — AD-2 is contradicted by the spine's own deployment diagram and stack. `critical`

AD-2's Rule: *"Audio buffers exist only in the Capture context on the device. Only extracted text and structured observations cross the network. No adapter outside `edge/device/` may accept an audio type."*

The Structural Seed deployment diagram says:

```
PI --> STT
PI --> TTS
```

with STT and TTS in the `Vendors["External adapters"]` subgraph. The Stack names **Deepgram Nova-3** — a cloud API. The source tree places the adapter at `adapters/deepgram/`, which is outside `edge/device/`, and it must accept an audio type to function.

So the architecture as drawn sends the senior's raw audio to a third-party cloud vendor. That is precisely "raw audio crossing the device boundary" and "raw audio leaving the home" — the thing the Design Paradigm section calls one of "the two guarantees this product actually sells." The `tests/architecture/` assertion AD-2 mandates would fail against the spine's own stack, or worse, would be written to permit the Deepgram adapter and thereby certify the violation.

This is not a nitpick about diagram fidelity. It is load-bearing three ways:

1. **Consent.** `consent-and-data-governance.md` scopes access to the enrolling care worker, the named recipient, and named research access. A US speech vendor is in none of those categories, and the senior consented to none of it.
2. **CAP-1 and CAP-9.** CAP-1's success criterion is that non-addressed audio is "absent from storage." If a vendor buffers, logs, or trains on submitted audio, the system cannot assert that. CAP-9's "no audio exists in any store or backup" becomes unverifiable, because the stores are someone else's.
3. **Pitch discipline.** The SPEC's hardest sales constraint is that v1 never reads as surveillance. "Your mother's voice is streamed to an American company" is the sentence that ends the procurement conversation.

**Also note the Deferred entry compounds it:** STT/TTS vendor selection is deferred to a bake-off. That means the boundary condition for the system's number-one invariant is currently deferred to a vendor evaluation — a rubric item 3 violation on top of the contradiction.

**Fix — pick one, explicitly, in the spine:**

- **(a) On-device STT.** Restate AD-2 as literally true and put the recogniser on the Pi. This makes MERaLiON's edge deployment (already named in the spine as the standing alternative) the *default* rather than the challenger, and it turns the bake-off criterion from "accuracy" into "accuracy achievable within the Pi 5 thermal and memory envelope." Note the Pi 5 8GB is marginal for this — the stack row should say which model class is assumed, because a Pi that cannot run the recogniser is a hardware decision, not an epic decision.
- **(b) Reword AD-2 honestly** to something like *"raw audio is never persisted anywhere, and leaves the device only to a contractually bound extraction processor under zero-retention terms; it never reaches application stores, log aggregators, backups, or model prompts"* — and then add a new AD fixing the vendor data-processing boundary (see F-03). This is a weaker product promise and the spine should say so out loud, because the marketing copy and the funder pitch both depend on which of (a) and (b) is true.

Option (a) is the one consistent with everything else in the spec. Whichever is chosen, the deployment diagram, the Stack table, the source-tree comment (`device/ # the ONLY place an audio type exists`), and the Deferred entry must all be reconciled — they currently disagree with each other.

---

### F-02 — AD-3 does not reach the Composer, which is where "no judgement" will actually break. `critical`

AD-3's Rule forbids v1 components from reading the log "in a way that compares, aggregates, orders, scores, or thresholds," and enforces it by making the windowed read model expose "no comparison, ranking, or aggregate primitive." As a structural guarantee for dashboards and rosters, this is excellent — it is exactly the right mechanism, and CAP-10's fixed-order roster falls out of it for free.

But the Composer (AD-8) is handed **a whole week of a senior's entries** and asked to write prose. Judgement in prose needs no aggregate primitive. All of these pass every check the spine defines:

- "She handled fewer letters this week than usual."
- "It's been a while since she mentioned her walking group."
- "She asked about the date more often than in previous weeks."

None contains a banned word. None calls a comparison API. Every one is a longitudinal judgement, rendered by an LLM, delivered to family — i.e. an unregulated screening output, which is the exact failure AD-3 exists to prevent and the exact thing that makes v1 a regulated device.

AD-12 states the principle that would catch this — *"a prompt may shape tone; it may never be the only thing standing between the system and a rule violation"* — and then AD-8's enforcement is lexical (`communication-rules.md`'s forbidden list is a vocabulary list), so for AD-3 the prompt **is** the only thing standing there. AD-12 and AD-8 contradict each other on the spine's most important guarantee.

**Fix — the constraint belongs on the Composer's input, not its output.** Candidate rules, any of which is enforceable:

- The Composer's input contract is **a single window's entries with no prior-window context**, and the port's type makes multi-window input unrepresentable. A model that has never seen last week cannot compare to it.
- Add a deterministic post-check for **comparative and frequency constructions** — comparatives, "more/less/fewer/again/still/no longer/used to/as usual/than before," and any temporal-contrast connective — to `communication-rules.md`'s enforcement, alongside the vocabulary list. Lexical, testable, fails the write per the Errors convention.
- State explicitly that the Composer is a **renderer of a fixed slot structure** (per `communication-rules.md`: her week / one opener / the learning note), not a free-form writer, so the surface area for smuggled judgement is bounded by the slots.

Whatever the mechanism, the spine must name it. Right now the flagship guarantee is enforced by prompt text.

---

### F-03 — No AD governs what third-party processors may receive, while the design sends senior content to three of them. `critical`

The deployment diagram routes senior-derived content to **Deepgram** (audio, per F-01), **ElevenLabs** (the text of what the device says to her), and the **Anthropic API** (turn handling and weekly composition — i.e. her observations). `consent-and-data-governance.md` enumerates who may access her data and names exactly three parties, none of which is a vendor. It also mandates *"every access is logged."*

The spine has no rule on this at all. It is not decided, not deferred, and not an open question. Consequences that will diverge between epics if left unstated:

- Whether vendor contracts must carry **zero-retention / no-training / no-human-review** terms.
- Whether **cross-border transfer** is permitted at all, given the spine fixes "Singapore-resident" for its own storage while shipping the same content offshore in the same diagram. The PDPA open question is deferred, but the deferral only covers *hosting region* — it does not cover onward transfer to processors, which is the harder half.
- Whether vendor calls count as "access" for the access-logging obligation.
- Whether de-identification is required before a payload reaches a vendor.

**Fix — add an AD.** Something like: *"Any adapter that transmits senior-derived content outside the system boundary is a registered processor. Registration requires zero-retention and no-training terms, Singapore-permissible transfer, and an entry in the access log. An unregistered egress adapter fails the architecture test."* This makes the vendor bake-off (currently deferred) a decision against a fixed contract rather than a free choice, which is the whole point of deferring it behind a port.

---

## HIGH

### F-04 — CAP-6's unreachable-state guarantee is not enforced by anything. `high`

CAP-6's success criterion: *"sending the family window while suppressing the senior delivery is not a reachable state."* That is an atomicity requirement.

AD-8 covers CAP-6 by requiring that both renderings "derive from the same Composer call." Same-composition is not same-delivery. Concretely: the family window is a push to a phone; the senior's disclosure is a **voice delivery on a device that may be dark** — and AD-6 exists precisely because devices go dark. The realistic failure is: device offline Thursday, family window sends Friday, senior hears nothing. Reachable, and it breaks the consent model's foundation (`consent-and-data-governance.md`: *"there is no reveal because there is no secret"*).

The spine does not say whether the pair is transactional, whether family send blocks on senior delivery **acknowledgement**, or what happens when the device stays dark past the week boundary.

**Fix:** state the ordering and the failure semantics. E.g. *"Weekly delivery is a single unit: the family window is not dispatched until the senior's delivery is acknowledged by the device. An unacknowledged senior delivery holds the family window and appends a `DisclosureDeferred` event; it never drops one side."* Note this interacts with AD-6 — decide whether a Gap week suppresses both deliveries or defers both.

### F-05 — AD-6 has no threshold, and CAP-8's 24-hour criterion has no owner. `high`

AD-6 says heartbeats are a separate stream and gaps are written as explicit `Gap` events. It does not say **heartbeat interval**, **how long a silence must be before it is a Gap**, or **who is notified when**. CAP-8's success criterion is specific: *"liveness reports 'unreachable' to the care worker within 24 hours."*

Two epics will pick different intervals. Worse, `Gap` is not an operational detail — it is a **first-class entity in the observation series** (it appears in the ER diagram) and the read model must exclude gap periods. Two units with different gap thresholds produce non-comparable functional records, which is exactly the "phantom decline" corruption AD-6 was written to prevent. The rule prevents the failure mode in principle and permits it in practice.

Compounding: the Deferred section drops **"observability and alerting stack"** with the justification *"no independent builders diverge on it yet."* That is not true — CAP-8 requires a user-facing alert to a care worker within a stated latency. That is a product requirement wearing an ops costume, and it is deferred.

**Fix:** put the numbers in AD-6 (heartbeat interval, gap threshold, notification latency budget derived from CAP-8's 24h), and split the Deferred entry: defer the *observability vendor*, decide the *liveness alerting path*.

### F-06 — AD-13's crypto-shredding has no key-management decision, which makes the erasure guarantee undecidable. `high`

AD-13 is a genuinely good call — it resolves the append-only-vs-erasure deadlock cleanly, and the spine deserves credit for spotting that deadlock before it was discovered "on the day someone withdraws." But the entire guarantee reduces to one question the spine never asks: **where do the per-senior keys live, and what does destroying one actually mean?**

Undecided and divergence-producing:

- KMS/HSM vs application-managed keys vs envelope encryption.
- Whether the key store is **included in backups** — if it is, restoring any backup resurrects every shredded senior, and AD-13 is decorative. CAP-9 demands erasure be "verifiable by inspection afterwards"; a backup with keys in it fails that inspection.
- Whether **replicas, WAL archives, and PITR windows** hold pre-shred ciphertext (fine) and keys (fatal).
- Who can authorise destruction, and how destruction is evidenced.

The spine also has **no AD on backups or disaster recovery at all** — the word "backups" appears only inside AD-2's *Prevents* clause, never in a Rule.

**Fix:** add key custody and backup semantics to AD-13, explicitly including *"the key store is excluded from all backups and snapshots, or is itself subject to the same destruction"* — and say which. This is the single cheapest high-severity fix in the review.

### F-07 — AD-13's de-identified projection contradicts the withdrawal choice recorded at enrolment. `high`

AD-13: *"De-identified retention, where she consented to it, is a separate projection written at ingest, never a later derivation."*

`consent-and-data-governance.md`: *"her data is removed or de-identified according to what she consented to at enrolment. Which of the two is her choice."*

Write-at-ingest means the projection is created **before** any withdrawal event. So for a senior who chose full removal, either (a) the projection was written anyway and survives the key destruction — she asked to be removed and was not; or (b) the projection is encrypted under the same per-senior key, in which case it dies with the key and the "de-identified retention" path does not work for anyone. Both are wrong; the spine picks neither.

**Fix:** make the ingest-time projection **conditional on the enrolment's recorded withdrawal choice** (removal-choosers get no projection), and state the projection's key domain explicitly. If it is genuinely de-identified it should be outside the per-senior key domain — which then requires the spine to say what "de-identified" means concretely enough to test, because a dated per-person functional series is close to irreducibly re-identifiable.

### F-08 — Deferring device provisioning defers the trust root for AD-2 and AD-5. `high`

Deferred: *"Device provisioning, fleet update, and physical install. Owned by the epic that builds the appliance; nothing at this altitude constrains two units incompatibly."*

That last clause is not correct. The Pi is the **sole enforcement point** for the system's two structural promises: AD-2 (audio never leaves) and AD-5 (address determination before egress). The deployment diagram already assumes `mTLS` — which means device identity, certificate issuance, rotation, and revocation are already architectural facts, just unstated ones. And "fleet update" is not an install detail when the thing being updated is the component enforcing the invariants: an un-updatable Pi running a stale address detector is a silent AD-5 failure across the fleet.

Two units *can* diverge here — one provisioned with a shared cert, one per-device; one with an update channel, one without — and the divergence is invisible until it is a breach.

**Fix:** keep physical install and BOM deferred. Decide, at spine level: device identity is per-unit and attested; certificates are rotatable and revocable; the capture agent is remotely updatable and its version is recorded on the heartbeat (which also gives AD-6's stream a useful second job).

### F-09 — Speaker attribution is unaddressed, and the SPEC names it as a corruption mode. `high`

AD-5 determines whether a turn is *addressed to the device*. It says nothing about **who is speaking**. CAP-1's success scenario explicitly includes "a visiting helper" in the room, and the SPEC's non-goals reject ambient listening partly because it *"corrupts the baseline through speaker misattribution."*

The gap: a visiting helper, a family member, or a care worker who says the wake word and asks the device something produces an `Observation` attributed to the senior. Every one of those is a plausible weekly occurrence — the care worker is *contractually in her home on visits*. Those observations enter the functional series and, per the SPEC's whole thesis, become the evidence base for a screening layer. Misattributed helper turns look like preserved function; misattributed confusion looks like decline.

The spine's constraint list mentions the single-capture-surface rule (good, that is the split-capture failure) but not the multi-speaker-one-surface failure.

**Fix:** decide it. Options: on-device speaker verification against an enrolment voiceprint (note: this is new biometric data and needs a consent line, so it is not free); a non-senior-speaker signal recorded on the observation so a later reader can exclude it; or an explicit accepted-risk statement with the confound recorded. Any of the three is fine; silence is not, because it silently poisons the artifact the product exists to produce.

### F-10 — The human-contact counter-metric is absent from the spine and conflicts with AD-3. `high`

The SPEC constraint is unambiguous and has veto power: *"Real human contact is a counter-metric with veto: AI talk-time rising while human contact falls is logged as a regression even when task completion rises."* `signal-catalog.md` lists it as a capture source. It is one of the SPEC's genuinely distinctive design commitments — the thing that stops the product from manufacturing the withdrawal it measures.

The spine never mentions it. Not in an AD, not in the capability map (it maps to no CAP because it is a Constraint, which is exactly how it fell through), not in Deferred, not as an open question.

And it is not a trivial addition, because **computing it requires exactly what AD-3 forbids**: comparing AI talk-time trend against human-contact trend across entries over time. So the spine must either carve it out of AD-3 or place it outside the v1 read path.

**Fix:** add an AD. The clean resolution is that the counter-metric is a **programme-level evaluation output, not a product surface** — computed offline, never rendered to any of the three user roles, and therefore outside AD-3's "no v1 component may read the log in a way that compares" because it is not a v1 surface component. That carve-out must be *written*, or the first engineer to implement the counter-metric will either violate AD-3 or quietly drop the requirement.

### F-11 — Environments and non-production data are wholly silent. `high`

The spine has no statement about dev/staging/production, and no statement about what data non-production environments may hold. In a system whose production dataset is elderly people's transcribed speech and functional decline records, this is the operational dimension most likely to produce a breach, and it is not even listed as deferred.

It also collides with AD-4, which is otherwise one of the best rules here: *"There is no bypass, test flag included."* Correct and admirable — and it means every epic needs a way to populate an environment with valid enrolments including three consent artefacts. With no guidance, each epic invents one, and the fastest path for at least one of them will be a copy of production.

**Fix:** decide the environment ladder and one rule: *"No non-production environment holds real senior data. Fixtures are synthetic and generated through the real enrolment path, satisfying AD-4 rather than bypassing it."* Cheap, and it removes an entire class of incident.

---

## MEDIUM

### F-12 — Language and locale are deferred, but CAP-6 requires per-senior language and nothing carries it. `medium`

Deferred: *"Language and dialect coverage. Open in the SPEC."* Reasonable as a *coverage* decision. But CAP-6 requires the senior's weekly disclosure to be *"in her own language,"* and `communication-rules.md` repeats it. That means language is a **property of the `Senior` record**, the Composer is language-parameterised, and `communication-rules.md`'s enforcement (banned vocabulary, and F-02's comparative check) must work in every supported language — a lexical rule engine that only works in English is an enforcement gap the moment the first Mandarin senior enrols.

The ER diagram has no locale on `SENIOR`; no AD mentions it.

**Fix:** decide the *plumbing* (locale on `Senior`, set at enrolment; Composer takes it as input; rule enforcement is per-locale and a missing rule set is a boot failure, consistent with the Config convention) while keeping the *coverage list* deferred.

### F-13 — Python 3.13 is not current, in a table headed "verified current 2026-09-08." `medium`

As of this date, Python 3.14.7 is the current stable release (3.14.0 shipped 2025-10-07); 3.15 is at rc and due October 2026. Python 3.13 is a full release line behind. It is still supported, so this is not a correctness problem — it is a **credibility** problem: a table that says "verified current" and is not undermines trust in every other row, including the rows a reader cannot easily check.

Verified as genuinely current: **Next.js 16.3.4** (released 2026-08-31, Active LTS) and the model IDs **`claude-sonnet-5`** / **`claude-opus-5`**. The claim that Anthropic ships no STT/TTS API is also **verified correct** — the three-stage pipeline is a real constraint, not a preference, exactly as the spine says.

**Fix:** either move to 3.14 or relabel the row *"3.13 — deliberate, one line behind current for ecosystem stability."* A stated reason is fine; an unstated staleness under a "verified" header is not.

### F-14 — Offline buffering is undefined, and it puts AD-6 and AD-1 in conflict. `medium`

The SPEC's first open question is wifi vs cellular, and flags that *"wifi fails through household changes nobody reports."* So intermittent connectivity is expected, not exceptional. The spine never says whether the Pi buffers turns when the network is down.

If it buffers: the device is alive, heartbeats do not arrive, AD-6 writes `Gap` events for those days — and then the buffered observations arrive **for days already marked as Gap**. AD-1 permits only supersede-by-new-event, never edits, so the series now carries a Gap and observations for the same day, and the read model is instructed to *exclude* gap periods. Real data silently discarded, on the exact days the spec cares most about.

If it does not buffer: real interactions are lost outright, which is worse.

The spine's deferral of connectivity says *"AD-6 holds either way, which is why the spine can wait."* AD-6 holds; the AD-6 × AD-1 interaction does not.

**Fix:** decide buffering (yes, with a bounded local queue and a stated cap), and add the reconciliation rule — e.g. a `GapClosed` superseding event, and a read-model rule that observations win over an overlapping Gap. Note this also means the Pi holds observation data at rest, which loops back to F-06 (key custody) and F-08 (device provisioning).

### F-15 — Confounds have no representation in the entity model. `medium`

`signal-catalog.md` is explicit: *"An observation of decline is uninterpretable without these. v1 must capture enough to let a later reader rule them in or out"* — acute illness, medication change, poor sleep, bereavement, hearing loss, late-life depression, education and language background.

The spine's ER diagram gives `OBSERVATION }o--|| SIGNAL_TYPE`, and AD-10 requires "its signal type per `signal-catalog.md`." But confounds are not signal types — they are a different axis, and several (education and language background, hearing loss) are properties of the *senior*, not of an observation. If epics build only the signal-type enum, confounds are unrepresentable.

That directly violates the SPEC's hardest cross-cutting constraint: *"v1 must not preclude v2."* A series with no confound axis is a series a screening layer cannot responsibly read.

**Fix:** put confounds in the entity model — a `Context`/`Confound` event type on the series plus a small set of enrolment-time senior attributes — and reference `signal-catalog.md`'s confound list from AD-10 the way the signal list already is.

### F-16 — openWakeWord is stale and is being asked to do more than it does. `medium`

Two separate issues in one Stack row (`openWakeWord — on-device address detection`):

1. **Currency.** Its last tagged release is 0.6.0, February 2024 — roughly two and a half years old as of this review. It is widely used (notably in Home Assistant) and not abandoned, but it does not meet the "verified current 2026-09-08" bar the table claims, and it is the only component enforcing AD-5.
2. **Scope.** openWakeWord is a *wake-word* detector. AD-5 requires *address detection* — distinguishing speech addressed to the device from a TV, a phone call, a conversation between two people in the room, and crucially **follow-up turns in a multi-turn exchange that do not repeat the wake word**. A wake-word model does the first turn only. The spine's own CAP-1 test scene (TV, visiting helper, phone call) is a harder problem than the named library solves.

**Fix:** either constrain the interaction model to wake-word-per-turn (a real UX cost for an elderly user, and it should be stated as a decision), or name the additional mechanism for follow-up-turn addressing and its egress rule under AD-5. Also re-verify the library or name an alternative.

### F-17 — AD-8's fail-the-write semantics have no fallback, which endangers CAP-5's twelve-consecutive-windows criterion. `medium`

The Errors convention is *"Rule violations raise typed domain errors and fail the write. Never a warning, never a log-and-continue."* This is the right default and one of the spine's best lines.

Applied to AD-8, though: a Composer output that trips a `communication-rules.md` check fails. CAP-5's success criterion is **twelve consecutive** weekly windows; CAP-6 requires a matching senior delivery every week. LLM output is nondeterministic — a violation is a *when*, not an *if*. The spine does not say what happens: retry with what budget, fall back to a template, or genuinely skip the week and break the streak.

**Fix:** one line in AD-8 — bounded regeneration, then a deterministic template rendering of the same slot structure, and the fallback is recorded as an event. Never a silent skip, never an unchecked send.

### F-18 — The Composer's role in the live conversational path is unspecified, and the topology contradicts it. `medium`

AD-8: *"Every string a senior, family member, or care worker reads or hears is produced by the Composer."* `communication-rules.md` confirms the scope includes *"every device utterance."*

But the deployment diagram shows `PI --> TTS` with no path from the Composer to the device, and the Composer is placed downstream of the read model (`LOG → READ → COMP → SURF`) — a batch-shaped position. Meanwhile `API --> LLM` exists with no stated role. So it is unclear whether live turns route through the Composer, and if they do, whether the rule-check runs synchronously in a real-time voice loop (a latency question with real elderly-UX consequences).

Two epics — one building live conversation, one building the weekly job — will answer this differently, and the live one will be the one that skips the check.

**Fix:** say whether there is one Composer with two modes (live, batch) or two paths with a shared enforcement library, and draw the live path in the diagram. The enforcement must be identical either way — that is AD-8's entire point.

---

## LOW

### F-19 — Several stack versions are plausible but unverifiable as stated. `low`

FastAPI 0.141.1, SQLAlchemy 2.0.44, Alembic 1.17.1, asyncpg 0.31.0, PostgreSQL 18.3 are all plausible for this date and none contradicts anything known. FastAPI 0.136.1 was current in April 2026 and that project ships frequently, so 0.141.x by September is reasonable. Flagged only because F-13 and F-16 show the "verified current" header is not uniformly reliable. The spine's own framing — *"Seed... The code owns this once it exists"* — is the right posture; the header just overclaims.

### F-20 — No tenancy or organisation boundary. `low`

The SPEC's buyer is "a Singapore community care organisation." The spine has `Senior` and `Grant` but no `Organisation`. AD-7's grant model probably covers single-org v1 adequately, and care-worker scoping falls out of grants. Worth one sentence stating single-tenant-per-deployment (or not), since retrofitting tenancy is expensive and the funder conversation may involve more than one org.

### F-21 — Access logging is required by governance and appears in no AD. `low`

`consent-and-data-governance.md`: *"Every access is logged."* The spine's Logging convention covers *application* logging (structured JSON, id-only) but an access audit trail is a different artifact with different retention and different readers. CAP-9 maps to AD-2 and AD-13 only. Low severity because it is additive rather than divergence-producing, but it is a stated obligation with no home. See also F-03 — vendor calls are arguably accesses.

### F-22 — Enrolment's same-visit constraint is not in AD-4. `low`

CAP-7 and `consent-and-data-governance.md` both require the three artefacts be *"timestamped to the same visit."* AD-4 requires all three exist but not that they be co-temporal. The distinction matters: the whole defensibility argument for the Ulysses contract is that consent was taken in one sitting while she was clearly able. Trivial to add to AD-4's rule.

---

## What is genuinely good here

Worth recording, because a review that lists only findings misrepresents the artifact:

- **The paradigm justification is exactly right.** *"Written as coding conventions they last until the first person in a hurry. Written as dependency directions they hold."* That sentence is the reason this spine will outperform most.
- **AD-13** anticipates the append-only-vs-erasure deadlock before it becomes a crisis. Most architectures discover this in production.
- **AD-6** correctly identifies phantom decline as a first-class corruption and gives `Gap` entity status rather than treating it as a null.
- **AD-12** draws the model/policy line in the right place, and names the four specific things that must be deterministic.
- **AD-5's** "no network call of any kind, including telemetry" is falsifiable with a packet capture — that is what an enforceable rule looks like.
- **Banning `Patient`, `Score`, `Level`, `Risk`, `Flag` in code**, not just in copy, is the correct instinct: the vocabulary leak into the domain model is how a no-judgement product becomes a judging one.
- **The Deferred section argues each deferral** instead of listing it. Even where the argument fails (F-05, F-08), the argument is *present* and therefore reviewable — which is the point.

## Recommended order of work

1. **F-01** — resolve the audio boundary. Everything about the device epic, the vendor bake-off, and the product promise depends on which way this goes.
2. **F-02** — put AD-3's enforcement on the Composer's input contract.
3. **F-03** — add the processor-boundary AD (partly falls out of F-01).
4. **F-06, F-07** — key custody, backup semantics, and the projection condition. One AD-13 revision covers all three.
5. **F-10, F-04, F-05** — the counter-metric carve-out, delivery atomicity, liveness thresholds.
6. **F-08, F-09, F-11, F-14, F-15** — device trust root, speaker attribution, environments, buffering reconciliation, confound representation.
7. The remainder as editing passes.

Items 1–4 should land before epics are cut. Items 5–6 should land before the epics that touch them are cut.

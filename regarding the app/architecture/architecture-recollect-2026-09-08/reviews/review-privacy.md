---
review: privacy-consent-regulatory
artifact: ../ARCHITECTURE-SPINE.md
sources:
  - ../../../specs/spec-recollect/SPEC.md
  - ../../../specs/spec-recollect/consent-and-data-governance.md
  - ../../../specs/spec-recollect/communication-rules.md
  - ../../../specs/spec-recollect/signal-catalog.md
reviewer: privacy, consent and regulatory-compliance lens
date: '2026-09-08'
status: draft
---

# Privacy, Consent and Regulatory Review — Architecture Spine

## Verdict

The spine is unusually disciplined for a document at this altitude — AD-4, AD-6, AD-10, AD-12 and AD-13 are real architectural enforcement rather than aspiration, and the decision to make the two selling guarantees structural is the right instinct. But the two guarantees it sells are not yet structurally true. AD-2's headline claim is contradicted by the architecture's own deployment diagram; AD-3's wall is enforced at the one place a determined feature will not go through; the consent model's operative terms exist only as unstructured audio and therefore cannot be executed by code; and the document names no PDPA obligation at all, in an architecture that transfers health-adjacent personal data of vulnerable adults across borders to three commercial vendors.

Not a rewrite. A set of missing ADs, one corrected diagram, and one legal question that has to be answered before enrolment, not after.

Severity tiers used: **CRITICAL** (ship-blocking; creates legal exposure or breaks a promise made to the senior), **HIGH** (must be resolved before pilot enrolment), **MEDIUM** (before scale), **LOW** (hygiene / wording).

---

## 1. Does the architecture enforce the consent model, or only describe it?

**Partly enforce, mostly describe.** AD-4 is the strongest rule in the document and does real work. Everything downstream of it is narrative.

### F-01 — AD-4 enforces enrolment *completeness*, not consent *content* — CRITICAL

AD-4 gates the write path on the presence of three artefacts. Presence is all it checks. But the Ulysses contract's operative terms are all *semantic*:

- who gets told (named recipient or recipients);
- whether she is told first, told together, or not told at the moment;
- whether withdrawal means deletion or de-identification (`consent-and-data-governance.md`: "Which of the two is her choice, recorded at enrolment");
- the death path for both the functional series and the consent audio.

None of these exist in the entity model. `CONSENT_ARTEFACT` is undifferentiated. There is no `DisclosureElection`, no `WithdrawalElection`, no `DeathDisposition`. AD-13 says "de-identified retention, **where she consented to it**" — but nothing in the architecture stores whether she did. The system cannot execute her instruction; it can only prove that an instruction was recorded, as audio, somewhere.

That is the whole consent model reduced to a filing requirement. The Ulysses contract's defensibility rests on the system *executing a standing instruction*; an architecture that cannot read the instruction cannot execute it, and a human replaying audio at disclosure time reintroduces exactly the discretion the Ulysses design exists to remove.

**Fix:** a new AD — *the consent artefact is parsed into a structured, machine-readable `ConsentTerms` value object at enrolment, validated in the same sitting against the recording, and the audio is the evidentiary record of the terms, never the runtime source of them.* Enrolment cannot activate unless the structured terms parse and are confirmed. Every disclosure decision reads `ConsentTerms`, never a human.

### F-02 — Ulysses "no veto" is very likely unenforceable under PDPA s16, and the architecture implements the unenforceable version — CRITICAL

`consent-and-data-governance.md` is explicit: "At disclosure time the system executes the standing instruction. There is no veto at that point — that is the whole point of taking it early."

Under the PDPA, an individual may **withdraw consent** to the collection, use or disclosure of personal data at any time on reasonable notice, and an organisation must cease that activity. This right is statutory and is not defeated by a prior contractual undertaking; the Act contemplates that withdrawal may have consequences and requires the organisation to inform her of them, not that she can pre-commit them away. The PDPA contains no advance-consent or Ulysses doctrine — the ACP/LPA analogy in the spec is drawn from mental-capacity law, which is a different statute with a different trigger (loss of capacity, formally assessed) than the one this product operates on (nobody assesses capacity; the device just keeps running).

So the architecture as written will, at disclosure time, execute a disclosure to family against a senior who is at that moment saying no. AD-4 gates *collection* on active enrolment. Nothing gates *disclosure* on live consent status. That is the exact failure that ends a community-care pilot.

This needs counsel, and the answer materially shapes the architecture. Note the fork:

- If she still has capacity, PDPA withdrawal almost certainly wins and the standing instruction must yield.
- If she has lost capacity, the PDPA question is displaced by the Mental Capacity Act and the disclosure basis is different again — and the architecture has no concept of a capacity determination, nor of who makes one.

**Fix (architectural, independent of the legal answer):** a `ConsentState` machine on the senior — `active | withdrawn | suspended | capacity-in-question | deceased` — that is a precondition on *both* the write path (AD-4) and every disclosure path (Composer, notify adapter, TTS delivery, roster, research projection). Make the disclosure gate a named AD. Whatever counsel decides, the gate must exist for the decision to be implementable at all.

### F-03 — No consent-status propagation to the device; withdrawal is enforced only cloud-side — HIGH

AD-4 places the check in the log's write path. The Pi is upstream of that. On withdrawal, the device keeps waking, keeps capturing, and keeps calling STT/TTS vendors; only the final cloud write is rejected. Collection has not stopped — it has been redirected into a vendor's logs.

`consent-and-data-governance.md` requires "collection stops". The architecture does not deliver that, and cannot, because there is no consent channel to the device and no fail-closed rule.

**Fix:** an AD stating that the device holds a signed, short-TTL consent lease; an expired or revoked lease disables capture locally; a device that cannot refresh its lease fails closed rather than open. This also fixes the in-flight case (buffered turns, mid-run composition jobs), which is currently unspecified.

### F-04 — Grants are not bound to the persons she actually named — HIGH

AD-7 is right that family and care workers are `Grant`s, not entities, and that each carries "the consent clause that authorises it". But nothing verifies that a Grant's holder is a recipient she named in the Ulysses instruction. A care worker can mint a Grant for anyone. Given F-01 (the named recipients are not machine-readable), this cannot currently be checked even in principle.

**Fix:** Grants may only be created against a recipient identity captured in the structured `ConsentTerms` (F-01), and adding a recipient requires a new consent act, not an admin action.

### F-05 — "Every access is logged" appears in the spec and nowhere in the architecture — HIGH

`consent-and-data-governance.md` mandates access logging. The spine has no `AccessLog` entity, no read-path audit rule, no AD. The Logging convention actively works against it: "No transcript text, no observation content... ever, at any level" is correct for content but says nothing about recording *that* a named grant-holder read a named senior's window at a time.

This is also a PDPA Accountability expectation and the only way CAP-9's "verifiable by inspection afterwards" is satisfiable for the access boundary.

**Fix:** AD — *every read of a senior's observation data, read model, or weekly window by any human-facing surface or research export writes an immutable `AccessRecorded` event carrying actor, grant, senior id, scope and time. Reads that cannot write the audit record fail.*

### F-06 — Consent audio is a permanent, unshredded, home-originating recording that AD-2 does not cover — HIGH

AD-2's rule is absolute: "Audio buffers exist only in the Capture context on the device... No adapter outside `edge/device/` may accept an audio type." The Ulysses instruction is audio, recorded in the home, that must leave the home and be retained for the life of the enrolment and beyond. It is an unstated exception to the document's most prominent invariant — which means either AD-2 is false as written, or the architecture test for AD-2 will block the consent-capture path and be weakened in a hurry by whoever hits it first.

Compounding: AD-13 crypto-shreds "each senior's **observation payloads**". Consent artefacts are not observation payloads. On death or withdrawal, her voice recording survives — directly contradicting `consent-and-data-governance.md`, which requires the death path to cover "both the functional series **and the consent audio**".

**Fix:** state the carve-out explicitly in AD-2 (consent artefacts are a named, separately-governed audio class with their own adapter, store, and key), and extend AD-13 to cover consent artefacts under the same per-senior key, with the death/withdrawal disposition read from `ConsentTerms`.

---

## 2. Is the AD-3 "no judgement" wall load-bearing, or trivially crossed?

**Load-bearing on one flank; open on the other, and the open flank is the one a feature will actually walk through.**

What AD-3 gets right: forbidding comparison primitives *in the read model's API type* is a genuine structural constraint, and pairing it with an architecture test on dependency direction is the correct instrument for that half. A dashboard engineer cannot compute a trend from a type that has no ordering.

### F-07 — The Composer is an unconstrained aggregator and AD-3 does not reach it — CRITICAL

AD-8 requires every human-facing string to come from one Composer. AD-3 forbids v1 components from comparing, aggregating, ordering, scoring or thresholding across log entries. The Composer is handed a **week** of observations and asked, by Claude Opus 5, to produce "her week... plus one conversation opener". That is aggregation across entries by construction, and any competent summariser performs implicit comparison to decide what is worth saying. "She asked about her medication three times this week" is a threshold. "She hasn't mentioned the market since the 3rd" is a trend. Both are judgement; both pass every rule the architecture actually enforces.

The wall is crossed by editing a prompt. No code changes. No type changes. No architecture test fails. AD-12 explicitly promises this cannot happen — "a prompt may shape tone; it may never be the only thing standing between the system and a rule violation" — and for AD-3 at the Composer, a prompt is precisely and only what is standing there.

**Fix:** the Composer must not receive the window as free text. Give it a typed, per-entry `NarratableObservation` set with no cross-entry fields, no counts, no ordinals, no "since last week" slot — and make the Composer's contract *render these entries*, not *summarise this week*. Then the no-comparison property is a property of the input type, testable, and the LLM cannot compare what it was never given.

### F-08 — AD-3 forbids aggregation while CAP-5 requires it; the boundary is undefined — HIGH

A weekly window *is* a temporal aggregate. AD-3 bans aggregation. The document never says where the permitted line falls, which makes the rule untestable and guarantees it will be interpreted generously by whoever is under deadline.

**Fix:** state the line. Suggested: *within-window narration of individual dated entries is permitted; any value computed from more than one entry (count, rate, delta, ordering, presence-vs-previous-window) is forbidden.* That is checkable.

### F-09 — AD-8 promises deterministic rejection of rules that are not deterministically checkable — HIGH

AD-8 says the Composer "rejects violations as errors rather than warnings", and AD-12 classes Composer rule enforcement as "deterministic code with unit tests". A banned-vocabulary list is deterministic. But `communication-rules.md` also forbids "**anything phrased as a verdict about her, however gently**" and requires the governing test ("not fit for her to hear about herself"). Neither is a lexical property. A sentence can pass every banned word and still be a verdict.

As written, AD-8+AD-12 will produce a filter that catches "Stable" and "cognition" and ships "she seems to be finding the mail harder than she used to" — the exact output class the whole product is architected to prevent.

**Fix:** be honest in the AD about the two layers — a deterministic lexical gate that fails the write, plus a stated human-review requirement for the pilot period, plus F-07's input-type constraint doing the real structural work. Do not claim determinism the rule cannot have.

### F-10 — Gap density is a usable proxy signal on the roster — MEDIUM

AD-6 correctly separates liveness from interaction. But `Gap` events are cross-entry data the roster legitimately shows (CAP-10 requires consent and liveness status). A care worker reading "unreachable 4 of last 14 days" across a roster is performing exactly the cross-person comparison CAP-10's fixed-order rule exists to prevent. Not fatal — liveness is an operational fact about a device, not an observation about her — but the architecture should say so explicitly and require that liveness rendering is binary and current-state only, never a history or a count.

---

## 3. Does the data lifecycle (AD-2, AD-13) satisfy withdrawal and death?

**No. AD-13 is the right idea and is defeated by three things it does not name.**

### F-11 — AD-2 is contradicted by the architecture's own deployment diagram — CRITICAL

AD-2: "Raw audio never crosses the device boundary... Only extracted text and structured observations cross the network."

The Structural Seed diagram: `PI --> STT` and `PI --> TTS`, with STT and TTS in a `Vendors["External adapters"]` subgraph outside both the flat and the Singapore cloud region. The Stack names Deepgram Nova-3 — a cloud API. Note also that the mTLS and "text only" annotation is applied to `PI -->|text only, mTLS| API` and to *nothing else*.

So raw audio leaves the home on every single addressed turn, to a commercial vendor, very likely outside Singapore. The product's headline guarantee is false as diagrammed, and it is false in the same document that asserts it.

Worse, AD-2's enforcement mechanism cannot catch it. The rule is expressed as *where an audio type may live* ("no adapter outside `edge/device/` may accept an audio type") and tested as a dependency-direction assertion. An STT adapter that lives inside `edge/device/` and POSTs a WAV to api.deepgram.com satisfies the rule and passes the test. **A namespace constraint is the wrong instrument for a network-egress guarantee.**

**Fix, and this is the single most important change in this review:**

1. Decide, and state, whether STT/TTS run on-device or in the cloud. The MERaLiON note already flags edge deployment as available — if the guarantee is real, the bake-off criterion is not just accuracy on code-switched elderly speech, it is *runs on the appliance*.
2. If they must be cloud, **stop saying raw audio never leaves the home.** Rewrite AD-2 as what is actually true (e.g. audio leaves only to a named zero-retention processor under contract, never to your own stores, never to backups, never to prompts) and rewrite every downstream artefact, including the consent script, to match. The senior is being told something in her own language at enrolment; it needs to be true.
3. Replace the dependency-direction test with an egress test: an allowlist of destination hosts reachable from the device, enforced at the network layer, with an architecture test asserting that no audio-typed value reaches any HTTP client other than the approved STT/TTS client.

### F-12 — Crypto-shredding is silently reversible unless key custody is specified — CRITICAL

AD-13's guarantee holds only if the per-senior key is genuinely destroyable. The architecture says nothing about where keys live, and the default outcome of "per-senior key in PostgreSQL 18" is that keys are captured in every `pg_dump`, every PITR base backup, and every replica. Destroying the row destroys nothing; a restore resurrects the plaintext.

**Fix:** AD — *per-senior data keys live only in a managed KMS/HSM, never in the application database, never in a backup, never in an environment variable. Destruction is a KMS key-destruction operation. No key escrow exists; there is no break-glass path, and this is a deliberate accepted cost.* Also state that backup retention is bounded and reconciled with the shred path, and that shredding is verified by a post-hoc restore-and-fail test.

### F-13 — Shredding does not reach vendor-side copies; CAP-9 is therefore not verifiable — CRITICAL

CAP-9's success criterion: "a withdrawal request executes the path in `consent-and-data-governance.md` and is verifiable by inspection afterwards", and "for any interaction older than the raw-audio retention window, no audio exists in **any store or backup**".

Destroying your key does nothing to audio held by the STT vendor, text held by the TTS vendor, or prompts and completions held by the LLM vendor. Three data intermediaries hold copies the architecture cannot shred and does not mention.

**Fix:** AD — *no vendor may be adopted without contractual zero-retention (or a retention window shorter than the stated raw-audio window), a PDPA-compliant data-intermediary agreement, a named processing region, and a sub-processor list. Vendor selection is a privacy decision with a veto, not only an accuracy bake-off.* Add the vendor-side deletion step to the withdrawal path and make it part of the verification.

### F-14 — The raw-audio retention window is deferred in both directions and therefore does not exist — HIGH

AD-2: "Transcripts are retained only as long as extraction needs them, then discarded **per `consent-and-data-governance.md`**." That document: "Define the extraction-to-discard window explicitly; it is the shortest interval the pipeline can support." Neither states a number. The `edge/jobs/retention sweep` exists with no policy to sweep against, and CAP-9's success criterion is untestable.

**Fix:** put the number in the architecture. A concrete proposal to argue with: audio held in memory only, never written to disk, discarded on extraction completion or 60 seconds, whichever first; transcript text retained ≤ 24 hours for extraction retry, then discarded; observations retained per the stated series retention. Also state the series retention period, which is likewise absent (`signal-catalog.md` requires only that months-long windows be computable).

### F-15 — Death has no trigger, no event, and no effect on disclosure — HIGH

AD-13 says death destroys the key. Nothing says how the system learns of a death, who may assert it, what evidence is required, or what happens between death and notification. Meanwhile AD-6 will faithfully record `Gap`s, the weekly composition job will keep running, and the family window will keep arriving in the named recipient's inbox for a woman who has died. That is a foreseeable and severe harm, and it is currently the default behaviour.

**Fix:** a `SeniorDeceased` event with a defined asserting party (care worker, with a second-person confirmation), an immediate halt on all composition and delivery, and only then the disposition path from `ConsentTerms`. Note also that under PDPA, personal data of a deceased individual remains subject to the protection and disclosure obligations for ten years from death — so the de-identified research projection surviving her requires a stated basis, and the record of the death itself must be protected.

### F-16 — The de-identified projection may not be anonymous, and survives a delete election — HIGH

Writing the de-identified projection at ingest rather than deriving it later is a genuinely good decision. But: a per-senior, day-resolution longitudinal functional series, from a small pilot cohort in a known set of estates, with dated life events (bereavement, hospitalisation, scam approaches) is re-identifiable by anyone holding a fragment of context. Under PDPC anonymisation guidance, data that can be re-identified with reasonable effort remains personal data — with every obligation attached.

Second problem: if she elects deletion on withdrawal, does the projection go? AD-13 implies it stays ("where she consented to it"), but if the projection carries any link key back to `snr_`, it is neither anonymous nor deleted, and her election was not honoured.

**Fix:** state that the projection carries no link key and no reversible pseudonym; require a documented re-identification risk assessment before any research export; and make the projection's survival explicitly one of the elections in `ConsentTerms`.

---

## 4. Singapore PDPA — obligations this architecture does not name

The word PDPA appears twice in the spine, both times in **Deferred** ("Blocked on the PDPA question in the SPEC"). That is not a tenable position for a document that is the build substrate: several of these obligations have structural consequences that get more expensive the later they land.

Health-adjacent data raises the stakes specifically — the PDPC treats healthcare-related data as a category carrying a higher risk of significant harm, which lowers the threshold at which a breach becomes notifiable. And voice recordings of identifiable individuals are personal data; voice is additionally a biometric sample under the PDPC's biometric guidance, so a pipeline holding her audio is holding biometric personal data even if it never builds a voiceprint.

### F-17 — Controller / data-intermediary split is undefined — CRITICAL

The single most consequential unnamed thing. Is the community care organisation the **Organisation** (controller) with this product as its **Data Intermediary** (processor), or is the product the Organisation? The answer determines who owns consent, who answers access requests, who notifies the PDPC on breach, who signs vendor agreements, and who is liable. It also determines whether the architecture needs a per-tenant data boundary (it probably does, since the buyer is "a Singapore community care organisation", plural over time).

**Fix:** state it in the spine, with the data flow annotated by role. If the care org is the Organisation, then the product is an intermediary and the architecture inherits the intermediary's reduced-but-real obligations (protection, retention, breach notification to the controller **within hours, not days**) plus contractual ones.

### F-18 — Transfer Limitation Obligation — CRITICAL

Deployment puts STT, TTS and the Anthropic API outside the Singapore region box, and the Deferred section fixes only that hosting "is Singapore-resident". Transferring personal data out of Singapore requires ensuring the recipient is bound to a comparable standard of protection — contractually, by binding corporate rules, or by an applicable certification. Nothing names this, and three vendors are in the diagram.

**Fix:** name the obligation, name the mechanism per vendor, and state processing regions. This interacts with F-11 and F-13; solve them together, at vendor selection.

### F-19 — Data Breach Notification — HIGH

Notifiable breaches must be assessed and reported to the PDPC within **3 calendar days** of the organisation becoming aware that a breach is likely notifiable, with affected individuals notified as soon as practicable; where the data class carries a higher risk of significant harm, the notifiability threshold is met more readily, and this data class does. Intermediary-to-controller notification is expected in hours.

The architecture has no incident detection, no breach-assessment path, no clock, and — relevantly — a fleet of physically accessible Raspberry Pis in unattended flats, which is a stolen-device breach vector with no compensating control named (no full-disk encryption, no secure boot, no key storage, no remote wipe).

**Fix:** an AD covering device-at-rest protection and remote revocation, and a named breach-response path with the 3-day clock and the intermediary escalation.

### F-20 — Access and Correction Obligation — HIGH

An individual may request access to her personal data and to information about how it has been used or disclosed in the preceding year, and may request correction. The architecture has no access-request port, no export path, and no correction path exposed to her. Both invariants complicate it: AD-1 forbids update-in-place (correction-as-supersede is the right answer but the read model must then surface the corrected value and the architecture does not say it does), and AD-13's shredding means an access request after withdrawal returns nothing — which is correct, but must be a designed answer rather than a crash.

Note also that the "how it has been used or disclosed" limb is unanswerable without F-05's access log. These are the same fix.

**Fix:** an `app/subject-requests/` use case with access, correction and use-and-disclosure-history paths, and a stated response commitment. Also flag Data Portability as forward risk: it sits in the Act pending commencement, and AD-13 makes late compliance harder, not easier.

### F-21 — Retention Limitation — HIGH

No retention period is stated anywhere in the architecture for any data class. See F-14. Retention Limitation requires ceasing retention when the purpose is no longer served and retention is no longer necessary for legal or business purposes. "Long enough to compute months-long windows" is not a period.

### F-22 — Purpose Limitation across the two consents — MEDIUM

Research/validation consent is a *separate purpose* taken as a separate act. The architecture has one log and one projection, and observations carry no purpose tag. Purpose limitation cannot be enforced downstream: nothing structurally prevents an observation collected under the observation purpose from being read by a research export, and F-01 means the research election is not machine-readable either.

**Fix:** purpose tags on the projection write path, keyed off structured `ConsentTerms`.

### F-23 — Accountability: DPO, policies, DPIA — MEDIUM

A DPO is mandatory for every organisation regardless of size, with published business contact details, alongside documented data-protection policies and practices. None of this is architecture per se, but a DPIA is — for this data class, this population and this collection method, a DPIA is the expected artefact and its findings feed directly back into the ADs. Name it as a deliverable with an owner and a date, before enrolment.

### F-24 — Protection Obligation coverage is thin — MEDIUM

mTLS is annotated on one link. Nothing addresses: encryption at rest beyond the per-senior payload key; the Next.js surfaces' session handling; the device's physical and boot security; the research export channel; or key rotation. The Auth convention correctly places grant checks in `app/` rather than delivery — good — but says nothing about grant scoping enforcement for the research role, which is the highest-blast-radius grant in the system.

### F-25 — Consent capacity at enrolment is assumed and never recorded — MEDIUM

The SPEC assumes present capacity ("the enrolment path assumes present capacity"). By the product's own targeting premise, "the enrolment population is already subtly declining". Valid consent under the PDPA requires that she can understand what she is agreeing to. The architecture records three artefacts and no capacity attestation.

**Fix:** a fourth artefact — a care-worker capacity attestation against a stated, documented checklist, timestamped to the visit. Cheap to add now, impossible to retrofit, and it is the first thing anyone will ask for when the consent is challenged.

---

## 5. Does anything establish a medical-device intended purpose prematurely?

**Yes, and the riskiest instance is this document itself.**

### F-26 — The architecture is discoverable evidence of screening intent — HIGH

Under HSA's regime, whether a product is a medical device turns on its **intended purpose**, and intended purpose is established by claims, labelling, promotional material *and design documentation*. The SPEC already understands the exposure — "stating a screening purpose in a funder meeting establishes that intended purpose regardless of what v1 ships" — and then the architecture states it in writing, repeatedly, in a document that will be shared with the buying care organisation, with funders during diligence, and with any regulator who asks:

- Scope line: "Excludes the **regulated screening layer**."
- The C4 diagram literally renders a `SCREENING — v2, not built` node pointing at the log.
- AD-1: "the **evidentiary value the screening layer depends on**."
- AD-3: "thereby shipping an **unregulated screening product**."
- Deferred: "**The screening layer in full.** ... The port exists with no v1 implementation."
- Inherited by frontmatter reference: `signal-catalog.md`'s two-speed routing naming delirium, "the dementia pathway", and "the depression pathway".

A reasonable regulator reading this concludes that v1 is stage one of a device for detecting cognitive impairment, being deployed to build its validation corpus. That is, in fairness, exactly what it is — but the whole regulatory strategy depends on v1 not carrying that intended purpose yet, and this document donates it.

**Fix:**
1. Add an **Intended Purpose** section to the spine that states v1's purpose affirmatively, in ageing-in-place and functional-support terms, and states that v1 makes no claim about any condition. An architecture with no stated intended purpose invites the reader to infer one from context, and the context here is damning.
2. Move all v2/screening rationale into a separate, internally-scoped annex that is not distributed with the build substrate. The ADs can stand on their own reasoning: AD-1's append-only log is justified by evidentiary integrity of a functional record; AD-3 is justified by the no-judgement product constraint. Neither needs the word "screening" to be a good rule.
3. Rename the deferred port. `CrossEntryAnalysisPort` is a neutral capability. A port named for screening is a design-file statement of intent.
4. Reconsider `signal-catalog.md` remaining in `companions:` on this document. It is needed to build the record; the two-speed routing section is not, and it names three clinical pathways.
5. Elevate the HSA classification question from a SPEC open question to a named architectural decision with an owner and a date. It affects AD-1's retention, AD-10's provenance detail and the design-history-file discipline the v2 submission will need — and design-history requirements are far cheaper to adopt now than to reconstruct.

### F-27 — Internal vocabulary carries clinical-assessment weight — LOW

The naming convention correctly bans `Patient`, `Score`, `Level`, `Risk`, `Flag`. It leaves `instrument`, `item bank`, `refractory window`, `baseline period` and `Observation` — the vocabulary of a psychometric assessment protocol, in a discoverable design file. `communication-rules.md` bans "assessment, screening, baseline" in user-facing copy for the same reason it matters here. Low severity because these are genuinely the right internal terms and renaming carries its own cost; but note it, and never let this vocabulary reach a funder deck or a device-facing string.

### F-28 — CAP-6's "unreachable state" is reachable, which is a regulatory problem as well as an ethical one — HIGH

CAP-6's success criterion: "sending the family window while suppressing the senior delivery is **not a reachable state**." AD-8 delivers only "the senior-facing and family-facing renderings of a given week derive from the same **Composer call**". Same call is not same transaction. Delivery is two different adapters: notify (to the family's phone, reliable) and TTS-to-device (to a Pi in a flat, which AD-6 exists precisely because it goes dark).

The overwhelmingly common failure — device offline for a week — sends the family a window about a woman who has not heard it. The "no reveal because there is no secret" premise, which `consent-and-data-governance.md` names as "what makes the Ulysses contract defensible against 'I never agreed to this'", quietly fails on exactly the weeks when something is most likely to be worth saying.

**Fix:** an AD making the pairing transactional — *the family window is not released until the senior delivery is acknowledged by the device, or a stated fallback disclosure path completes (care worker delivers at next visit). A window pending senior delivery is held, and a held window past N days escalates to the care worker, never to the family.*

---

## 6. Third parties in the home who never consented — is AD-5 sufficient?

**Sufficient for the ambient case. Insufficient for four others, one of which is created by the product's own design.**

AD-5 is a good rule and correctly placed: address determination on-device, and a failed turn produces no network call "including telemetry". That closes the TV-and-phone-call scenario in CAP-1's test scene, and closing telemetry too shows real care. But:

### F-29 — Third parties named in her own speech are collected with no basis and no redaction — HIGH

`signal-catalog.md` requires capturing reports of scam approaches, bereavement, mood and social withdrawal, financial difficulty, and mail handling. Every one of those observations is likely to contain another identifiable person: a daughter's name, a neighbour, a doctor, a bank officer, a man who called about her CPF. Those people are data subjects. They did not consent, and health-adjacent inferences about *them* ("her son shouted at her again") may be recorded.

AD-2 governs audio; AD-10 governs provenance. Nothing governs the *content* of an observation. There is no redaction port and no AD.

**Fix:** an AD placing third-party-identifier minimisation on the ingest path, before the log write — observations reference third parties by relationship role, never by name or identifier, and this is enforced deterministically (per AD-12) rather than by prompt. Note this also improves the observation's usefulness, since role is the analytically relevant field.

### F-30 — Co-present speech during an addressed turn — HIGH

A far-field USB mic array capturing an addressed turn in a small flat captures whoever else is speaking in the room. AD-5 determines *that the turn was addressed*; it says nothing about *whose voice is in the buffer*. Combined with F-11 (audio egressing to a cloud STT), a visiting helper's speech reaches a vendor. The non-goals correctly reject ambient listening partly because it "records non-consenting visitors" — but addressed-turn capture records them too, just less of them.

**Fix:** state the mitigation and its limits. Speaker-turn segmentation with non-enrolled-speaker discard is one answer but is itself voice-biometric processing, which raises its own PDPA question — so this is a genuine trade-off that needs a stated decision rather than silence.

### F-31 — Wake-word false accepts have no discard rule — MEDIUM

openWakeWord will false-accept. AD-5 covers detection; it says nothing about detection *error*. On a false accept, unaddressed household audio is captured and egressed, and there is no rule requiring post-hoc confirmation or destruction.

**Fix:** extend AD-5 — *a turn that fails secondary address confirmation is destroyed on-device and produces no log entry, no observation, and no vendor call; false-accept rate is a tracked device metric.*

### F-32 — No notice to anyone in the home other than the senior — MEDIUM

Anyone entering the flat may have their speech incidentally captured and has no way to know. The PDPC's treatment of CCTV in analogous circumstances expects notification of individuals whose data may be collected. There is nothing here: no physical notice requirement, no capture indicator, no disclosure obligation on the care organisation to visiting helpers or family.

**Fix:** name it as an architecture-adjacent product requirement — a visible capture indicator on the appliance and a physical notice, both specified as part of the device, not left to the deployment epic.

### F-33 — Voice delivery of her weekly window discloses to whoever is in the room — HIGH, and unresolved by design

CAP-6 requires the senior's weekly account to be delivered **by voice, in her home**. If a helper, a neighbour or a grandchild is present, they hear health-adjacent content about her that she consented to disclose to a named recipient — not to them. Detecting presence would require the ambient listening the product bans outright. The two constraints genuinely collide, and neither the spec nor the architecture notices.

**Fix (options, all imperfect — pick one and record it):** deliver only on her explicit request rather than on a schedule, with an ambient prompt ("I've got your week whenever you'd like it") that discloses nothing; or require her to confirm she is alone; or accept the risk explicitly, in `ConsentTerms`, in her own voice at enrolment. The one unacceptable outcome is leaving it unstated so that it is decided by whoever implements the TTS job.

---

## Summary table

| # | Finding | Severity | Area |
|---|---|---|---|
| F-11 | AD-2's "audio never leaves the home" is contradicted by the deployment diagram; namespace test cannot enforce egress | CRITICAL | Data lifecycle |
| F-02 | Ulysses "no veto" likely unenforceable under PDPA s16; no disclosure-time consent gate exists | CRITICAL | Consent |
| F-01 | AD-4 enforces artefact presence, not consent terms; the instruction is not machine-readable | CRITICAL | Consent |
| F-07 | AD-3 does not reach the Composer; the no-judgement wall is crossed by a prompt edit | CRITICAL | No-judgement |
| F-12 | Crypto-shredding reversible via DB-resident keys in backups; key custody unspecified | CRITICAL | Data lifecycle |
| F-13 | Shredding does not reach vendor copies; CAP-9 not verifiable | CRITICAL | Data lifecycle |
| F-17 | Controller / data-intermediary split undefined | CRITICAL | PDPA |
| F-18 | Transfer Limitation Obligation unnamed; three vendors outside SG region | CRITICAL | PDPA |
| F-03 | Withdrawal enforced cloud-side only; device keeps capturing and calling vendors | HIGH | Consent |
| F-04 | Grants not bound to recipients she actually named | HIGH | Consent |
| F-05 | "Every access is logged" absent from the architecture entirely | HIGH | Consent / PDPA |
| F-06 | Consent audio is an unstated AD-2 exception and survives AD-13 shredding | HIGH | Data lifecycle |
| F-08 | AD-3 bans aggregation while CAP-5 requires it; boundary undefined and untestable | HIGH | No-judgement |
| F-09 | AD-8/AD-12 claim deterministic enforcement of a non-lexical rule | HIGH | No-judgement |
| F-14 | Raw-audio retention window deferred in both directions; no number exists | HIGH | Data lifecycle |
| F-15 | Death has no trigger and no effect; windows keep sending after death | HIGH | Data lifecycle |
| F-16 | De-identified projection likely re-identifiable; survives a delete election | HIGH | Data lifecycle |
| F-19 | Breach notification (3-day clock) and stolen-Pi vector unaddressed | HIGH | PDPA |
| F-20 | Access, correction and use-history obligations have no port | HIGH | PDPA |
| F-21 | No retention period stated for any data class | HIGH | PDPA |
| F-26 | Architecture document itself is discoverable evidence of screening intended purpose | HIGH | Regulatory |
| F-28 | CAP-6's "unreachable state" is reachable when the device is offline | HIGH | Consent / disclosure |
| F-29 | Third parties named in her speech collected with no basis or redaction | HIGH | Third parties |
| F-30 | Co-present speech captured during addressed turns | HIGH | Third parties |
| F-33 | Voice delivery discloses to whoever is in the room; collides with the ambient-listening ban | HIGH | Third parties |
| F-10 | Gap density usable as a proxy signal on the roster | MEDIUM | No-judgement |
| F-22 | Purpose limitation unenforceable; observations carry no purpose tag | MEDIUM | PDPA |
| F-23 | DPO, policies and DPIA not named as deliverables | MEDIUM | PDPA |
| F-24 | Protection Obligation coverage thin (at-rest, device boot, sessions, rotation) | MEDIUM | PDPA |
| F-25 | Capacity at enrolment assumed and never attested | MEDIUM | Consent |
| F-31 | Wake-word false accepts have no discard rule | MEDIUM | Third parties |
| F-32 | No notice or capture indicator for others in the home | MEDIUM | Third parties |
| F-27 | Internal vocabulary carries clinical-assessment weight | LOW | Regulatory |

## Recommended new ADs

Consolidating the fixes above, the spine is short roughly nine invariants:

- **AD-14 — Consent terms are structured and machine-readable.** (F-01, F-04, F-22, F-25)
- **AD-15 — Consent state gates disclosure, not only collection; the device holds a short-TTL lease and fails closed.** (F-02, F-03)
- **AD-16 — Egress allowlist: the audio boundary is a network property, tested as one.** (F-11, F-30)
- **AD-17 — Keys live in a KMS, never in the database or a backup; there is no escrow.** (F-12)
- **AD-18 — No vendor without zero-retention, a DPA, and a named region; vendor choice carries a privacy veto.** (F-13, F-18)
- **AD-19 — Every read is audited; a read that cannot write its audit record fails.** (F-05, F-20)
- **AD-20 — Third-party identifiers are minimised deterministically at ingest.** (F-29)
- **AD-21 — Disclosure pairing is transactional: no family window without senior delivery or its stated fallback.** (F-28, F-33)
- **AD-22 — Lifecycle events (`SeniorDeceased`, `ConsentWithdrawn`) halt composition and delivery before disposition runs.** (F-15)

Plus one non-AD change with the highest leverage per unit of effort: an **Intended Purpose** section, and the removal of screening rationale from the distributed build substrate (F-26).

## Sources

- [PDPC — Data Protection Obligations](https://www.pdpc.gov.sg/overview-of-pdpa/the-legislation/personal-data-protection-act/data-protection-obligations)
- [PDPC — Advisory Guidelines on Key Concepts in the PDPA](https://www.pdpc.gov.sg/-/media/files/pdpc/pdf-files/advisory-guidelines/ag-on-key-concepts/advisory-guidelines-on-key-concepts-in-the-pdpa-17-may-2022.pdf)
- [PDPC — Guide on Responsible Use of Biometric Data in Security Applications](https://www.pdpc.gov.sg/-/media/files/pdpc/pdf-files/other-guides/guide-to-biometric_17may2022.pdf)
- [PDPC — Advisory Guidelines index](https://www.pdpc.gov.sg/resources/advisory-guidelines)
- [Mandatory Data Breach Notification Under Singapore's PDPA (2026)](https://rafflescorporateservices.com/mandatory-data-breach-notification-pdpa-singapore-2026/)
- [Singapore PDPA Guide 2026: Fines, DPO and the 3-Day Breach Rule](https://vucense.com/tech-guides/security-101/singapore-pdpa-compliance-guide-2026/)
- [PDPA Compliance Singapore — complete guide (2026)](https://sageshield.com/pdpa-compliance-singapore-complete-guide-2026/)
- [Relying on the Legitimate Interests Exception under the PDPA — Norton Rose Fulbright Data Protection Report](https://www.dataprotectionreport.com/2023/03/relying-on-the-legitimate-interests-exception-under-the-personal-data-protection-act-2012/)
- [Guidelines for Expanded Forms of Deemed Consent and Exceptions to the Consent Obligation — OrionW](https://www.orionw.com/news-insights/guidelines-for-expanded-forms-of-deemed-consent-and-exceptions-to-the-consent-obligation)
- [PDPA Compliance: Voice Recordings and Call Centres in Singapore](https://www.i2coms.com/blog/pdpa-compliance-voice-recordings-and-call-centers-in-singapore/)
- [Personal Data Protection Act 2012 — overview](https://en.wikipedia.org/wiki/Personal_Data_Protection_Act_2012)
- [CMS Expert Guide — Digital Health Apps and Telemedicine in Singapore](https://cms.law/en/int/expert-guides/cms-expert-guide-to-digital-health-apps-and-telemedicine/singapore)
- [HSA — Regulatory Guidance for Software Medical Devices, a Life Cycle Approach (overview)](https://www.makrocare.com/blog/singapore-hsa-regulatory-guidelines-for-software-medical-devices-a-life-cycle-approach/)
- [HSA medical device regulations — classification by intended purpose](https://www.pureglobal.com/markets/singapore/hsa-medical-device-regulations)

Legal positions above are a reviewer's reading and are not legal advice; F-02, F-17, F-18 and F-26 in particular should be put to Singapore counsel before enrolment begins.

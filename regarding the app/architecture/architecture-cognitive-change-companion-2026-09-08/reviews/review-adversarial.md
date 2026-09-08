---
review: adversarial
target: ../ARCHITECTURE-SPINE.md
spec: ../../../specs/spec-cognitive-change-companion/SPEC.md
date: '2026-09-08'
stance: 'Assume two competent teams, each reading only the spine, each obeying every AD to the letter, each shipping something the other cannot integrate with.'
---

# Adversarial review — cognitive-change-companion architecture spine

## Method

The spine's claim is that its ADs are strong enough that independent units built one level
down (epics, stories, teams) cannot build incompatibly. I tested that claim the only way it
can be tested: by constructing, for each seam, **a concrete pair of units that both satisfy
every AD as written and still cannot be integrated** — or that satisfy every AD and still
break a guarantee the SPEC sells.

Seventeen such pairs were constructible. Six are CRITICAL: two of them are flat internal
contradictions in the spine (a build cannot satisfy both halves), and one of them means
AD-13 does not actually erase anything.

A note on what is *not* wrong. The paradigm choice is right, the four contexts are the right
four, and AD-2/AD-3/AD-5/AD-9/AD-12 are correctly identified as the load-bearing rules. The
spine's failures are almost entirely failures of **closure**: it names the right invariants
and then leaves the data shapes, the ownership of three entities, and the semantics of four
verbs open, which is exactly where two teams diverge. Every finding below is closable with
text; none requires re-founding the architecture.

## Severity key

| Tier | Meaning |
|---|---|
| **CRITICAL** | Two compliant units produce an unintegrable build, OR a guarantee the SPEC sells is not actually delivered, OR the spine contradicts itself. |
| **HIGH** | Two compliant units diverge on something expensive to reconcile later, or a SPEC constraint has no architectural home. |
| **MEDIUM** | Divergence is real but cheap to reconcile; or a convention is missing where a convention would do. |
| **LOW** | Worth a line; no divergence pressure yet. |

---

# CRITICAL

## F-1 — AD-2 contradicts the layer map, the source tree, and CAP-7. A compliant build is impossible.

**Severity: CRITICAL — internal contradiction.**

AD-2: *"No adapter outside `edge/device/` may accept an audio type."*

The layer map: *"Adapters (STT, TTS, LLM, DB, notification) → `adapters/`."*
The source tree: `adapters/ # anthropic/ deepgram/ elevenlabs/ postgres/ notify/`.

An STT adapter that does not accept audio is not an STT adapter. A TTS adapter's *return*
type is audio. Both live in `adapters/` by the spine's own map, and both are forbidden by
AD-2 by the spine's own rule.

**The pair.** Team A (device epic) reads AD-2 as supreme and implements STT and TTS inside
`edge/device/`, with `core/ports/` declaring only `transcribe(handle) -> Transcript`. Team B
(adapters epic) reads the layer map and the tree and implements `adapters/deepgram/` with an
`AudioBuffer` parameter, plus the architecture test in `tests/architecture/` asserting only
that `core/` imports nothing. Both cite the spine. Team B's build fails Team A's AD-2
architecture test; Team A's build has no adapter layer for the two vendors the stack section
names, and the vendor bake-off the Deferred section promises has nowhere to happen.

**The second, worse half: CAP-7 enrolment audio.** The Ulysses instruction is *"Recorded as
audio, not asserted on her behalf"*, captured on the **care worker's phone** during a home
visit, retained for years, and **played back** at disclosure time. That is audio that (a)
never touches the senior's device at all, (b) must be stored server-side, and (c) must be
retrievable. AD-2 as written forbids its existence: it is audio, and it is handled outside
`edge/device/`. Team A's enrolment epic therefore either violates AD-2 or ships CAP-7 with
the consent artefact stored as a transcript — which destroys the entire defensibility
argument in `consent-and-data-governance.md` ("the consent is in her own voice, played back
rather than asserted"). Team B ships it as a blob in `adapters/s3/` and silently punches a
hole through the product's headline guarantee, with no rule distinguishing that hole from
the one AD-2 exists to prevent.

**Root cause.** AD-2 conflates two different things: *the senior's captured speech* (which
must never leave the home) and *audio as a type* (which the system legitimately handles in
three other places — STT input on-device, TTS output to the device, and consent recordings
on the care worker's phone).

**Proposed close — replace AD-2 and add AD-2b.**

> ### AD-2 — Captured speech never crosses the device boundary
>
> - **Rule:** *Captured speech* — any audio containing a senior's utterances, and any
>   near-verbatim transcript of it — exists only within the Capture context on the senior's
>   appliance. It is never transmitted, never persisted off-device, never included in a model
>   prompt that leaves the device, and never written to any log at any level. STT runs
>   on-device or against an adapter invoked *from* `edge/device/`; the port's audio-typed
>   surface is declared in `core/ports/audio.py` and may be implemented **only** by modules
>   under `edge/device/`. TTS output is audio flowing *toward* the device and is exempt.
>   What crosses the network from the appliance is defined exclusively by AD-14 (the Capture
>   → Ingest contract); nothing else.
>
> ### AD-2b — Consent audio is a sealed artefact, not observation data
>
> - **Binds:** CAP-7, CAP-9
> - **Prevents:** The Ulysses recording being downgraded to a transcript to satisfy AD-2 —
>   which would collapse the consent model — or being treated as capture data and swept into
>   the pipeline.
> - **Rule:** The own-voice Ulysses instruction is captured on the care worker's device,
>   stored encrypted under the senior's AD-13 key in a store that no ingest, read-model,
>   composer, or research code path may reference, and is readable only by (a) playback to
>   the senior or the named recipient at disclosure and (b) the enrolment context. It is never
>   transcribed into an `Observation`, never sent to any model, and never enters the research
>   projection. Its end-of-life path is the one recorded at enrolment, independent of the
>   observation series' retention.

---

## F-2 — "Observation" is undefined. Its cardinality, its payload schema, and its encryption envelope are all open.

**Severity: CRITICAL — clashing shared-data shape at the centre of the system.**

AD-10 fixes provenance and nothing else: *interaction, date, signal type, item-bank variant*.
It says nothing about what the observation **is**, how many an interaction yields, or which
fields are ciphertext under AD-13.

**Pair A — cardinality.**
- Story 1 (task support, CAP-2) writes **one Observation per extracted fact**. A single
  conversation yields three: `daily_tasks/completed`, `medication/dose_confirmed`,
  `social_behavioural/mentioned_low_mood`.
- Story 2 (instrument delivery, CAP-3) writes **one Observation per interaction**, carrying a
  list of typed entries, because an item administration is naturally one unit.

Both satisfy AD-1, AD-10 and AD-11 exactly. The resulting series has two incompatible
grain sizes. CAP-4's success criterion ("returns the series with every entry traceable")
passes for both and is therefore not a tiebreak. The v2 screening layer — which the SPEC
says v1 must not preclude — cannot compute a days-long window over a series with two grains.

**Pair B — payload schema.**
- Team A types the payload as `dict[str, Any]` free JSON, per signal type, undocumented.
- Team B types it as `text: str` prose plus `signal_type`, because the Composer needs prose
  and the catalog describes observations in prose ("word-finding pauses", "reporting things
  put somewhere unusual").

Both comply. The Composer, written by a third team, can render neither generically. Worse,
Team B's prose payload carries direct identifiers (names, addresses from mail handling) that
Team A's structured payload does not — which lands directly on F-4.

**Pair C — the encryption envelope (this is the one that bites AD-13).**
AD-13 encrypts "observation payloads". Which fields are payload?
- Team A encrypts only the free-text/response body, leaving `senior_id`, `interaction_id`,
  `signal_type`, `item_variant_id` and `observed_at` in cleartext — because AD-3's read model
  and AD-10's provenance need to be queryable without the key.
- Team B encrypts the whole record except `senior_id` and `observed_at`, and stores
  `signal_type` inside the ciphertext.

Team A's build, after crypto-shredding, still exposes a complete dated timeline of
*which signal types fired on which days* for a withdrawn senior — which is most of the
functional series, and is exactly the thing withdrawal was supposed to destroy. Team B's
build cannot serve the windowed read model or the research projection without decrypting
every row. Both obey AD-13 to the letter.

**Proposed close — new AD-14 (the observation contract), and tighten AD-10.**

> ### AD-14 — One closed Observation contract; one fact per Observation
>
> - **Binds:** CAP-2, CAP-3, CAP-4, CAP-5, CAP-9
> - **Prevents:** Two producers writing two grains and two payload shapes into one series,
>   leaving the read model, the Composer, the research projection and the v2 layer unable to
>   consume it; and leaving AD-13's ciphertext boundary to each team's judgement.
> - **Rule:** An `Observation` records **exactly one fact about exactly one signal type**. An
>   interaction yielding three facts yields three Observations. Every Observation has the
>   same envelope, and the envelope is closed — adding a field is an architecture change:
>
>   | Field | Cleartext? | Content |
>   |---|---|---|
>   | `observation_id` | clear | UUIDv7, `obs_` |
>   | `senior_id` | clear | UUIDv7, `snr_` |
>   | `interaction_id` | clear | UUIDv7, `int_` — AD-10 |
>   | `observed_at` | clear | UTC ISO-8601 — AD-11 |
>   | `recorded_at` | clear | UTC ISO-8601, log write time |
>   | `supersedes` | clear | `obs_` or null — AD-1, AD-15 |
>   | `extractor` | clear | model id + prompt version + code version — AD-16 |
>   | `payload` | **ciphertext under the AD-13 senior key** | everything else |
>
>   `signal_type`, the item-bank variant, the response, the outcome, and every free-text
>   fragment live **inside** `payload`. No signal type, no variant id, no outcome, no
>   content-bearing field of any kind is stored, indexed, or logged in cleartext — an
>   unkeyed reader may learn only that *some* observation existed for a senior at a time.
>   `payload` conforms to a per-signal-type schema in `core/observations/schemas/`, versioned,
>   with one schema per row of `signal-catalog.md`; the log rejects a payload that fails its
>   schema. A new signal type is a schema addition, never a free-form field.

Also amend AD-10's list to read *"…records the interaction it came from, its date, its signal
type per `signal-catalog.md`, its extractor identity per AD-16, and the item-bank variant
where one applies"*, so that the provenance list and AD-14's envelope cannot drift.

---

## F-3 — The Capture → Ingest seam has no contract: no minted-id owner, no clock authority, no idempotency, and no agreed extraction site.

**Severity: CRITICAL — the seam the review was asked to attack hardest, and it is empty.**

AD-2 says *"only extracted text and structured observations cross the network."* The word
"and" is doing catastrophic work: it permits both, and does not say which.

**Pair A — where extraction happens.**
- Team A (device epic) reads "structured observations cross" plus AD-5's on-device
  determination and ships a Pi that extracts Observations locally (small on-device model or
  rules) and POSTs `Observation[]`. It is defensible: it minimises what leaves the home, which
  is the spirit of AD-2.
- Team B (ingest epic) reads the context diagram — `ING[Ingest — extraction]` — and the
  stack (Claude Sonnet 5 "turn handling", server-side) and builds an ingest service expecting
  `{turn_text}` and doing extraction in the cloud.

Both are compliant. They ship a device that emits Observations into a service that accepts
turns. This is not a schema mismatch that a serializer fixes; it is two different products.
And it decides, silently, whether the LLM extractor sees near-verbatim senior speech
server-side — a privacy posture question resolved by whichever team merges first.

**Pair B — who mints `Interaction`, and whose clock.**
AD-7 assigns exactly one owner: `Senior`, to Enrolment. `Interaction` and `Gap` have no owner
named anywhere. So:
- Team A mints `int_<uuidv7>` on-device at turn boundary (it must — AD-5 puts turn
  determination there) and stamps the Pi's clock.
- Team B mints `int_` at the API edge and treats the device payload as untrusted, stamping
  server receipt time.

Under Team A + Team B's ingest, provenance points at an id the server never recorded. Under
Team B's minting, a device retry after a flaky link produces two Interactions for one turn
and duplicates every Observation in it — the record now shows repetition, which
`signal-catalog.md` lists as the **Memory** signal. A dropped connection manufactures a
dementia signal.

**Pair C — clock authority.** AD-11 mandates UTC and Singapore windowing but never says
*whose* UTC. A Pi that loses power (the precise CAP-8 scenario) and has no RTC boots to an
epoch or a stale time. Team A trusts device time (it is closer to the event); Team B trusts
server time (it is monotonic). Day-boundary drift is exactly what AD-11 exists to prevent,
and AD-11 does not prevent it.

**Proposed close — new AD-15.**

> ### AD-15 — The Capture → Ingest contract is one message, one direction, once
>
> - **Binds:** CAP-1, CAP-2, CAP-4, CAP-8
> - **Prevents:** Two teams disagreeing about where extraction happens, who owns an
>   `Interaction`, whose clock is true, and what a retry means — the four ways a one-way
>   pipeline silently becomes two-way, duplicated, or misdated.
> - **Rule:**
>   1. **Shape.** The appliance emits exactly one message type, `TurnCaptured`, containing:
>      device id, `interaction_id`, `client_captured_at` (device UTC), `client_clock_state`
>      (`synced` | `unsynced`), turn text, and a monotonic per-device `sequence`. It never
>      emits `Observation`s. **Extraction is Ingest's job**, in the cloud, behind the AD-12
>      port. Capture decides *whether* a turn exists (AD-5); Ingest decides *what it means*.
>   2. **Ownership.** The Capture context solely mints `Interaction` ids (UUIDv7, `int_`). No
>      other context creates one. Ingest may reject an Interaction; it may never invent one.
>   3. **Idempotency.** `interaction_id` is the idempotency key for the entire pipeline. A
>      re-delivered `TurnCaptured` with a known id is acknowledged and discarded, at any
>      depth. Retry is the appliance's only failure response; it never re-mints.
>   4. **Clock.** `observed_at` is `client_captured_at` **only when** `client_clock_state` is
>      `synced` against a trusted source within the last 24h. An unsynced turn is ingested
>      with `observed_at` = server receipt time and a `clock_degraded` marker in its payload,
>      and the affected span is written as a `Gap` (AD-6) rather than trusted for day
>      resolution. A turn whose device time differs from server receipt by more than the
>      configured skew is treated as unsynced.
>   5. **One direction.** The only traffic from Ingest to the appliance is acknowledgement,
>      configuration, and the AD-9 scheduler's item lease (AD-17). No observation content, no
>      read-model content, and no other senior's data ever travels toward a device.

---

## F-4 — AD-13 does not erase. The read model, the weekly windows, the vendor, and the research projection all survive the shred.

**Severity: CRITICAL — a guarantee the SPEC sells is not delivered.**

AD-13 shreds "observation payloads". AD-1 says read models are "derived and disposable". At
least five stores hold the same content in cleartext and none of them is covered:

1. **The windowed read model** (AD-3). It is a derived, persisted store of decrypted
   observation content, per senior, per week. Shredding the log key does nothing to it.
2. **Composer output.** CAP-5 windows are read by family, plausibly re-read later; CAP-6
   deliveries are logged as sent. These are prose *about her*, derived and stored.
3. **The LLM vendor.** Observation content and window drafts are sent to the Anthropic API.
   AD-2 forbids audio in "persisted model prompts"; nothing forbids or bounds retention of
   *observation* prompts by a third party. Post-shred, they persist wherever they persist.
4. **Notification payloads** (`adapters/notify/`), email or push, containing window prose.
5. **The de-identified research projection**, addressed below.

**The pair.** Team A (data-lifecycle epic, CAP-9) implements AD-13 exactly: per-senior key,
destroy on withdrawal, append tombstone, verify by attempting decryption. Their test passes.
Team B (read-model epic, CAP-5/CAP-10) implements a materialised weekly table plus a
`weekly_window_rendered` table so the family app is fast and windows are re-openable. Neither
team violates any AD. Together they ship a system where "withdrawal is verifiable by
inspection afterwards" (CAP-9's success criterion) is **false**, and nobody notices, because
Team A's verification only inspects the log.

**The second half — the withdrawal choice is unimplementable.** `consent-and-data-governance.md`:
*"her data is removed or de-identified according to what she consented to at enrolment. Which
of the two is her choice."* AD-13 makes shredding unconditional **and** makes the
de-identified projection a separate artefact written at ingest that the shred does not touch.
So both of her possible choices produce the same outcome: log shredded, projection retained.
The senior who chose full removal does not get it. The choice recorded at enrolment has no
effect on any code path. Two teams reading AD-13 will both build this, because AD-13 says
exactly this.

**The third half — the projection is re-identifiable.** "De-identified" is nowhere defined.
- Team C builds it as `pseudonym = HMAC(global_salt, senior_id)` with full payload text and
  day-resolution dates.
- Team D builds it as a fresh random id per senior, coded signal types only, no free text,
  week-resolution dates.

Both call themselves de-identified. Team C's projection joins to the *structurally surviving*
log on timestamps and interaction cadence and re-identifies a shredded senior trivially; it
also retains prose containing names and addresses (F-2 Pair B). And under F-2 Pair C's Team A
envelope, the surviving cleartext log columns are themselves the join key.

**Proposed close — replace AD-13's final sentence and add AD-16.**

> ### AD-13 — Erasure by crypto-shredding, not deletion *(amended)*
>
> - **Rule:** …*(as written, through "the content becomes unrecoverable")*… **Every derived
>   store is a shred obligation.** A store is derived if it holds, in any form, content
>   traceable to a senior: the windowed read model, Composer drafts and rendered windows,
>   delivery and notification payloads, caches, search indexes, exports, and backups. Each
>   derived store is registered in `core/erasure/registry.py` with its shred method
>   (key-destruction where it holds ciphertext, hard delete where it does not). Erasure runs
>   the registry, not a list in someone's head, and fails loudly if a store is unregistered.
>   A test asserts that every module writing senior-traceable content is registered. Model
>   adapters (AD-12) must be configured for zero vendor-side retention of observation content;
>   any adapter that cannot guarantee this may not receive it.
>
>   **De-identified retention is opt-in, at ingest, and irreversible-by-construction.** Where
>   and only where she consented to it, a projection is written at ingest under a pseudonym
>   generated from a **per-senior random secret held with her AD-13 key**, so that destroying
>   the key destroys the linkage as well as the content. The projection carries coded signal
>   types and schema-typed fields only — never free text, never a quotation, never an
>   `interaction_id`, never a `senior_id`, and never finer than week resolution. If she chose
>   removal rather than de-identified retention, withdrawal destroys the projection rows too;
>   the enrolment-recorded choice is a stored field that the erasure path branches on, and
>   both branches have tests.

> ### AD-16 — Corrections reach the projection, or the projection is wrong
>
> *(see F-9; the projection must subscribe to supersession or it permanently retains
> retracted facts. Text given there.)*

---

## F-5 — AD-3 binds only readers of the log. Judgement is legal everywhere else — and the Memory signal cannot be recorded without it.

**Severity: CRITICAL — the no-judgement guarantee has a loophole wide enough to drive the
whole product through.**

AD-3: *"No v1 component may **read the observation log** in a way that compares, aggregates,
orders, scores, or thresholds across entries."*

The Capture context never reads the observation log. Neither does the extraction step in
Ingest, which sees a turn and a session. So:

**The pair.**
- Team A (ingest epic) implements the Memory signal from `signal-catalog.md` —
  *"repeating a question **within a session or across days**"* — as an on-device/in-session
  comparator that flags a repeated question and emits
  `Observation{signal_type: memory, payload: {repeat_of_turn: …}}`. It never reads the log.
  **Fully AD-3 compliant.** It is also a cross-entry comparison producing a judgement, and it
  is invisible to the `tests/architecture/` dependency assertion, which only checks who
  imports the log port.
- Team B (record epic) reads AD-3 as prohibitive and refuses: it records only atomic turn
  facts and emits no memory-signal observation at all, because detecting repetition is
  comparison.

Both comply. Team A's series carries the Memory signal; Team B's does not. CAP-4's success
criterion is silent — it only forbids "a score, level, ranking, or classification", and
"repeated a question" is none of those. The two builds produce records of different
scientific content, and the v2 layer built on Team B's record cannot see the single most
cited early functional signal.

**The deeper problem.** `signal-catalog.md` defines *several* signals that are inherently
comparative — Memory ("across days"), Daily tasks ("previously completed now incomplete"),
Finances ("previously managed without help"), Attention ("difficulty sustaining"), Social
("marked change"). AD-3, read literally, forbids the system from ever recording any of them,
which would gut CAP-4. Read loosely, it permits the ingest path to compute anything at all.
The spine offers no third reading, so each team invents one.

**Proposed close — replace AD-3's rule with an operation whitelist that binds every context.**

> ### AD-3 — No judgement: dependency direction *and* a closed operation set
>
> - **Rule:** The prohibition binds **every v1 component, not only log readers** — Capture,
>   Ingest, extraction, read model, Composer, surfaces and jobs alike. No component may
>   produce, store, or render any of: a score, total, index, percentage, rate, count-over-time,
>   trend, delta, slope, direction, threshold crossing, category assignment of severity, a
>   ranking, a sort or an ordering of seniors by any property of the series, or a
>   highlight/badge/colour derived from it.
>
>   **Comparison is permitted only to constitute an observation, never to characterise a
>   senior.** A component may compare entries when and only when: (a) the comparison is
>   confined to a single senior and to the window `signal-catalog.md` defines for that signal,
>   (b) its output is a single dated `Observation` describing a discrete event ("asked the
>   same question twice in one conversation"), and (c) it produces no ordinal, cardinal, or
>   severity-bearing value of any kind. Each such comparator is declared in
>   `core/observations/comparators/`, one per signal type, and the list is closed — a new
>   comparator is an architecture change.
>
>   Everything else — comparison across seniors, across signal types, across windows, or
>   producing anything other than a discrete dated `Observation` — lives behind
>   `core/ports/screening.py`, which has no v1 implementation.
>
>   The windowed read model exposes no comparison, ranking, threshold, or aggregate
>   primitive; it returns dated entries and gap-excluded window boundaries, nothing else.
>   The architecture test asserts both the dependency direction **and** that no module outside
>   `core/observations/comparators/` reads more than one entry per call.

---

## F-6 — Extraction is model-driven, unversioned, and unowned. A model upgrade mid-baseline is indistinguishable from decline.

**Severity: CRITICAL — the scientific validity of the 12-week baseline.**

AD-12 lists what must be deterministic: consent gating, item eligibility, the audio boundary,
Composer rule enforcement. **Extraction is not on the list** — correctly, because it cannot
be. But that means the single function that decides what the record *says* is a
nondeterministic LLM call, and no AD governs its versioning, reproducibility, or drift.

**The pair.**
- Team A (ingest epic, week 1) uses `claude-sonnet-5` with prompt v1 and records nothing
  about either in the Observation — AD-10's provenance list is closed and does not include
  them, so recording them is over-delivery.
- Team B (platform epic, week 7) upgrades the model or tunes the extraction prompt to improve
  recall of mood mentions. Every AD is satisfied; AD-12's port made the swap cheap, which the
  spine explicitly celebrates.

Week 7 onward, the same senior behaving identically produces observably more mood and social
observations. The series contains a step change with no marker. Under `signal-catalog.md`'s
own two-speed routing, a step change over days is the **delirium** shape. The v2 screening
layer — which the SPEC insists v1 must not preclude — is trained on a corpus with an
uncontrolled instrument change in the middle of it and cannot tell the extractor apart from
the senior. There is no way to detect this after the fact, because nothing recorded which
extractor produced which row.

This is the failure the SPEC calls the most dangerous available direction, arriving through
the back door: not practice effects, but *instrument* drift.

**Proposed close — new AD-17, and the `extractor` field already added in AD-14.**

> ### AD-17 — The extractor is versioned, pinned, and its changes are events in the series
>
> - **Binds:** CAP-4, CAP-3, CAP-5; AD-10, AD-12, AD-14
> - **Prevents:** A model or prompt change reading as a change in the senior — an instrument
>   shift that is invisible after the fact and that the v2 layer cannot correct for.
> - **Rule:** Every `Observation` records its `extractor`: model identifier, prompt template
>   version, and extraction code version. The extraction model and prompt are **pinned by
>   configuration and validated at boot** (a floating model alias is a boot failure, per the
>   Config convention). Changing either appends an `ExtractorChanged` event to the observation
>   series for every affected senior, dated, so the series carries its own instrument history.
>   A change is preceded by a replay of a held-out fixture corpus, and the diff against the
>   previous extractor is recorded with the event. During the baseline period defined in
>   `instrument-protocol.md`, an extractor change requires the same deliberation as an
>   architecture change. Extraction output is schema-validated against AD-14; a payload the
>   model returns that fails its schema is a rejected write, not a coerced one.

---

# HIGH

## F-7 — AD-1's supersession is undefined, and resolving it is forbidden by AD-3.

**Severity: HIGH.**

AD-1: *"Corrections are new events that supersede, never edits."* Nothing says how
supersession is expressed, who may write one, or who resolves it. And resolving a
supersession chain is, by definition, reading more than one entry and choosing between them —
which AD-3 forbids the read model from doing.

**The pair.**
- Team A (ingest) writes corrections as new Observations with `supersedes: obs_…`, considering
  the job done — the log is correct.
- Team B (read model) returns every entry in the window, because filtering superseded entries
  means comparing entries, which AD-3 forbids, and because AD-3 says the read model's API has
  no comparison primitive.

Both compliant. The family's weekly window contains a fact and its retraction, or worse, only
the retracted fact if the Composer picks the first. CAP-5's "at least one specific dated
detail" gets built on a fact the system already knows is wrong.

**Proposed close — amend AD-1.**

> Append to AD-1's rule: *"A correction is an `Observation` whose `supersedes` names exactly
> one prior `Observation` for the same senior; chains are permitted, cycles rejected at write,
> and a superseded observation may not itself be superseded twice. Supersession resolution is
> a **projection concern, not a judgement**: the windowed read model resolves each chain to
> its head and returns only heads. This is explicitly permitted under AD-3 and is the only
> multi-entry operation the read model performs. Only the context that owns the signal type
> may write a correction to it. The research projection (AD-13) subscribes to supersession —
> see AD-16."*

> ### AD-16 — Corrections propagate to every projection, including the research one
>
> - **Binds:** CAP-4, CAP-9; AD-1, AD-13
> - **Prevents:** The de-identified corpus permanently containing facts the system has
>   retracted, discovered at validation time when the corpus is the whole asset.
> - **Rule:** AD-13's ingest-time research projection is not write-once. It subscribes to
>   supersession events and to confound annotations (`signal-catalog.md`) that arrive after
>   the observation, and applies them by appending a superseding projection row under the same
>   pseudonym. Nothing in the projection is edited or deleted except by the erasure path. A
>   projection row whose source observation has been superseded and not reconciled is excluded
>   from any research export.

---

## F-8 — AD-4's "no bypass, test flag included" makes tombstones, gaps and heartbeats after withdrawal impossible.

**Severity: HIGH — conflicting state-mutation paths.**

AD-4: *"The log rejects any observation for a senior without an active enrolment… There is no
bypass, test flag included."*
AD-13: *"Withdrawal or death destroys the key and **appends a tombstone event**."*
AD-6: *"Any period without a heartbeat is **written to the observation series** as an explicit
`Gap`."*

After withdrawal the enrolment is not active. The tombstone is an event appended for that
senior. The gap writer keeps running until the appliance is physically collected — days or
weeks in a real community-care operation.

**The pair.**
- Team A (enrolment/lifecycle epic) implements withdrawal, finds AD-4 rejects its own
  tombstone, and adds a privileged system-event write path. It reasons that a tombstone is not
  "an observation". Defensible; also now an unmonitored second write path into an append-only
  log, which is the thing AD-1 and AD-4 jointly exist to prevent.
- Team B (liveness epic) implements the heartbeat sweep. Post-withdrawal it starts throwing
  `ConsentMissing` on every sweep, per the Errors convention (typed error, fail the write,
  never log-and-continue). The sweep job dies or floods. Or Team B classifies `Gap` as "not an
  observation" and writes it outside the consent gate — meaning a class of senior-derived data
  bypasses AD-4 entirely, forever, including *before* withdrawal, including for a partial
  enrolment that AD-4 exists to stop from collecting data.

The unanswered question underneath: **is a heartbeat a fact derived from a senior?** AD-1
says every such fact is an Observation. A heartbeat is derived from her appliance, but it is
a presence proxy and it is per-senior. AD-6 says heartbeats are "their own event stream" —
outside the log? Adjacent to it? Two teams, two answers.

**Proposed close — amend AD-4 and AD-6.**

> Append to AD-4's rule: *"The gate applies to `Observation` writes. Three event classes are
> explicitly outside it and are enumerated here exhaustively: `Enrolment` lifecycle events,
> AD-13 tombstones, and `Heartbeat` events. These may be written without an active enrolment
> and only by their owning context; there is no other exemption and adding one is an
> architecture change. `Gap` is an `Observation` and is gated. On withdrawal, gap generation
> for that senior stops at the tombstone; heartbeats continue to be recorded for fleet
> operations until the appliance is decommissioned, are never linked to observation data, and
> carry a device id rather than a senior id from the tombstone forward."*

> Append to AD-6's rule: *"`Heartbeat` is a device-scoped event stream, not part of the
> observation series, and carries no senior-derived content. `Gap` is a senior-scoped
> `Observation` derived from heartbeat absence. The heartbeat sweep job (`edge/jobs/`) is the
> **sole** writer of `Gap`; no read model or surface derives gaps on the fly. A `Gap` names a
> half-open UTC interval; the read model excludes a Singapore day (AD-11) if any part of it
> intersects a `Gap`, and reports the day as excluded rather than empty. Unreachability is
> surfaced to the care worker per CAP-8 as a device state, never as an observation about her."*

---

## F-9 — AD-9's single scheduler cannot survive an offline appliance, and the failure direction is the one the SPEC calls most dangerous.

**Severity: HIGH.**

AD-9 puts item selection and refractory-window eligibility in exactly one service. That
service is in the cloud (`app/instruments/`). But delivery is conversational and in-the-moment
(`instrument-protocol.md`: items arrive inside conversational context, never announced), and
two eligibility conditions are knowable **only on-device**: "no item in the same interaction
as a task the senior initiated under time pressure or distress", and the conversational
opening for a naturally-woven item.

**The pair.**
- Team A (instrument epic) ships the scheduler as specified: one service, one selection call.
  To make in-conversation delivery possible over a flaky link, it pre-fetches a queue of five
  eligible variants to the appliance each morning. AD-9 is satisfied — selection happened in
  exactly one service.
- Team B (device epic) consumes the queue opportunistically, administering when the
  conversational moment arises and reporting administrations back with the turn.

Now consider the appliance that administers variant `recall-07`, then crashes, or loses
connectivity for three days, or is reflashed. The administration is never reported. The
scheduler's refractory window for `recall-07` never starts. Within 90 days the senior gets
`recall-07` again — a repeat inside the refractory window, which
`instrument-protocol.md` calls a **build-blocking condition**, and which produces practice
effects, and whose error direction the SPEC names as *"false reassurance… the most dangerous
available failure direction."* Both teams obeyed AD-9 exactly.

Symmetrically, an unconsumed queue is not distinguishable from an administered one, so a
conservative scheduler burns eligible variants and hits bank exhaustion early.

**Proposed close — new AD-18.**

> ### AD-18 — Instrument items are leased, and an unconfirmed lease is a burn
>
> - **Binds:** CAP-3; AD-9, AD-15
> - **Prevents:** An offline or crashed appliance losing an administration report and
>   reintroducing a repeat inside the refractory window — false reassurance, the SPEC's worst
>   failure direction — or, symmetrically, burning the bank on items never delivered.
> - **Rule:** The single scheduler (AD-9) never pushes items; it issues **leases**. A lease
>   names one variant, one senior, and an expiry, and the scheduler treats the variant's
>   refractory window as **started at lease issue, not at confirmed administration**. An
>   expired, unconfirmed lease is recorded as an omission (AD-9) and the variant stays
>   ineligible — the system loses an item rather than risking a repeat. At most one lease is
>   outstanding per senior at a time. The appliance decides only *whether and when* to
>   administer a leased item within the conversational and distress constraints of
>   `instrument-protocol.md`; it never selects, never reorders, never caches beyond the lease,
>   and never administers an expired lease. Administration outcome (completed, partial,
>   declined, interrupted) returns as a normal `Observation` under AD-14/AD-15.

---

## F-10 — CAP-6's "not a reachable state" has no atomicity rule, and collides head-on with CAP-8.

**Severity: HIGH.**

CAP-6's success criterion: *"sending the family window while suppressing the senior delivery
is not a reachable state."* AD-8 gets close — same Composer call — but conflates *composition*
with *delivery*. Composing once says nothing about two deliveries over two channels, one of
which (the appliance speaker) may be in a `Gap`.

**Pair A — what "the same Composer call" produces.**
- Team A: one call returns `{family_text, senior_text}`; the senior's is fed to TTS.
- Team B: one call returns a neutral content object, then two rendering calls apply
  register/language. Team B satisfies "derive from the same call" at the content layer, and
  its two renderings can diverge in substance because two independent LLM calls made them —
  which is exactly the failure AD-8 exists to prevent, achieved while complying with AD-8.

Note also that the senior's delivery is *in her language* while the family's may not be, so
Team A's single call is doing translation as well as register — with no rule saying the two
must be semantically equivalent or that equivalence is checked.

**Pair B — delivery atomicity vs. an unreachable appliance.**
The appliance is dark (CAP-8). The senior delivery cannot happen this week.
- Team C (compose epic) blocks the family window, honouring CAP-6 literally. The family's
  weekly connection surface goes silent exactly when the device is down — and
  `communication-rules.md` warns that a channel families stop opening kills the safety layer.
- Team D (notification epic) sends the family window and queues the senior delivery for when
  the device returns, reasoning that "suppressing" implies intent and a queue is not
  suppression.

Both compliant. Team D has reached the state CAP-6 says is unreachable.

**Proposed close — amend AD-8 and add AD-19.**

> Append to AD-8's rule: *"One Composer call produces one `WeeklyContent` object containing the
> facts and the conversation opener. Both renderings — senior-facing, in her language, and
> family-facing — are produced within that same call and returned together; a rendering
> produced by a second model call is a violation. The Composer asserts, deterministically,
> that both renderings cite the same set of dated observations, and rejects the pair if they
> do not."*

> ### AD-19 — Disclosure is atomic: the senior's delivery is the precondition, not the sequel
>
> - **Binds:** CAP-6, CAP-5, CAP-8
> - **Prevents:** The family learning something about her before or without her — the failure
>   that would collapse the continuous-disclosure argument on which the whole Ulysses consent
>   model rests.
> - **Rule:** A `WeeklyDisclosure` is one transactional unit. The family window is released
>   only after the senior-facing delivery is **confirmed played** on her appliance. If the
>   appliance is unreachable, the family window is held, not cancelled, and the family is told
>   only that the device is unreachable (CAP-8 wording, never an observation about her). If it
>   remains unreachable past the configured hold, the week is recorded as an undelivered
>   disclosure and the content is folded into the next successful disclosure — it is never
>   released one-sided and never silently dropped. "Held" and "sent" are states on the
>   disclosure record; there is no code path that sets family-sent without senior-confirmed.

---

## F-11 — The human-contact counter-metric is a SPEC constraint with veto power, no capability, no AD, and no legal home under AD-3.

**Severity: HIGH — an unmapped constraint.**

The SPEC: *"Real human contact is a counter-metric with veto: AI talk-time rising while human
contact falls is logged as a regression even when task completion rises."* This is one of the
few constraints in the SPEC with the word *veto* in it. It appears nowhere in the spine — not
in the capability map, not in an AD, not in the entity model.

And it is unbuildable under AD-3 as written: "rising" and "falling" are trends; comparing two
trends is aggregation across entries. So:

**The pair.** Team A (metrics epic) builds it, because the SPEC demands it, and in doing so
builds the first cross-entry trend engine in the codebase — the exact component AD-3 exists to
prevent, now present, and available for the dashboard feature AD-3's *Prevents* clause names.
Team B (record epic) does not build it, because AD-3 forbids it, and the counter-metric with
veto silently does not exist. Both are compliant.

Note also that "human contact" is a signal the system can only know if the senior mentions it
— it is `signal-catalog.md`'s Social/behavioural row — so the counter-metric is measured from
the same extraction path it is meant to police.

**Proposed close — new AD-20.**

> ### AD-20 — The counter-metric is programme-level and de-identified, never per-senior
>
> - **Binds:** CAP-4; AD-3
> - **Prevents:** Either building the SPEC's veto counter-metric as a per-senior trend engine
>   — the first judgement component, and the crack AD-3 exists to seal — or not building it at
>   all and losing the SPEC's only veto.
> - **Rule:** AI talk-time and mentioned human contact are recorded per interaction as
>   ordinary observations under AD-14. Their comparison is a **programme evaluation output,
>   computed over the cohort, de-identified, at cohort granularity, on a cadence measured in
>   months**, produced by a job in `edge/jobs/evaluation/` that writes to a separate store and
>   is forbidden by dependency test from writing to the observation log, the read model, or
>   any surface. No per-senior talk-time trend, ratio, or comparison is computed, stored, or
>   rendered anywhere, ever. Time-talking-to-AI never appears on a surface (SPEC: a
>   diagnostic, never a target).

---

## F-12 — `Grant`, `ConsentArtefact` and the recipient are three names for possibly the same thing, and nobody owns family or care-worker identity.

**Severity: HIGH — two owners of one entity, by the back door.**

AD-7 assigns one owner to `Senior` and dissolves family and care workers into `Grant`s
"carrying a role, a scope, and the consent clause that authorises it". The ER diagram shows
`GRANT` and `CONSENT_ARTEFACT` as separate children of different parents. The named recipient
appears in both: she co-signs (a consent artefact) and she receives weekly windows (a grant).

**Pair A — is the recipient one record or two?**
- Team A (enrolment epic) models the co-signature as a `ConsentArtefact` holding recipient
  name and signature, and separately creates a `Grant{role: recipient}` for delivery.
  Revoking the grant leaves the consent artefact — correct, since the artefact is historical
  evidence. But nothing links them, so the system cannot answer "who is authorised, and under
  which clause".
- Team B models the recipient as a `Grant` whose `consent_clause` points at the artefact, and
  treats revoking as deactivating the grant. Now the two builds disagree about what
  authorisation *is*, and CAP-10's "consent status" column renders differently on each.

**Pair B — `scope` has no vocabulary.** AD-7 says a grant carries "a scope" and stops.
Team A: `scope = ["weekly_window"]` resource strings. Team B: `scope = {seniors: [...],
surfaces: [...]}`. The Auth convention says grants are checked in `app/` — so `web/` must
render conditionally from *some* shape returned over the wire, and that shape is undefined.
Two surfaces, two grant DTOs, two authorisation semantics.

**Pair C — who owns a family member's identity?** They authenticate (Auth convention). An
authenticating principal is an entity with a lifecycle, credentials, and a name. AD-7 says
they "are not entities" — but a `Grant` must reference *someone*, and one person may hold
grants against several seniors (a care worker certainly does; CAP-10 is a roster). So there is
a person record, unnamed and unowned, and two contexts will create it: Enrolment (when the
care worker enrols) and Auth/Web (at first login). Two writers of one person — precisely what
AD-7 was written to prevent, arriving because AD-7 declared the problem away instead of
assigning it.

**Proposed close — amend AD-7.**

> Append to AD-7's rule: *"`Principal` — any human who authenticates (care worker, family
> member) — is owned solely by the Enrolment and Consent context, which is the only writer.
> A `Principal` is created at enrolment or by invitation from it, never by the auth or
> delivery layer, which may only bind a credential to an existing principal. A `Grant` is
> `(principal_id, senior_id, role, scope, consent_clause_ref, granted_at, revoked_at)`. `role`
> is a closed enum: `care_worker`, `named_recipient`. `scope` is a closed set of named
> capability strings defined in `core/access/scopes.py`; a grant carries no free-form scope,
> and both `app/` enforcement and the surface DTO read that one definition. A
> `ConsentArtefact` is immutable historical evidence and is never revoked; a `Grant` is
> revocable and always names the artefact that authorises it. Revoking a grant never mutates
> an artefact, and an artefact never grants access by itself."*

Additionally, `consent-and-data-governance.md` mandates *"every access is logged"* and the
spine has no rule for it:

> Add to Consistency Conventions — **Access**: *Every read of senior-traceable content is
> recorded as an access event (principal, senior, scope, purpose, timestamp) in `app/`, at the
> same choke point where grants are checked, not in delivery. An unlogged read path is a
> failing architecture test. Access events carry ids only, never content (Logging), and are
> themselves subject to AD-13's registry.*

---

# MEDIUM

## F-13 — AD-11 fixes the timezone and leaves the week undefined; "no local-time persisted" collides with the persisted read model.

**Severity: MEDIUM.**

AD-11 mandates `Asia/Singapore` arithmetic but never defines the week. Team A uses ISO weeks
(Mon–Sun). Team B uses enrolment-anniversary weeks, which is more natural for "twelve
consecutive weekly windows" per senior (CAP-5) and for a 12-week baseline. CAP-6 requires the
senior delivery "in the same week" as the family window — untestable across two week
definitions, and the roster (CAP-10) shows "this week" per senior from a third.

Second half: "No local-time value is ever persisted" versus AD-1's persisted, derived,
Singapore-day-keyed read model, whose partition key is by construction a local date. Team A
reads AD-11 literally and keys the read model on UTC instants, reintroducing the boundary
drift AD-11 exists to prevent. Team B stores `singapore_date` and technically violates AD-11.

**Proposed close — amend AD-11.**

> Append: *"A week is Monday 00:00 to Sunday 23:59:59.999 `Asia/Singapore`, ISO-8601 week
> numbering, for every senior; there are no per-senior week offsets. A day is a
> `Asia/Singapore` calendar day. The prohibition on persisting local time applies to **event
> timestamps**; derived read-model and window records may and should carry an explicit
> `singapore_date` / `iso_week` key alongside the UTC instant, since a derived partition key
> is not an event time. `Asia/Singapore` has no DST, but the rule holds by named zone rather
> than fixed offset regardless."*

## F-14 — The retention sweep has no defined semantics against an append-only log.

**Severity: MEDIUM.**

`edge/jobs/` lists a "retention sweep". AD-1 forbids delete. AD-13 replaces deletion with
shredding. So what does the sweep do? Team A implements it as scheduled key destruction at
the stated retention period. Team B implements it as physical deletion of transcripts,
heartbeats, gaps, access logs and the read model — all of which AD-1 arguably does not cover,
since AD-1 speaks only of Observations. Team B may also delete consent audio, which
`consent-and-data-governance.md` says has a death path recorded at enrolment and a different
lifetime.

**Proposed close.** Add to AD-13's registry rule: *"Each registered store declares its
retention period and its expiry method independently; `edge/jobs/retention/` executes the
registry and nothing else. Observation payloads expire by key destruction, never row deletion.
Consent artefacts (AD-2b) expire only by the path recorded at enrolment, never by the sweep.
The sweep emits a per-run report of what it expired, by store, by count — never by content."*

## F-15 — Banned vocabulary is enforced in the Composer and in code review, but not at the port or vendor boundary.

**Severity: MEDIUM.**

AD-8 makes the Composer reject violations. The Naming convention bans `Score`, `Level`,
`Risk`, `Flag` in code. Neither covers: model output that reaches a surface through a path
other than the Composer (an error message, a device's in-conversation reply — AD-8 says
"every string a senior… reads or hears", which technically includes every turn response, but
CAP-1's real-time conversation is not routed through the weekly Composer in any team's
reading), vendor-supplied strings, or the notification title in `adapters/notify/`.

**The pair.** Team A treats the Composer as the weekly-composition service and lets the
turn-handling path (Sonnet 5) reply directly to the senior. Team B routes every device
utterance through Composer validation and eats the latency. Team A ships a device that can say
"your memory scores look fine" on a bad day.

**Proposed close.** Amend AD-8: *"'Composer' means the rule-enforcement component, not the
weekly job. Every model-produced string reaching any human — weekly windows, in-conversation
device replies, notification titles and bodies, error and empty states, care-worker roster
copy — passes through `core/compose/rules.py` validation before delivery, synchronously.
Validation is deterministic lexical and structural enforcement of `communication-rules.md`
(AD-12), not a model call; it is fast enough for the turn path by construction. A string that
fails is an error, never a redaction — the turn falls back to a fixed, pre-validated
utterance."*

## F-16 — `Interaction` has no definition of its boundary, and its shape is shared across three contexts.

**Severity: MEDIUM.**

The ER diagram has `SENIOR ||--o{ INTERACTION` and `INTERACTION ||--o{ OBSERVATION`, and
nothing defines what an Interaction *is*: one turn? one wake-to-silence exchange? one
conversational session? `signal-catalog.md`'s Memory signal says "within a session", so a
session concept is required and does not exist. `instrument-protocol.md` says no item "in the
same interaction as a task under time pressure" — the eligibility rule depends on the
boundary. AD-15 above makes Capture the minting owner, which settles *who*, not *what*.

**Proposed close.** Add to AD-15: *"An `Interaction` is one wake-to-silence exchange, bounded
on-device by address detection (AD-5) and an inactivity threshold. A `Session` is the
maximal run of interactions separated by less than the configured session gap; it is a derived
window computed by the read model, not a stored entity. Comparators (AD-3) that operate
'within a session' operate on that derived window."*

---

# LOW

## F-17 — Assorted

- **`Gap` is in the naming convention's entity list and in the ER diagram but has no owner in
  AD-7.** Closed by F-8's AD-6 amendment.
- **The Errors convention says rule violations "fail the write" — but AD-2's boundary and
  AD-3's read prohibition are read/architecture concerns, not writes.** Reword to *"fail the
  operation"*.
- **Config validates "a missing consent-enforcement or retention setting" at boot.** Extend to
  the AD-17 extractor pin and the AD-13 store registry, both of which are silent-failure
  candidates.
- **The stack pins Claude Sonnet 5 for turn handling and Opus 5 for weekly composition** but
  the Deferred section does not list model selection as deferred, so a team may treat the pin
  as architectural while another treats it as a seed. Say which. Given F-6, it must be
  architectural for extraction.
- **"UUIDv7 everywhere" is a good rule that leaks time.** UUIDv7 embeds a millisecond
  timestamp. After AD-13 shredding, a surviving `obs_` id still discloses when the observation
  was created — a cleartext timeline of activity for a shredded senior. Consider random v4
  for `obs_` specifically, or accept it explicitly.

---

# Summary table

| # | Finding | Severity | Closes with |
|---|---|---|---|
| F-1 | AD-2 contradicts the layer map and CAP-7 consent audio | CRITICAL | Rewrite AD-2; add AD-2b |
| F-2 | `Observation` shape, cardinality and ciphertext envelope undefined | CRITICAL | New AD-14; amend AD-10 |
| F-3 | Capture→Ingest seam: no contract, owner, clock or idempotency | CRITICAL | New AD-15 |
| F-4 | AD-13 does not erase derived stores; withdrawal choice inert | CRITICAL | Amend AD-13; add AD-16 |
| F-5 | AD-3 binds only log readers; catalog signals need comparison | CRITICAL | Rewrite AD-3 with an operation whitelist |
| F-6 | Extraction unversioned — model drift reads as decline | CRITICAL | New AD-17 |
| F-7 | Supersession undefined and forbidden by AD-3 | HIGH | Amend AD-1; AD-16 |
| F-8 | AD-4 rejects tombstones, gaps and post-withdrawal writes | HIGH | Amend AD-4 and AD-6 |
| F-9 | AD-9 vs offline appliance → repeat inside refractory window | HIGH | New AD-18 |
| F-10 | CAP-6 atomicity vs CAP-8 unreachable device | HIGH | Amend AD-8; add AD-19 |
| F-11 | Human-contact counter-metric unmapped and AD-3-illegal | HIGH | New AD-20 |
| F-12 | `Grant`/`ConsentArtefact`/`Principal` ownership; no access-log rule | HIGH | Amend AD-7; add Access convention |
| F-13 | Week undefined; local-time rule vs persisted read model | MEDIUM | Amend AD-11 |
| F-14 | Retention sweep semantics vs append-only | MEDIUM | Amend AD-13 |
| F-15 | Banned vocabulary unenforced off the weekly path | MEDIUM | Amend AD-8 |
| F-16 | `Interaction` boundary undefined; no `Session` concept | MEDIUM | Amend AD-15 |
| F-17 | Assorted (Gap owner, error wording, config, model pins, UUIDv7 leak) | LOW | Inline |

**Net:** the spine goes from 13 ADs to 20 plus six amendments. That is not bloat — five of the
new ADs are data contracts the spine currently leaves to whichever team writes the first
migration, and the other two (AD-19, AD-20) are SPEC constraints with veto power that
currently have no architectural home at all.

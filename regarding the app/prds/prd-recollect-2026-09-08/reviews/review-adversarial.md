# Adversarial PRD Review — Recollect v1 Observation Layer

**Reviewed artifact:** `prds/prd-recollect-2026-09-08/prd.md`
**Cross-checked against:** `specs/spec-recollect/SPEC.md` + four companions, `architecture/architecture-recollect-2026-09-08/ARCHITECTURE-SPINE.md` (AD-1..16)
**Reviewer posture:** decision-readiness, scope honesty, done-ness, downstream usability.

Verdict up front: this is a strong, unusually disciplined PRD. Scope honesty is nearly impeccable, cross-references resolve, and the counter-metrics are genuinely product-specific rather than boilerplate. The problems are not "demo residue" — they are four substantive gaps (two HIGH, two MEDIUM-HIGH) where the PRD's own invariants contradict its own metrics, and where the record claims data that nothing produces. Each is a place `bmad-create-epics-and-stories` will stall.

---

## 1. Scope honesty

### 1.1 HIGH — "mood/sleep/appetite mention" is claimed but nothing produces it

The Glossary defines **Observation** (§3, line 92) to include "a mood/sleep/appetite mention." §4.4's description (line 227) and **FR-12** (line 233) both state the functional series contains "mood/sleep/appetite mentions."

No feature, FR, instrument, or task class generates such a mention:

- Task classes (FR-4..7) are `medication`, `appointment`, `mail`, `routine` — none is "mood," "sleep," or "appetite."
- Instrument items (FR-8..11) are *structured cognitive items* — delayed recall, orientation, naming — not mood/sleep/appetite.
- There is no FR of the form "when the senior mentions sleep/appetite/mood in conversation, the device records a mention."

This is a **silent** omission, not an explicit deferral. It is compounded by the companion spec: `signal-catalog.md` lists "Poor sleep" under confounds "v1 must capture" and lists "Drop alongside mood, sleep or appetite change" as a v2 routing shape. So the SPEC *demands* this data, and the PRD *promises* it in the record — but neither assigns it a producer. Downstream will search for a story to build it and find none.

**Ask:** either (a) add an FR that captures mood/sleep/appetite mentions as an Observation subtype, or (b) explicitly remove "mood/sleep/appetite mention" from the Observation definition and FR-12 and add a Non-Goal stating v1 does not capture it (reconciling with signal-catalog.md).

### 1.2 LOW — status/self-description mismatch

§0 (line 12) calls this "the … decision-ready statement." The header says `status: draft`, and §8 carries 10 open questions including OQ-1, which the memlog itself tags a "phase-blocker (blocks enrolment)." "Decision-ready" overstates a document with an open enrolment blocker. Not a scope lie — but the framing will mislead a downstream consumer about how much is settled.

### 1.3 PASS — no demo/hackathon residue

The only occurrence of "demo" is the explicit "there is no demo-slice reduction" note (§6.2). "Forge" appears once as a provenance label in §9, not a framing leak. "Pilot" appears only to *reject* a pilot on the phone surface. §5 Non-Goals and §1 Vision are clean. This passes the "ship the full product" test.

---

## 2. Decision-readiness

### 2.1 HIGH — SM-1 contradicts the §4.2 / AD-3 cohort-only NFR

- **§4.2** feature NFR (line 183): task completion "must be computable at cohort level only (AD-3 carve-out); **never per named senior**, never on a human surface."
- **AD-3** (spine, line 81): the operating metric is "computed … at cohort level only, never per named senior, and never reachable from any surface."
- **SM-1** (line 442): "**each enrolled senior** completes all four task classes through the device at least once within a two-week period."

SM-1 as written is a per-senior determination — to know whether "each enrolled senior" completed all four classes you must compute, per senior, that completion. That is exactly what the NFR forbids. The PRD does not reconcile the two (the "never on a human surface" qualifier does not save it: SM-1 is a metric the team reads, not a senior-facing surface). A downstream epic author will either implement SM-1 and violate AD-3, or honor AD-3 and be unable to validate FR-4..7.

**Ask:** restate SM-1 in cohort terms (e.g., "X% of enrolled seniors complete all four task classes within a two-week period, computed in the programme-evaluation projection only") and note explicitly that the per-senior figure is never rendered.

### 2.2 MEDIUM — named-recipient physical co-signature is an unstated reachability trade-off

FR-21/FR-22 and UJ-2 require the named recipient to be **physically present** and co-sign at enrolment. The canonical recipient is an adult child — and UJ-3's own persona (Rachel) "lives in another estate," while a large share of Singapore seniors have children working overseas. Requiring physical presence silently excludes the very "no engaged family nearby / family at a distance" seniors v1 claims to reach. The trade-off (enrolment integrity vs. reachability) is never named as a cost. OQ-7 gestures at enrolment-population decline generally but does not flag this specific constraint.

**Ask:** name the trade-off — either allow a remote/attested co-signature with its risks, or accept reduced reach and state it.

### 2.3 LOW — OQ-10 duplicates §6.2

OQ-10 (line 467) restates §6.2 bullet 2 (line 431) nearly verbatim ("Cross-person prioritisation … unsolved, will be pushed on by funders"). Harmless, but it signals the Open Questions list was not deduped against Out of Scope. Minor hygiene.

### 2.4 PASS — Open Questions are genuinely open

OQ-1 (PDPA s16 vs. Ulysses), OQ-3 (vendor language coverage), OQ-4 (connectivity), OQ-8 (procurement clock) are real, consequential, and correctly flagged as blocking. None is rhetorical padding. This is the strongest section of the document.

---

## 3. Done-ness clarity

### 3.1 MEDIUM-HIGH — "no detected change" in FR-15/SM-2 is incoherent with the no-judgement invariant

- **FR-15** consequence (line 264): "Twelve consecutive weekly windows are generated for a senior **with no detected change**…"
- **SM-2** (line 446): same "with no detected change" precondition.
- **AD-3** (spine, line 78): "No v1 component may read the observation log in a way that compares, aggregates, orders, scores, or thresholds across entries." **FR-13**: "the record makes no judgement."

v1 has no change detection — it is forbidden from it. A test precondition of "no detected change" therefore has no definition inside v1: nothing in the system can *establish* that no change was detected. As written the requirement is unfalsifiable and reads as if the no-judgement boundary has been crossed.

**Ask:** restate the precondition as a test-harness control ("a senior whose underlying function is held constant by the test fixture") rather than a system property.

### 3.2 MEDIUM — consequences pinned to undefined configuration values

- **FR-10** (line 211): "Instrument turns never exceed the **configured per-week ceiling**." The ceiling is never given a value (`instrument-protocol.md`: "set low enough"). Testable only against an unnamed number.
- **FR-26** (line 370): "no audio exists after the **raw-audio retention window**." The window is never given a value (`consent-and-data-governance.md`: "Define the extraction-to-discard window explicitly" — still open).

Both are the "hand-wavy config" cousin of "handles gracefully." Downstream will have to invent the numbers, silently.

### 3.3 PASS — no "handles gracefully" / "reasonable performance" boilerplate

Grepping found zero occurrences of the classic hand-waving phrases. Every FR has at least one concrete consequence, and most are falsifiable (FR-19 "fails by construction", FR-22 "no bypass", FR-24 "within 24 hours", FR-16 "passes communication-rules.md"). FR-8's "above chance" is acceptable given its psychometric intent.

### 3.4 LOW — FR-27's death path is untested

FR-27 (line 372) promises an end-of-life path covering "withdrawal and death," but the consequence (line 377) tests only withdrawal via crypto-shred. The death path is stated as a requirement and left with no testable consequence.

---

## 4. Downstream usability

### 4.1 MEDIUM — Glossary drift: terms used but not defined in the controlled vocabulary

§3 (line 82) instructs downstream to "use these terms exactly … FRs, UJs, and SMs use them verbatim." Several terms violate this:

- **"Grant"** — `Named recipient` (line 86): "Exists as a Grant against the senior." "Grant" is defined nowhere; it is an architecture/identity concept leaking into the PRD glossary. A reader told §3 is the canonical vocabulary cannot resolve it.
- **"heartbeat"** — used in `Gap` (line 95) and `Liveness` (line 108), never defined.
- **"crypto-shred"** — FR-27 consequence (line 377), not a Glossary term.
- **"conversation opener"** — used in FR-15, UJ-3, and `Weekly window`; never an entry.
- **"mention"** — the "mood/sleep/appetite mention" subtype (see 1.1) is itself undefined.
- **"STT / TTS / LLM"** — first appear unexpanded in `Processor disclosure` (line 91); expanded only much later in §9.

Minor drift: FR-6 title and §4.2 say "official mail and letters," but the Observation type tag in the consequence is `mail` (line 173), while `Task` (line 96) uses the full phrase. A downstream schema author will fork on `mail` vs. `official-mail` as the type name.

### 4.2 PASS — ID continuity and cross-reference resolution

- AD-1..AD-16 all exist and every AD-n referenced by a feature resolves (verified against the spine).
- CAP-7 (Glossary `Enrolment`) resolves to SPEC.md.
- FR-1..FR-29, UJ-1..UJ-5, SM-1..SM-4 + SM-C1..C3 are continuous with no dangling or duplicated IDs.
- UJ protagonists are present and named (Mdm Lim = Senior, Siti = Care worker, Rachel = Named recipient); every FR maps to a real UJ.
- `communication-rules.md` and `signal-catalog.md` references resolve.

One asymmetry worth noting: features reference the *spine* (AD-n), while the Glossary's `Enrolment` references the *SPEC* (CAP-7). A reader can't tell from §0 which source governs which section. Minor.

---

## 5. NFR / Vision theater

### 5.1 PASS — little to no boilerplate

§1 Vision is specific and grounded (Alzheimer's Society 2025 figures, the "who-to-test" argument, the blood-biomarker rejoinder). §5 Non-Goals each carries a product-specific reason ("warmth is the texture of delivery, not the job"; "piloting there measures the wrong product"). The counter-metrics (SM-C1..C3) are the most non-boilerplate element of the document — a veto on human contact falling, a diagnostic that must never be optimised, and DAU-growth framed as regression. These read as genuine product doctrine, not lorem-ipsum NFRs.

### 5.2 MEDIUM — SM-C1 "human contact must not fall" has no sensor (counter-metric theater risk)

SM-C1 (line 452) requires logging a "regression" when "human contact falls" and counterbalancing SM-1 with it. But no FR, feature, or device capability captures human contact. The device observes addressed speech and task completions; it cannot observe the senior's face-to-face or phone contact with actual humans. AD-3 names "the human-contact counter-metric" as an aggregate, but the PRD never states how the underlying datum is produced. A veto metric with no sensor is unmeasurable — the one place the otherwise-honest counter-metric section shades into theater.

**Ask:** add an explicit producer for the human-contact datum (e.g., a family/care-worker contact log, or a device-prompted check-in), or state clearly that SM-C1 is measured out-of-band (e.g., by the care organisation) and therefore not a v1 build requirement.

---

## Findings summary (severity-ordered)

| # | Severity | Finding |
|---|----------|---------|
| 1 | HIGH | "mood/sleep/appetite mention" claimed in Observation/FR-12 with no producing FR or feature |
| 2 | HIGH | SM-1 (per-senior) contradicts §4.2 / AD-3 cohort-only NFR |
| 3 | MEDIUM-HIGH | FR-15 / SM-2 "no detected change" precondition is incoherent with the no-judgement invariant |
| 4 | MEDIUM | Glossary drift — "Grant", "heartbeat", "crypto-shred", "conversation opener", "mention", unexpanded STT/TTS/LLM |
| 5 | MEDIUM | SM-C1 "human contact must not fall" has no capture mechanism |
| 6 | MEDIUM | Consequences pinned to undefined config values (FR-10 ceiling, FR-26 retention window) |
| 7 | MEDIUM | Named-recipient physical co-signature is an unstated reachability trade-off |
| 8 | LOW | FR-27 death path untested; OQ-10 duplicates §6.2; "decision-ready" vs `status: draft` |

**Overall:** publishable with targeted fixes. Fix #1 and #2 before feeding `bmad-create-epics-and-stories` — they are the two places a downstream author will produce contradictory or un-schedulable work. #3, #4, #5 should be resolved in the same pass; the rest are polish.

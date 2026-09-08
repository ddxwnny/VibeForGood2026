# PRD Quality Review — Recollect v1 Observation Layer

## Overall verdict

This is a genuinely strong, funder-ready PRD: it faithfully mirrors the SPEC (no contradictions found against CAP-1..CAP-10 or the Constraints), its Non-Goals and counter-metrics are the best part of the document, and every FR carries a testable consequence. What's at risk is the *decision* layer, not the writing: the PRD asserts "v1 ships in full — there is no demo-slice reduction" (§6.2) while carrying two existential unresolved questions (PDPA s16 vs the Ulysses contract, and STT feasibility for Singapore code-switching) that are listed but never elevated to go/no-go gates, and the primary success metric is calibrated at two weeks against a SPEC success signal that demands twelve.

## Decision-readiness — adequate

The trade-offs are surfaced with unusual honesty — every Non-Goal in §5 names *why* it was rejected ("gives the real family permission to stay away, manufactures the withdrawal signal being measured"), not just that it was rejected. Open Questions in §8 are genuinely open and sharp: OQ-8 ("Can the community-care procurement clock be cleared at all? Right channel, possibly fatal timeline") and OQ-9 (pitch discipline / intended purpose) are exactly the tensions a funder-ready document must not dodge. The one `[NOTE FOR PM]` at a real tension (§6.2, split-product posture is "load-bearing") is placed correctly.

The gap: two of the ten open questions are *fatal-or-feasible*, not nice-to-resolve. OQ-1 — "Does PDPA s16 override the Ulysses contract? … blocks enrolment rather than build" — strikes at the single load-bearing consent premise the whole product rests on, yet it sits as item #1 in a ten-item list with no gate framing, no "decision required before X" statement, and no escalation to the top of the document. OQ-3 (the leading commercial speech vendor "covers ten languages, none of them Singapore's, so this gates vendor feasibility") is the same class: the product may not be buildable at all, and the PRD treats it as a scoping note. For a document that simultaneously states there is no demo-slice reduction, a decision-maker reading §8 alone has no signal about which of these ten items can sink the project and which are merely deferred.

### Findings
- **[high]** Existential blockers are not gated (§8.1, §8.3, §6.2) — PDPA s16 vs the Ulysses contract and STT feasibility for Singapore dialects can each sink the product, but both are presented as flat list items; §6.2's "v1 ships in full" stance coexists with them without reconciliation. *Fix:* Add a short "Decision gates before build" block naming OQ-1 and OQ-3 as go/no-go with owners, and either soften the "ships in full" claim or state explicitly which increments can proceed while those two stay open.
- **[medium]** No "decision required" elevation anywhere — the document surfaces tension but never tells a reader *what to decide and by when*. *Fix:* A one-line "Decision requested" line under each of the two fatal OQs.

## Substance over theater — strong

The Vision (§1) is not swappable: it is anchored to Singapore, to anosognosia, to the Alzheimer's Society 2025 survey (28% / 16%), and to the "layer before one" thesis. JTBD (§2.1) are load-bearing — the five roles each drive at least one feature or metric (task completion → SM-1; care-worker enrolment → FR-21..23; buyer → the ageing-in-place budget line in §2.1). There is no persona theater: the five JTBD entries map to the SPEC's actors, and the UJs carry named protagonists (Mdm Lim, Siti, Rachel) who recur through the FRs via "Realizes UJ-n." There is no innovation theater and no differentiation section written to satisfy a template. The Feature-specific NFRs (§4.2, §4.3) are product-specific, not boilerplate: "task completion … computable at cohort level only (AD-3 carve-out); never per named senior," and "minimum 90 days for recall items." No "scalable/secure/reliable" furniture anywhere.

The one caution is an *absence*, not theater: there are no performance, latency, availability, or security NFRs at all, for a product whose entire UX is real-time voice. That is filed under Done-ness rather than here.

### Findings
- (none that rise to a flag — no furniture detected)

## Strategic coherence — strong

The PRD has a real thesis and it is enforced downstream: "task completion carries the primary signal weight because it has no practice effect and IADL decline is already a recognised clinical signal" (§4.2), and the primary metric SM-1 is task completion. The counter-metrics are the strongest strategic move in the document — SM-C1 ("Real human contact — must not fall… a veto"), SM-C2 ("Time-talking-to-AI — a diagnostic, never a target"), SM-C3 ("Engagement / DAU-style growth — not a target") directly operationalize the Non-Goals and the "not a companionship product" constraint. This is the rare PRD whose success metrics *validate the thesis* rather than measure activity.

The weakness is calibration and coverage. SM-1's threshold is "completes all four task classes … within a two-week period," whereas the SPEC's own Success signal is "Twelve weeks later she is still using the device weekly … her recorded contact with real people has not fallen." The PRD's primary metric is six times weaker than the outcome the product actually claims to produce, and no SM measures twelve-week retention or the evidentiary quality of the record — even though OQ-6 ("Is retention real?") names retention as a genuine open risk. The thesis is "the evidence base for a regulated layer"; no metric tests whether that evidence base is actually produced.

### Findings
- **[high]** Primary SM-1 under-calibrated vs the SPEC success signal (§7 vs SPEC "Success signal") — a two-week task-completion floor does not test "twelve weeks later she is still using the device weekly," and nothing measures 12-week retention despite OQ-6 flagging it as the known failure mode. *Fix:* Add a retention/continuity SM (or strengthen SM-1's window) to match the SPEC's success signal, or explicitly state why the PRD deliberately stops short of it.
- **[medium]** No metric for the record's evidentiary quality — the actual product is "a dated per-senior functional record a regulator could accept"; no SM asserts completeness, provenance integrity, or day-resolution continuity over the baseline. *Fix:* An SM on series completeness/provenance would tie the thesis to a measurable outcome.

## Done-ness clarity — strong

This is the PRD's most defensible dimension. All 29 FRs carry a "Consequences (testable)" block with concrete, verifiable conditions, and several are exemplary: FR-8 ("Three lay readers given full transcripts cannot identify which turns were instrument items above chance"), FR-19 ("A test that attempts to send the family window without the senior delivery fails by construction"), FR-25 ("Sustained unrecognised turns surface as an operational alert to the care worker, not as an observation about the senior"). There is almost no "handles X gracefully" / "user-friendly" boilerplate anywhere — a rare outcome. Bounds do appear where they matter (FR-24 "within 24 hours"; FR-15 "twelve consecutive weekly windows").

The gaps are non-functional. There is no latency bound for a voice product ("an addressed utterance produces a spoken response" in FR-1 has no time budget — a response in 90 seconds technically satisfies the consequence). There is no availability/uptime requirement. FR-10's "configured per-week ceiling" and FR-26's "raw-audio retention window" reference values that are never stated in the PRD (the ceiling is "set low enough" in `instrument-protocol.md`; the retention window is "the shortest interval the pipeline can support" in `consent-and-data-governance.md`) — an engineer cannot implement against an undefined bound without opening the companions.

### Findings
- **[medium]** No latency or availability bounds for a voice companion (§4.1) — "produces a spoken response" is unbounded; a funder-facing PRD for real-time voice should state a time-to-response and an availability target. *Fix:* Add a non-functional bounds block (e.g., end-of-turn response latency, weekly-window generation reliability).
- **[medium]** Undefined thresholds referenced as if stated (FR-10 "configured per-week ceiling"; FR-26 "retention window") — the values live only in companions, not in the PRD. *Fix:* State the values or mark them `[NOTE FOR PM: value TBD]`.

## Scope honesty — strong

Non-Goals (§5) are explicit and do real work: eight items, each with a reason, and several prevent silent scope assumptions ("Passive or ambient listening … corrupts the baseline through speaker misattribution"). Out of Scope for MVP (§6.2) is present and carries the split-product `[NOTE FOR PM]`. Deferred decisions are surfaced rather than hidden. Open-question density (10 OQs + 7 assumptions + 2 `[NOTE FOR PM]`) is high, which is appropriate for these stakes — though the two fatal OQs should be gated (see Decision-readiness).

The defect is that the `[ASSUMPTION: …]` tagging discipline is largely absent. Only one inline tag exists in the whole document (§4.3, the 90-day floor). The Assumptions Index (§9) lists seven entries citing §2.3/§4.7/§4.1/§4.2/§4.5, but none of those locations carries an inline tag. So the index does not roundtrip: a reader at §4.7 (enrolment) cannot tell that "dedicated always-powered voice speaker," "buyer is a Singapore community care organisation," and "senior has capacity at enrolment" are assumptions the user did not confirm rather than settled facts. For a health-adjacent PRD where consent-and-capacity assumptions are legally consequential, this matters.

### Findings
- **[medium]** Assumption tagging absent on 6 of 7 indexed entries (§9 vs §2.3/§4.1/§4.2/§4.5/§4.7) — only the 90-day floor is tagged inline; the "senior has capacity at enrolment" and "Singapore community care organisation buyer" assumptions, which are consent-critical, read as settled facts. *Fix:* Add `[ASSUMPTION: …]` tags at the cited locations so the index roundtrips.

## Downstream usability — strong

The Glossary (§3) is present and a controlled vocabulary is enforced: FRs, UJs, and SMs use "Senior," "Named recipient," "Observation," "Gap," "Weekly window," "Baseline period" verbatim, and the ban on "patient"/"score"/"level" is observed in the prose. ID continuity is clean — FR-1..FR-29 contiguous and unique, UJ-1..UJ-5 contiguous, SM-1..SM-4 plus SM-C1..SM-C3 — and every cross-reference I checked resolves: all "Governed by AD-n" blocks match the spine's Capability → Architecture Map exactly (e.g., §4.4 lists "AD-1, AD-3, AD-10, AD-11, AD-14, AD-15," which is precisely CAP-4's set). `communication-rules.md` (referenced in FR-16 and SM-2) exists. Every UJ has a named protagonist, and the same protagonists (Mdm Lim, Siti, Rachel) recur consistently across UJs and FRs.

Two gaps. First, SM coverage is incomplete relative to the ten capabilities: CAP-1 (addressed-only), CAP-3 (instrument delivery — a core differentiator), CAP-6 (continuous disclosure), CAP-9 (data lifecycle), and CAP-10 (roster) have no success metric. The SPEC's CAP-3 success condition ("no item recurs inside its refractory window" and the lay-reader test) is carried in FR-8/FR-9 as acceptance but never promoted to an SM, so the instrument-fidelity guarantee — the feature most sensitive to practice effects — is not measured at the metric level. Second, the PRD cites only `communication-rules.md` explicitly; the other three companions (`signal-catalog.md`, `instrument-protocol.md`, `consent-and-data-governance.md`) are load-bearing sources for §4.3 and §4.7 but are never named, so a downstream story-writer pulling §4.3 alone will not know where the refractory-window values and consent artefacts are defined.

### Findings
- **[medium]** SM coverage gap (§7) — five of ten capabilities (CAP-1, CAP-3, CAP-6, CAP-9, CAP-10) have no success metric; instrument fidelity (CAP-3), the most practice-effect-sensitive feature, is unmeasured at the metric level. *Fix:* Add SMs for instrument rotation fidelity and continuous-disclosure parity, or state explicitly why these are verified by FR acceptance only.
- **[low]** Under-citation of companions (§4.3, §4.7) — `instrument-protocol.md`, `consent-and-data-governance.md`, and `signal-catalog.md` are never referenced by name, forcing downstream readers to find their sources by inference. *Fix:* Name the governing companion in each feature header, as `communication-rules.md` already is.

## Shape fit — strong

The shape is correct for the product. This is a multi-stakeholder, health-adjacent consumer-facing product (senior, care worker, family recipient, community-care buyer) with a meaningful, ethics-heavy UX, so named-protagonist UJs are load-bearing — and the PRD supplies them. It is chain-top: §0 states explicitly that it feeds `bmad-ux` and `bmad-create-epics-and-stories`, which raises the bar on downstream usability — and the PRD meets it. It is not over-formalized (29 FRs with testable consequences is proportionate to ten capabilities and funder stakes, not theatre) and not under-formalized (no floating UJs, no missing glossary). The one structural observation is that §6.2's "no demo-slice reduction" note is arguably a planning artifact leaking into a PRD; the Architecture Spine's "Deferred → demo slice" entry correctly leaves increment-slicing to sprint planning, and the PRD's phrasing ("Which FRs land in the first shippable increment is a `bmad-create-epics-and-stories` call") is actually self-consistent — worth flagging only as a wording tightening, not a defect.

### Findings
- (none — shape matches product and stake)

## Mechanical notes

- **Glossary drift** — minor and mostly deliberate. "Functional series" vs "functional record" is explicitly synonymized in §3, but the §4.4 feature *title* ("Longitudinal functional record") uses the non-primary term while its body and FR-12 use "functional series"; "Observation"/"observation," "Gap"/"gap," and "Task completion"/"task completion" drift in case. None misleads, but a downstream extractor should canonicalize on the Glossary's primary forms.
- **ID continuity** — clean. FR-1..29, UJ-1..5, SM-1..4 and SM-C1..3 are contiguous and unique; no gaps or duplicates. The SM-C prefix (counter-metrics sharing the "SM" prefix) is slightly unconventional but unambiguous.
- **Cross-references** — all resolve. Every "Governed by AD-n" list matches the Architecture Spine's Capability → Architecture Map verbatim; `communication-rules.md` resolves. No broken "see above" fallbacks.
- **Assumptions Index roundtrip** — fails. Six of seven §9 entries lack a matching inline `[ASSUMPTION: …]` tag at their cited locations; only §4.3's 90-day floor is tagged. This is the single most actionable mechanical fix (see Scope honesty).
- **UJ protagonist naming** — all named (Mdm Lim ×2, Siti ×2, Rachel ×1) and consistent across UJs and FRs; the named recipient in UJ-2 (Rachel) is the UJ-3 protagonist, so the thread holds.
- **Required sections** — present for the stakes: Vision, Target User/JTBD, Glossary, Features (with per-FR consequences), Non-Goals, MVP Scope, Success Metrics, Open Questions, Assumptions Index. Absent (flagged, not required): a dedicated compliance/regulatory-posture summary; for a health-adjacent funder-ready PRD this is currently carried implicitly by FR-21..27, §5, and §8 rather than stated in one place.
- **OQ duplication** — OQ-10 (cross-person prioritisation) restates §6.2 Out of Scope nearly verbatim; OQ-5 (comparative signal-catalog entries) is substantially resolved by AD-3's "comparative signals" rule in the spine but is listed open without a cross-reference to AD-3.

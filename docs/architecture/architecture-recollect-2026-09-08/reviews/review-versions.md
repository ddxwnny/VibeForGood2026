---
review: version-and-technology-verification
artifact: ../ARCHITECTURE-SPINE.md
reviewer: verification reviewer (web-enabled)
date: '2026-09-08'
scope: 'Stack table, the Anthropic voice-pipeline constraint, and every named vendor technology. Does NOT review the invariants, the domain model, or the capability map.'
verdict: 'Load-bearing Anthropic claim verified true. Vendor row failed reality check — the named STT model cannot transcribe three of Singapore''s four official languages.'
---

# Version & Technology Verification Review

## Method

Every committed technology decision in the Stack section was checked against a live
primary source today (2026-09-08). Package versions came from the PyPI and npm JSON
endpoints, not from search summaries. Platform lifecycles came from endoflife.date.
Anthropic claims came from `platform.claude.com` docs. Vendor claims came from each
vendor's own documentation. Where a source was secondary (news, blog) it is marked as
such below.

The question this review answers is not "are these good choices" but "was each of these
looked up, or recalled." Those produce different failure signatures, and the Stack
section shows both.

---

## Summary of findings

| # | Severity | Finding |
|---|---|---|
| 1 | **Critical** | Deepgram Nova-3 Multilingual does not support Mandarin, Malay, or Tamil — three of Singapore's four official languages, and the code-switched speech the product exists to capture |
| 2 | **High** | Deepgram Flux — the vendor's own recommendation for real-time voice agents, with integrated turn detection that overlaps AD-5 — is absent from the bake-off frame |
| 3 | **High** | MERaLiON's "now offered via cloud API" is stated as present fact; published sources describe it as announced/roadmap, and it carries no `[ASSUMPTION]` tag |
| 4 | **Medium** | Three of seven pinned versions are stale under a blanket "verified current 2026-09-08" header |
| 5 | **Medium** | Raspberry Pi 5 unit cost has roughly tripled since launch on the DRAM shortage — unacknowledged in a one-appliance-per-home product |
| 6 | **Low** | Python 3.13 is a full generation behind and will be two behind before v1 ships |
| 7 | **Low** | The Anthropic constraint is true but stated with a scope that will read as false in six months |
| 8 | **Low** | `[ASSUMPTION]` tagging is inverted — the least verifiable rows are the untagged ones |

**Verified correct, no action:** the no-STT/TTS constraint, `claude-sonnet-5`,
`claude-opus-5`, FastAPI 0.141.1, asyncpg 0.31.0, Next.js 16.3.4, Raspberry Pi 5 as
current hardware, openWakeWord as maintained, ElevenLabs as a live TTS vendor.

---

## Confirmed correct

These were checked and hold. Recording them so a later reader does not re-litigate.

### The load-bearing Anthropic claim is TRUE

> "Anthropic ships no speech-to-text or text-to-speech API, so voice is necessarily a
> three-stage pipeline rather than speech-to-speech."

Verified two independent ways against `platform.claude.com`:

1. **The complete endpoint list** (API overview) is Messages, Message Batches, Token
   Counting, Models, Files, Skills, plus beta Agents, Sessions, and Environments. There
   is no audio, transcription, speech, or voice endpoint of any kind.
2. **The modality line** in the models overview: *"All current models support text and
   image input, text output, multilingual capabilities, vision, and tool use."* Audio is
   not an input modality and not an output modality on any current model.

The constraint holds, and the three-stage STT → LLM → TTS conclusion follows correctly
from it. This is the strongest-supported claim in the section.

One corroborating detail the spine does not use but should: Anthropic's own consumer
voice mode reportedly uses ElevenLabs as a TTS subcontractor (listed in its terms of
service — secondary source). If Anthropic itself runs a three-stage pipeline against a
third-party TTS vendor, the architecture here is not working around a gap, it is matching
the reference implementation. That is a stronger argument than "verified constraint" and
it is free.

### Anthropic model IDs are correct and current

Both IDs verified against the live model table:

| Spine says | Status |
|---|---|
| `claude-sonnet-5` | Correct. Current, 1M context, $2/$10 per MTok, retirement not sooner than 2027-06-30 |
| `claude-opus-5` | Correct. Current, 1M context, $5/$25 per MTok, retirement not sooner than 2027-07-24 |

Both are dateless pinned snapshots — the correct form. No date suffix should be appended.
Neither is deprecated. See finding 6 for what is *missing* from the model reasoning.

### Package versions that are exactly right

| Name | Spine | Live (verified today) | |
|---|---|---|---|
| FastAPI | 0.141.1 | 0.141.1 (PyPI) | exact |
| asyncpg | 0.31.0 | 0.31.0 (PyPI) | exact |
| Next.js | 16.3.4 | 16.3.4 (npm `latest`) | exact |

Patch-exact matches on three independent registries are not something a training prior
produces. These rows were looked up. That is precisely what makes finding 4 diagnostic
rather than trivial.

### Hardware and on-device stack

- **Raspberry Pi 5** is the current flagship. Raspberry Pi 6 is not expected before 2028
  at the earliest (Upton, via secondary sources); there is no newer board to have missed.
  The 8GB SKU remains available alongside a 16GB SKU. Capability choice is sound —
  see finding 5 for the cost problem.
- **openWakeWord** (`dscripka/openWakeWord`) is alive and actively maintained, and remains
  the standard open-source choice in this space. It fits AD-5's stated role. Viable
  alternatives if it ever stalls: Picovoice Porcupine (commercial), LiveKit Wakeword
  (openWakeWord-derived, better training pipeline), ViolaWake (Apache 2.0). No action.
- **ElevenLabs** is current and shipping. Latest models are Eleven v3 and Eleven v3
  Conversational (70+ languages, public API available), alongside `eleven_flash_v2_5` and
  `eleven_multilingual_v2`. The role fits. Given AD-8's requirement that the senior hear
  Composer-produced text, `eleven_flash_v2_5` is likely the relevant model for latency,
  and v3's inline audio tags are a tone lever the Composer could drive — neither is
  decided here and neither needs to be, but the row should not simply say "ElevenLabs."

---

## Finding 1 — CRITICAL

### Deepgram Nova-3 Multilingual cannot transcribe three of Singapore's four official languages

The Stack table commits `Deepgram Nova-3 Multilingual` to the STT role. The model exists,
is current, and got a real accuracy update in February 2026 with the largest gains
specifically in code-switching. So far the row survives.

It does not survive the language set. Nova-3's multilingual code-switching mode (`multi`)
covers exactly ten languages:

> English, Spanish, French, German, Hindi, Russian, Portuguese, Japanese, Italian, Dutch

Singapore's four official languages are English, **Mandarin Chinese**, **Malay**, and
**Tamil**. Three of the four are absent. The elderly Singaporean speech this product is
built to listen to also routinely includes Hokkien, Teochew, Cantonese, and Singlish —
none of which appear either. The one adjacent language Deepgram has added is Indonesian,
which shares roots with Malay but is not Malay and is not what a Singaporean senior speaks.

Nova-3 supports 36+ languages in **monolingual** mode, and the February 2026 expansion
added Southeast Asian languages there. But monolingual mode is the wrong capability: this
product's defining input is code-switched conversational speech from one speaker, which is
the `multi` mode, which is the ten-language list.

**Why this is critical rather than a vendor detail.** The spine defers "Language and
dialect coverage" as an open question and notes it "drives the vendor choice above." That
sequencing is backwards for a commitment already written into the Stack table and into the
source tree (`adapters/deepgram/`). The deferred question does not merely *inform* the
Deepgram row — for the most likely answers it *eliminates* it. A senior speaking Mandarin
and English in the same sentence, which is the modal case, produces either garbage or
silence, and under AD-1 that silence is written into an append-only, evidentiary record.
Worse, under AD-6 the system correctly distinguishes a dead unit from a withdrawn senior —
but nothing distinguishes a *live unit whose STT cannot hear this senior's language* from a
senior who has genuinely gone quiet. That is exactly the phantom-decline failure AD-6
exists to prevent, arriving through a door AD-6 does not cover.

**What to do.** Three options, in order of my preference:

1. Demote the Deepgram row from a named model to `[ASSUMPTION] STT vendor — TBD by
   bake-off`, and move the language-coverage question from Deferred into a blocking
   prerequisite for the bake-off. The port under AD-12 already makes this cheap; the spine
   should stop naming a specific model it has not language-checked.
2. Keep Deepgram but name the actual candidate configuration, which is not Nova-3
   Multilingual — see finding 2 on `flux-general-multi`, and check its language set before
   committing.
3. If MERaLiON's Southeast Asian coverage is the real reason it "should win the bake-off,"
   say that explicitly. Right now the spine gives an aesthetic reason ("built for
   Singapore's multilingual and code-switched speech") where it has a decisive technical
   one, and the decisive one is invisible to a reader who does not check Nova-3's language
   table.

Add a test to the bake-off criteria that is not about accuracy: *does the candidate
transcribe Mandarin-English and Malay-English code-switching at all.* That is a pass/fail
gate before word error rate is even interesting.

---

## Finding 2 — HIGH

### Deepgram Flux is missing from the frame, and its turn detection touches AD-5

Deepgram's current model lineup, per their own documentation, positions **Flux** as *"the
first conversational speech recognition model built specifically for voice agents,"* with
integrated turn detection and ultra-low latency. Deepgram's guidance is explicit about the
split: Flux for real-time voice agents, Nova-3 for batch and streaming transcription of
meetings, captioning, and general multilingual work.

This product is a real-time voice agent. The spine picked the model from the other column.

Two consequences, and the second matters more:

1. **Latency and turn-taking.** A senior in conversation with an appliance is a
   turn-taking workload, which is what Flux was built for and what Nova-3 was not.
2. **Flux's integrated turn detection overlaps AD-5.** AD-5 states that wake and address
   detection run entirely in the Capture context, and that a turn failing address detection
   produces *no network call of any kind, including telemetry*. Flux performs turn
   detection **as part of cloud transcription** — which means audio has already left the
   home before the turn boundary is known. Adopting Flux naively would put the product in
   direct violation of AD-5 and, through it, AD-2. This is not a reason to reject Flux; it
   is a reason the spine must say which half of turn handling is on-device. Right now the
   Stack table names an STT vendor and AD-5 names a boundary, and nothing in the document
   notices that the leading candidate in that category ships a feature that crosses it.

Note also that Flux has a multilingual variant (`flux-general-multi`) that also does
code-switching. Whether its language set fixes finding 1 is unverified and should be
checked before either model is committed.

**What to do.** Add one sentence to the paragraph under the Stack table naming Flux and
stating that any candidate's server-side turn detection is subordinate to AD-5 —
on-device address determination is not negotiable, and a vendor turn-detection feature may
only refine a turn that has already passed the on-device gate. That sentence costs nothing
now and prevents a genuinely expensive discovery during the bake-off.

---

## Finding 3 — HIGH

### MERaLiON availability is asserted in the present tense on roadmap evidence

The spine states:

> MERaLiON-AudioLLM (I2R / A\*STAR) ... **now offered via cloud API and edge deployment**,
> is the standing alternative to Deepgram and should win the bake-off if it holds up.

What is actually published reads as announcement, not availability. A\*STAR and Singapore
EDB material describes MERaLiON AudioLLM v3 as something that **"will"** deliver
paralinguistic intelligence across Southeast Asian languages and **"would be available"**
through cloud hosting, API access, and edge computing including Apple silicon. `meralion.ai`
surfaces a try-it interface at `studio.meralion.ai` and ATxSG 2026 update material, but I
could not confirm a generally-available commercial API endpoint, pricing, SLA, or terms
covering health-adjacent data. The model weights are genuinely public on Hugging Face
(`MERaLiON/MERaLiON-AudioLLM-Whisper-SEA-LION`) and the research is real and strong — the
research is not in question, the *procurement* is.

This is the highest-consequence unverified claim in the document, because of how the spine
loads it: MERaLiON is the candidate that "should win the bake-off," and finding 1 removes
its only named competitor from contention for the actual language requirement. The
architecture is therefore leaning on a vendor whose commercial availability is
unconfirmed, while tagging its *fallback* with `[ASSUMPTION]` and this one with nothing.

**What to do.** Soften to what is checkable — self-hostable open weights (confirmed) plus
an announced cloud API (not yet confirmed GA) — and tag the row `[ASSUMPTION]` like its
peers. Then add to Deferred: *confirm MERaLiON commercial API availability, pricing, and
data-handling terms.* If the answer is "weights only, self-hosted," that is still a
perfectly good answer and arguably a better one under AD-2 — but it is a materially
different deployment, and the deployment diagram's `STT` box currently implies a vendor
call the spine has not confirmed can be bought.

---

## Finding 4 — MEDIUM

### Three of seven pinned versions are stale under a blanket "verified current" header

The section header reads *"Seed — verified current 2026-09-08."* Checked against live
registries today:

| Name | Spine pins | Actually current | Drift |
|---|---|---|---|
| Python | 3.13 | 3.14.7 (3.14 line since 2025-10-07) | one generation — see finding 6 |
| FastAPI | 0.141.1 | 0.141.1 | correct |
| SQLAlchemy | 2.0.44 | **2.0.52** | 8 patch releases behind |
| Alembic | 1.17.1 | **1.19.2** | two minor lines behind |
| asyncpg | 0.31.0 | 0.31.0 | correct |
| PostgreSQL | 18.3 | **18.6** (released 2026-08-11) | ~2 quarterly patch rounds behind |
| Next.js | 16.3.4 | 16.3.4 | correct |

Sources: PyPI JSON endpoints for the Python packages, npm registry for Next.js,
endoflife.date for Python and PostgreSQL cycles.

None of these breaks anything — they are all same-major, and `pip install` would surface
the drift on day one. The severity is not in the drift, it is in the **pattern**:
three rows are exact to the patch and three are not. Patch-exact agreement across three
separate registries is not something recall produces; ~8-patch and 2-minor lags are
exactly what recall produces. So some rows were verified on 2026-09-08 and some were
filled in around them, and the header asserts one provenance for all seven.

The PostgreSQL row deserves a specific note: quarterly PostgreSQL minors carry security
fixes, and pinning 18.3 in a document that will be read as authoritative by whoever writes
the Dockerfile means shipping a database two security rounds behind on a system holding
health-adjacent longitudinal data about vulnerable adults. The deployment diagram's
`PostgreSQL 18` is correct and sufficient; it is the table's `.3` that is wrong. Consider
dropping to the major line in the table too, since the spine's own note says the code owns
this once it exists.

**What to do.** Correct the three rows, then either drop the "verified current" header
(the code owns it anyway) or add per-row provenance so a later reader knows which
assertions were checked. As written, the header makes the three correct rows look as
unreliable as the three wrong ones.

---

## Finding 5 — MEDIUM

### Raspberry Pi 5 unit economics have moved sharply, and the spine treats the row as a capability question only

The hardware row is `Raspberry Pi 5, 8GB + far-field USB mic array [ASSUMPTION]`. The
`[ASSUMPTION]` tag is doing capability work — will it run openWakeWord and capture — and
that assumption is fine. The Pi 5 is current, well-supported, and has the headroom.

What has changed, per secondary sources (Tom's Hardware, April 2026 Raspberry Pi product
updates), is price. The 16GB Pi 5 has gone from $120 at launch to $205 in early 2026 to
roughly $305 now, driven by roughly 7x LPDDR4 cost increases as AI infrastructure buildout
consumed DRAM supply. The 8GB SKU is exposed to the same shortage. I did not find a
confirmed current 8GB list price and am not asserting one — but a board whose top SKU
tripled is not a board whose mid SKU held flat.

This matters here more than it would elsewhere because the deployment unit is *one
appliance per senior's flat*. Per-unit cost is not a line item, it is the scaling
function. It also interacts with two Deferred entries — "cellular vs wifi, and the
connectivity bill of materials" and "device provisioning, fleet update, and physical
install" — which together constitute the BOM the spine has decided it can wait on. That
deferral was reasonable when the compute was $80; it is a different decision when the
compute is a multiple of that and moving.

This is the clearest case in the document of a row that a reality check catches and a
training prior does not: nothing about "Raspberry Pi 5, 8GB" is *wrong*, and the entire
finding lives in a market condition that postdates any static knowledge of the part.

**What to do.** Nothing architectural — AD-2 and AD-5 hold on any capable board. Add one
line to the Deferred entry on the bill of materials noting that Pi 5 pricing is currently
volatile and that the BOM decision has a shorter useful shelf life than the rest of the
spine. If the demo slice is near-term, price the actual 8GB SKU this week rather than at
build time.

---

## Finding 6 — LOW

### Python 3.13 is a generation behind, and the model-tier reasoning is thinner than it looks

**Python.** Python 3.14 shipped 2025-10-07 and is at 3.14.7 (2026-08-05); 3.15 is due
around October 2026. Python 3.13 is supported until 2029-10-31, so this is a defensible
conservative pin — but it is not "current," which is what the section header claims, and a
greenfield project starting today on 3.13 will be two generations behind before v1 ships.
Either move to 3.14 or state the conservatism deliberately ("3.13 for ecosystem maturity
on asyncpg/SQLAlchemy") so the choice reads as made rather than defaulted.

**Model tiers.** Both named IDs are correct, and Sonnet 5 for per-turn handling / Opus 5
for weekly composition is a sensible split on latency and cost. Two things the current
lineup offers that the spine does not appear to have considered:

- **Claude Haiku 4.5** (`claude-haiku-4-5`, $1/$5 per MTok, fastest) is the natural
  candidate for per-turn handling. Turn handling here is high-volume, latency-critical,
  and — crucially — *not* where judgement lives, because AD-12 puts every rule in
  deterministic code and AD-8 puts every human-facing string through the Composer. The
  spine has already engineered away the reasons to pay Sonnet prices on the turn path.
- **Claude Fable 5.1** (`claude-fable-5-1`) is now Anthropic's most capable model. Weekly
  composition is low-volume, latency-insensitive, and quality-critical — the exact profile
  where the top tier is affordable. Whether it beats Opus 5 at higher effort is an
  empirical question, but it is not asked.

Also unremarked: Sonnet 5's reliable knowledge cutoff is January 2026 versus Opus 5's May
2026. Immaterial here, since the Composer works from the observation log rather than world
knowledge — but the spine does not say it noticed.

**What to do.** Nothing blocking. Add a clause stating that model tier per role is a cost
and latency decision the Composer's rule enforcement makes safe, and that the specific
tiers are revisitable behind AD-12's port. That converts two bare IDs into a decision.

---

## Finding 7 — LOW

### The Anthropic claim is true but scoped in a way that will read as false

The sentence says *"Anthropic ships no speech-to-text or text-to-speech API."* Verified
true of the Claude API. But Anthropic ships voice *features* across its products: Claude
voice mode on web, iOS, and Android; dictation in the Claude iOS app since 2025; `/voice`
in Claude Code from March 2026; multilingual voice input out of beta in June 2026 across
18 languages.

A reader six months from now who knows "Claude has voice" will read this sentence, see an
obvious contradiction, and lose confidence in a claim that is in fact correct and
correctly reasoned. The distinction is product surface versus API surface, and the
sentence does not draw it.

**What to do.** Name what was checked, in one clause: *the Claude API surface — Messages,
Batches, Token Counting, Models, Files, Skills, plus beta Agents/Sessions/Environments —
exposes no audio endpoint, and all current models are text-and-image in, text out.
Anthropic's consumer voice features are product-layer and not available as an API.* Same
claim, now unfalsifiable by a casual objection, and it shows its work.

---

## Finding 8 — LOW

### `[ASSUMPTION]` tagging is inverted

Tagged: Deepgram, ElevenLabs, the Pi. Untagged: MERaLiON, the Anthropic model selection,
and every version pin.

Deepgram and ElevenLabs are the two rows I could verify most completely — both vendors
publish current model documentation, language tables, and pricing. MERaLiON is the row I
could verify least (finding 3). The tags mark the confident rows as uncertain and leave
the uncertain row bare. Whatever the tags meant when written, a reader will take them as
confidence signals and will be misled in the direction that matters.

**What to do.** Either tag MERaLiON to match its peers, or replace the binary tag with a
provenance column — `verified 2026-09-08 / announced, not confirmed / to be decided by
bake-off`. The Stack table is seven rows; a third column is cheap and it is the difference
between a table that records decisions and one that records lookups.

---

## What holds

The architecture does not depend on any of this being right, and that is the section's
real strength. AD-12 puts the LLM behind a port; the STT and TTS ports sit beside it; the
Deferred section already says vendor selection is a bake-off outcome rather than a spec-sheet
one. Finding 1 is severe as a *fact* and cheap as a *change* precisely because the spine
was built to absorb it — swapping `adapters/deepgram/` costs an adapter, not a redesign.

The invariants were not reviewed here and are not implicated. The three-stage pipeline
conclusion is correct and correctly derived. What needs work is the Stack table's claim to
have been verified, which is true of four rows and not of three, and the language question
in finding 1, which is not a version problem at all but a fit problem that a version check
happened to surface.

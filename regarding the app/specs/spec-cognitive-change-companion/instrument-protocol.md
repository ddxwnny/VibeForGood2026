# Instrument protocol

Governs CAP-3. Structured instrument items are kept because they are normed and defensible, and delivered by voice because voice is their original form — MoCA, MMSE and ACE-III items were administered aloud by a human long before they were printed on a clipboard. Conversation is not a workaround for the instrument; it is the instrument's native channel.

## Item sources

Draw items from the established batteries (MoCA, MMSE, ACE-III) across their domains: delayed recall, orientation, naming, attention, language, abstraction, visuospatial-by-description. Do not administer any battery whole, in order, or under its own name. Scoring an assembled battery would constitute screening, which v1 does not do — v1 records the response, not a total.

## Rotation

- Every item type has an **item bank** of interchangeable variants (different word lists, different naming targets, different attention sequences).
- An item is never re-administered inside its **refractory window**. Set per item type, minimum 90 days for recall items, which are the most practice-sensitive.
- Bank selection is pseudo-random with exclusion, not round-robin: a predictable cycle is learnable.
- Bank exhaustion is a build-blocking condition. If a senior's window makes every variant ineligible, the item is skipped and the omission recorded — never a repeat.

## Spacing

- Items are distributed across ordinary interactions, never clustered into a session that would read as a test.
- Ceiling on instrument turns per week per senior, set low enough that instrument content stays a minority of interaction.
- No item is administered in the same interaction as a task the senior initiated under time pressure or distress.

## Delivery rules

- Items arrive inside conversational context, not as a stated question set. No announcement, no framing as a check, no score read back.
- The senior is never told she passed, failed, or scored.
- If she asks whether she is being tested, she is told the truth plainly — the disclosure discipline in `communication-rules.md` governs the wording.
- A refused or deflected item is recorded as declined, never re-pressed in that interaction.

## What is recorded

Per administration: item type, bank variant identifier, date, the response, and whether it was completed, partial, declined, or interrupted. **No total, no score, no normed comparison** — those belong to the screening layer.

## Why practice effects are load-bearing

Repeated administration inflates responses. The resulting error direction is false reassurance: the record looks unchanged while function declines behind it. That is the worst failure this design can produce, and it is the default behaviour of any naive implementation, which is why rotation and spacing are constraints rather than recommendations.

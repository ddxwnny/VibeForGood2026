# Consent and data governance

Governs CAP-7 and CAP-9, and the consent artefacts the later screening layer will execute against.

## The Ulysses contract

Consent to disclosure is taken **at onboarding, while she is clearly able** — not at the moment something is noticed. Asking permission at flag time asks the exact faculty being measured: loss of insight is a symptom of the thing being detected, so a consent-at-the-moment model fails hardest on the target population. The model mirrors Advance Care Planning and Lasting Power of Attorney logic that Singapore already trusts.

At onboarding she states, in her own voice:

1. **Who gets told** — the named recipient or recipients.
2. **Whether she is told first**, told together, or not told at the moment of disclosure.

Recorded as audio, not asserted on her behalf. The named recipient is **physically present and co-signs** at that visit. At disclosure time the system executes the standing instruction. There is no veto at that point — that is the whole point of taking it early.

## Research and validation consent

Taken in the **same sitting**, as a separate act. Non-negotiable and non-deferrable: collecting a corpus under an "observation" purpose and later using it to validate a medical screening claim risks a legally unusable dataset, and the discovery would come at the worst possible moment. It cannot be retrofitted across an already-enrolled senior cohort.

## Named processors

She consents to a named set of parties, never to a category. Every external service that touches her data — speech-to-text, text-to-speech, the language model — is named to her in the enrolment script, recorded in her enrolment, contracted for zero retention and no training use, and listed in the erasure path so deletion is enumerable rather than remembered. Adding a processor later is a consent change requiring re-consent, not a deployment change.

The community care organisation is the controller. Every named processor is an intermediary. Any cross-border transfer of her data needs a PDPA Transfer Limitation basis recorded against that processor.

## Enrolment completeness

An enrolment is not active until all four exist and are timestamped to the same visit:

- Own-voice Ulysses instruction
- Named recipient's physical co-signature
- Research/validation consent
- Processor disclosure, acknowledged

Partial enrolments do not collect data.

## Data lifecycle

- **Raw audio** is discarded once features are extracted. Define the extraction-to-discard window explicitly; it is the shortest interval the pipeline can support.
- **Extracted features and the functional series** are retained long enough to compute both days-long and months-long windows (see `signal-catalog.md`), under a stated retention period.
- **Access** is scoped: the care worker who enrolled her, the named recipient (weekly window only), and named research access under the research consent. Every access is logged.
- **Withdrawal** executes on request: collection stops, and her data is removed or de-identified according to what she consented to at enrolment. Which of the two is her choice, recorded at enrolment.
- **Death** has a defined path recorded at enrolment, covering both the functional series and the consent audio.

## Continuous disclosure

She hears weekly what her family sees (CAP-6). There is no reveal because there is no secret. This is what makes the Ulysses contract defensible against "I never agreed to this": the consent is in her own voice, played back rather than asserted, and the disclosure has been running all along.

## Regulatory posture

v1 collects observations and makes no claim. Do not call the output a biomarker — that word is itself an intended-purpose statement and raises regulatory weight for no gain. Prefer "functional observations over time". Strict biological biomarkers are out of scope entirely.

Open, not answered here: Singapore PDPA obligations for this data class, and the HSA device classification the screening layer will fall under.

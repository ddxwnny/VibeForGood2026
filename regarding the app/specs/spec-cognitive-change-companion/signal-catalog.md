# Signal catalog

The observable changes the functional series must be able to carry. v1 **records** these; it does not score, threshold, or classify them. Every entry below defines what the record must be able to represent, so that the later screening layer has something to read.

## Everyday-functioning signals

| Signal | What an observation looks like | Captured from |
|---|---|---|
| Memory | Repeating a question within a session or across days; asking again about something already handled; increasing reliance on the device for things she previously held herself | Task interactions, conversation turns |
| Date and time | Losing track of the date, day, month, season, or how long since an event | Instrument items, appointment handling |
| Language | Word-finding pauses, losing the thread of a conversation, substituting an unusual word for a familiar object | Conversation turns |
| Misplacing objects | Reporting things put somewhere unusual; being unable to retrace steps | Conversation turns |
| Judgement | Unusual financial decisions, reports of scam approaches, out-of-pattern choices | Conversation turns, mail handling |
| Finances | Growing difficulty with bills and money previously managed without help | Mail and letter handling |
| Daily tasks and routines | Falling off a familiar recipe, routine, or route; tasks previously completed now incomplete | Task completion series |
| Attention | Difficulty following multi-step instructions or sustaining a thread | Task interactions, instrument items |
| Social and behavioural | Withdrawal, apathy, marked mood or personality change | Conversation turns, human-contact counter-metric |
| Medication | Doses missed, doubled, or newly confused | Task completion series |

Task completion carries the primary signal weight: it has no practice effect, and IADL decline is already a recognised clinical signal.

## Confounds the record must be able to separate

An observation of decline is uninterpretable without these. v1 must capture enough to let a later reader rule them in or out.

- Acute illness, especially UTI and dehydration
- New or changed medication
- Poor sleep
- Bereavement or major life event
- Hearing loss
- Late-life depression (pseudodementia)
- Education and language background
- Device unreachable (see CAP-8 — never an observation about her)

## Two-speed routing — v2, recorded for shape only

The screening layer routes by the **shape** of a change, not its size. v1 does not implement this routing; it exists here so the series is captured at a resolution that makes it possible later.

- **Sharp drop over days** → possible delirium. Urgent, commonly reversible, and for someone living alone nobody is there to notice. Tuned for sensitivity: a false positive reads as "check for an infection", which is cheap and non-stigmatising.
- **Slow drift over months** → the dementia pathway. Tuned for specificity, with low-stakes wording, to the care worker only.
- **Drop alongside mood, sleep or appetite change** → the depression pathway.

The consequence for v1: the series must be dated at day resolution and retained long enough that both a days-long and a months-long window are computable from it.

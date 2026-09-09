---
name: Recollect
status: draft
updated: 2026-09-09
sources:
  - SOURCE.md
---

## Foundation

iPhone-only application, packaged with Capacitor in a native Xcode project. Portrait orientation and light appearance. Native HTML controls inside the bundled WKWebView; no separate desktop product layout. [DESIGN.md](DESIGN.md) defines visual identity. These documents describe the intended experience and explicitly distinguish current prototype limits. When finalized, the document contracts take precedence over illustrative screens.

The [interactive prototype](../../frontend/index.html) can run from bundled assets inside the iPhone app; the local Node server is only needed for browser preview. All profiles and metrics are fictional. Account access, pairing, speech capture and AI replies are simulated. The prototype keeps state in memory for one app session; app restart or WebView reload resets it. No browser microphone permission is requested, no email is sent, no clinical calculation runs, and no cross-device synchronization occurs.

## Information Architecture

| Surface / hash | Entry | Purpose / journey |
|---|---|---|
| Welcome / #welcome | Initial visit or brand | Choose caregiver or conversation; Mei and Arun journeys. |
| Account / #auth | Supporting someone | Signup/login preview; Mei onboarding. |
| Recovery / #reset | Login recovery link | Explain recovery behavior and return to login. |
| Family / #family | Successful account preview | Find each adult; Mei reviews multiple relatives. |
| Invitation / #invite | Link someone | Name recipient, generate invitation, copy or regenerate it. |
| Code entry / #connect | Conversation role or phone preview | Validate six digits before consent. |
| Consent / #consent | Valid invitation | Check caregiver identity and agree to sharing. |
| Overview / #dashboard | Family card or navigation | View selected adult's activity, example changes and next steps. |
| Observations / #observations | Overview or navigation | Add/edit/remove family reports for selected adult. |
| Conversation / #chat | Consent or returning role | Speak-preview or type, see scripted replies, finish. |
| Connection / #connection | Conversation link | Review and revoke link. |
| Completion / #finish | Finish conversation | End clearly and return later or restart. |

All surfaces are represented in the clickable prototype. Password-reset email delivery is explanatory only. Production loading, server failures and microphone permission states are specified below but not live integrations.

## Voice and Tone

Use “loved one” or the person's name in caregiver copy. Address older adults directly, never as dependents. Prefer “An update to explore” and “Information available: limited” to diagnostic certainty. Distinguish family-reported information, conversation-derived observations, and prewritten demo recommendations. Do not imply that absent data or unflagged results establish good health.

## Component Patterns

| Component | Behavior |
|---|---|
| Primary/secondary button | One primary action per task area; explicit secondary exit. |
| Card | Family card's explicit overview action sets the adult before navigation. |
| Navigation | URLs support Back/Forward; active page labelled; focus moves to main content after route changes. |
| Profile selector | Selects dashboard/form context. Unsaved observations require a discard decision before switching. |
| Form field | Native validation; persistent labels. Code accepts paste and numeric keyboard. |
| Concern checkbox | Multiple selections; unchecked means unreported, not absence. Add date, frequency and optional example; save explicitly. |
| Attention label | Descriptive text without a diagnosis or percentage. |
| Activity chart | Counts sessions; accessible textual equivalent; never represented as cognitive score. |
| Invitation code | Separate invitation per new adult; ten-minute demo expiry, regenerate invalidates old code. New invitations consumed at acceptance. Fixed 123456 is a reusable fictional preview shortcut, not a security mechanism. |
| Conversation bubble | Speaker label; typed text inserted safely; scripted reply announced. |
| Microphone | First tap begins simulated listening; second tap stops and inserts a clearly fictional sample transcript. Real capture is not implemented. |
| Demo notice | Always visible on page; contextual detail explains account and speech simulation. |

## State Patterns

| Area | Current prototype | Production requirement |
|---|---|---|
| Account | Signup/login forms and validation; no real authentication. | Pending submit, generic credential errors, rate limiting and real recovery. |
| Family | Two seeded profiles; newly linked profiles have no data. | No-family empty state, retry on load error, last successful refresh and connection state. |
| Invitation | Pending, wrong code, expired code, regenerated code, consent acceptance, clipboard failure fallback. | Server-issued unguessable authorization, attempt limits, consumed/revoked code enforcement and authenticated caregiver ownership. |
| Consent | Sharing explanation, unchecked agreement, decline back to code entry. | Review approved sharing scope and retention; bind device only after explicit consent. |
| Overview | Separate seeded datasets and honest no-data state for new links. | Loading, partial data, stale/offline data and source provenance; no reassurance from unavailable data. |
| Observations | Saved, unsaved, edit, clear confirmation; separate per adult. | Durable storage, save failure without dropping inputs, attribution and modification history. |
| Conversation | Idle, simulated listening, transcript, scripted response and completion; typing available. | Explicit microphone consent, listening/stop/cancel, editable transcription, denied/unsupported/no-speech states, interrupted connection and AI service failure. |
| Connection | Review/disconnect in session. | Revocation on both devices; lost-device and caregiver recovery flow. |
| Offline/reload | No remote calls or durable state; reload resets demo. | Explicit offline status and storage policy; never claim a caregiver update was shared before acknowledgment. |

## Interaction Primitives

Use tap/click and native keyboard controls. Do not depend on dragging, hover, auto-advancing carousels or timed answers. All state changes need readable feedback. Unsaved observation changes prompt before navigation, profile changes or reload. Microphone simulation stops on leaving the conversation.

## Accessibility Floor

Body uses {typography.body.fontSize}; older-adult copy uses {typography.older-adult-body.fontSize}. Primary targets are 52px minimum, 56px in the older-adult flow; back and navigation targets are at least 44px; microphone 88px. Provide skip link, visible focus, ordered headings, semantic forms, labelled controls, status announcements and chart descriptions. Support wrapping, zoom and reduced motion. No mandatory audio; typing is available. Production testing must include keyboard, VoiceOver/TalkBack, zoom, hearing and speech differences. Do not claim completed accessibility certification from this prototype.

## Key Flows

### Mei connects a new relative

1. Mei chooses the caregiver role and previews caregiver signup.
2. She sees Arun and Lily, fictional seeded profiles, in her family list.
3. She chooses Link someone and creates an invitation for Sam.
4. Sam opens the code-entry flow, enters the invitation and sees Mei's name and sharing explanation.
5. Sam actively agrees to connect.
6. **Climax:** Sam enters a welcoming conversation; Mei can find a separate Sam card with an honest no-data overview.

Failure: wrong code retains the form and explains retry; expired code requires a replacement; declined consent creates no link. The demo requires previewing both roles in the same page session.

### Mei catches up with Arun and Lily

1. Mei opens Arun's card and reads the simulated summary.
2. She sees session counts, illustrative transcript markers and the source of the next-step suggestion.
3. She opens observations and selects something she has noticed, adding an example and frequency.
4. She saves, returns to overview, and sees the family report separately.
5. She switches to Lily.
6. **Climax:** Lily's distinct overview appears without Arun's concerns, preserving context and trust.

Failure: unsaved entries prompt before leaving or switching. A new adult's empty overview explains that no data is available.

### Arun has a conversation

1. Arun enters the demo invitation and confirms connection with Mei.
2. Recollect greets him by name and offers an open-ended prompt.
3. He previews speaking, stops explicitly and sees a sample transcript, or types a fictional reply.
4. Recollect responds with a labelled scripted message.
5. **Climax:** Arun ends the conversation and sees a calm completion message without a score or performance judgment.

Failure: real speech recognition is absent; the interface says so and always offers typing. Later visits to the role screen within this session can return to the conversation without a password; reload persistence is deferred.

### Arun changes his mind about sharing

1. From conversation, Arun opens Your connection.
2. He reviews the link with Mei and chooses Disconnect.
3. He confirms the decision.
4. **Climax:** The active demo connection is removed and the code-entry screen returns.

Production must also revoke caregiver access; the demo does not have a real authorization backend.

### Mei needs account recovery

1. Mei switches to login and opens Forgot password.
2. She sees the intended email-recovery behavior and an explicit no-email demo notice.
3. **Climax:** She can return to the account preview without believing an email was sent.

## Responsive & Platform

Caregiver navigation is a fixed bottom tab bar: Family, Overview and Notes. The active adult persists across Overview and Notes. Welcome and onboarding use full-screen phone layouts with compact back navigation; no tabs until caregiver access. Older adults have no caregiver tabs. All content respects the iPhone safe areas and portrait orientation; cards stack and metrics use two columns. Browser preview is capped at 480px. Scrolling keeps content clear of the bottom tab bar. Conversation controls are in document flow so enlarged text and the keyboard cannot be trapped behind a fixed composer. Use device capabilities only after permission in the eventual implementation.

## Inspiration & Anti-patterns

The user's Figma image establishes role selection, caregiver credentials, six-digit invitation, recipient entry, voice conversation, checklist and overview. Preserve that short sequence; extend it with multi-person navigation, explicit sharing consent and recoverable states. Avoid hidden score changes, diagnosis gauges and recording indicators for inactive microphones.

## Health interpretation and release boundary

Hackathon content is fictional. Observation counts and next steps are prewritten examples, not clinical instruments. Caregiver concerns may inform future follow-up topics; any weighting, dementia screening claims, thresholds and recommendations need separately validated clinical design before real health monitoring. Browser authentication, device authorization, secure storage, consent/retention, clinician review and live AI integrations are outside this UI prototype.

## Open items

Non-blocking draft assumptions: English-first iPhone app; one caregiver per demo connection; no actual voice recording or read-aloud; simulated in-memory data; no production risk algorithm. Resolve language needs, shared-caregiver permissions, clinical measures, transcript sharing/retention and durable device linking before live implementation. Optional UX reviewer validation has not been run. BMad workflow logging/finalization remains unavailable as documented in SOURCE.md.

## iPhone packaging and validation

`ios/App/App.xcodeproj` is the native app project. `npm run ios:sync` copies the current frontend into the app bundle; it does not run the Node server on the phone. Bundle ID `com.recollect.demo` is a development placeholder. The project targets iPhone only, iOS 15+, portrait and light appearance. Real-device signing is configured in Xcode. No Android target is included. Browser/mobile checks are separate from native verification: the current Mac could not run the simulator build because its Xcode installation is missing DVTDownloads.framework. Native compilation, safe-area behavior and keyboard interaction still need verification after Xcode setup is repaired.

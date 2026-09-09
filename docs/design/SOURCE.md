# Recollect design intake

Source: user instructions and attached seven-screen Figma wireframe in this conversation, 8–9 September 2026. The image is a conversation attachment; no local image copy or Figma URL was available.

Confirmed: two audiences, caregiver and older adult; caregiver login/signup; invitations linking older adults without their own login; each adult uses their own phone; one caregiver can link multiple adults; individual dashboards and recommendations; family concern checkboxes and optional notes; voice-to-text conversations with AI. Hackathon uses fictional personas and simulated results. Longer-term intent is health monitoring. User invited design suggestions and requested UI/UX creation based on the resulting plan.

Reference screens: role selection, caregiver credentials, code generation, older-adult code entry, AI conversation, caregiver checklist, caregiver overview.

Proposed additions: family list, connection consent and revocation, expiry/retry states, profile selector, typed alternative, conversation completion, and source-labelled observations.

The proposed warm cream/teal design is not a separately approved brand system. Personas Mei, Arun and Lily are fictional. Layouts are implemented in ../../frontend/ as an interactive prototype.

Workflow limitation: BMad project scripts (including memlog.py) and project config are absent. uv exists at /Users/dawn/.local/bin/uv but is not on the tool session PATH. These draft design documents are a reviewable handoff, not a completed/logged BMad finalization. No canonical .memlog.md has been hand-created. Optional reviewer gate remains available.

## Mobile direction, 9 September 2026

User requested a phone application instead of a web application, and selected **iPhone only**. This supersedes the earlier responsive-web/desktop direction. Implemented an iPhone-oriented interface, Capacitor iOS packaging, bundled assets, bottom caregiver tabs, compact back headers, safe-area spacing and mobile onboarding. The prototype remains simulated; this request does not make health assessment, credentials or cross-device linking live. App icon source: [app-icon.svg](app-icon.svg).

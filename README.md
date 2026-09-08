# Recollect

Author: NgYanHerng

A responsive UI/UX prototype for family connection and everyday conversations.
Built with plain HTML, CSS and JavaScript, served by a dependency-free Node.js backend.

## Run locally

Use Node.js 22 or newer. From this directory:

```bash
npm run dev
```

Open http://127.0.0.1:3000. No dependency installation or frontend build is needed.
Refresh the browser after frontend edits; the backend restarts when its files change.
Stop with Ctrl+C. Use `PORT=3001 npm run dev` to change ports.

## Explore the demo

1. Choose **I'm supporting someone**. The signup/login preview has fictional credentials prefilled; accept the demo acknowledgment and continue.
2. Open Arun or Lily from **Your family**. Use the profile selector to compare their separate dashboards.
3. Open **Observations**, select concerns and optionally enter fictional notes. Save to see the selected concerns in that person's overview.
4. Choose **Link someone**, enter a fictional first name and generate a code. Choose **Preview loved one's phone**, enter the displayed code and confirm sharing consent.
5. In the conversation, tap the microphone twice to preview listening and a sample transcript, or type a fictional reply. Responses are scripted. Finish explicitly.
6. Return to the caregiver family list to find the newly linked profile. **Your connection** on the conversation screen allows disconnecting the demo link.

To preview the older-adult journey directly, select **I'm here for a conversation** and use `123456` when no new invitation is pending. This is a reusable demonstration shortcut. Newly generated invitations expire after ten minutes and are consumed on acceptance.

## What is simulated

All profiles, metrics and recommendations are fictional. Account creation, login,
linking and AI conversations are UI demonstrations. No passwords are saved,
no email is sent, no microphone audio is captured, and no clinical assessment runs.
State is held only in the current page session; refreshing resets it. Linking is
not synchronized across separate phones or tabs. Do not enter real personal or
health information into this demo.

The planned product supports durable linking on each adult's phone. Real accounts,
server-side authorization, storage, consent management, speech recognition, AI
integration and validated health interpretation are future implementation work.
Family observations in this prototype do not modify any score or recommendation.

## Project files

```text
backend/server.js          Local HTTP server, frontend assets and /api/health
frontend/index.html        App entry, metadata and accessible status region
frontend/styles.css        Responsive Recollect design and layout
frontend/app.js            Interactive screens and demo state
package.json               Development commands
docs/recollect/DESIGN.md    Draft visual tokens and component specifications
docs/recollect/EXPERIENCE.md Draft journeys, states and accessibility behavior
docs/recollect/SOURCE.md    User requirements and workflow limitations
```

## Checks

```bash
npm run check   # Backend and frontend JavaScript syntax
npm start       # Run without backend file watching
```

The prototype was also exercised in headless Chrome for account preview, profile
switching, observation isolation, invitation/consent, voice simulation, completion,
safe rendering of typed text, and mobile overflow across all twelve routes.
This is not a clinical or accessibility certification.

The design documents remain draft: the repository is missing BMad's project
logging/finalization scripts. They are usable for review and further implementation.

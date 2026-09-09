# Recollect — iPhone app

Author: NgYanHerng

An iPhone UI/UX prototype for family connection and everyday conversations.
The mobile interface is packaged in a native iOS app using Capacitor. Screens are
bundled on the phone; the demo does not require a running backend or browser URL.
The UI uses HTML/CSS/JavaScript inside the app's WebView, rather than SwiftUI.

## Open the iPhone app in Xcode

Prerequisites: Node.js 22+, Xcode 26+ with first-launch components installed,
and an iOS simulator runtime or an iPhone. The app targets iOS 15+.

```bash
npm ci
npm run ios:open
```

In Xcode, select the **App** scheme and an iPhone simulator, then press **Run**.
For your own iPhone, select your development team under **Signing & Capabilities**,
choose a unique bundle identifier if needed, connect the phone and select it as
the destination. The current `com.recollect.demo` identifier is a development placeholder.

After changing frontend files, run `npm run ios:sync` before rebuilding in Xcode.
`npm run ios:run` also synchronizes and launches Capacitor's device selection flow.

**Current machine limitation:** native build verification stopped before compiling
because this Mac's Xcode installation is missing `DVTDownloads.framework`.
Complete Xcode's first-launch setup (Xcode's diagnostic suggests
`xcodebuild -runFirstLaunch`) and install an iOS simulator runtime. If the framework
remains missing, repair/reinstall Xcode. Native compilation has not yet been verified.

## Quick visual preview on your computer

```bash
npm run dev
```

Open http://127.0.0.1:3000. This is a development preview of the same phone interface,
constrained to 480px on large displays. It is not a separate desktop layout.
No npm dependencies are needed for this browser-only preview. Refresh after edits.

## Mobile experience

- Full-screen welcome, caregiver signup/login and invitation onboarding.
- Bottom tabs for **Family**, **Overview** and **Notes**.
- Separate adult profiles, two-column metric cards and stacked recommendations.
- Large conversation controls, typing alternative and an explicit finish action.
- iPhone safe-area spacing, portrait orientation, light appearance, Recollect app icon
  and a matching launch screen. No Android project is included.

## Explore the demo

1. Choose **I'm a caregiver**, accept the demo acknowledgment and continue with the fictional credentials.
2. Open Arun or Lily. Use **Overview** and the profile selector to view their separate data.
3. Use **Notes** to select concerns and add fictional examples; save before switching adults.
4. On **Family**, choose **Link someone**, enter a fictional name and create an invitation.
5. Choose **Try their invitation**, enter the displayed code and confirm sharing consent.
6. Preview speaking by tapping the microphone twice, or type a fictional reply. Finish explicitly.

To try the older-adult experience directly, choose **I'd like to talk** and enter
`123456` when no generated invitation is pending. This is a reusable demo shortcut.
Generated invitations expire after ten minutes and are consumed on acceptance.

## Simulation boundaries

All profiles, metrics and recommendations are fictional. Account creation, login,
linking and AI responses are UI demonstrations. No passwords are saved, no email
is sent, no audio is recorded, and no clinical assessment runs. State lasts only
for the current app session; restarting resets it. Invites are not synchronized
across different phones. Use fictional personal and health information only.

Real accounts, durable device authorization, storage, consent management, speech
recognition, AI and validated health interpretation remain future implementation.
Family concerns do not modify any score or recommendation in this prototype.

## Project files and commands

```text
frontend/                   Mobile screens, styles and simulated interactions
ios/App/App.xcodeproj       Native iPhone project
ios/App/App/                App lifecycle, launch screen and icon
capacitor.config.json       App ID, bundled frontend and iOS configuration
backend/server.js           Optional development preview server and /api/health
docs/recollect/              Draft design and experience specifications
```

```bash
npm run check      # Check frontend/backend JavaScript syntax
npm run ios:sync   # Copy mobile UI into the native app bundle
npm run ios:open   # Sync and open Xcode
npm run ios:run    # Sync and run on an available iOS target
npm run dev       # Browser preview with backend watching
```

Generated bundled assets in `ios/App/App/public` are ignored by Git; always sync
after pulling frontend updates. Commit the Xcode project and package lockfile.
Do not commit signing credentials, build output or personal Xcode state.

Design documents remain draft because the repository lacks BMad's logging and
finalization scripts. UI checks are not clinical or accessibility certification.

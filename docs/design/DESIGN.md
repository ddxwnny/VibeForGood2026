---
name: Recollect
description: An iPhone application for family connection and everyday conversations.
status: draft
updated: 2026-09-09
sources:
  - SOURCE.md
colors:
  canvas: '#F8F7F2'
  surface: '#FFFEFA'
  ink: '#243D36'
  muted: '#59685F'
  primary: '#19594E'
  on-primary: '#FFFFFF'
  soft: '#E8EFDF'
  border: '#DCE1D6'
  control-border: '#8B9E92'
  attention: '#775414'
  attention-surface: '#FBEFD7'
  error: '#A02E32'
  focus: '#946117'
typography:
  display:
    fontFamily: Georgia, serif
    fontSize: 35px
    fontWeight: '400'
    lineHeight: '1.12'
  body:
    fontFamily: -apple-system, BlinkMacSystemFont, sans-serif
    fontSize: 16px
    lineHeight: '1.55'
  older-adult-body:
    fontFamily: -apple-system, BlinkMacSystemFont, sans-serif
    fontSize: 19px
    lineHeight: '1.55'
rounded:
  sm: 10px
  md: 12px
  lg: 22px
  full: 9999px
spacing:
  small: 8px
  related: 16px
  section: 24px
  app-max-width: 480px
  mobile-gutter: 20px
components:
  primary-button:
    background: '{colors.primary}'
    foreground: '{colors.on-primary}'
    radius: '{rounded.md}'
  card:
    background: '{colors.surface}'
    radius: '{rounded.lg}'
  attention-label:
    background: '{colors.attention-surface}'
    foreground: '{colors.attention}'
---

## Brand & Style

Recollect feels like an invitation to connect. Warm paper-like backgrounds, botanical shapes, restrained teal and generous space support the user's proposed onboarding and conversation screens. This is a proposed direction, open to user refinement. System fonts and native form controls complement the mobile layout. Capacitor packages these screens in an iOS app; this is a hybrid interface, not a SwiftUI rewrite.

## Colors

Use primary teal for actions and navigation. Soft sage groups supportive context. Amber labels an update to explore; pair it with words and never imply a confirmed condition through colour. Red is reserved for form errors. Target 4.5:1 for normal text and 3:1 for large text and meaningful controls; verify rendered combinations before a production handoff.

## Typography

Georgia headlines supply warmth; system sans-serif handles controls and information. Display headlines shrink on phones. Older-adult body copy uses {typography.older-adult-body.fontSize}. Labels remain visible outside inputs. Never use placeholder text as the only label.

## Layout & Spacing

iPhone portrait is the product surface. Every screen is single-column; metric cards use two columns. The app header is compact, with a back control on child screens. Caregiver navigation uses a fixed bottom tab bar (Family / Overview / Notes). Content reserves space for the tab bar and the home indicator. Respect top and bottom safe-area insets. Use {spacing.mobile-gutter} on phones. Browser previews stay at a maximum of 480px instead of switching to a desktop layout. Preserve natural scrolling, wrapping and text zoom. Keyboard focus must scroll fields into view; no fixed speech composer obscures replies.

## Elevation & Depth

Cards use thin borders and contrasting surfaces. The microphone receives a modest halo; shadows do not encode status.

## Shapes

Cards use {rounded.lg}; inputs {rounded.sm}; buttons {rounded.md}. Circles are for initials and the microphone. The welcome illustration is built in CSS and needs no remote assets. [App icon source](app-icon.svg) uses the same two-leaf mark on an opaque cream square, rasterized to 1024px for Xcode. iOS applies its own icon mask. The launch screen shows the Recollect wordmark on cream.

## Components

| Component | Visual rules |
|---|---|
| Primary button | Teal with white text; 52px minimum height, 56px on older-adult screens; secondary navigation targets are at least 44px. |
| Secondary button | Transparent fill, dark text and visible border. |
| Card | Warm surface, 22px radius, 22–27px padding. |
| Navigation | Bottom tabs use sage active fill, icon and visible text; child screens have a labelled Back control. |
| Profile selector | Visible adult context, labelled native select. |
| Form field | Visible label, 52px minimum height, contrast border and focus ring. |
| Concern checkbox | Full-width bordered row with large native checkbox; selected state includes a checkmark. |
| Attention label | Amber background and dark amber wording; no red risk gauge. |
| Activity chart | Sage bars, latest bar teal; values and period labels remain visible. |
| Invitation code | Large, spaced digits; one pasteable input on the recipient screen. |
| Conversation bubble | Sage for Recollect, warm bordered white for the adult; speaker name included. |
| Microphone | 88px teal circle with visible adjacent state wording. |
| Demo notice | Persistent top banner, plus contextual disclosure at account, link and conversation screens. |

## Do's and Don'ts

Use direct language and adult-respectful typography. Always pair state colour with text. Keep each person's name visible on their dashboard and observation form. Do not show an invented dementia percentage, reward streaks, childish imagery, or a microphone that appears to record without explanation.

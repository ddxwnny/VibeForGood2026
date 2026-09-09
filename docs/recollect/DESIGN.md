---
name: Recollect
description: A calm family connection and conversation interface.
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
    fontSize: 42px
    fontWeight: '400'
    lineHeight: '1.12'
  body:
    fontFamily: Avenir Next, Segoe UI, sans-serif
    fontSize: 16px
    lineHeight: '1.55'
  older-adult-body:
    fontFamily: Avenir Next, Segoe UI, sans-serif
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
  desktop-gutter: 42px
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

Recollect feels like an invitation to connect. Warm paper-like backgrounds, botanical shapes, restrained teal and generous space support the user's proposed onboarding and conversation screens. This is a proposed direction, open to user refinement. No existing component system is imposed.

## Colors

Use primary teal for actions and navigation. Soft sage groups supportive context. Amber labels an update to explore; pair it with words and never imply a confirmed condition through colour. Red is reserved for form errors. Target 4.5:1 for normal text and 3:1 for large text and meaningful controls; verify rendered combinations before a production handoff.

## Typography

Georgia headlines supply warmth; system sans-serif handles controls and information. Display headlines shrink on phones. Older-adult body copy uses {typography.older-adult-body.fontSize}. Labels remain visible outside inputs. Never use placeholder text as the only label.

## Layout & Spacing

Caregiver: 236px sidebar and constrained main area on desktop; top navigation and a single-column card layout below 720px. Metrics become two columns below 1050px. Older-adult content stays within 740px; linking forms within 540px. Use {spacing.mobile-gutter} on phones. Preserve natural scrolling and wrapping at zoom.

## Elevation & Depth

Cards use thin borders and contrasting surfaces. The welcome quote and microphone receive modest shadows; shadows do not encode status.

## Shapes

Cards use {rounded.lg}; inputs {rounded.sm}; buttons {rounded.md}. Circles are for initials and the microphone. The welcome illustration is built in CSS and needs no remote assets.

## Components

| Component | Visual rules |
|---|---|
| Primary button | Teal with white text; 48px minimum height, 56px on older-adult screens. |
| Secondary button | Transparent fill, dark text and visible border. |
| Card | Warm surface, 22px radius, 22–27px padding. |
| Navigation | Active item has sage fill and a text label; icons supplement words. |
| Profile selector | Visible adult context, labelled native select. |
| Form field | Visible label, 48px minimum height, contrast border and focus ring. |
| Concern checkbox | Full-width bordered row with large native checkbox; selected state includes a checkmark. |
| Attention label | Amber background and dark amber wording; no red risk gauge. |
| Activity chart | Sage bars, latest bar teal; values and period labels remain visible. |
| Invitation code | Large, spaced digits; one pasteable input on the recipient screen. |
| Conversation bubble | Sage for Recollect, warm bordered white for the adult; speaker name included. |
| Microphone | 88px teal circle with visible adjacent state wording. |
| Demo notice | Persistent top banner, plus contextual disclosure at account, link and conversation screens. |

## Do's and Don'ts

Use direct language and adult-respectful typography. Always pair state colour with text. Keep each person's name visible on their dashboard and observation form. Do not show an invented dementia percentage, reward streaks, childish imagery, or a microphone that appears to record without explanation.

# EMS-OPG User Interface Design Specification

**Project:** EMS Operations Production Gateway (EMS-OPG)

**Version:** 1.1

**Author:** Zachary McMillan

---

# Table of Contents

1. Purpose
2. Design Philosophy
3. Application Goals
4. Operator Workflow
5. UI Design Principles
6. Color Palette
7. Typography
8. Window Layout
9. Screen Specifications
10. Widget Standards
11. Navigation
12. User Workflows
13. Backend Integration
14. PyQt Architecture
15. Future Improvements

---

# 1. Purpose

This document defines the complete user interface architecture for EMS-OPG.

The purpose of this document is to establish a consistent user experience before implementation begins.

Rather than designing the interface while writing code, every major UI decision is documented beforehand. This allows development to proceed quickly while maintaining consistency across the entire application.

This document should be treated as the single source of truth for all future UI development.

---

# 2. Design Philosophy

The application is not intended to look like a typical business application.

It is industrial manufacturing software.

Every screen should optimize for:

- Speed
- Simplicity
- Reliability
- Readability

The operator should never have to search for information.

Every important action should require a single click.

The operator's attention should always remain on the Device Under Test (DUT), not the software.

---

## Core Design Principles

### 1. Large Targets

Buttons should be large enough for operators wearing gloves.

Minimum height:

50 pixels

Preferred height:

60 pixels

---

### 2. Large QR Codes

The QR code is the primary purpose of the application.

It should always occupy the largest amount of available screen space.

The QR code should never be scaled smaller simply to display more information.

---

### 3. Minimal Typing

Typing slows production.

The application should request only:

• Order Number

• Serial Number

• First MAC Address

Everything else should be automatic.

---

### 4. Sequential Workflow

Operators should never wonder what to do next.

The application controls the workflow.

Previous

↓

Current Step

↓

Next Step

---

### 5. One Screen Focus

Only one major task should exist on each screen.

Avoid multiple unrelated windows.

Avoid excessive dialog boxes.

Avoid nested menus.

---

# 3. Application Goals

The primary goals of EMS-OPG are:

• Generate QR codes rapidly

• Track device traceability

• Prevent MAC address duplication

• Simplify operator workflow

• Reduce operator mistakes

• Provide audit history

• Maintain manufacturing speed

The software should disappear into the background.

The operator should think about the hardware—not the application.

---

# 4. Operator Workflow

Home

↓

Enter Order Number

↓

Enter Serial Number

↓

Scan First MAC Label

↓

Validate MAC

↓

Assign Second MAC Automatically

↓

Generate QR Codes

↓

Display Step 1

↓

Operator Scans QR

↓

Next Step

↓

Repeat Until Complete

↓

Finalize Device

↓

Database Updated

↓

Return Home

---

# 5. UI Design Principles

These principles govern every screen in the application, not just the workflow steps.

### 5.1 Consistency

Every screen uses the same header, the same button placement, and the same visual language.

An operator who learns one screen has learned them all.

### 5.2 Immediate Feedback

Every action produces a visible response within 200ms.

A scan, a click, or a keystroke should never leave the operator wondering if it registered.

Feedback types:

- Color change (button press, field validation)
- Status banner (success, warning, error)
- Sound cue (optional, configurable per station)

### 5.3 Error Prevention Over Error Correction

The interface should make invalid input impossible where feasible, rather than catching it after the fact.

Examples:

- Disable "Next" until required fields are valid
- Reject malformed MAC addresses at the input level, not after submission
- Grey out actions that are not currently valid

### 5.4 Fail Loud, Fail Clear

When something does go wrong (duplicate MAC, network failure, invalid scan), the error must be:

- Large
- Red
- Impossible to miss
- Written in plain language, not error codes

An operator should never need to interpret a stack trace or a status number.

### 5.5 No Idle Ambiguity

The current state of the system should always be visible. An operator glancing at the screen after being away for 30 seconds should immediately understand what step they are on and what is expected of them.

### 5.6 Glove-First Accessibility

All interactive elements assume the operator may be wearing thick work gloves:

- Minimum touch target: 50px height (per Section 2)
- Minimum spacing between adjacent targets: 15px
- No hover-dependent interactions (gloves and touchscreens don't hover)
- No small checkboxes, radio buttons, or dropdown arrows

---

# 6. Color Palette

The palette is built for a factory floor: variable lighting, safety-glass glare, and operators glancing at the screen quickly rather than studying it.

### 6.1 Base Colors

| Role | Color | Hex |
|---|---|---|
| Background (primary) | Near-black charcoal | #1A1D21 |
| Background (panel) | Dark slate | #24282E |
| Primary text | Off-white | #F2F2F2 |
| Secondary text | Light grey | #A0A6AD |
| Border / divider | Muted grey | #3A3F46 |

### 6.2 Accent Colors

| Role | Color | Hex |
|---|---|---|
| Primary action | Safety blue | #2E7CF6 |
| Success / validated | Safety green | #2FB86E |
| Warning | Amber | #F5A623 |
| Error / critical | Safety red | #E5484D |
| Disabled state | Flat grey | #565C64 |

### 6.3 Usage Rules

- Red is reserved exclusively for errors and blocking conditions. It is never used decoratively.
- Green only appears after successful validation (MAC accepted, QR generated, device finalized).
- No more than one accent color should dominate a screen at a time.
- Backgrounds stay dark. This is a deliberate choice for eye strain reduction during long shifts and for QR code contrast.

---

# 7. Typography

### 7.1 Typeface

A single sans-serif typeface is used throughout the application (e.g., Inter, Segoe UI, or an equivalent system font). No decorative or serif fonts.

### 7.2 Type Scale

| Use | Size | Weight |
|---|---|---|
| Screen title | 32px | Bold |
| Step indicator | 20px | Medium |
| Body / labels | 18px | Regular |
| Input field text | 22px | Regular |
| Button text | 22px | Semibold |
| Error / status banner | 24px | Bold |

### 7.3 Monospace for Identifiers

Order numbers, serial numbers, and MAC addresses are always displayed in a monospaced font. This prevents ambiguity between characters like `0` / `O` or `1` / `l`, which matters when an operator is cross-checking a physical label against the screen.

### 7.4 Readability Rules

- Minimum body text size: 18px (never smaller, regardless of screen density)
- Line height: 1.4x font size minimum
- No text truncation with ellipsis on identifiers — always wrap or scroll instead, since a hidden character in a MAC address is a traceability defect.

---

# 8. Window Layout

### 8.1 Application Mode

EMS-OPG runs in fullscreen kiosk mode on a fixed-resolution station display. The window is not resizable and has no OS chrome (title bar, minimize/maximize/close controls are hidden or disabled).

### 8.2 Structure

```
┌─────────────────────────────────────────┐
│  Header Bar (fixed, 60px)                │
│  [Station ID]     [Step Indicator]  [⌂]  │
├─────────────────────────────────────────┤
│                                           │
│                                           │
│            Main Content Area             │
│         (single screen at a time)        │
│                                           │
│                                           │
├─────────────────────────────────────────┤
│  Footer Bar (fixed, 70px)                │
│  [Previous]              [Next / Action] │
└─────────────────────────────────────────┘
```

### 8.3 Header Bar

- Left: Station ID / operator badge (read-only, informational)
- Center: Current step indicator (e.g., "Step 3 of 6: Scan MAC")
- Right: Home icon — always available, always takes the operator back to Home (see Section 11)

### 8.4 Main Content Area

Reserved exclusively for the current screen's task. On QR display screens, this area is dominated by the QR code itself per the Section 2 principle that QR codes are never scaled down to fit other content.

### 8.5 Footer Bar

Houses the primary navigation actions only: Previous (when applicable) and Next / primary action. No secondary or tertiary buttons live in the footer — anything else does not belong on the screen at all.

---

# 9. Screen Specifications

### 9.1 Home Screen

- Large "Start New Device" button, centered, dominant on screen
- Station status summary (idle / ready)
- Access to audit history (small, secondary button — not competing visually with Start)

### 9.2 Order Number Entry

- Single large input field, numeric keypad or scanner input
- "Next" disabled until a valid, recognized order number is entered
- Inline validation against the order database

### 9.3 Serial Number Entry

- Single large input field
- Duplicate-serial check runs on submit
- Clear error state if the serial already exists in the system

### 9.4 MAC Scan Screen

- Single large input field, scanner-focused (auto-focus on load)
- Real-time format validation as characters are entered
- On valid scan: green confirmation state, auto-advance
- On duplicate MAC: full-screen red error state, scan is rejected, operator must rescan a different unit

### 9.5 QR Display Screen (Steps 1–N)

- QR code occupies at minimum 70% of the main content area
- Step label and short instruction text above or below the code, never overlapping it
- "Confirm Scan" advances only after the corresponding scan event is received from the backend — not on a manual click, to prevent operators skipping a step

### 9.6 Finalize Screen

- Summary of order number, serial number, both MAC addresses
- Single "Finalize Device" button
- On success: green confirmation banner, auto-return to Home after a short delay

### 9.7 Error Screen (modal overlay, not a separate route)

- Full-width red banner at the top of the current screen
- Plain-language message + suggested next action
- Does not block the rest of the screen unless the error is blocking by nature (e.g., duplicate MAC)

---

# 10. Widget Standards

### 10.1 Buttons

- Height: 50px minimum, 60px preferred (per Section 2)
- Corner radius: 6px
- States: default, pressed, disabled — each visually distinct
- Primary action buttons use the primary blue accent; destructive actions (abort, cancel device) use red and require a confirmation step

### 10.2 Text Input Fields

- Height: 50px minimum
- Large, high-contrast border on focus
- Auto-focus on screen load so the operator (or scanner) can begin immediately without clicking into the field
- Font: monospace for identifier fields (per Section 7.3)

### 10.3 QR Display Widget

- Fixed aspect ratio (1:1), scales with available space
- White background behind the code regardless of app theme, to preserve scan contrast
- Never overlaid with text or icons

### 10.4 Status Banner

- Full-width, fixed position at top of content area
- Color-coded per Section 6.2 (green / amber / red)
- Auto-dismisses on success after 2–3 seconds; persists on error until acknowledged or resolved

### 10.5 Step Indicator

- Horizontal progress stepper in the header
- Completed steps shown filled/green, current step highlighted, future steps greyed out
- No step is ever skippable by clicking ahead on the indicator — it is informational only, not navigational

---

# 11. Navigation

### 11.1 Linear by Default

Navigation follows the Operator Workflow (Section 4) strictly. There is no free navigation between arbitrary screens.

### 11.2 Previous

Available only where going back does not violate data integrity (e.g., before a MAC has been validated). Once a MAC is validated and QR codes are generated, "Previous" is disabled — the operator must complete or abort instead.

### 11.3 Home

Always available via the header icon. Selecting Home from mid-workflow prompts a confirmation dialog if the current device is incomplete, since this discards in-progress work.

### 11.4 No Nested Menus

There are no dropdown menus, no settings buried in submenus, and no hidden gestures. Anything the operator needs is a single click away from the current screen.

---

# 12. User Workflows

### 12.1 Happy Path

Home → STEP1: username (root) → STEP2: password (default) → STEP3-6: Functional test QR code → STEP7: MAC Scan → Validate →STEP8: Auto-assign second MAC →STEP9: Generate QR codes → validate (step 10) Finalize (order number, serial number) → Return Home.

### 12.2 Duplicate MAC Path

MAC Scan → Validation fails (duplicate detected) → Full-screen red error → Operator rescans a different unit → Validation retried.

### 12.3 Duplicate Serial Path

Serial Number Entry → Validation fails (serial already exists) → Inline red error on the field → Operator corrects or escalates.

### 12.4 Network / Backend Failure Path

Any step requiring backend validation → Request times out or fails → Amber "Retrying..." state shown automatically → If retries are exhausted, red error with a manual "Retry" action → Workflow does not advance until backend confirms.

### 12.5 Operator Abort Path

Any in-progress screen → Home icon selected → Confirmation dialog ("Discard current device?") → On confirm, in-progress data is discarded and logged; on cancel, operator returns to the current step.

---

# 13. Backend Integration

### 13.1 Integration Model

The UI is a thin client. All validation, MAC assignment, QR generation, and persistence logic lives in the backend service layer — the UI never makes traceability decisions on its own.

### 13.2 Key Integration Points

| UI Event | Backend Call | Response Handling |
|---|---|---|
| QR step scanned | Confirm scan event received | Auto-advance to next step |
| MAC scanned | Validate format + check for duplicate | Auto-advance or show error |
| MAC validated | Request second MAC assignment | Populate second MAC, generate QR set |
| Order number entered | Validate order exists | Enable/disable Next |
| Serial number entered | Check for duplicate serial | Enable/disable Next, show error |
| Finalize pressed | Commit device record to database | Show success banner, return Home |

### 13.3 Failure Handling

All backend calls run asynchronously with a visible loading/waiting state (never a frozen UI). Timeouts trigger the Network Failure Path defined in Section 12.4. The UI never assumes success — every state transition is driven by a confirmed backend response.

### 13.4 Audit Trail

Every state transition (order entered, serial entered, MAC validated, device finalized, device aborted) is logged with a timestamp and station ID, satisfying the audit history goal in Section 3.

---

# 14. PyQt Architecture

### 14.1 Structure

- **QMainWindow** as the application shell, hosting the fixed header and footer.
- **QStackedWidget** as the main content area, with one widget per screen defined in Section 9. Screen transitions are stack-index changes, not new windows.
- Each screen is its own `QWidget` subclass, kept in its own module, separating layout/UI code from business logic.

### 14.2 Signal/Slot Pattern

- UI widgets emit signals only (button clicks, field changes, scan events).
- A controller layer listens for these signals and coordinates backend calls, keeping screen classes free of business logic.
- Backend responses come back as signals as well, so the UI layer never blocks waiting on I/O.

### 14.3 Threading

- All backend/network calls run on a `QThread` (or `QThreadPool` worker), never on the main UI thread.
- The main thread is reserved exclusively for rendering and input handling, preserving the "immediate feedback" principle in Section 5.2.

### 14.4 State Management

- A single `DeviceSession` object holds the in-progress device's data (order number, serial, MACs, step index) for the current workflow run.
- This object is passed to the controller, not duplicated across screens, so there is one source of truth for "what device is currently being built."

### 14.5 Styling

- Centralized QSS (Qt Style Sheets) stylesheet implementing the Color Palette (Section 6) and Typography (Section 7) rules, loaded once at application startup — no per-widget inline styling.

---

# 15. Future Improvements

The following are out of scope for v1.0 but recorded for future consideration:

- Barcode scanner auto-focus recovery (re-focus scan input automatically if an operator accidentally clicks elsewhere)
- Multi-language support for operator-facing text
- Direct label printer integration for QR/serial labels
- Station-level analytics dashboard (throughput, error rates, average cycle time)
- Configurable sound cues per station
- Optional dark/light theme toggle for stations with different ambient lighting
- Remote monitoring view for line supervisors (read-only, separate from operator stations)
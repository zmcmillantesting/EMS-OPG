# EMS-OPG User Interface Design Specification

**Project:** EMS Operations Production Gateway (EMS-OPG)

**Version:** 1.0

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

# 5. UI Design Principles

## Philosophy

The EMS-OPG interface should feel like industrial manufacturing software rather than a traditional desktop application.

The operator should immediately understand what the application expects from them without requiring training.

Every screen should answer three questions:

1. What am I working on?
2. What do I do next?
3. Is everything working correctly?

If the operator has to stop and think, the interface has failed.

---

## Design Objectives

The interface should prioritize:

- Speed
- Simplicity
- Consistency
- Readability
- Reliability

Not:

- Fancy animations
- Unnecessary graphics
- Complex menus
- Excessive customization

---

## Industrial Theme

The existing EMS-OPG application already has an industrial appearance.

The redesigned interface should preserve this identity while modernizing the layout.

### Theme Characteristics

- Dark workspace
- Light content cards
- Blue primary actions
- Green success indicators
- Red destructive actions
- Neutral gray backgrounds

The application should feel similar to:

- Industrial PLC software
- Manufacturing execution systems (MES)
- Network management consoles
- Equipment configuration software

---

# 6. Color Palette

The color palette will remain consistent with the original EMS-OPG application.

The existing application's colors should be preserved wherever practical to maintain operator familiarity.

## Primary Background

```
#202124
```

Application background.

---

## Secondary Background

```
#2D2D30
```

Main content panels.

---

## Tertiary Background

```
#33363C
```

Headers and footers.

---

## Card Background

```
#35383D
```

Information cards.

---

## Primary Button

```
#3D7EFF
```

Used for:

- Next
- Save
- Generate
- Continue

---

## Success

```
#4CAF50
```

Used for:

- Connected
- Database Online
- Test Passed
- Ready

---

## Warning

```
#FFC107
```

Used for:

- Waiting
- Validation Required
- Operator Attention

---

## Error

```
#C62828
```

Used for:

- Duplicate MAC
- Database Error
- Cancel Test
- Invalid Input

---

## Disabled

```
#666666
```

Inactive controls.

---

## Text

Primary

```
#FFFFFF
```

Secondary

```
#B0B0B0
```

Muted

```
#808080
```

---

# 7. Typography

The interface should prioritize readability.

Preferred font:

```
Segoe UI
```

Fallbacks:

```
Arial
Sans Serif
```

---

## Font Sizes

Window Title

28 px

Section Header

22 px

Card Header

18 px

Body Text

16 px

Small Labels

12 px

Status Bar

11 px

---

## Font Weight

Titles

Bold

Section Headers

Semi-Bold

Body

Regular

Labels

Light

---

# 8. Window Layout

The application consists of four primary pages.

```
Home

↓

Testing

↓

History

↓

Settings
```

These pages should be managed using a QStackedWidget.

Only one page should be visible at any time.

---

## Window Size

Recommended development size:

```
1600 × 900
```

Minimum supported:

```
1400 × 900
```

Preferred operator monitor:

```
1920 × 1080
```

---

## Main Layout

```
+------------------------------------------------------------+
| Header                                                     |
+------------------------------------------------------------+
| Session / Progress                                         |
+----------------------+-------------------------------------+
|                      |                                     |
| Session Panel        |          Primary Content            |
|                      |                                     |
|                      |                                     |
|                      |                                     |
+----------------------+-------------------------------------+
| Footer / Navigation                                        |
+------------------------------------------------------------+
```

---

## Header

Contains:

- Application name
- Operator
- Connection status
- Database status
- Current version

Example

```
EMS-OPG

Operator: Zach

Database ● Connected

Version 1.0
```

---

## Footer

The footer remains visible throughout the application.

Typical buttons include:

Previous

Repeat

Next

Finish

Cancel

The button order should remain identical on every workflow page.

Operators quickly develop muscle memory.

Do not rearrange buttons between screens.

---

# 9. Navigation

The application intentionally contains only four primary pages.

```
Home

Testing

History

Settings
```

No additional navigation should exist.

Avoid:

- Ribbon menus
- Nested menus
- Floating toolbars
- Multiple windows

Everything should remain discoverable within one or two clicks.

---

## Future Navigation

A collapsible sidebar may be implemented later.

```
🏠 Home

🧪 Testing

📜 History

⚙ Settings
```

During active testing the sidebar may collapse to maximize QR code size.

This behavior is optional but recommended.

---

# General Layout Rules

Maintain at least 20 pixels of spacing between cards.

Cards should use rounded corners.

Avoid more than two nested panels.

Do not place unrelated information together.

Information should be grouped logically:

Session

↓

Device Information

↓

Current Step

↓

Actions

This creates a predictable visual hierarchy for operators.

# 10. Screen Specifications

The EMS-OPG interface consists of four primary pages.

Each page has a single responsibility.

```
Home
        ↓
Testing
        ↓
History
        ↓
Settings
```

No additional primary windows should exist.

Dialogs should only be used when absolutely necessary.

---

# 10.1 Home Screen

## Purpose

The Home screen serves as the application's landing page.

Operators arrive here after launching the application and after successfully completing a device.

The Home page should contain no unnecessary information.

Its purpose is simply to begin testing quickly.

---

## Layout

```
+--------------------------------------------------------------+
| EMS-OPG                                      Operator: Zach  |
+--------------------------------------------------------------+

              EMS Operations Production Gateway

                    [ New Test ]

              [ History ]   [ Settings ]

---------------------------------------------------------------

 Database        Connected

 Devices Today   124

 Last Backup     Today 08:00

 Version         1.0.0

---------------------------------------------------------------

 Status: Ready
```

---

## Widgets

### Header

Displays:

- Application Name
- Operator
- Connection Status

---

### New Test Button

Primary action.

Large blue button.

This begins a new testing session.

Calls:

```
WorkflowEngine.start_session()
```

---

### History Button

Navigates to:

History Screen

---

### Settings Button

Navigates to:

Settings Screen

---

### Status Cards

Display:

Database

Operator

Today's Device Count

Current Version

Last Backup

---

## Backend Connections

WorkflowEngine

Application

DatabaseService

AuditService

---

## Validation

None required.

---

# 10.2 Testing Screen

## Purpose

This is the primary production screen.

Operators spend approximately 95% of their time here.

Everything about this page should optimize for speed.

The QR code is the most important element.

---

## Layout

```
+-----------------------------------------------------------------------------------+
| EMS-OPG                         Operator              Database Connected           |
+-----------------------------------------------------------------------------------+

 Order: 123456              Serial: SN123456            Step 4 of 8

 ███████████████████░░░░░░░░░░░░░░░░░░░░

+--------------------------+--------------------------------------------------------+
|                          |                                                        |
| Session                  |                                                        |
|                          |                                                        |
| MAC 1                    |                                                        |
|                          |                                                        |
| MAC 2                    |                                                        |
|                          |                  QR CODE                               |
| Operator                 |                                                        |
|                          |                                                        |
| Elapsed Time             |                                                        |
|                          |                                                        |
| Status                   |                                                        |
|                          |                                                        |
+--------------------------+--------------------------------------------------------+

 Current Command

 timeout 2s loopback /dev/port0[2-4] -q

+--------------------------------------------------------------------------+

 Previous      Repeat      Next      Cancel Test
```

---

## Session Panel

The left panel remains visible throughout testing.

It displays:

Order Number

Serial Number

MAC 1

MAC 2

Operator

Current Step

Elapsed Time

Database Status

Logging Status

Workflow State

---

## QR Display

Largest widget on screen.

Approximately

500 x 500 pixels

Minimum acceptable size:

400 x 400

---

## Current Command

Displays the exact command encoded inside the QR code.

This allows manual verification.

Example

```
timeout 2s loopback /dev/port0[2-4] -q
```

---

## Progress Bar

Displays

Current Step

Total Steps

Percentage Complete

---

## Footer Buttons

### Previous

Returns to previous workflow step.

Disabled during Step 1.

---

### Repeat

Regenerates the current QR.

No workflow changes occur.

---

### Next

Advances the workflow.

Loads next QR.

Updates progress.

---

### Cancel

Cancels the session.

Confirmation dialog required.

---

## Backend Connections

WorkflowEngine

WorkflowSession

QRService

DeviceService

OrderService

AuditService

Logger

---

## Validation Rules

Order Number required.

Serial Number required.

MAC1 required.

MAC1 must exist.

MAC1 cannot already be used.

MAC2 assigned automatically.

MAC2 cannot already be used.

Workflow cannot continue if validation fails.

---

## Workflow

```
New Test

↓

Enter Order

↓

Enter Serial

↓

Scan MAC1

↓

Assign MAC2

↓

Generate QR

↓

Display Step

↓

Next

↓

Display Step

↓

Repeat

↓

Finish

↓

Database Commit

↓

Return Home
```

---

# 10.3 History Screen

## Purpose

Provides traceability.

Allows supervisors and operators to locate previous devices.

Supports troubleshooting.

No editing occurs here.

Editing belongs in Settings.

---

## Layout

```
+--------------------------------------------------------------+

 Search

 [__________________________]

---------------------------------------------------------------

 Order

 Serial

 MAC

 Operator

 Date

---------------------------------------------------------------

 123456

 SN001

 00:60...

 Zach

 2026-08-01

---------------------------------------------------------------

 View Details

 Export CSV

 Return
```

---

## Widgets

Search Box

Search Button

History Table

Export Button

View Device Button

Return Button

---

## Search Options

Order Number

Serial Number

MAC Address

Operator

Date

---

## Table Columns

Date

Order

Serial

MAC1

MAC2

Operator

Result

Status

---

## Backend Connections

AuditService

DeviceService

OrderService

Repositories

---

## Future Enhancements

Advanced Filters

Sorting

CSV Export

PDF Export

Statistics

---

# 10.4 Settings Screen

## Purpose

Provides configuration and maintenance tools.

Operators should rarely access this page.

Supervisors will use it more frequently.

---

## Layout

```
+--------------------------------------------------------------+

 Database

 [ Backup ]

 [ Restore ]

 [ Export ]

---------------------------------------------------------------

 Logging

 Log Level

 Open Logs

---------------------------------------------------------------

 Manual Corrections

 Edit Device

 Edit Order

 Edit Serial

 Edit Operator

 Reset MAC

---------------------------------------------------------------

 Workflow

 Reload Config

 Verify Database

 Regenerate Cache

---------------------------------------------------------------

 Save

 Cancel

 Return Home
```

---

## Database Section

Functions

Backup Database

Restore Database

Verify Database

Export CSV

---

## Logging Section

Log Level

Open Log Folder

Clear Logs

---

## Manual Corrections

Search Device

Modify Order

Modify Serial

Modify Operator

Reset Used Status

Reassign MAC

View Audit History

Every modification must generate an audit log entry.

---

## Workflow Section

Reload configuration

Verify QR cache

Rebuild cache

Validate configuration

---

## Backend Connections

ConfigurationManager

PathManager

Logger

AuditService

Repositories

WorkflowEngine

DatabaseService

---

## Security

Future versions may restrict this page to supervisors.

Operator mode should hide advanced maintenance functions.

# 11. Widget Standards

The EMS-OPG interface should use a consistent widget library throughout the application.

Each widget should have a single purpose.

No widget should perform business logic.

Business logic belongs inside Services and the Workflow Engine.

Widgets display information.

Services perform work.

---

# General Widget Rules

Every widget should have:

- A descriptive objectName
- A single responsibility
- No direct database access
- No SQL statements
- No QR generation logic

Widgets should communicate through:

Signals

↓

Workflow Engine

↓

Services

↓

Repositories

↓

Database

Never:

Widget

↓

Database

---

# Primary Widgets

## Primary Button

Purpose

Starts or advances a workflow.

Examples

Next

Save

Generate

Begin Test

Appearance

Blue

Large

Rounded corners

Height

60 pixels

---

## Secondary Button

Purpose

Navigation

History

Settings

Previous

Repeat

Gray

---

## Danger Button

Purpose

Cancel

Delete

Reset

Appearance

Red

Confirmation required

---

## Information Card

Purpose

Displays read-only information.

Examples

Order Number

Serial Number

MAC Address

Operator

Current Step

Cards never accept user input.

---

## Input Field

Purpose

Collect operator input.

Examples

Order Number

Serial Number

MAC Address

Every input field should validate immediately.

Never wait until Finish.

---

## QR Display

Largest widget in the application.

Minimum Size

400 x 400

Preferred

500 x 500

Displays

QR Image

Current Command

Generation Status

---

## Progress Widget

Displays

Current Step

Total Steps

Percent Complete

Should always remain visible.

---

## Status Indicator

Displays

Database

Logging

Workflow

QR Generator

Green

Connected

Yellow

Waiting

Red

Error

---

# 12. Widget Naming Standards

The project should use consistent names.

Avoid generic names like

button1

label2

textbox

Use descriptive names instead.

---

Buttons

btn_new_test

btn_next

btn_previous

btn_repeat

btn_cancel

btn_finish

btn_history

btn_settings

btn_backup

btn_restore

---

Labels

lbl_operator

lbl_order

lbl_serial

lbl_mac1

lbl_mac2

lbl_status

lbl_elapsed

lbl_command

---

Input Fields

txt_order

txt_serial

txt_mac

---

QR

img_qr

lbl_qr_command

---

Tables

tbl_history

tbl_devices

tbl_audit

---

Progress

progress_workflow

---

Cards

card_session

card_status

card_device

card_network

---

# 13. PyQt Architecture

The application should follow a layered architecture.

```

Application

↓

MainWindow

↓

Navigation

↓

Pages

↓

Workflow Engine

↓

Services

↓

Repositories

↓

Database

```

---

# Recommended Folder Structure

```
src/

ems_opg/

ui/

main_window.py

pages/

home_page.py

testing_page.py

history_page.py

settings_page.py

dialogs/

edit_device_dialog.py

edit_order_dialog.py

edit_serial_dialog.py

widgets/

session_panel.py

status_bar.py

progress_widget.py

qr_display.py

device_card.py

navigation_bar.py

styles/

theme.qss

resources/

icons/

images/

```

---

# Main Window

Responsibilities

Application startup

Navigation

Window management

Theme loading

Nothing else.

No workflow logic.

---

# Home Page

Responsibilities

Start Test

Navigate

Display application status

---

# Testing Page

Responsibilities

Display workflow

Display QR

Show session

Forward operator actions

No QR generation.

No database work.

---

# History Page

Responsibilities

Display previous devices

Search

Export

No editing.

---

# Settings Page

Responsibilities

Configuration

Maintenance

Manual corrections

Database tools

---

# Reusable Widgets

Session Panel

Used on

Testing

History

Manual Correction Dialog

Displays

Order

Serial

MAC

Operator

Status

Elapsed Time

---

QR Widget

Displays

QR image

Current command

Validation status

Generation timestamp

---

Progress Widget

Displays

Current workflow position.

Can be reused by future workflows.

---

# 14. Signal / Slot Architecture

Every operator action should emit a signal.

Signals should never talk directly to repositories.

Example

```

Next Button

↓

Testing Page

↓

Workflow Engine

↓

QR Service

↓

Update UI

```

---

Example

```

Scan MAC

↓

Validation Service

↓

MAC Repository

↓

Assign Second MAC

↓

Workflow Engine

↓

Update Session Panel

↓

Generate QR

```

---

Example

```

Finish

↓

Workflow Engine

↓

Device Service

↓

Audit Service

↓

Logger

↓

Return Home

```

---

# Signals

Recommended Signals

newTestRequested

nextRequested

previousRequested

repeatRequested

finishRequested

cancelRequested

historyRequested

settingsRequested

workflowChanged

sessionUpdated

qrUpdated

deviceUpdated

databaseError

validationError

workflowCompleted

---

# 15. Backend Integration

The UI should never know how anything works.

The UI only asks for actions.

Example

Wrong

```

button.clicked

↓

session.commit()

```

Correct

```

button.clicked

↓

workflow_engine.next()

↓

device_service.complete_step()

↓

repository.update()

↓

database

```

---

# UI → Backend Relationships

MainWindow

↓

WorkflowEngine

TestingPage

↓

WorkflowSession

↓

QRService

↓

DeviceService

↓

AuditService

↓

Repositories

↓

Database

---

# Service Responsibilities

Workflow Engine

Controls workflow.

QR Service

Generates QR images.

Device Service

Device validation.

Device updates.

Order Service

Order creation.

Order lookup.

Audit Service

Every database modification.

Every operator action.

Configuration Manager

Reads config.

Never writes workflow state.

Logger

Application logs.

Error logs.

Operator logs.

Workflow logs.

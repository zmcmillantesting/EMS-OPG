# 14. Web Frontend Development Guide

Version 1.0

---

# Purpose

This document defines the HTML, CSS, and JavaScript standards used throughout the EMS-OPG frontend.

It serves as the implementation guide for building and maintaining the user interface.

This document intentionally excludes backend implementation details.

---

# Frontend Goals

The interface should be:

- Fast
- Clean
- Professional
- Consistent
- Easy to navigate
- Optimized for production operators

The operator should always know:

- What step they are on
- What command to execute
- Which QR code to scan
- What action comes next

---

# Design Philosophy

The interface should resemble modern manufacturing software rather than a traditional website.

Visual design should prioritize:

- readability
- speed
- consistency

Avoid unnecessary decorations or animations.

Every page should focus on one primary task.

---

# Folder Structure

frontend/

```
frontend/

│

├── index.html

├── testing.html

├── history.html

├── settings.html

│

├── css/

│     main.css

│     layout.css

│     components.css

│     home.css

│     testing.css

│     history.css

│     settings.css

│

├── js/

│     api.js

│     common.js

│     home.js

│     testing.js

│     history.js

│     settings.js

│

├── components/

│     header.html

│     footer.html

│     navigation.html

│     qr_panel.html

│     command_panel.html

│

└── images/

```

---

# Directory Responsibilities

## html

Contains page layouts only.

No styling.

No business logic.

---

## css

Contains all application styling.

Global styling belongs in:

main.css

Page-specific styling belongs in:

testing.css

history.css

settings.css

---

## js

Contains page behavior.

Each page has its own JavaScript file.

Shared functions belong in:

common.js

Communication with Python belongs in:

api.js

---

## components

Reusable HTML sections shared by multiple pages.

Examples

Header

Footer

Navigation

QR Panel

Status Bar

---

# Naming Convention

HTML

kebab-case

```
testing.html

history.html

```

CSS

kebab-case

```
testing.css

main.css

```

JavaScript

camelCase

```
updateQr()

nextStep()

loadHistory()

```

CSS Classes

```
session-card

primary-button

status-bar

command-box

qr-panel

```

IDs

```
current-command

qr-image

next-button

previous-button

```

# Theme

Theme Name

Industrial Light

The interface should match other manufacturing applications currently used by operators.

---

# Color Palette

Background

```
#F8F9FA
```

Workspace

```
#FFFFFF
```

Primary Button

```
#2E7D32
```

Secondary Button

```
#F2F4F6
```

Border

```
#E1E6EB
```

Primary Text

```
#2C3E50
```

Secondary Text

```
#667085
```

Success

```
#2E7D32
```

Warning

```
#F9A825
```

Error

```
#D32F2F
```

Information

```
#1976D2
```

---

# Typography

Font

Segoe UI

Fallback

Arial

sans-serif

Buttons

18px

Body

16px

Titles

28px

Commands

Consolas

# Testing Page

Purpose

Guide the operator through the current workflow step.

The screen should contain only the information required to complete the current task.

---

Layout

```
+--------------------------------------------------------------+

 EMS-OPG                                    ⚙

---------------------------------------------------------------

Functional Test

Step 2 of 4

---------------------------------------------------------------

Current Command

+------------------------------------------------------------+

timeout 2s loopback /dev/port0[2-4] -q

+------------------------------------------------------------+

                          QR CODE

                  ████████████████

                  █              █

                  ████████████████

---------------------------------------------------------------

Previous          Home          Next

---------------------------------------------------------------

EMS-OPG v1.0

SQLite Connected

Workflow Ready

```

---

Displayed Information

- Current workflow name
- Current step
- Bash command
- QR code
- Navigation buttons
- Persistent status bar

---

Do Not Display

- Database information
- Session statistics
- Elapsed time
- Logging status
- Large side panels
- Advanced options

The testing screen should remain focused on the current workflow step.

# Frontend Development Plan

Phase 1

- Create frontend directory
- Build HTML page layouts
- Create CSS theme
- Create reusable components

---

Phase 2

- Build JavaScript utilities
- Create navigation
- Create API helper functions

---

Phase 3

- Connect workflow navigation
- Display QR codes
- Display workflow commands

---

Phase 4

- Build History page
- Build Settings page
- Add manual corrections

---

Phase 5

- UI polish
- Keyboard shortcuts
- Loading indicators
- Final testing
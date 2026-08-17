# System Architecture

## Overview

The system consists of two completely independent environments.

```
Company Network
        │
        │
        ▼
Flask Workflow Application
(HTML/CSS/JS frontend, served locally)
        │
        │
 (Human Operator)
        │
        ▼
Isolated Test Bench
```

The application is a flask server (`src/ems_opg/api/`) serving a
static
HTML/CSS/vanilla-JS frontend (`frontend/`) over a local
connection -- not a 
PyQt desktop application, despite earlier drafts of this documents. See
`docs/04_Project_Structure.md`

No direct communication exists between the application and the test bench.

The operator transfers information between the two systems by scanning QR codes.

---

## Workflow

```
Operator Login

↓

Select Production Order

↓

Select Device

↓

Application Displays QR Code

↓

Operator Scans QR Code

↓

Test Bench Executes Bash Command

↓

Operator Verifies Result

↓

Application Displays Next QR Code

↓

Operator scanned MAC Address label

↓
Generate QR Code with scanned MAC Address and next one (each board recives two MACs)

↓

↓

Operator Records

• Order Number
• Serial Number
• MAC Addresses
• Notes

↓

Save Traceability Record
```

---

## Responsibilities

### Workflow Application

Responsible for:

- Order management
- Device tracking
- QR code display
- Operator guidance
- Logging
- Database management
- Reporting
- Backups

The application is **not responsible** for executing Bash commands.

---

### Isolated Test Bench

Responsible for:

- Receiving scanned Bash commands
- Executing functional tests
- Displaying test results

The isolated test bench has no network communication with the application.

---

## Design Principle

The application manages the workflow.

The isolated test bench performs the testing.

Keeping these responsibilities separate simplifies the software and respects the network isolation requirements.
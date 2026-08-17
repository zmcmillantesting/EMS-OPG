# System Architecture

## Overview

The system consists of two completely independent environments.

```
Company Network
        │
        │
        ▼
EMS-OPG Desktop Window (PyWebView)
(HTML/CSS/JS frontend, served locally by waitress)
        │
        │
 (Human Operator)
        │
        ▼
Isolated Test Bench
```

The application is a Flask app (`src/ems_opg/api/`) serving a static
HTML/CSS/vanilla-JS frontend (`frontend/`), run behind a waitress WSGI
server and opened in a native PyWebView window rather than a browser tab —
operators never see a URL bar. See `docs/04_Project_Structure.md` and
`docs/11_Deployment.md`.

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
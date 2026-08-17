# EMS-OPG Documentation

Welcome to the developer documentation.


| Document | Description |
|----------|-------------|
| 01 | Project Overview |
| 02 | System Architecture |
| 03 | User Interface Specs |
| 04 | Project Structure |
| 05 | Database Design |
| 06 | UI/UX Guidelines |
| 07 | Configuration System Design |
| 08 | Logging |
| 09 | Backup & Recovery |
| 10 | Testing Strategy |
| 11 | Deployment |
| 12 | Git Workflow |
| 13 | Coding Standards |
| 14 | Frontend Development Guide |
| 15 | Release Process |
| 19 | Disaster Recovery |
| 20 | Development Environment Setup |
| 21 | Test Instructions |
| 22 | User Manual |
| 29 | Known Issues |
| 30 | Database Initialization |
| 31 | Test Workflow |
| 32 | Action Plan |
| 33 | Pre-Deployment Data Path Checklist |

Also in `docs/`: `flask_guide.md`, `todos.md`, `test_instructions.pdf`
(not numbered).

---

## Design Principles

- Modular
- Testable
- Secure
- Portable
- Maintainable
- Well documented

--- 

## Functional Requirements

- What does the application do:
    - Streamlines the OPG 409250, 409251, and 409252 PCBA functional testing while providing mac address, serial number, and order numbers traceability. 
    - tracks mac address usage by order number
    - tracks who and when made changes

- What problems are solved:
    - Prevents the need for manual bash testing entries
    - lack of mac address tracebility

- Who Uses is:
    - All test personell 

- Major Modules:
    - `core/` — application bootstrap, path resolution, config wiring
    - `api/` — Flask app and all `/api/*` routes
    - `database/` — SQLAlchemy models, engine, session, backup/restore
    - `repositories/` — per-model DB access (orders, devices, MAC pool, audit log)
    - `services/` — business logic (order provisioning, device reservation, QR command building)
    - `workflow/` — in-memory operator workflow/step state
    - `QR_Codes/` — QR command generation and per-step validation
    - `app_logging/` — logging setup (rotating file handler)
    - `frontend/` — static HTML/CSS/JS UI served by Flask
    - `scripts/` — standalone admin scripts (MAC pool import, weekly health report)


- Data Stored:
    - Order number
    - Serial number
    - Mac Address useability, printed or not, status
    - operator per mac address
    - changes made post functional test per mac-address
    - timestamp per mac address

## Non-Functional Requirements

- Supports multiple concurrent users
- Database backup every application shutdown
- startup under 10 seconds
- error logging
- smooth transitions between functional test steps
- mac address searching and filtering by operator, serial number and order number (under 2 seconds)
- audit all db changes
- offline capable
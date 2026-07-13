# EMS-OPG Documentation

Welcome to the developer documentation.

## Documentation

| Document | Description |
|----------|-------------|
| 01 | Project Overview |
| 02 | System Architecture |
| 03 | Development Standards |
| 04 | Project Structure |
| 05 | Database Design |
| 06 | UI/UX Guidelines |
| 07 | Security |
| 08 | Logging |
| 09 | Backup & Recovery |
| 10 | Testing Strategy |
| 11 | Deployment |
| 12 | Git Workflow |
| 13 | Coding Standards |
| 14 | API & Interfaces |
| 15 | Release Process |
| 16 | Roadmap |

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
    - 

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
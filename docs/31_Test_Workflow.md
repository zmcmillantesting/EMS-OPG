# Test Workflow

**Document Version:** 1.0

---

# Purpose

This document defines the complete operational workflow of the Production Test Workflow and Traceability System.

Unlike the System Architecture document, which explains **how the software is organized**, this document explains **how the operator uses the application** during production testing.

This workflow serves as the authoritative reference for developers, testers, operators, and project stakeholders.

---

# Overview

The application is used alongside an isolated functional test bench.

The application and the test bench **never communicate directly**.

Instead, the operator serves as the bridge between the two environments.

The application's responsibility is to:

- Guide the operator
- Display QR codes
- Record traceability information
- Store production records

The isolated test bench is responsible for:

- Receiving scanned Bash commands
- Executing functional tests
- Displaying results

---

# System Workflow

```
Production Network

┌──────────────────────────┐
│                          │
│ PyQt Workflow Application│
│                          │
└──────────────┬───────────┘
               │
               │ Human Operator
               ▼
┌──────────────────────────┐
│  Isolated Test Bench     │
│                          │
│ Linux Terminal           │
│ Device Under Test        │
└──────────────────────────┘
```

No network communication exists between these systems.

---

# Test Session

A **Test Session** represents the complete testing process for a single device.

Each session begins when the operator selects an order and ends when the traceability record is saved.

No database changes should be permanently committed until the session is completed successfully.

---

# Standard Workflow

```
Operator Login
        │
        ▼
Select Production Order
        │
        ▼
Create Test Session
        │
        ▼
Display QR Code
        │
        ▼
Operator Scans QR Code
        │
        ▼
Command Executes on Test Bench
        │
        ▼
Operator Confirms Completion
        │
        ▼
Display Next QR Code
        │
        ▼
Repeat Until Final Step
        │
        ▼
Enter Device Information
        │
        ▼
Review Summary
        │
        ▼
Save Traceability Record
        │
        ▼
End Session
```

---

# Operator Responsibilities

The operator is responsible for:

- Selecting the correct production order
- Scanning each QR code
- Verifying test completion
- Entering the correct Serial Number
- Entering the correct MAC Address
- Recording any post-test changes
- Saving the completed record

The operator is **not** responsible for manually typing Bash commands unless instructed by engineering.

---

# QR Code Workflow

Each QR code represents one client-provided Bash command.

Example:

```
Step 1

Display QR Code

↓

Operator scans QR

↓

Terminal receives command

↓

Command executes

↓

Operator confirms completion

↓

Application displays next QR
```

The application never executes or validates the command.

Its responsibility ends once the QR code has been displayed.

---

# Device Information Entry

After all QR code steps have been completed, the operator records:

- Serial Number
- MAC Address
- Order Number (if not already selected)
- Post-Test Changes
- Test Result (Pass / Fail)

Once validated, the record is saved to the database.

---

# Session Validation

Before a session may be completed, the application should verify:

- Production order selected
- Serial Number entered
- MAC Address entered
- Required workflow steps completed

If validation fails, the operator should receive a clear explanation of what information is missing.

---

# Session Cancellation

If testing is interrupted:

- No partial production record should be created.
- The session should be discarded.
- An audit log entry should record that the session was canceled.

---

# Error Recovery

Examples of recoverable errors include:

- Incorrect Serial Number entered
- Incorrect MAC Address entered
- QR code scanned out of order
- Operator cancels the session

The application should provide a method to restart or cancel the session without leaving incomplete records.

---

# Logging Requirements

The following events should be logged:

- Operator login
- Order selected
- Session started
- Session completed
- Session canceled
- Record saved
- Database backup
- Record modified
- Record deleted

The application should log workflow events rather than test execution.

---

# Future Expansion

The workflow is intentionally modular.

Future versions may include:

- Multiple production lines
- Multiple test benches
- Additional QR code sequences
- Additional traceability fields
- Automated reporting

These additions should not require redesigning the existing workflow.

---

# Guiding Principles

The workflow should always prioritize:

1. Simplicity
2. Repeatability
3. Traceability
4. Data Integrity
5. Operator Efficiency

Every screen should answer one question:

> **"What does the operator need to do next?"**

If a screen does not help answer that question, it should be reconsidered.
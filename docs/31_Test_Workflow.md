# Test Workflow

**Document Version:** 2.0

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

---

# Standard Workflow
Home Screen
│
▼
Operator enters Operator ID
│
▼
Operator selects an existing Order
(or creates one: order number + quantity)
│
▼
Operator enters Serial Number
│
▼
Start Test → navigates to Testing Screen
│
▼
QR Steps 1–4 (functional test)
│
▼
Pass / Fail prompt
│
┌────┴────┐
│ │
PASS FAIL
│ │
▼ ▼
Scan MAC1 Operator enters
(MAC2 auto- failure reason
assigned) │
│ │
▼ │
Verify MAC │
addresses │
│ │
└─────────┬─────────┘
▼
Device saved automatically
│
▼
Returns to Home Screen
(Operator ID retained,
order/serial re-prompted)

There is no separate "Save & Repeat" confirmation step — saving happens
automatically the instant a PASS is verified or a FAIL reason is
submitted, and the app returns straight to the order/serial entry screen
for the next unit.

---

# Order Number and Serial Number Are Captured First

Unlike the original design, serial number entry happens **before** the
functional test runs, not after — the operator applies the serial number
label to the physical unit up front. Order number is chosen from a
dropdown of already-created orders (created via a small "+ New Order"
action: order number + quantity, nothing else); it is not typed freely.

---

# MAC Addresses Are Assigned Only on PASS

A failed device never receives MAC addresses. Only once a device passes
does the operator scan MAC1 (from the physical label) — MAC2 is chosen
automatically as the next available address in the shared pool. Both are
then written to the device and verified via QR-scanned commands before
the record saves.

---

# Retesting a Failed Device

If a serial number previously failed under a given order, entering that
same order + serial again resumes testing on the **same** device record
rather than creating a new one. Its prior failure reason(s) remain
attached as history even after it eventually passes. A serial that has
already **passed** cannot be re-tested under the same order — the app
rejects starting a session for it.

---

# Operator Responsibilities

The operator is responsible for:

- Entering their Operator ID
- Selecting or creating the correct production order
- Applying and entering the correct Serial Number before testing begins
- Scanning each QR code during the functional test
- Recording a Pass/Fail result
- On PASS: scanning MAC1 and verifying both MAC addresses
- On FAIL: providing a clear failure reason

The operator is **not** responsible for manually typing Bash commands unless instructed by engineering.

---

# Session Validation

Before a device may be saved, the application verifies:

- Order selected and exists
- Serial Number entered and correctly formatted
- All four QR steps completed
- A Pass/Fail result recorded
- On PASS only: both MAC addresses assigned and verified

If validation fails, the operator receives a clear explanation of what's missing.

---

# Error Recovery

Examples of recoverable errors include:

- Wrong order selected — operator cancels and restarts from Home
- QR code scanned out of order
- MAC1 scanned doesn't match an available pool address (rejected immediately)
- Operator cancels the session before completion — no partial record is saved

---

# Logging Requirements

The following events are logged:

- Order created / corrected / deleted
- Test failed (with reason)
- Device manually corrected
- MAC addresses reset (undoing a PASS)
- Database backup
- CSV export

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
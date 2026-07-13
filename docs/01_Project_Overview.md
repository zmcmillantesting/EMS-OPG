# Project Overview

## Purpose

This application is a **Production Test Workflow and Traceability System** designed specifically for the manufacturing test department.

The application has two primary objectives:

1. **Reduce operator error and improve testing efficiency** by replacing manually typed Bash commands with QR codes that can be scanned directly into an isolated test bench.

2. **Provide complete traceability** for every tested device by recording the associated Order Number, Serial Number, MAC Address, operator information, timestamps, and post-test notes.

---

## Problem Statement

The functional test bench operates on an isolated network and cannot communicate directly with the production network.

Because of this isolation:

- Test commands cannot be transmitted electronically.
- Operators currently type lengthy Bash commands manually.
- Manual typing is slow and susceptible to transcription errors.

This application eliminates manual command entry by displaying QR codes that encode the required Bash commands. The operator scans each QR code into the isolated test bench, allowing the commands to be entered accurately and consistently.

---

## Scope

Version 1 of the application focuses exclusively on the functional testing department.

The application **does not**:

- Execute Bash commands.
- Communicate with the isolated test bench.
- Monitor test execution.
- Collect automated test results.

Instead, the application manages the operator workflow and maintains production traceability records.

---

## Primary Functions

### Workflow Management

- Display QR codes containing client-provided Bash commands.
- Guide the operator through each testing step.
- Track testing progress.

### Traceability

Store:

- Order Number
- Serial Number
- MAC Address
- Test Status
- Operator
- Timestamp
- Post-test changes

### Administration

- Database backups
- Logging
- Record searching
- CSV export
- Settings

---

## Guiding Philosophy

The application serves as a **workflow management system**, not a test execution system.

The operator acts as the bridge between the production network and the isolated test bench.
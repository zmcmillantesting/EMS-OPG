# UI / UX Guidelines

## Design Philosophy

The application is intended for production operators.

The interface should require minimal training and allow operators to work quickly while minimizing the chance of error.

The UI should always present the next required action.

---

# Primary Workflow

```
Select Order

↓

Select Device

↓

Display QR Code

↓

Scan QR Code

↓

Next Step

↓

Repeat

↓

Enter Device Information

↓

Save
```

---

# Main Test Window

```
-------------------------------------------------------

Order Number:
123456

--------------------------------------------

Serial Number

______________________

MAC Address

______________________

--------------------------------------------

Step 3 of 8

██████████████
█            █
█   QR CODE  █
█            █
██████████████

Description

Run Functional Test

--------------------------------------------

Previous        Next

-------------------------------------------------------
```

---

# Design Goals

- Large readable fonts
- High contrast
- Minimal typing
- Large buttons
- Keyboard friendly
- Scanner friendly
- Simple navigation

---

# Operator Workflow

The application does not evaluate test results.

Instead it:

1. Displays the appropriate QR code.
2. Waits for the operator to complete the step.
3. Advances to the next step.
4. Records traceability information.

---

# Workflow Engine

The application functions as a workflow engine.

Responsibilities include:

- Displaying QR codes
- Tracking workflow progress
- Recording production information
- Saving traceability records

The application does **not** execute Bash commands.

The isolated test bench remains responsible for all functional testing.
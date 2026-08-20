# Database Design

## Design Philosophy

The database is designed to provide production traceability rather than manage manufacturing processes.

The primary purpose of the database is to answer:

- Which MAC address belongs to which order?
- Which serial number belongs to which MAC address?
- Who tested the device?
- When was it tested?
- Has this device failed before, and why?

---

# Orders

Stores customer production orders. Orders are created explicitly by an
operator (order number + quantity only) before any testing against them
can begin — there is no MAC or device provisioning step anymore.

| Column | Description |
|---------|-------------|
| id | Primary Key |
| order_number | Customer Order Number, unique |
| quantity | Target device count for this order |
| status | Open / Closed |
| created_at | Record creation timestamp |

"Completed" for an order is computed, not stored: the count of its
`Device` rows with `test_result == "PASS"`. Remaining = `quantity - passed`.

---

# Devices

Stores traceability information for every tested device. A device row is
created the first time a serial number is tested under an order, and
**reused** on every subsequent retest of that same serial+order — it is
not append-only. Serial numbers are unique only within an order (the same
serial can appear under two different orders without conflict).

| Column | Description |
|---------|-------------|
| id | Primary Key |
| order_number | Foreign Key to Orders |
| serial_number | Device Serial Number (unique per order, not globally) |
| ethaddr_id | First MAC Address — **nullable** |
| eth1addr_id | Second MAC Address — **nullable** |
| used | True iff `test_result == "PASS"` — i.e. this device currently holds a MAC pair |
| test_result | PASS / FAIL |
| operator | Operator of the most recent test attempt |
| timestamp | Time of the most recent test attempt |
| created_at | Record created (first attempt) |
| updated_at | Last modified |
| post_test_changes | Notes entered after testing (manual corrections) |

A device that has only ever failed has `ethaddr_id`/`eth1addr_id` both
`NULL` — MAC addresses are claimed from the pool "à la carte," one pair at
a time, only at the moment a device passes. A FAIL never touches the MAC
pool.

---

# MAC Address Pool

Stores all MAC addresses the client provided. Unchanged by the workflow
redesign — this table has no concept of orders or devices; it is a flat
first-come-first-served pool.

| Column | Description |
|---------|-------------|
| id | Primary Key |
| mac_address | One address from the client-provided range |
| used | Whether this specific address has been claimed by a passing device |

---

# Device Failure Notes

One row per failed test attempt. Because a device row is reused across
retests, this table is the only place a full failure history survives —
a board that fails twice keeps both comments, even after it eventually
passes.

| Column | Description |
|---------|-------------|
| id | Primary Key |
| device_id | Foreign Key to Devices |
| timestamp | When this failure was recorded |
| operator | Who recorded it |
| reason | Free-text failure description |

---

# Audit Log

Records important application events.

| Column | Description |
|---------|-------------|
| id | Primary Key |
| timestamp | Event timestamp |
| operator | User responsible |
| action | Action performed |
| details | Additional information |

Examples:

- Order Created
- Order Corrected
- Order Deleted
- Test Failed
- Manual Correction
- MAC Reset
- Database Backup
- CSV Export

---

# Relationships
Orders
│
│ 1
│
│ *
Devices ──── * DeviceFailureNote

MACAddressPool (independent - referenced by MAC string, no FK)

# Audit Log

Each production order may contain multiple devices. Each device belongs
to exactly one production order. Each device may have zero or more
failure notes, accumulated across retests.

---

# Design Principles

- Use an internal integer ID as the primary key.
- Do not use the MAC Address as the primary key.
- Store business identifiers separately.
- Record timestamps for auditing.
- A device's identity is (order_number, serial_number) — not a
  provisioned slot. It exists in the database only once real testing has
  produced a result for it.
- MAC addresses are never reserved in advance. They are claimed
  individually, only at the moment of a PASS.


# Database Design

## Design Philosophy

The database is designed to provide production traceability rather than manage manufacturing processes.

The primary purpose of the database is to answer:

- Which MAC address belongs to which order?
- Which serial number belongs to which MAC address?
- Who tested the device?
- When was it tested?
- Were any post-test changes made?

---

# Orders

Stores customer production orders.

| Column | Description |
|---------|-------------|
| id | Primary Key |
| order_number | Customer Order Number |
| part_number | FIN |
| quantity | int |
| status | Open / Closed |
| created_at | Record creation timestamp |
---

# Devices

Stores traceability information for every tested device.

| Column | Description |
|---------|-------------|
| id | Primary Key |
| order_number | Foreign Key to Orders |
| serial_number | Device Serial Number |
| ethaddr_id | First MAC Address |
| ethaddr1_id | Second MAC Address |
| used | Boolean indicating MAC allocation |
| test_result | Pass / Fail |
| operator | Test Operator |
| timestamp | Time of testing |
| created_at | Record created |
| updated_at | Last modified |
| post_test_changes | Notes entered after testing |
| order | Orders that have used each device |

---

# MAC Address Pool

Stores all MAC addresses that client provided

| Column | Description |
|---------|-------------|
| id | Primary Key |
| mac_address | range provided by client |
| used | status of each unique mac address |

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

- Created Order
- Modified Device
- Deleted Record
- Database Backup
- CSV Export

---

# Relationships

```
Orders
   │
   │ 1
   │
   │ *
Devices

Audit Log
```

Each production order may contain multiple devices.

Each device belongs to exactly one production order.

---

# Design Principles

- Use an internal integer ID as the primary key.
- Do not use the MAC Address as the primary key.
- Store business identifiers separately.
- Record timestamps for auditing.
- Normalize production order information.

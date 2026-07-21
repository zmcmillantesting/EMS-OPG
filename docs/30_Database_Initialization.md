# Database Initialization and MAC Import Guide

This document explains how to initialize a new SQLite database for EMS-OPG and load the MAC address pool from the CSV file into that database.

## 1. Prerequisites

Before starting, make sure:

- Python is installed and the project virtual environment is active
- The project dependencies are installed
- The CSV file exists at [scripts/mac_addresses.csv](../scripts/mac_addresses.csv)

If needed, activate the virtual environment:

### Linux / WSL

```bash
source .venv/bin/activate
```

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

## 2. Initialize a new database

The application uses SQLite and expects the database file at [database/ems_opg.db](../database/ems_opg.db).

From the project root, run:

```bash
python -m src.ems_opg.database.init_db
```

This creates the database tables defined by the SQLAlchemy models.

If you want to verify that the database file exists, check:

```bash
ls database
```

## 3. Load MAC addresses into the database

The importer script reads the CSV file and inserts the MAC addresses into the `devices` table.

Run:

```bash
python scripts/load_database.py
```

The script will:

- read the MAC addresses from [scripts/mac_addresses.csv](../scripts/mac_addresses.csv)
- validate each MAC address format
- insert valid rows into the database
- skip duplicates
- verify that all imported addresses were stored successfully

## 4. Expected output

A successful run prints a summary similar to:

```text
MAC Database Initialization Complete
---------------------------------------
CSV Entries : 53504
Inserted    : 53504
Duplicates  : 0
Verified    : 53504
Missing     : 0
---------------------------------------
```

## 5. Troubleshooting

### Database file not created

- Confirm you ran the initialization command from the project root
- Check that [database/ems_opg.db](../database/ems_opg.db) exists after the command completes

### CSV file not found

- Ensure [scripts/mac_addresses.csv](../scripts/mac_addresses.csv) is present
- Confirm the working directory is the project root

### Import errors

- Check the log file at [logs/mac_database_initialization.log](../logs/mac_database_initialization.log)
- Re-run the importer after fixing the issue

## 6. Notes

- The importer expects the CSV to contain a `mac_address` column.
- If the database already contains an older schema, the importer will recreate the tables to match the current models.
- For a completely fresh import, delete or rename the old database file before re-initializing.

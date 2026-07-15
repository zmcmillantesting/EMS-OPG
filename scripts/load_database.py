"""
initialize_mac_database.py

One-time utility for importing the client's MAC address pool into the EMS OPG
database.

Features
--------
- Reads MAC addresses from a CSV file
- Validates MAC address format
- Skips duplicates already in the database
- Imports new MAC addresses
- Rolls back on failure
- Verifies every imported MAC exists
- Logs all activity
- Calculates SHA-256 checksum of the source CSV
"""

from __future__ import annotations

import csv
import hashlib
import logging
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import select

from src.ems_opg.database.models import Device
from src.ems_opg.database.session import SessionLocal


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CSV_FILE = Path("mac_addresses.csv")
LOG_FILE = Path("logs/mac_database_initialization.log")

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)

logger = logging.getLogger("MACImporter")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MAC_REGEX = re.compile(
    r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$"
)


def file_checksum(path: Path) -> str:
    """Return SHA-256 checksum of a file."""

    sha = hashlib.sha256()

    with path.open("rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)

    return sha.hexdigest()


def load_csv(path: Path) -> list[str]:
    """
    Read MAC addresses from CSV.
    """

    macs = []

    with path.open(newline="") as f:

        reader = csv.reader(f)

        for row in reader:

            if not row:
                continue

            mac = row[0].strip()

            if not mac:
                continue

            if not MAC_REGEX.match(mac):

                logger.warning(
                    "Skipping invalid MAC address: %s",
                    mac,
                )

                continue

            macs.append(mac)

    return macs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():

    logger.info("=" * 70)
    logger.info("Starting MAC Database Initialization")
    logger.info("=" * 70)

    print("Starting MAC Database Initialization")
    print(f"Checking CSV file: {CSV_FILE}")

    if not CSV_FILE.exists():

        msg = f"CSV file not found: {CSV_FILE}"
        logger.error(msg)
        print(msg)
        print(f"Please place the MAC address file at: {CSV_FILE.resolve()}")
        print(f"See log file for details: {LOG_FILE.resolve()}")

        return

    checksum = file_checksum(CSV_FILE)

    logger.info("CSV File: %s", CSV_FILE)
    logger.info("SHA256: %s", checksum)

    csv_macs = load_csv(CSV_FILE)

    logger.info("Read %d MAC addresses", len(csv_macs))

    inserted = 0
    duplicates = 0

    with SessionLocal() as session:

        try:

            for mac in csv_macs:

                exists = session.scalar(
                    select(Device).where(
                        Device.mac_address == mac
                    )
                )

                if exists:
                    duplicates += 1
                    continue

                session.add(
                    Device(
                        mac_address=mac,
                        used=False,
                        order_number=None,
                        serial_number=None,
                        operator=None,
                        timestamp=None,
                        post_testing_changes=None,
                    )
                )

                inserted += 1

            session.commit()

            logger.info(
                "Commit successful."
            )

        except Exception:

            session.rollback()

            logger.exception(
                "Database initialization failed."
            )

            raise

        logger.info("Beginning verification...")

        missing = []

        for mac in csv_macs:

            exists = session.scalar(
                select(Device).where(
                    Device.mac_address == mac
                )
            )

            if exists is None:
                missing.append(mac)

        if missing:

            logger.error(
                "Verification FAILED. %d MAC addresses missing.",
                len(missing),
            )

            for mac in missing:

                logger.error(
                    "Missing: %s",
                    mac,
                )

        else:

            logger.info(
                "Verification PASSED."
            )

    logger.info("")
    logger.info("Summary")
    logger.info("------------------------------")
    logger.info("CSV Entries      : %d", len(csv_macs))
    logger.info("Inserted         : %d", inserted)
    logger.info("Duplicates       : %d", duplicates)
    logger.info("Verified         : %d", len(csv_macs) - len(missing))
    logger.info("Missing          : %d", len(missing))
    logger.info("=" * 70)

    print()
    print("---------------------------------------")
    print("MAC Database Initialization Complete")
    print("---------------------------------------")
    print(f"CSV Entries : {len(csv_macs)}")
    print(f"Inserted    : {inserted}")
    print(f"Duplicates  : {duplicates}")
    print(f"Verified    : {len(csv_macs) - len(missing)}")
    print(f"Missing     : {len(missing)}")
    print("---------------------------------------")


if __name__ == "__main__":
    main()
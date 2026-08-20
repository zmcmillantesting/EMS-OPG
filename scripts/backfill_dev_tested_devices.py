"""
backfill_orders_devices.py

One-time utility for rebuilding real Order + Device history from
scripts/mac_addresses.csv's order_number/serial_number columns. This is
separate from load_database.py on purpose: load_database.py only ever
touches mac_address_pool (by mac_address/used), it deliberately ignores
order/serial columns entirely. This script is the other half - it reads
those same columns to recreate the Order and Device rows that the pool
import intentionally skips.

Run this AFTER load_database.py, so the MAC pool already reflects which
MACs are used before device history gets attached to them.

Order quantity cannot be derived from the CSV alone - the CSV only
records serials that were actually tested and MAC-assigned in the past,
which can be fewer than the real target quantity for an order that's
still in progress. Put any order whose real quantity differs from
"however many clean serials are in the CSV" in QUANTITY_OVERRIDES below.
"""

from __future__ import annotations

import csv
import logging
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ems_opg.core.validators import is_valid_order_number, is_valid_serial_number
from ems_opg.database.base import Base
from ems_opg.database.engine import engine
from ems_opg.database.models import Device, Order
from ems_opg.database.session import SessionLocal


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CSV_FILE = Path("scripts/mac_addresses.csv")
LOG_FILE = Path("logs/order_device_backfill.log")

# Real target quantity for an order, when it differs from the number of
# clean (2-MAC) serials found for that order in the CSV. Add entries here
# as needed - order_number -> quantity.
QUANTITY_OVERRIDES = {
    "9618.1": 450,
}

DEFAULT_OPERATOR = "894"

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)

logger = logging.getLogger("OrderDeviceBackfill")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_groups(path: Path) -> dict[str, dict[str, list[str]]]:
    """
    Read the CSV and group MAC addresses by (order_number, serial_number).

    Returns {order_number: {serial_number: [mac_address, ...]}}. Rows with
    no order_number or no serial_number are skipped - those are pool-only
    MACs that have never been assigned to a board.
    """

    groups: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            order_number = (row.get("order_number") or "").strip()
            serial_number = (row.get("serial_number") or "").strip()
            mac_address = (row.get("mac_address") or "").strip().upper()

            if not order_number or not serial_number or not mac_address:
                continue

            groups[order_number][serial_number].append(mac_address)

    return groups


def ensure_database_schema() -> None:
    Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    logger.info("=" * 70)
    logger.info("Starting Order/Device Backfill")
    logger.info("=" * 70)

    print("Starting Order/Device Backfill")
    print(f"Reading: {CSV_FILE}")

    if not CSV_FILE.exists():
        msg = f"CSV file not found: {CSV_FILE}"
        logger.error(msg)
        print(msg)
        return

    groups = load_groups(CSV_FILE)

    ensure_database_schema()

    orders_created = 0
    orders_skipped_existing = 0
    devices_created = 0
    devices_skipped_existing = 0
    irregular_serials: list[tuple[str, str, int]] = []
    invalid_serials: list[tuple[str, str]] = []
    invalid_orders: list[str] = []

    with SessionLocal() as session:
        try:
            for order_number, serials in groups.items():

                if not is_valid_order_number(order_number):
                    invalid_orders.append(order_number)
                    logger.warning("Skipping invalid order number: %s", order_number)
                    continue

                clean_serials = {
                    serial: macs for serial, macs in serials.items() if len(macs) == 2
                }

                for serial, macs in serials.items():
                    if len(macs) != 2:
                        irregular_serials.append((order_number, serial, len(macs)))
                        logger.warning(
                            "Skipping %s/%s - found %d MAC(s), expected 2",
                            order_number, serial, len(macs),
                        )

                order = session.query(Order).filter_by(order_number=order_number).one_or_none()

                if order is None:
                    quantity = QUANTITY_OVERRIDES.get(order_number, len(clean_serials))
                    order = Order(order_number=order_number, quantity=quantity)
                    session.add(order)
                    session.flush()
                    orders_created += 1
                    logger.info(
                        "Created order %s with quantity %d (%d clean serials in CSV)",
                        order_number, quantity, len(clean_serials),
                    )
                else:
                    orders_skipped_existing += 1
                    logger.info("Order %s already exists - leaving quantity as-is", order_number)

                for serial, macs in clean_serials.items():
                    if not is_valid_serial_number(serial):
                        invalid_serials.append((order_number, serial))
                        logger.warning("Skipping invalid serial number: %s/%s", order_number, serial)
                        continue

                    existing = (
                        session.query(Device)
                        .filter_by(order_number=order_number, serial_number=serial)
                        .one_or_none()
                    )
                    if existing is not None:
                        devices_skipped_existing += 1
                        continue

                    device = Device(
                        order_number=order_number,
                        serial_number=serial,
                        ethaddr_id=macs[0],
                        eth1addr_id=macs[1],
                        used=True,
                        test_result="PASS",
                        operator=DEFAULT_OPERATOR,
                    )
                    session.add(device)
                    devices_created += 1

            session.commit()
            logger.info("Commit successful.")

        except Exception:
            session.rollback()
            logger.exception("Backfill failed.")
            raise

    logger.info("")
    logger.info("Summary")
    logger.info("------------------------------")
    logger.info("Orders created          : %d", orders_created)
    logger.info("Orders already existed  : %d", orders_skipped_existing)
    logger.info("Devices created         : %d", devices_created)
    logger.info("Devices already existed : %d", devices_skipped_existing)
    logger.info("Irregular serials       : %d", len(irregular_serials))
    logger.info("Invalid serial numbers  : %d", len(invalid_serials))
    logger.info("Invalid order numbers   : %d", len(invalid_orders))

    print()
    print("---------------------------------------")
    print("Order/Device Backfill Complete")
    print("---------------------------------------")
    print(f"Orders created          : {orders_created}")
    print(f"Orders already existed  : {orders_skipped_existing}")
    print(f"Devices created         : {devices_created}")
    print(f"Devices already existed : {devices_skipped_existing}")
    print(f"Irregular serials       : {len(irregular_serials)}")
    for order_number, serial, count in irregular_serials:
        print(f"  - {order_number}/{serial}: {count} MAC(s) found, expected 2")
    if invalid_serials:
        print(f"Invalid serial numbers   : {len(invalid_serials)}")
        for order_number, serial in invalid_serials:
            print(f"  - {order_number}/{serial}")
    if invalid_orders:
        print(f"Invalid order numbers    : {len(invalid_orders)}")
        for order_number in invalid_orders:
            print(f"  - {order_number}")
    print("---------------------------------------")
    print(f"See log file for details: {LOG_FILE.resolve()}")


if __name__ == "__main__":
    main()

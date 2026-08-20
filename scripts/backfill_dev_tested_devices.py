"""
backfill_dev_test_devices.py

One-time utility: creates the Order + Device traceability records that
scripts/load_database.py intentionally didn't - that script only ever
marks MAC pool entries as used=True, since MACAddressPool has no
order/serial columns at all. This script reads the same
temp_mac_tracker.csv and builds the actual Device rows (and their parent
Orders) so this dev-testing history shows up in the app's history/order
views, not just as "unavailable" pool entries.

Must run AFTER load_database.py has already marked these MACs used=True
in the pool - this script does not touch MACAddressPool, it only adds
Device/Order rows on top of that already-correct pool state.

Safe to re-run: a serial that already has a Device row is left alone,
not duplicated or overwritten.
"""

from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import select

from ems_opg.database.base import Base
from ems_opg.database.engine import engine
from ems_opg.database.models import Device, Order
from ems_opg.database.session import SessionLocal


# ---------------------------------------------------------------------------
# Configuration - edit these two before running
# ---------------------------------------------------------------------------

TRACKER_CSV = Path("scripts/temp_mac_tracker.csv")
OPERATOR = "894"

MAC_REGEX = re.compile(r"^[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5}$")


def load_groups(path: Path) -> dict[tuple[str, str], list[str]]:
    """
    Group tracker rows into {(order_number, serial_number): [mac, mac]}.
    Skips blank/malformed rows (the tracker's known trailing garbage
    block) the same way the merge script did.
    """

    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    header = [c.strip().lower() for c in rows[0]]
    mac_i, order_i, serial_i = header.index("mac"), header.index("order"), header.index("serial")

    groups: dict[tuple[str, str], list[str]] = defaultdict(list)

    for row in rows[1:]:
        if len(row) <= mac_i:
            continue

        mac = row[mac_i].strip().upper()
        if not MAC_REGEX.match(mac):
            continue

        order = row[order_i].strip() if len(row) > order_i else ""
        serial = row[serial_i].strip() if len(row) > serial_i else ""

        if not order or not serial:
            continue

        groups[(order, serial)].append(mac)

    return groups


def main():
    if not TRACKER_CSV.exists():
        sys.exit(
            f"Not found: {TRACKER_CSV} - this script needs the tracker file "
            "to still exist. Restore it from git history if you already "
            "deleted it, then re-run."
        )

    Base.metadata.create_all(bind=engine)

    groups = load_groups(TRACKER_CSV)

    clean = {k: v for k, v in groups.items() if len(v) == 2}
    irregular = {k: v for k, v in groups.items() if len(v) != 2}

    if irregular:
        print(f"Skipping {len(irregular)} serial(s) with an irregular MAC count (not exactly 2):")
        for (order, serial), macs in irregular.items():
            print(f"  {order} / {serial}: {macs}")
        print()

    quantities: dict[str, int] = defaultdict(int)
    for (order, _serial) in clean:
        quantities[order] += 1

    created_orders = 0
    created_devices = 0
    already_existed = 0

    with SessionLocal() as session:
        try:
            order_cache: dict[str, Order] = {}

            for (order_number, serial_number), macs in clean.items():
                order = order_cache.get(order_number)
                if order is None:
                    order = session.scalar(
                        select(Order).where(Order.order_number == order_number)
                    )
                    if order is None:
                        order = Order(
                            order_number=order_number,
                            quantity=quantities[order_number],
                        )
                        session.add(order)
                        session.flush()
                        created_orders += 1
                    order_cache[order_number] = order

                existing = session.scalar(
                    select(Device)
                    .where(Device.order_number == order_number)
                    .where(Device.serial_number == serial_number)
                )
                if existing is not None:
                    already_existed += 1
                    continue

                now = datetime.now(UTC)
                session.add(Device(
                    order_number=order_number,
                    serial_number=serial_number,
                    ethaddr_id=macs[0],
                    eth1addr_id=macs[1],
                    used=True,
                    test_result="PASS",
                    operator=OPERATOR,
                    timestamp=now,
                    created_at=now,
                    updated_at=now,
                ))
                created_devices += 1

            session.commit()

        except Exception:
            session.rollback()
            raise

    print("---------------------------------------")
    print("Backfill complete")
    print("---------------------------------------")
    print(f"Orders created         : {created_orders}")
    print(f"Devices created        : {created_devices}")
    print(f"Devices already present: {already_existed}")
    print(f"Skipped (irregular)    : {len(irregular)}")


if __name__ == "__main__":
    main()
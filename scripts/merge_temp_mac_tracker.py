"""
merge_temp_mac_tracker.py

One-time utility: folds scripts/temp_mac_tracker.csv (order/MAC/serial
records from dev testing) into scripts/mac_addresses.csv, marking every
MAC that was actually written to a real board as used=True with its
order/serial - instead of the flat used=False every row currently has.

Every MAC in the tracker is already present in mac_addresses.csv (same
underlying block), so this only ever upgrades existing rows, never adds
new ones. A row already marked used=True is left alone rather than
overwritten, so re-running this is safe.

Malformed/blank tracker rows (a 37-row trailing block of truncated MACs
with no serial, left over from however this file was exported) are
skipped and reported, not treated as errors.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MAC_ADDRESSES_CSV = ROOT / "scripts" / "mac_addresses.csv"
TRACKER_CSV = ROOT / "scripts" / "temp_mac_tracker.csv"

MAC_REGEX = re.compile(r"^[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5}$")


def load_pool(path: Path) -> tuple[list[str], dict[str, dict]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        pool = {}
        for row in reader:
            mac = row["mac_address"].strip().upper()
            clean = {k: (v.strip() if v else "") for k, v in row.items()}
            clean["mac_address"] = mac
            pool[mac] = clean
    return fieldnames, pool


def load_tracker(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    header = [c.strip().lower() for c in rows[0]]
    mac_i, order_i, serial_i = header.index("mac"), header.index("order"), header.index("serial")

    entries = []
    skipped = 0

    for row in rows[1:]:
        if len(row) <= mac_i:
            skipped += 1
            continue

        mac = row[mac_i].strip().upper()
        if not MAC_REGEX.match(mac):
            skipped += 1
            continue

        entries.append({
            "mac_address": mac,
            "order_number": row[order_i].strip() if len(row) > order_i else "",
            "serial_number": row[serial_i].strip() if len(row) > serial_i else "",
        })

    print(f"Tracker: {len(entries)} valid rows, {skipped} skipped (blank/malformed).")
    return entries


def main():
    if not MAC_ADDRESSES_CSV.exists():
        sys.exit(f"Not found: {MAC_ADDRESSES_CSV}")
    if not TRACKER_CSV.exists():
        sys.exit(f"Not found: {TRACKER_CSV}")

    fieldnames, pool = load_pool(MAC_ADDRESSES_CSV)
    tracker_entries = load_tracker(TRACKER_CSV)

    upgraded = 0
    added = 0
    already_used = 0
    duplicate_serial_macs = 0

    seen_macs_this_run = set()

    for entry in tracker_entries:
        mac = entry["mac_address"]

        if mac in seen_macs_this_run:
            duplicate_serial_macs += 1
        seen_macs_this_run.add(mac)

        if mac in pool:
            if pool[mac].get("used", "").lower() == "true":
                already_used += 1
                continue
            pool[mac]["used"] = "True"
            pool[mac]["order_number"] = entry["order_number"]
            pool[mac]["serial_number"] = entry["serial_number"]
            upgraded += 1
        else:
            # Not expected given the current files (every tracker MAC is
            # already in the pool), but handled in case that changes.
            pool[mac] = {name: "" for name in fieldnames}
            pool[mac]["mac_address"] = mac
            pool[mac]["order_number"] = entry["order_number"]
            pool[mac]["serial_number"] = entry["serial_number"]
            pool[mac]["used"] = "True"
            added += 1

    with MAC_ADDRESSES_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for mac in sorted(pool):
            writer.writerow(pool[mac])

    print()
    print("---------------------------------------")
    print("Merge complete")
    print("---------------------------------------")
    print(f"Upgraded to used=True : {upgraded}")
    print(f"Already used=True     : {already_used}")
    print(f"New rows added        : {added}")
    print(f"Final pool size       : {len(pool)}")
    print(f"Final used=True count : {sum(1 for v in pool.values() if v.get('used','').lower()=='true')}")


if __name__ == "__main__":
    main()
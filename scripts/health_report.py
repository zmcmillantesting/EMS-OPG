"""
health_report.py

Weekly operational health report for EMS-OPG.

Standalone script - run this on a schedule (Windows Task Scheduler / cron).
It does not require the Flask app to be running. Writes a plain-text
summary to the exports/ directory under the configured data root
(config.json's "data_root", resolved via PathManager).
"""

from __future__ import annotations

import shutil
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for path in (SRC, ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from sqlalchemy import select

from ems_opg.core.paths_manager import PathManager
from ems_opg.database.database import DatabaseManager
from ems_opg.database.models import AuditLog, Device, MACAddressPool, Order

RECENT_AUDIT_ACTIONS = ("Test Failed", "Manual Correction", "MAC Reset")
RECENT_AUDIT_WINDOW_DAYS = 7


def collect_report(paths: PathManager) -> str:
    db = DatabaseManager()
    lines = []

    lines.append("=" * 70)
    lines.append(
        f"EMS-OPG Health Report - "
        f"{datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}"
    )
    lines.append("=" * 70)
    lines.append("")

    if not db.health_check():
        lines.append("DATABASE: UNREACHABLE")
        lines.append("")
        lines.append("Unable to query the database - remaining checks skipped.")
        return "\n".join(lines) + "\n"

    lines.append("DATABASE: reachable")
    lines.append("")

    with db.session() as session:
        total_macs = session.query(MACAddressPool).count()
        used_macs = session.query(MACAddressPool).filter_by(used=True).count()
        available_macs = total_macs - used_macs

        lines.append("MAC Address Pool")
        lines.append("-" * 70)
        lines.append(f"  Total     : {total_macs}")
        lines.append(f"  Used      : {used_macs}")
        lines.append(f"  Available : {available_macs}")
        lines.append("")

        open_orders = []
        for order in session.scalars(select(Order)).all():
            devices = session.scalars(
                select(Device).where(Device.order_number == order.order_number)
            ).all()
            completed = sum(1 for d in devices if d.used)
            if completed < order.quantity:
                open_orders.append((order.order_number, completed, order.quantity))

        lines.append("Open Orders")
        lines.append("-" * 70)
        lines.append(f"  Count: {len(open_orders)}")
        for order_number, completed, quantity in open_orders:
            lines.append(f"    {order_number}: {completed}/{quantity} devices completed")
        lines.append("")

        cutoff = datetime.now(UTC) - timedelta(days=RECENT_AUDIT_WINDOW_DAYS)
        recent_flags = session.scalars(
            select(AuditLog)
            .where(AuditLog.timestamp >= cutoff)
            .where(AuditLog.action.in_(RECENT_AUDIT_ACTIONS))
            .order_by(AuditLog.timestamp.desc())
        ).all()

        lines.append(f"Audit Flags - last {RECENT_AUDIT_WINDOW_DAYS} days")
        lines.append("-" * 70)
        lines.append(f"  Count: {len(recent_flags)}")
        for entry in recent_flags:
            lines.append(
                f"    [{entry.timestamp}] {entry.action} - "
                f"{entry.operator}: {entry.details}"
            )
        lines.append("")

    lines.append("Storage")
    lines.append("-" * 70)
    try:
        usage = shutil.disk_usage(paths.data_root)
        free_gb = usage.free / (1024 ** 3)
        total_gb = usage.total / (1024 ** 3)
        lines.append(f"  Data root : {paths.data_root}")
        lines.append(f"  Free      : {free_gb:.1f} GB / {total_gb:.1f} GB")
    except OSError as error:
        lines.append(f"  Unable to read disk usage for {paths.data_root}: {error}")
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> None:
    paths = PathManager()
    paths.create_directories()

    report = collect_report(paths)

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    destination = paths.exports_dir / f"health_report_{timestamp}.txt"
    destination.write_text(report, encoding="utf-8")

    print(report)
    print(f"Report written to {destination}")


if __name__ == "__main__":
    main()

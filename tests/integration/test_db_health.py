"""
Integration Tests - Database Health

Read-only sanity checks against the real application database: confirms
the file exists, is reachable, its tables are queryable, and — when data
has actually been loaded (e.g. via load_database.py) — that the file size
and MAC address pool look like a genuinely populated database rather than
an empty or corrupted one.

These tests never write to the database.
"""

import pytest

from ems_opg.database.database import DatabaseManager
from ems_opg.database.engine import DATABASE_FILE
from ems_opg.database.models import AuditLog, Device, MACAddressPool, Order

# A freshly-created, schema-only SQLite file is a few dozen KB. Anything
# meaningfully populated with the client's MAC range is far larger than this.
POPULATED_SIZE_THRESHOLD_BYTES = 100_000


def test_database_file_exists():
    assert DATABASE_FILE.exists(), f"Database file not found at {DATABASE_FILE}"


def test_database_is_reachable():
    db = DatabaseManager()
    assert db.health_check() is True


def test_database_tables_are_queryable():
    db = DatabaseManager()

    with db.session() as session:
        counts = {
            "orders": session.query(Order).count(),
            "devices": session.query(Device).count(),
            "mac_address_pool": session.query(MACAddressPool).count(),
            "audit_log": session.query(AuditLog).count(),
        }

    for table, count in counts.items():
        assert count >= 0, f"Query against {table} did not return a valid count"


def test_mac_pool_used_and_available_add_up_to_total():
    db = DatabaseManager()

    with db.session() as session:
        total = session.query(MACAddressPool).count()
        used = session.query(MACAddressPool).filter_by(used=True).count()
        available = session.query(MACAddressPool).filter_by(used=False).count()

    assert used + available == total, (
        "Used + available MAC counts should always add up to the pool total "
        f"(used={used}, available={available}, total={total})"
    )


def test_mac_pool_is_populated_with_client_data():
    db = DatabaseManager()

    with db.session() as session:
        total = session.query(MACAddressPool).count()

    if total == 0:
        pytest.skip(
            "MAC address pool is empty in this environment — "
            "run scripts/load_database.py to load the client's MAC range."
        )

    assert total > 1000, (
        f"MAC address pool has only {total} entries — expected the full "
        "client-provided range to be loaded."
    )

    size = DATABASE_FILE.stat().st_size
    assert size > POPULATED_SIZE_THRESHOLD_BYTES, (
        f"Database file is only {size} bytes despite {total} MAC pool rows — "
        "expected a database this size to be well over "
        f"{POPULATED_SIZE_THRESHOLD_BYTES} bytes."
    )

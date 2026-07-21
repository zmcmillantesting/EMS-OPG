import argparse
import sys
from pathlib import Path

from sqlalchemy import inspect

if __package__ in {None, ""}:
    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    SRC_ROOT = PROJECT_ROOT / "src"

    for path in (SRC_ROOT, PROJECT_ROOT):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))

    from ems_opg.database.base import Base
    from ems_opg.database.engine import DATABASE_FILE, engine
    from ems_opg.database import models  # noqa: F401
else:
    from .base import Base
    from .engine import DATABASE_FILE, engine
    from . import models  # noqa: F401


def is_schema_outdated() -> bool:
    if not DATABASE_FILE.exists():
        return False

    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    required_tables = {"orders", "devices", "audit_log"}

    if not required_tables.issubset(tables):
        return True

    order_columns = {column["name"] for column in inspector.get_columns("orders")}
    if "quantity" not in order_columns:
        return True

    return False


def recreate_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def init_database(force: bool = False) -> None:
    if force:
        recreate_database()
        print("Database schema recreated.")
        return

    if not DATABASE_FILE.exists():
        Base.metadata.create_all(bind=engine)
        print("Database initialized.")
        return

    if is_schema_outdated():
        print("Schema is outdated. Recreating database.")
        recreate_database()
        return

    Base.metadata.create_all(bind=engine)
    print("Database schema is already up to date.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize the EMS-OPG database."
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Drop and recreate the database schema from current models.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    init_database(force=args.recreate)

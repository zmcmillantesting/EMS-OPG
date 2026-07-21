import sys
from pathlib import Path

if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[3]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from ems_opg.database.base import Base
    from ems_opg.database.engine import engine
    from ems_opg.database import models  # noqa: F401
else:
    from .base import Base
    from .engine import engine
    from . import models  # noqa: F401


def init_database():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_database()
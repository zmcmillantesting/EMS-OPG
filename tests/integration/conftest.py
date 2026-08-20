from types import SimpleNamespace

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ems_opg.database.base import Base
import ems_opg.database.database as database_module


@pytest.fixture()
def session():
    """
    Create a brand-new in-memory database for every test.
    """

    engine = create_engine("sqlite:///:memory:")

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(engine)

    session = TestingSessionLocal()

    yield session

    session.close()


class _StubLogger:
    def info(self, *args, **kwargs):
        pass

    def exception(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


class _StubConfig:
    backup = {"max_backups": 5}

    def load(self):
        pass


@pytest.fixture()
def test_db(tmp_path, monkeypatch):
    """
    Points DatabaseManager at an isolated, file-backed SQLite database for
    the duration of one test. File-backed (not :memory:) because routes.py
    opens a brand-new DatabaseManager()/session per request - an
    in-memory DB would reset on every connection unless every route
    handler shared one connection, which they don't.

    Patched on ems_opg.database.database (where DatabaseManager imports
    SessionLocal from), not ems_opg.database.session (where it's
    defined) - Python binds names at import time, so patching the
    original module wouldn't affect the already-imported reference.
    """

    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)

    TestSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    monkeypatch.setattr(database_module, "SessionLocal", TestSessionLocal)

    return TestSessionLocal


@pytest.fixture()
def seed(test_db):
    """
    Insert rows directly ahead of hitting routes through the Flask test
    client - e.g. an Order and some MACAddressPool entries a workflow
    test needs to already exist.
    """

    def _seed(*objects):
        session = test_db()
        session.add_all(objects)
        session.commit()
        session.close()

    return _seed


@pytest.fixture()
def client(test_db, tmp_path):
    """
    A Flask test client wired to the isolated test_db, with a minimal
    stand-in Application object (paths/config/logger) satisfying what
    create_app() and the route handlers touch.
    """

    from ems_opg.api.server import create_app

    root = tmp_path / "app"
    (root / "frontend").mkdir(parents=True)

    application = SimpleNamespace(
        paths=SimpleNamespace(
            root=root,
            qr_cache=tmp_path / "qr_cache",
            exports_dir=tmp_path / "exports",
            logs_dir=tmp_path / "logs",
            backup_dir=tmp_path / "backups",
        ),
        config=_StubConfig(),
        logger=_StubLogger(),
    )

    app = create_app(application)
    app.testing = True

    with app.test_client() as test_client:
        yield test_client
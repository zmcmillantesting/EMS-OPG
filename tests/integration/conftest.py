import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ems_opg.database.base import Base


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

from .base import Base
from .engine import engine

# Import models so SQLAlchemy knows about them
from . import models


def init_database():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_database()
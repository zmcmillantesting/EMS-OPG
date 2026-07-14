"""
Database initialization.
"""

from ems_opg.database.base import Base
from ems_opg.database.engine import engine

from datetime import datetime
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column


# Import every model here
# from ems_opg.database.models.user import User


def initialize_database() -> None:
    """
    Create all missing database tables.
    """
    Base.metadata.create_all(bind=engine)
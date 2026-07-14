"""
Database manager.
"""

from contextlib import contextmanager

from sqlalchemy import text

from ems_opg.database.session import SessionLocal


class DatabaseManager:
    """
    Handles database connections and sessions.
    """

    @contextmanager
    def session(self):
        session = SessionLocal()

        try:
            yield session
            session.commit()

        except Exception: #TODO: create custom db exception
            session.rollback()
            raise

        finally:
            session.close()

    def health_check(self) -> bool:
        """
        Verify the database is reachable.
        """

        try:
            with self.session() as session:
                session.execute(text("SELECT 1"))
            return True

        except Exception:
            return False
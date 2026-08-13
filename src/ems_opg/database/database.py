"""
Database manager.
"""
import shutil
from contextlib import contextmanager
from datetime import UTC, datetime
from sqlalchemy import text
from pathlib import Path

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
        
    def backup(self, source: Path, backup_dir: Path, keep: int = 5) -> Path:
        """
        Copy the database file into backup_dir with a timestamped name,
        then prune down to the `keep` most recent backups.
        """

        if not source.exists():
            raise FileNotFoundError(f"No database file found at {source}")

        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        destination = backup_dir / f"ems_opg_{timestamp}.db"

        shutil.copy2(source, destination)

        self._prune_backups(backup_dir, keep)

        return destination

    def _prune_backups(self, backup_dir: Path, keep: int) -> None:
        backups = sorted(
            backup_dir.glob("ems_opg_*.db"),
            key=lambda path: path.stat().st_mtime,
        )

        excess = max(0, len(backups) - keep)

        for stale in backups[:excess]:
            stale.unlink()
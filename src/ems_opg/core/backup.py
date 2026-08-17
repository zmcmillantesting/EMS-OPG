"""
Shared automatic-backup trigger, used on both application startup and
shutdown. Which one(s) actually run is controlled entirely by
config.json's "backup" section - see docs/09_Backup_and_Recovery.md.
"""

from ems_opg.database.database import DatabaseManager
from ems_opg.database.engine import DATABASE_FILE


def run_backup_if_enabled(app, trigger: str) -> None:
    """
    Create a database backup if config.backup.enabled and
    config.backup[trigger] are both true. `trigger` is
    "backup_on_startup" or "backup_on_shutdown".
    """

    backup_config = app.config.backup

    if not backup_config.get("enabled", True):
        return

    if not backup_config.get(trigger, False):
        return

    try:
        db = DatabaseManager()
        destination = db.backup(
            DATABASE_FILE,
            app.paths.backup_dir,
            keep=backup_config.get("max_backups", 5),
        )
        app.logger.info("Database backed up to %s (%s)", destination.name, trigger)

    except Exception:
        app.logger.exception("Database backup failed (%s).", trigger)

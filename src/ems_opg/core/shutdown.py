from src.ems_opg.app_logging.logger import Logger
from src.ems_opg.database.database import DatabaseManager
from src.ems_opg.database.engine import DATABASE_FILE

class Shutdown:

    def __init__(self, app):

        self.app = app
        self.app.logger = Logger().get_logger()
        self.logger = self.app.logger

    def shutdown(self):

        self.app.logger.info("Shutdown requested.")
        self.app.logger.info("=" * 60)

        self.app.logger.info("Closing database...")
        self.backup_database()
        self.app.logger.info("Saving configuration...")
        self.app.logger.info("Application shutdown complete.")
        self.app.logger.info("=" * 60)

    def backup_database(self):

        backup_config = self.app.config.backup

        if not backup_config.get("enabled", True):
            return

        if not backup_config.get("backup_on_shutdown", False):
            return

        try:
            db = DatabaseManager()
            destination = db.backup(
                DATABASE_FILE,
                self.app.paths.backup_dir,
                keep=backup_config.get("max_backups", 5),
            )
            self.app.logger.info("Database backed up to %s", destination.name)

        except Exception:
            self.app.logger.exception("Database backup failed during shutdown.")

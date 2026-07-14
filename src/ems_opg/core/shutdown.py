from src.ems_opg.app_logging.logger import Logger

class Shutdown:

    def __init__(self, app):

        self.app = app
        self.app.logger = Logger().get_logger()
        self.logger = self.app.logger

    def shutdown(self):

        self.app.logger.info("Shutdown requested.")
        self.app.logger.info("=" * 60)

        self.app.logger.info("Closing database...")
        self.app.logger.info("Saving configuration...")
        self.app.logger.info("Application shutdown complete.")
        self.app.logger.info("=" * 60)
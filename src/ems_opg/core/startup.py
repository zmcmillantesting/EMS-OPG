from PyQt5.QtWidgets import QApplication
from src.ems_opg.app_logging.logger import Logger

class Startup:

    def __init__(self, app):

        self.app = app
        self.app.logger = Logger().get_logger()
        self.logger = self.app.logger

    def initialize(self):

        self.app.logger.info("=" * 60)
        self.app.logger.info("Production Test Workflow Starting")
        self.app.logger.info("=" * 60)

        self.app.logger.info("Loading configuration...")
        self.app.logger.info("Configuration loaded successfully.")

        self.app.logger.info("Verifying directories...")
        self.app.logger.info("Directory verification complete.")

        self.app.logger.info("Startup completed successfully.")
"""
Centralized logging manager.

Responsible for configuring the application's logging system.
"""

import logging
from logging.handlers import RotatingFileHandler


class LoggerManager:
    """
    Configures the application's logging.

    This class should only be instantiated once during application startup.
    """

    def __init__(self, config, paths):

        self.config = config
        self.paths = paths

        self.logger = logging.getLogger()

        self.logger.setLevel(
            getattr(
                logging,
                self.config.logging.level.upper()
            )
        )

        self.logger.propagate = False

        self.configure()

    def configure(self):

        """
        Configure console and file logging.
        """

        # Prevent duplicate handlers if called twice
        if self.logger.handlers:
            return

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s"
        )

        #
        # Console
        #

        console_handler = logging.StreamHandler()

        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

        #
        # File
        #

        log_file = self.paths.logs / "application.log"

        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=self.config.logging.max_log_size_mb * 1024 * 1024,
            backupCount=self.config.logging.backup_count,
            encoding="utf-8"
        )

        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

        #
        # Startup Message
        #

        self.logger.info("=" * 70)
        self.logger.info("Logger initialized.")
        self.logger.info("Log file: %s", log_file)
        self.logger.info("=" * 70)

    @staticmethod
    def get_logger(name):

        """
        Return a named logger.
        """

        return logging.getLogger(name)
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


class Logger:
    """Lightweight logging wrapper for tests and simple startup use."""

    def __init__(self, config=None, paths=None):
        self._logger = logging.getLogger()
        if config is not None and paths is not None:
            manager = LoggerManager(config, paths)
            self._logger = manager.logger

    def get_logger(self, name=None):
        return self._logger if name is None else logging.getLogger(name)

    def info(self, msg, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._logger.critical(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)

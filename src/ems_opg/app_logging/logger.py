"""
Logging module for the EMS-OPG application.

Usage:
    from logger import logging
    logger = logging.getLogger(__name__)
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")
    logger.debug("This is a debug message.")
"""
import logging

class Logger:
    """
    Logger class for the EMS-OPG application. This class provides a centralized logging mechanism for the application.
    """
    def __init__(self):
        """
        Initializes the Logger instance.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)

        # Create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Add formatter to console handler
        ch.setFormatter(formatter)

        # Add console handler to logger
        self.logger.addHandler(ch)

        print("Logger initialized")

    def get_logger(self):
        """
        Returns the logger instance.

        Returns:
            logging.Logger: The logger instance.
        """
        return self.logger
    
    def info(self, message):
        """
        Logs an info message.

        Args:
            message (str): The message to log.
        """
        self.logger.info(message)

    def warning(self, message):
        """
        Logs a warning message.

        Args:
            message (str): The message to log.
        """
        self.logger.warning(message)

    def error(self, message):
        """
        Logs an error message.

        Args:
            message (str): The message to log.
        """
        self.logger.error(message)

    def critical(self, message):
        """
        Logs a critical message.

        Args:
            message (str): The message to log.
        """
        self.logger.critical(message)

    def debug(self, message):
        """
        Logs a debug message.

        Args:
            message (str): The message to log.
        """
        self.logger.debug(message)
"""
Logging verification tests for the EMS-OPG application.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ems_opg.app_logging.logger import Logger

def test_logger_initialization():
    logger = Logger()
    assert logger.get_logger() is not None

def test_logger_info_message():
    logger = Logger()
    logger.info("This is an info message.")

def test_logger_warning_message():
    logger = Logger()
    logger.warning("This is a warning message.")

def test_logger_error_message():
    logger = Logger()
    logger.error("This is an error message.")

def test_logger_critical_message():
    logger = Logger()
    logger.critical("This is a critical message.")

def test_logger_debug_message():
    logger = Logger()
    logger.debug("This is a debug message.")
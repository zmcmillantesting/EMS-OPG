"""
Application-wide constants.

This module contains values that should remain constant throughout the
application's lifetime. Configuration values that may change between
environments belong in the configuration manager instead.
"""

from pathlib import Path

# ==========================================================
# Application Information
# ==========================================================

APP_NAME = "EMS OPG"
APP_VERSION = "0.1.0"

# ==========================================================
# Project Directories
# ==========================================================

SRC_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = SRC_DIR.parent

DB_DIR = PROJECT_ROOT / "database"
LOG_DIR = PROJECT_ROOT / "logs"
BACKUP_DIR = PROJECT_ROOT / "backups"
RESOURCE_DIR = PROJECT_ROOT / "resources"

# ==========================================================
# Database
# ==========================================================

DEFAULT_DATABASE_NAME = "ems_opg.db"

# ==========================================================
# Logging
# ==========================================================

DEFAULT_LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | "
    "%(name)s | %(filename)s:%(lineno)d | %(message)s"
)

DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ==========================================================
# Date & Time
# ==========================================================

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
FILE_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

# ==========================================================
# QR Code
# ==========================================================

QR_IMAGE_SIZE = (400, 400)
QR_BORDER = 4
QR_BOX_SIZE = 10

# ==========================================================
# Status Values
# ==========================================================

STATUS_AVAILABLE = "AVAILABLE"
STATUS_IN_USE = "IN_USE"
STATUS_TESTING = "TESTING"
STATUS_PASSED = "PASSED"
STATUS_FAILED = "FAILED"

# ==========================================================
# MAC Address
# ==========================================================

MAC_ADDRESS_LENGTH = 17

# ==========================================================
# Common Messages
# ==========================================================

MSG_DATABASE_CONNECTED = "Database connection established."
MSG_DATABASE_CLOSED = "Database connection closed."
MSG_APPLICATION_STARTED = "Application started."
MSG_APPLICATION_EXITED = "Application shutdown complete."

# ==========================================================
# Exit Codes
# ==========================================================

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_CONFIGURATION_ERROR = 2
EXIT_DATABASE_ERROR = 3
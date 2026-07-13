"""
Custom application exceptions.
"""
# Usage:
#   from core.exceptions import ApplicationError, ConfigurationError, DatabaseError, BackupError, ValidationError, WorkflowError


class ApplicationError(Exception):
    """Base application exception."""


class ConfigurationError(ApplicationError):
    """Configuration problem."""


class DatabaseError(ApplicationError):
    """Database problem."""


class BackupError(ApplicationError):
    """Backup problem."""


class ValidationError(ApplicationError):
    """Validation failed."""


class WorkflowError(ApplicationError):
    """Workflow error."""


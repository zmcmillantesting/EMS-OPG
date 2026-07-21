"""
Custom application exceptions.
"""
# Usage:
#   from core.exceptions import ApplicationError, ConfigurationError, DatabaseError, BackupError, ValidationError, WorkflowError


class ApplicationError(Exception):
    """Base class for application exceptions."""
    def __init__(self, message: str = ""):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class ConfigurationError(ApplicationError):
    """Configuration problem."""
    def __init__(self, message: str = ""):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message

class DatabaseError(ApplicationError):
    """Database problem."""
    def __init__(self, message: str = ""):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message

class BackupError(ApplicationError):
    """Backup problem."""
    def __init__(self, message: str = ""):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message

class ValidationError(ApplicationError):
    """Validation failed."""
    def __init__(self, message: str = ""):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message

class WorkflowError(ApplicationError):
    """Workflow error."""
    def __init__(self, message: str = ""):
        super().__init__(message)
        self.message = message

class OrderNotFoundError(WorkflowError):
    """Order not found."""
    def __init__(self, message: str = ""):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message
    
class DeviceNotFoundError(WorkflowError):
    """Device not found."""
    def __init__(self, message: str = ""):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message
    
class MACImportError(WorkflowError):
    """MAC address import error."""
    def __init__(self, message: str = ""):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message

class SchemaOutdatedError(WorkflowError):
    """Database schema is outdated."""
    def __init__(self, message: str = ""):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message

    def __str__(self):
        return self.message

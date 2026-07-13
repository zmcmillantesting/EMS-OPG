"""
Application environment.
"""

from enum import Enum
import os


class Environment(Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


def get_environment():

    env = os.getenv("APP_ENV", "development")

    try:
        return Environment(env)

    except ValueError:
        return Environment.DEVELOPMENT
    
# Usage:
#   from core.environment import get_environment
#   print(get_environment())  # Output: Environment.DEVELOPMENT
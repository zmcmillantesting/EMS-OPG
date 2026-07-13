"""
Application version information.
"""
# Usage:
#   from core.version import APP_VERSION
#   print(APP_VERSION)  # Output: 1.0.0

from dataclasses import dataclass


@dataclass(frozen=True)
class Version:
    major: int
    minor: int
    patch: int

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"


APP_VERSION = Version(
    major=1,
    minor=0,
    patch=0
)


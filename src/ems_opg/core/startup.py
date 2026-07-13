"""
Startup routines.
"""

from pathlib import Path


REQUIRED_DIRECTORIES = [

    "logs",

    "database",

    "backups",

    "config",

    "exports"

]


def create_required_directories():

    for directory in REQUIRED_DIRECTORIES:

        Path(directory).mkdir(
            parents=True,
            exist_ok=True
        )


def startup():

    print("Initializing application...")

    create_required_directories()

    print("Startup complete.")
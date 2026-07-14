from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class PathManager:

    def __init__(self):

        # Project root is two levels above the `src` package directory.
        self.root = Path(__file__).resolve().parents[3]

        self.config = self.root / "config"

        self.database = self.root / "database"

        self.logs = self.root / "logs"

        self.backup = self.root / "backup"

        self.assets = self.root / "assets"

    def create_directories(self):

        directories = [

            self.database,

            self.logs,

            self.backup,

            self.assets

        ]

        for directory in directories:

            directory.mkdir(
                parents=True,
                exist_ok=True
            )
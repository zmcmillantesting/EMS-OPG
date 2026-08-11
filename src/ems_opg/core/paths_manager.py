from pathlib import Path


class PathManager:

    def __init__(self):

        self.root = Path(__file__).resolve().parents[3]

        #
        # Directories
        #
        self.config_dir = self.root / "config"
        self.database_dir = self.root / "database"
        self.logs_dir = self.root / "logs"
        self.backup_dir = self.root / "backup"
        self.assets_dir = self.root / "assets"
        self.cache_dir = self.root / "cache"
        self.qr_cache = self.cache_dir / "qr"

        #
        # Files
        #
        self.config_file = self.config_dir / "config.json"
        self.database_file = self.database_dir / "ems_opg.db"

    def create_directories(self):

        for directory in (

            self.database_dir,

            self.logs_dir,

            self.backup_dir,

            self.assets_dir,

            self.cache_dir,

            self.qr_cache,

        ):

            directory.mkdir(
                parents=True,
                exist_ok=True,
            )
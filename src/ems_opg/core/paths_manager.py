from pathlib import Path
import json


class PathManager:

    def __init__(self):
        
        # Where the application's own code/frontend/config live. This
        # never moves - it's always wherever the app is installed
        self.root = Path(__file__).resolve().parents[3]

        #
        # Appliction directories (stay with the app install)
        #
        self.config_dir = self.root / "config"
        self.assets_dir = self.root / "assets"

        #
        # Files
        #
        self.config_file = self.config_dir / "config.json"
        # Database, logs, cache, and backups can live on a separate drive
        # from the application itself (e.g. app on C:, data on a shared
        # network P: drive). Set "data_root" in config.json to an absolute
        # path to point there; leave it blank/unset to keep everything
        # next to the app, which is the default.
        self.data_root = self._resolve_data_root()

        #
        # Data directories
        #
        self.database_dir = self.data_root / "database"
        self.logs_dir = self.data_root / "logs"
        self.backup_dir = self.data_root / "database/backups"
        self.cache_dir = self.data_root / "cache"
        self.qr_cache = self.cache_dir / "qr"
        self.exports_dir = self.data_root / "exports"   
        
        self.database_file = self.database_dir / "ems_opg.db"
        
    def _resolve_data_root(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                    
                data_root = config_data.get("data_root")
                if data_root:
                    return Path(data_root)
                
            except (json.JSONDecodeError, OSError):
                pass
            
        return self.root

    def create_directories(self):

        for directory in (

            self.database_dir,

            self.logs_dir,

            self.backup_dir,

            self.assets_dir,

            self.cache_dir,

            self.qr_cache,
            
            self.exports_dir,

        ):

            directory.mkdir(
                parents=True,
                exist_ok=True,
            )
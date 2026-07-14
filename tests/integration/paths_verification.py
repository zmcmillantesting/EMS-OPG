from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ems_opg.core.paths_manager import PathManager

def test_paths_manager_init():
    paths_manager = PathManager()
    assert paths_manager.config.exists()
    assert paths_manager.database.exists()
    assert paths_manager.logs.exists()
    assert paths_manager.backup.exists()
    assert paths_manager.assets.exists()

def test_paths_manager_mkdir():
    paths_manager = PathManager()
    paths_manager.create_directories()

    assert paths_manager.database.exists()
    assert paths_manager.logs.exists()
    assert paths_manager.backup.exists()
    assert paths_manager.assets.exists()

def test_paths_manager_directories():
    paths_manager = PathManager()
    directories = [
        paths_manager.database,
        paths_manager.logs,
        paths_manager.backup,
        paths_manager.assets
    ]

    for directory in directories:
        assert directory.exists()
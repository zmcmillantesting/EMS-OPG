from pathlib import Path

from src.ems_opg.core.paths_manager import PathManager

def test_paths_manager_init():
    paths_manager = PathManager()
    assert paths_manager.config_dir.exists()
    assert paths_manager.database_dir.exists()
    assert paths_manager.logs_dir.exists()
    assert paths_manager.backup_dir.exists()
    assert paths_manager.assets_dir.exists()

def test_paths_manager_mkdir():
    paths_manager = PathManager()
    paths_manager.create_directories()

    assert paths_manager.database_dir.exists()
    assert paths_manager.logs_dir.exists()
    assert paths_manager.backup_dir.exists()
    assert paths_manager.assets_dir.exists()

def test_paths_manager_directories():
    paths_manager = PathManager()
    directories = [
        paths_manager.database_dir,
        paths_manager.logs_dir,
        paths_manager.backup_dir,
        paths_manager.assets_dir
    ]

    for directory in directories:
        assert directory.exists()
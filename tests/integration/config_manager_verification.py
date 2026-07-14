from pathlib import Path
import sys

from src.ems_opg.config.config_manager import ConfigurationManager

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

config = ConfigurationManager(
    Path("config/config.json")
)

def test_config_manager_load():
    assert config.application["name"] == "EMS-OPG"
    assert config.application["version"] == "1.0.0"
    assert config.database["filename"] == "traceability_db.db"
    assert config.logging["level"] == "INFO"
    assert config.backup["directory"] == "backup"

def test_config_manager_save():
    # Modify a configuration value
    config.application["version"] = "1.0.1"
    config.save()

    # Reload the configuration to verify the change
    config.load()
    assert config.application["version"] == "1.0.1"

    # Revert the change for other tests
    config.application["version"] = "1.0.0"
    config.save()

def test_config_manager_application():
    assert config.application is not None
    assert isinstance(config.application, dict)

def test_config_manager_db():
    assert config.database is not None
    assert isinstance(config.database, dict)

def test_config_manager_logging():
    assert config.logging is not None
    assert isinstance(config.logging, dict)

def test_config_manager_backup():
    assert config.backup is not None
    assert isinstance(config.backup, dict)

# def test_config_manager_paths():
#     assert config.paths is not None
#     assert isinstance(config.paths, Path)


def test_config_manager_workflow():
    assert config.workflow is not None
    assert isinstance(config.workflow, dict)

def test_config_manager_window():
    assert config.window is not None
    assert isinstance(config.window, dict)




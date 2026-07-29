"""
Configuration Manager

usage:
from pathlib import Path

from config.config_manager import ConfigurationManager
from src.ems_opg.config.path_manager import PathManager


config = ConfigurationManager(
    Path("PathManager.config")
)
...
"""

from pathlib import Path
import json


class ConfigurationManager:

    def __init__(self, config_path: Path):

        self.config_path = config_path

        self._config = {}

        self.load()

    def load(self):

        with open(self.config_path, "r") as file:

            self._config = json.load(file)

    def save(self):

        with open(self.config_path, "w") as file:

            json.dump(
                self._config,
                file,
                indent=4
            )

    def get_qr_commands(self):
        return self._config["qr_commands"]


    def get_combined_steps(self):
        return self._config["combined_steps"]


    def get_qr_command(self, step):
        return self._config["qr_commands"][step]


    def get_workflow(self, workflow):
        return self._config["combined_steps"][workflow]

    def format_qr_command(self, step, **kwargs):
        command=self.get_qr_command(step)
        return command.format(**kwargs)

    @property
    def application(self):

        return self._config["application"]

    @property
    def database(self):

        return self._config["database"]

    @property
    def logging(self):

        return self._config["logging"]

    @property
    def backup(self):

        return self._config["backup"]

    @property
    def paths(self):

        return self._config["paths"]

    @property
    def qr_cache(self):
        return Path(self._config["paths"]["qr_cache"])

    @property
    def workflow(self):

        return self._config["workflow"]

    @property
    def window(self):

        return self._config["window"]
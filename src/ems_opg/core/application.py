from src.ems_opg.app_logging.logger import Logger 
from src.ems_opg.config.config_manager import ConfigurationManager
from src.ems_opg.core.paths_manager import PathManager

class Application:

    def __init__(self):

        self.paths = PathManager()
        self.paths.create_directories()

        self.config = ConfigurationManager(self.paths.config_file)

        self.logger = Logger().get_logger()

        self.logger.info("Application initialized.")

    def run(self):
        from ems_opg.api.server import create_app

        app = create_app(self)
        app.run(host="127.0.0.1", port=5000, debug=self.config.get("debug", False))
from src.ems_opg.app_logging.logger import Logger 
from src.ems_opg.config.config_manager import ConfigurationManager
from src.ems_opg.core.paths_manager import PathManager

class Application:

    def __init__(self):

        self.config = ConfigurationManager(...)
        self.paths = PathManager(self.config)

        self.logger = Logger().get_logger()

        self.logger.info("Application initialized.")
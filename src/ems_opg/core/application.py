import errno
from src.ems_opg.app_logging.logger import Logger 
from src.ems_opg.config.config_manager import ConfigurationManager
from src.ems_opg.core.paths_manager import PathManager

class Application:

    def __init__(self):

        self.paths = PathManager()
        self.paths.create_directories()

        self.config = ConfigurationManager(self.paths.config_file)

        self.logger = Logger(self.config, self.paths).get_logger()

        self.logger.info("Application initialized.")

    def run(self):
        from ems_opg.api.server import create_app

        app = create_app(self)
        try:
            app.run(host="127.0.0.1", port=5000)
        except OSError as error:
            if error.errno == errno.EADDRINUSE:
                self.logger.error(
                    "Port 5000 is already in use - a previous server is "
                    "likely still running. Stop it before running a new "
                    "one (Linux/macOS): `lsof -ti:5000 | xargs kill`; " 
                    "Windows PowerShell:" \
                    " `Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess`"
                )
                raise SystemExit(1) from error
            raise
        finally:
            self.logger.info("Server stopped")
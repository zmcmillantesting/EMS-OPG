import errno
import os

from ems_opg.app_logging.logger import Logger
from ems_opg.config.config_manager import ConfigurationManager
from ems_opg.core.paths_manager import PathManager

class Application:

    def __init__(self):

        self.paths = PathManager()
        self.paths.create_directories()

        self.config = ConfigurationManager(self.paths.config_file)

        self.logger = Logger(self.config, self.paths).get_logger()

        self.logger.info("Application initialized.")

    def run(self):
        from ems_opg.api.server import create_app
        from ems_opg.core.shutdown import Shutdown

        app = create_app(self)
        port = int(os.environ.get("EMS_OPG_PORT", 5000))
        started = True

        try:
            app.run(host="127.0.0.1", port=port)
        except OSError as error:
            started = False
            if error.errno == errno.EADDRINUSE:
                self.logger.error(
                    "Port %s is already in use - a previous server is "
                    "likely still running. Stop it before running a new "
                    "one (Linux/macOS): `lsof -ti:%s | xargs kill`; "
                    "Windows PowerShell: "
                    "`Stop-Process -Id (Get-NetTCPConnection -LocalPort %s).OwningProcess`. "
                    "Or run on a different port: `EMS_OPG_PORT=5001 python app.py`",
                    port, port, port,
                )
                raise SystemExit(1) from error
            raise
        except KeyboardInterupt:
            self.logger.info("Shutdown requested by operator")
        finally:
            self.logger.info("Server stopped")
            if started:
                Shutdown(self).shutdown()
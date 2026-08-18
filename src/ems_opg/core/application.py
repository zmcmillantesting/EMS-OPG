import errno
import os
import threading

import webview
from waitress import create_server

from ems_opg.app_logging.logger import Logger
from ems_opg.config.config_manager import ConfigurationManager
from ems_opg.core.paths_manager import PathManager
from ems_opg.core.webview_api import WebviewApi

class Application:

    def __init__(self):

        self.paths = PathManager()
        self.paths.create_directories()

        self.config = ConfigurationManager(self.paths.config_file)

        self.logger = Logger(self.config, self.paths).get_logger()

        self.logger.info("Application initialized.")

    def run(self):
        from ems_opg.api.server import create_app
        from ems_opg.core.backup import run_backup_if_enabled
        from ems_opg.core.shutdown import Shutdown

        app = create_app(self)
        port = int(os.environ.get("EMS_OPG_PORT", 5000))

        run_backup_if_enabled(self, "backup_on_startup")

        try:
            server = create_server(app, host="127.0.0.1", port=port)
        except OSError as error:
            if error.errno == errno.EADDRINUSE:
                self.logger.error(
                    "Port %s is already in use - a previous instance is "
                    "likely still running. Stop it before running a new "
                    "one (Linux/macOS): `lsof -ti:%s | xargs kill`; "
                    "Windows PowerShell: "
                    "`Stop-Process -Id (Get-NetTCPConnection -LocalPort %s).OwningProcess`. "
                    "Or run on a different port: `EMS_OPG_PORT=5001 python app.py`",
                    port, port, port,
                )
                raise SystemExit(1) from error
            raise
        
        no_window = os.environ.get("EMS_OPG_NO_WINDOW", "").strip().lower() in ("1", "true", "yes")
        
        if no_window:
            self.logger.info(
                "EMS_OPG_NO_WINDOW set - skipping the PyWebView window."
                "Open http://127.0.0.1%s in a browser.", port
            )
            
            try:
                server.run()
            except KeyboardInterrupt:
                self.logger.info("Shutdown requested by operator (Ctrl+C)")
            finally:
                self.logger.info("Server Stopped")
                server.close()
                Shutdown(self).shutdown()
            return

        server_thread = threading.Thread(target=server.run, daemon=True)
        server_thread.start()

        window_config = self.config.window
        window = webview.create_window(
            title=self.config.application.get("name", "EMS-OPG"),
            url=f"http://127.0.0.1:{port}",
            width=window_config.get("width", 1400),
            height=window_config.get("height", 900),
            maximized=window_config.get("maximize", False),
            js_api=WebviewApi()
        )

        shutdown_ran = False

        def on_window_closing():
            nonlocal shutdown_ran
            if shutdown_ran:
                return
            shutdown_ran = True
            self.logger.info("Window closed by operator.")
            server.close()
            Shutdown(self).shutdown()

        window.events.closing += on_window_closing

        try:
            webview.start()
        except KeyboardInterrupt:
            self.logger.info("Shutdown requested by operator (Ctrl+C).")
        finally:
            self.logger.info("Server stopped")
            on_window_closing()

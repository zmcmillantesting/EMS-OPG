"""
Application bootstrap.
"""

from PyQt5.QtWidgets import QApplication

import sys

from ems_opg.core.startup import startup
from ems_opg.core.shutdown import shutdown


class Application:

    def __init__(self):

        startup()

        self.qt_app = QApplication(sys.argv)

    def run(self):

        exit_code = self.qt_app.exec_()

        shutdown()

        return exit_code
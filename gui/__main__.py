"""
gui application bootstrapper.
initialises logging, the pyqt6 application instance, main window, and event loop.
"""

import logging
import sys

from PyQt6.QtWidgets import QApplication

from core.logger import setup_log
from gui.main_window import MainWindow

logger = logging.getLogger(__name__)


def main() -> None:
    """
    initialises gui logging, creates the qapplication, and launches the main window event loop.

    :return: none
    """
    # configure dedicated log file for gui sessions
    setup_log(log_file="logs/gui_game.log")
    logger.info("==========================================")
    logger.info("NEW CONNECT FOUR GUI SESSION STARTED")

    # create the main qt application instance
    app = QApplication(sys.argv)
    logger.info("QApplication instance created")

    # instantiate and display the main application window
    window = MainWindow()
    window.show()
    logger.info("MainWindow displayed; entering Qt event loop")

    # start the qt event loop and exit cleanly on window close
    exit_code = app.exec()
    logger.info("GUI session ended cleanly with exit code %d", exit_code)
    sys.exit(exit_code)

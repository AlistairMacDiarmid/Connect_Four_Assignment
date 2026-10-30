"""
game mode selection view for the connect 4 gui.
allows the user to choose between player vs player and player vs computer modes.
"""

import logging

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

logger = logging.getLogger(__name__)


class GameModeSelectScreen(QWidget):
    """
    screen widget presenting buttons to select the game mode or return to the title screen.
    emits mode_selected with an integer identifier (1 for pvp, 2 for pvc).
    """

    mode_selected = pyqtSignal(int)
    back_btn_clicked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        initialises the game mode selection screen and builds its user interface.

        :param parent: optional parent qwidget
        """
        super().__init__(parent)
        self.back_btn: QPushButton | None = None
        self.pvai_btn: QPushButton | None = None
        self.pvp_btn: QPushButton | None = None
        self.initUI()
        logger.debug("GameModeSelectScreen UI initialised")

    def initUI(self) -> None:
        """
        constructs the header label, game mode buttons, and back navigation button.

        :return: none
        """
        # create centered vertical layout for the menu options
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        header = QLabel("Select Game Mode")
        header.setObjectName("header_label")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # mode selection and back buttons
        self.pvp_btn = QPushButton("Player vs Player")
        self.pvai_btn = QPushButton("Player vs Computer")
        self.back_btn = QPushButton("Back")

        # emit an int to map to specific game mode (1 = pvp, 2 = pvc)
        self.pvp_btn.clicked.connect(lambda: self.mode_selected.emit(1))
        self.pvai_btn.clicked.connect(lambda: self.mode_selected.emit(2))
        self.back_btn.clicked.connect(self.back_btn_clicked.emit)

        layout.addWidget(self.pvp_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.pvai_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

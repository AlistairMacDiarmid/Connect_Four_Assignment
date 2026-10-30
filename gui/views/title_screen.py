"""
title screen view for the connect 4 gui.
displays the game title, subtitle, and main menu action buttons.
"""

import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

logger = logging.getLogger(__name__)


class TitleScreen(QWidget):
    """
    initial landing screen displaying the connect 4 title and play/exit buttons.
    emits signals when the user chooses to start or quit the application.
    """

    play_btn_clicked = pyqtSignal()
    exit_btn_clicked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        initialises the title screen widget and builds its user interface.

        :param parent: optional parent qwidget
        """
        super(TitleScreen, self).__init__(parent)
        self.exit_btn: QPushButton | None = None
        self.play_btn: QPushButton | None = None
        self.initUI()
        logger.debug("TitleScreen UI initialised")

    def initUI(self) -> None:
        """
        constructs and arranges the title labels and navigation buttons.

        :return: none
        """
        # create vertical layout centered in the window
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        # main title and subtitle labels with qss object names
        title_lbl = QLabel("CONNECT 4")
        title_lbl.setObjectName("title_label")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle_lbl = QLabel("Player vs Player  •  Player vs Computer")
        subtitle_lbl.setObjectName("subtitle_label")
        subtitle_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # action buttons for starting or exiting the game
        self.play_btn = QPushButton("Play")
        self.exit_btn = QPushButton("Exit")

        # forward button click events to custom view signals
        self.play_btn.clicked.connect(self.play_btn_clicked.emit)
        self.exit_btn.clicked.connect(self.exit_btn_clicked.emit)

        layout.addWidget(title_lbl)
        layout.addWidget(subtitle_lbl)
        layout.addWidget(self.play_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.exit_btn, alignment=Qt.AlignmentFlag.AlignCenter)

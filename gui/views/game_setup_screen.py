"""
game setup and configuration view for the connect 4 gui.
allows customisation of board dimensions and ai difficulty before starting a match.
"""

import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QSpinBox,
    QCheckBox,
    QButtonGroup,
    QPushButton,
)

logger = logging.getLogger(__name__)


class SetupScreen(QWidget):
    """
    configuration screen for setting board rows, columns, and ai difficulty level.
    emits start_game_clicked with (rows, cols, difficulty) when the start button is pressed.
    """

    start_game_clicked = pyqtSignal(int, int, str)
    back_btn_clicked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        initialises the setup screen widget and builds its user interface.

        :param parent: optional parent qwidget
        """
        super().__init__(parent)
        self.cols_spin: QSpinBox | None = None
        self.rows_spin: QSpinBox | None = None
        self.ai_group: QGroupBox | None = None
        self.easy_cb: QCheckBox | None = None
        self.medium_cb: QCheckBox | None = None
        self.difficulty_btn_group: QButtonGroup | None = None
        self.back_btn: QPushButton | None = None
        self.start_btn: QPushButton | None = None
        self.initUI()
        logger.info("SetupScreen initialised")

    def initUI(self) -> None:
        """
        constructs the board dimension spinboxes, ai difficulty checkboxes, and navigation buttons.

        :return: none
        """
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(20)

        header = QLabel("Game Configuration")
        header.setObjectName("header_label")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)

        # group box for board row and column dimension inputs
        board_group = QGroupBox("Board Dimensions (Min 6×7)")
        board_layout = QVBoxLayout(board_group)
        board_layout.setSpacing(14)

        # row count selector (minimum 6 rows)
        rows_row = QHBoxLayout()
        rows_row.setSpacing(30)
        rows_label = QLabel("Number of Rows (min 6):")
        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(6, 20)
        self.rows_spin.setValue(6)
        self.rows_spin.setFixedSize(128, 42)
        rows_row.addWidget(rows_label)
        rows_row.addWidget(self.rows_spin)

        # column count selector (minimum 7 columns)
        cols_row = QHBoxLayout()
        cols_row.setSpacing(30)
        cols_label = QLabel("Number of Columns (min 7):")
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(7, 20)
        self.cols_spin.setValue(7)
        self.cols_spin.setFixedSize(128, 42)
        cols_row.addWidget(cols_label)
        cols_row.addWidget(self.cols_spin)

        board_layout.addLayout(rows_row)
        board_layout.addLayout(cols_row)
        main_layout.addWidget(board_group, alignment=Qt.AlignmentFlag.AlignCenter)

        # group box for selecting ai opponent difficulty
        self.ai_group = QGroupBox("AI Difficulty")
        ai_layout = QVBoxLayout(self.ai_group)
        ai_layout.setSpacing(10)

        self.easy_cb = QCheckBox("Easy (Random Moves)")
        self.medium_cb = QCheckBox("Medium (MCTS Engine)")
        self.medium_cb.setChecked(True)

        # enforce mutually exclusive selection between difficulty checkboxes
        self.difficulty_btn_group = QButtonGroup(self)
        self.difficulty_btn_group.setExclusive(True)
        self.difficulty_btn_group.addButton(self.easy_cb)
        self.difficulty_btn_group.addButton(self.medium_cb)

        ai_layout.addWidget(self.easy_cb)
        ai_layout.addWidget(self.medium_cb)
        main_layout.addWidget(self.ai_group, alignment=Qt.AlignmentFlag.AlignCenter)

        # bottom navigation row for returning or starting the match
        nav_row = QHBoxLayout()
        nav_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_row.setSpacing(20)
        self.back_btn = QPushButton("Back")
        self.start_btn = QPushButton("Start")

        self.back_btn.clicked.connect(self.back_btn_clicked.emit)
        self.start_btn.clicked.connect(self.start_game)

        nav_row.addWidget(self.back_btn)
        nav_row.addWidget(self.start_btn)
        main_layout.addLayout(nav_row)

    def config_mode(self, mode: int) -> None:
        """
        enables or disables the ai difficulty group depending on the selected game mode.

        :param mode: integer representing the game mode (1 for pvp, 2 for pvc)
        :return: none
        """
        # only enable ai difficulty selection when playing against the computer (mode 2)
        is_ai_enabled = mode == 2
        self.ai_group.setEnabled(is_ai_enabled)
        logger.info(
            "SetupScreen configured for mode %d (AI difficulty selector enabled: %s)",
            mode,
            is_ai_enabled,
        )

    def start_game(self) -> None:
        """
        reads the current form values and emits start_game_clicked with the configuration.

        :return: none
        """
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()
        difficulty = "easy" if self.easy_cb.isChecked() else "medium"
        logger.info(
            "SetupScreen start_game triggered: rows=%d, cols=%d, difficulty=%s",
            rows,
            cols,
            difficulty,
        )
        self.start_game_clicked.emit(rows, cols, difficulty)

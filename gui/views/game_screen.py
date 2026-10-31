"""
game board screen view for the connect 4 gui.
displays a contained dynamic grid of clickable board cells, a side legend key, and a back navigation button.
"""

import logging
import numpy as np

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class GameScreen(QWidget):
    """
    contained grid screen displaying clickable board cells, a side key, and a back button.
    emits cell_clicked with (row, col) coordinates when a cell is pressed, and back_btn_clicked to return.
    """

    cell_clicked = pyqtSignal(int, int)
    back_btn_clicked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        initialises the game screen layout, central board grid container, key panel, and back button.

        :param parent: optional parent qwidget
        """
        super().__init__(parent)

        # main vertical layout keeping the board area and back button contained
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(10)

        # horizontal container holding the board on the left and the key on the right
        center_container = QWidget()
        center_layout = QHBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(16)
        root_layout.addWidget(center_container, stretch=1)

        # grid layout dedicated exclusively to board cell buttons
        self.grid_layout: QGridLayout = QGridLayout()
        self.grid_layout.setSpacing(4)
        center_layout.addLayout(self.grid_layout, stretch=1)

        # vertical layout for the legend panel pinned on the right
        self.key_layout = QVBoxLayout()
        self.key_layout.setSpacing(8)
        self.key_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        # header label for the legend
        key_header = QLabel("Legend:")
        key_header.setObjectName("key_header")
        self.key_layout.addWidget(key_header)

        # blocked cell key row: small square indicator + text label
        blocked_key_row = QHBoxLayout()
        blocked_key_row.setSpacing(8)

        blocked_color_box = QFrame()
        blocked_color_box.setFixedSize(27, 27)
        blocked_color_box.setStyleSheet(
            "background-color: red; border: 1px solid black; border-radius: 5px; margin-top:5px;margin-left:5px;"
        )

        blocked_label = QLabel("Blocked Cell")
        blocked_label.setObjectName("blocked_cell_label")

        blocked_key_row.addWidget(blocked_color_box, alignment=Qt.AlignmentFlag.AlignVCenter)
        blocked_key_row.addWidget(blocked_label, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.key_layout.addLayout(blocked_key_row)



        center_layout.addLayout(self.key_layout, stretch=0)

        # bottom navigation button to return to the game setup screen
        self.back_btn: QPushButton = QPushButton("Back")
        self.back_btn.clicked.connect(self.back_btn_clicked.emit)
        root_layout.addWidget(self.back_btn, stretch=0)

        logger.debug("Contained layout, side legend key, and back button initialised")

    def setup_board(self, board: np.ndarray) -> None:
        """
        clears previous cell buttons and populates the grid layout to match the numpy board array.

        :param board: 2d numpy array representing the current game board
        :return: none
        """
        # remove and schedule deletion of any buttons from a previous game session
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        rows, cols = board.shape

        # assign equal stretch factors across all rows and columns so cells scale evenly
        for r in range(rows):
            self.grid_layout.setRowStretch(r, 1)

        for c in range(cols):
            self.grid_layout.setColumnStretch(c, 1)

        # populate the grid with a clickable button for each (row, col) cell
        for r in range(rows):
            for c in range(cols):
                cell_btn = QPushButton(str(board[r, c]))
                cell_btn.setObjectName("board_cell")
                cell_btn.setMinimumSize(0, 0)
                cell_btn.setSizePolicy(
                    QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored
                )

                # map internal board characters ('#' and '!') to descriptive button labels
                if cell_btn.text() == "#":
                    cell_btn.setText("PLAYABLE CELL")
                elif cell_btn.text() == "!":
                    cell_btn.setStyleSheet("background-color: red")
                    cell_btn.setText("BLOCKED CELL")

                # connect button click to emit the cell's (row, col) coordinates
                cell_btn.clicked.connect(
                    lambda checked=False, row=r, col=c: print(row,col)
                )
                self.grid_layout.addWidget(cell_btn, r, c)

        logger.info("Populated contained board with %dx%d cells", rows, cols)
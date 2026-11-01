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

        # main vertical layout keeping the status bar on top and the board + side column below
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(10)

        # top lbl to display current turn, last move, or win/draw message
        self.status_lbl = QLabel("Player 1's turn")
        self.status_lbl.setObjectName("status_lbl")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        root_layout.addWidget(self.status_lbl, stretch=0)

        # horizontal container holding the expanding board on the left and the side column on the right
        center_container = QWidget()
        center_layout = QHBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(16)
        root_layout.addWidget(center_container, stretch=1)

        # grid layout dedicated exclusively to board cell buttons, expanding to fill remaining space
        self.grid_layout: QGridLayout = QGridLayout()
        self.grid_layout.setSpacing(4)
        center_layout.addLayout(self.grid_layout, stretch=1)

        # vertical layout for the right-hand side column holding the colour key and back button
        self.key_layout = QVBoxLayout()
        self.key_layout.setSpacing(8)

        # add legend rows for blocked cell, player 1, and player 2 / computer
        self.key_layout.addLayout(self.create_legend_row("red", "Blocked Cell"))
        self.key_layout.addLayout(self.create_legend_row("blue", "Player 1"))
        self.key_layout.addLayout(self.create_legend_row("yellow", "Player 2"))

        # push the back button to the bottom of the right-hand side column
        self.key_layout.addStretch(1)

        # navigation button in the side column to return to the game setup screen
        self.back_btn: QPushButton = QPushButton("Back")
        self.back_btn.clicked.connect(self.back_btn_clicked.emit)
        self.key_layout.addWidget(self.back_btn)

        center_layout.addLayout(self.key_layout, stretch=0)

        logger.info("GameScreen initialised with board grid, colour key, and back button")

    def setup_board(self, board: np.ndarray, active_piece: str | None = "X") -> None:
        """
        clears previous cell buttons and populates the grid layout to match the numpy board array.

        :param board: 2d numpy array representing the current game board
        :param active_piece: token of the currently active human player ('X' or 'O'), or none to disable hover
        :return: none
        """
        # remove and schedule deletion of any buttons from a previous game session
        previous_widgets = self.grid_layout.count()
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if previous_widgets > 0:
            logger.debug("Cleared %d cell button(s) from previous game board", previous_widgets)

        rows, cols = board.shape

        # assign equal stretch factors across all rows and columns so cells scale evenly
        for r in range(rows):
            self.grid_layout.setRowStretch(r, 1)

        for c in range(cols):
            self.grid_layout.setColumnStretch(c, 1)

        # populate the grid with a clickable button for each (row, col) cell
        for r in range(rows):
            for c in range(cols):
                token = str(board[r, c])
                cell_btn = QPushButton("")
                cell_btn.setObjectName("board_cell")
                cell_btn.setMinimumSize(0, 0)
                cell_btn.setSizePolicy(
                    QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored
                )

                # apply initial qss state styling for the cell
                self.style_cell_button(cell_btn, token, active_piece)

                # connect button click to emit the cell's (row, col) coordinates
                cell_btn.clicked.connect(
                    lambda checked=False, row=r, col=c: self.cell_clicked.emit(row, col)
                )
                self.grid_layout.addWidget(cell_btn, r, c)

        logger.info(
            "GameScreen populated %dx%d board grid (initial active_piece=%s)",
            rows,
            cols,
            active_piece,
        )

    def update_board(self, board: np.ndarray, active_piece: str | None = "X") -> None:
        """
        refreshes the visual styling of all cell buttons on the grid to match the current board state.

        :param board: 2d numpy array representing the current game board
        :param active_piece: token of the currently active human player ('X' or 'O'), or none to disable hover
        :return: none
        """
        rows, cols = board.shape
        for r in range(rows):
            for c in range(cols):
                item = self.grid_layout.itemAtPosition(r, c)
                if item is not None and item.widget() is not None:
                    cell_btn = item.widget()
                    if isinstance(cell_btn, QPushButton):
                        self.style_cell_button(cell_btn, str(board[r, c]), active_piece)

        logger.debug("Refreshed GameScreen board cells (active_piece=%s)", active_piece)

    def style_cell_button(
        self, cell_btn: QPushButton, char: str, active_piece: str | None = "X"
    ) -> None:
        """
        updates a single cell button's dynamic qss property based on its board token and active player.

        :param cell_btn: qpushbutton instance representing the cell
        :param char: single-character board token ('#', '!', 'X', or 'O')
        :param active_piece: token of the currently active human player ('X' or 'O'), or none to disable hover
        :return: none
        """
        if char == "#":
            if active_piece is None:
                state = "empty_disabled"
            elif active_piece == "X":
                state = "empty_x"
            else:
                state = "empty_o"
        elif char == "!":
            state = "blocked"
        elif char == "X":
            state = "x"
        elif char == "O":
            state = "o"
        else:
            state = "empty_disabled"

        cell_btn.setText("")
        self.apply_cell_state(cell_btn, state)

    def highlight_winning_cells(self, winning_cells: list[tuple[int, int]]) -> None:
        """
        sets the winning cell buttons to the 'win' qss state so they turn green.

        :param winning_cells: list of (row, col) coordinate tuples forming the winning line
        :return: none
        """
        for r, c in winning_cells:
            item = self.grid_layout.itemAtPosition(r, c)
            if item is not None and item.widget() is not None:
                cell_btn = item.widget()
                if isinstance(cell_btn, QPushButton):
                    self.apply_cell_state(cell_btn, "win")

        logger.info("Highlighted winning cells on GameScreen: %s", winning_cells)

    def apply_cell_state(self, cell_btn: QPushButton, state: str) -> None:
        """
        sets the cell_state dynamic property on a board button and refreshes its qss style.

        :param cell_btn: qpushbutton to update
        :param state: qss state identifier ('empty_x', 'empty_o', 'empty_disabled', 'blocked', 'x', 'o', 'win')
        :return: none
        """
        if cell_btn.property("cell_state") != state:
            cell_btn.setProperty("cell_state", state)
            style = cell_btn.style()
            if style is not None:
                style.unpolish(cell_btn)
                style.polish(cell_btn)

    def set_status(self, message: str) -> None:
        """
        updates the top status label text and colours it green when a win message is displayed.

        :param message: status text to display
        :return: none
        """
        self.status_lbl.setText(message)
        if "wins!" in message.lower():
            self.status_lbl.setStyleSheet("color: green;")
        else:
            self.status_lbl.setStyleSheet("")
        logger.debug("Updated GameScreen status label: '%s'", message)

    def create_legend_row(self, colour: str, lbl_txt: str) -> QHBoxLayout:
        """
        creates the horizontal legend entry containing a small coloured box along with a text label.

        :param colour: swatch colour identifier ('red', 'blue', or 'yellow') styled in styles.qss
        :param lbl_txt: text description for the legend item
        :return: populated qhboxlayout containing the colour swatch and label
        """
        row = QHBoxLayout()
        row.setSpacing(10)

        colour_box = QFrame()
        colour_box.setObjectName("legend_swatch")
        colour_box.setProperty("swatch_colour", colour)
        colour_box.setFixedSize(27, 27)

        colour_lbl = QLabel(lbl_txt)
        colour_lbl.setObjectName("colour_lbl")
        row.addWidget(colour_box, alignment=Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(colour_lbl, alignment=Qt.AlignmentFlag.AlignVCenter)
        return row

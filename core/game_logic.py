"""
game logic for connect 4
handles mathematical grid operations, random cell blocking, gravity-based piece dropping, and win checks.
"""

import logging
import random
import numpy as np

logger = logging.getLogger(__name__)


def create_board(rows: int, cols: int) -> np.ndarray:
    """
    initialises an empty board of dynamic size and applies random cell blocking.

    :param rows: integer representing the total number of rows on the board
    :param cols: integer representing the total number of columns on the board
    :return: 2d numpy array filled with empty slot tokens ('#') and random blockers ('!')
    :rtype: np.ndarray
    """
    board = np.full((rows, cols), "#")
    board = random_cell_blocking(board, block_char="!")
    blocked_count = int(np.sum(board == "!"))
    logger.info("Initialized board of size %dx%d with %d blocked cell(s)", rows, cols, blocked_count)
    return board


def random_cell_blocking(board: np.ndarray, block_char: str = "!") -> np.ndarray:
    """
    randomly selects between 1% and 10% of cells on the board and replaces them with block_char.

    these cells represent unplayable obstacles that neither player can drop pieces into.

    :param board: current 2d numpy array game board
    :param block_char: string character used to denote an unplayable space (default is '!')
    :return: updated 2d numpy array with blocked cells applied
    :rtype: np.ndarray
    """
    rows, cols = board.shape
    total_cells = rows * cols

    # calculate the random block percentage - between 1% and 10%
    block_percent = random.randint(1, 10) / 100
    # determine the number of cells to block - at least 1 and up to percentage limit
    num_to_block = max(1, int(total_cells * block_percent))

    # use np.random.choice to pick unique 1d indices without replacement - to prevent overlapping blocks
    chosen_cells_to_block = np.random.choice(
        total_cells, size=num_to_block, replace=False
    )

    # mathematically convert flat 1d indices back into 2d (row, col) coordinates
    for i in chosen_cells_to_block:
        row = i // cols
        col = i % cols
        board[row, col] = block_char

    return board


def check_win(board: np.ndarray, piece: str) -> bool:
    """
    scans the board for a winning condition of 4 consecutive matching pieces.

    uses boundary constraints to evaluate horizontal, vertical, and both diagonal directions.

    :param board: current 2d numpy array game board
    :param piece: string character representing the player's game piece
    :return: true if 4 consecutive matching pieces are found, otherwise false
    :rtype: bool
    """
    rows, cols = board.shape

    # check horizontal - uses range(cols - 3) so c+3 is always within the board bounds
    for c in range(cols - 3):
        for r in range(rows):
            if (
                board[r, c] == piece
                and board[r, c + 1] == piece
                and board[r, c + 2] == piece
                and board[r, c + 3] == piece
            ):
                return True

    # check vertical - uses range(rows - 3) so r+3 is always within the board bounds
    for c in range(cols):
        for r in range(rows - 3):
            if (
                board[r, c] == piece
                and board[r + 1, c] == piece
                and board[r + 2, c] == piece
                and board[r + 3, c] == piece
            ):
                return True

    # check back diagonals ( / ) limits both rows and cols bounds
    for c in range(cols - 3):
        for r in range(rows - 3):
            if (
                board[r, c] == piece
                and board[r + 1, c + 1] == piece
                and board[r + 2, c + 2] == piece
                and board[r + 3, c + 3] == piece
            ):
                return True

    # check forward diagonals ( \\ ) limits both rows and cols bounds
    for c in range(cols - 3):
        for r in range(3, rows):
            if (
                board[r, c] == piece
                and board[r - 1, c + 1] == piece
                and board[r - 2, c + 2] == piece
                and board[r - 3, c + 3] == piece
            ):
                return True

    return False


def get_winning_cells(board: np.ndarray, piece: str) -> list[tuple[int, int]]:
    """
    scans the board for 4 consecutive matching pieces and returns their (row, col) coordinates.

    :param board: current 2d numpy array game board
    :param piece: string character representing the player's game piece
    :return: list of 4 (row, col) coordinate tuples if a win is found, otherwise an empty list
    :rtype: list[tuple[int, int]]
    """
    rows, cols = board.shape

    # check horizontal - uses range(cols - 3) so c+3 is always within the board bounds
    for c in range(cols - 3):
        for r in range(rows):
            if all(board[r, c + i] == piece for i in range(4)):
                return [(r, c + i) for i in range(4)]

    # check vertical - uses range(rows - 3) so r+3 is always within the board bounds
    for c in range(cols):
        for r in range(rows - 3):
            if all(board[r + i, c] == piece for i in range(4)):
                return [(r + i, c) for i in range(4)]

    # check back diagonals ( \ ) limits both rows and cols bounds
    for c in range(cols - 3):
        for r in range(rows - 3):
            if all(board[r + i, c + i] == piece for i in range(4)):
                return [(r + i, c + i) for i in range(4)]

    # check forward diagonals ( / ) limits both rows and cols bounds
    for c in range(cols - 3):
        for r in range(3, rows):
            if all(board[r - i, c + i] == piece for i in range(4)):
                return [(r - i, c + i) for i in range(4)]

    return []


def drop_piece(board: np.ndarray, piece: str, col_index: int) -> bool:
    """
    simulates dropping a piece into the board down a specific column with gravity.

    scans backwards from the bottom row up to the top until an empty slot ('#')
    is found, placing the piece. returns false if the column is full.

    :param board: current 2d numpy array game board
    :param piece: string character representing the player's game piece
    :param col_index: 0-based integer index of the chosen column
    :return: true if the piece successfully dropped, false if the column was full
    :rtype: bool
    """
    rows, cols = board.shape

    # iterate backwards through the board from the bottom row up to the top
    for r in range(rows - 1, -1, -1):
        if board[r, col_index] == "#":
            board[r, col_index] = piece
            logger.debug("Dropped piece '%s' at row %d, col %d", piece, r, col_index)
            return True

    # if no space is available, return false
    logger.warning("Column %d is full; cannot drop piece '%s'", col_index + 1, piece)
    return False

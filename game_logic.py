"""
game logic for Connect 4
Handles the mathematical grid operations, cell blocking, and win checks.
"""
import random
import numpy as np


def create_board(rows: int, cols: int) -> np.ndarray:
    """
    initialises an empty board of dynamic size and applies the random cell blocking
    :param rows: integer representing the total number of rows on the board
    :param cols: integer representing the total number of columns on the board
    :return: a 2D NumPy array filled with empty slots and random blockers
    """
    board = np.full((rows, cols), "#")
    board = random_cell_blocking(board, block_char="!")
    return board


def random_cell_blocking(board: np.ndarray, block_char="!") -> np.ndarray:
    """
    randomly selects between 1% and 10% of cells on the board and replaces them with the block_char. These cells are unplayable
    :param board: the current 2D NumPy array game board
    :param block_char: the string character used to denote an unplayable space (default is "!")
    :return: the updated 2D NumPy array with the blocked cells applied
    """
    rows, cols = board.shape
    total_cells = rows * cols

    #calculate the random block percentage - between 1% and 10%
    block_percent = random.randint(1, 10) / 100
    #determine the number of cells to block - at least 1 and up to percentage limit
    num_to_block = max(1, int(total_cells * block_percent)) #at least 1 cell, up to total_cells * block_percent


    #use np.random.choice to pick unique 1D indices without replacement - to prevent overlapping blocks
    chosen_cells_to_block = np.random.choice(total_cells, size=num_to_block, replace=False)

    #mathematically convert the flat 1D indices back into 2D (row, col) coordinates
    for i in chosen_cells_to_block:
        row = i // cols
        col = i % cols
        board[row, col] = block_char

    return board



def check_win(board: np.ndarray, piece: str) -> bool:
    """
    scans the board for a winning condition
    uses boundary constraints to prevent IndexError out-of-bounds scanning
    :param board: the current 2D NumPy array game board
    :param piece: the string character representing the player's game piece
    :return: boolean True if 4 consecutive pieces are found, otherwise False
    """
    rows, cols = board.shape

    #check horizontal - uses range(cols - 3) so c+3 is always within the board bounds
    for c in range(cols - 3):
        for r in range(rows):
            if board[r, c] == piece and board[r, c+1] == piece and \
               board[r, c+2] == piece and board[r, c+3] == piece:
                return True

    #check vertical - uses range(rows - 3) so r+3 is always within the board bounds
    for c in range(cols):
        for r in range(rows - 3):
            if board[r, c] == piece and board[r+1, c] == piece and \
               board[r+2, c] == piece and board[r+3, c] == piece:
                return True

    #check back diagonals ( / )limits both rows and cols bounds
    for c in range(cols - 3):
        for r in range(rows - 3):
            if board[r, c] == piece and board[r+1, c+1] == piece and \
               board[r+2, c+2] == piece and board[r+3, c+3] == piece:
                return True

    #check forward diagonals ( \ )limits both rows and cols bounds
    for c in range(cols - 3):
        for r in range(3, rows):
            if board[r, c] == piece and board[r-1, c+1] == piece and \
               board[r-2, c+2] == piece and board[r-3, c+3] == piece:
                return True

    return False



def drop_piece(board: np.ndarray, piece: str, col_index: int) -> bool:
    """
    simulate dropping a piece into the board down a specific column until it hits the bottom
    or rests on another piece. Returns False if the column is full
    :param board: the current 2D NumPy array game board
    :param piece: the string character representing the player's game piece
    :param col_index: the 0-based integer index of the chosen column
    :return: boolean True if the piece successfully dropped, False if the column was entirely full
    """
    rows, cols = board.shape

    #iterate backwards through the board from the bottom row up to the top
    for r in range(rows - 1, -1, -1):
        if board[r, col_index] == "#":
            board[r, col_index] = piece
            return True

    #if no space is available, return False
    return False
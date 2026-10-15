import random
import numpy as np


def create_board(rows: int, cols: int) -> np.ndarray:
    board = np.full((rows, cols), "#")
    board = random_cell_blocking(board, block_char="!")
    return board


def random_cell_blocking(board, block_char="!") -> np.ndarray:
    rows, cols = board.shape
    total_cells = rows * cols

    #get a random % of cells to block
    block_percent = random.randint(1, 10) / 100
    #get the number of cells to block
    num_to_block = max(1,int(total_cells * block_percent)) #at least 1 cell, up to total_cells * block_percent

    #randomly select which cells to block
    chosen_cells_to_block = np.random.choice(total_cells, size=num_to_block, replace=False)

    #replace the empty cell char with the block char, using the row and col indices
    for i in chosen_cells_to_block:
        row = i // cols
        col = i % cols
        board[row, col] = block_char

    return board



def check_win(board, piece):
    rows, cols = board.shape

    #check horizontal
    for c in range(cols - 3):
        for r in range(rows):
            if board[r, c] == piece and board[r, c+1] == piece and \
               board[r, c+2] == piece and board[r, c+3] == piece:
                return True

    #check vertical
    for c in range(cols):
        for r in range(rows - 3):
            if board[r, c] == piece and board[r+1, c] == piece and \
               board[r+2, c] == piece and board[r+3, c] == piece:
                return True

    #check back diagonals ( / )
    for c in range(cols - 3):
        for r in range(rows - 3):
            if board[r, c] == piece and board[r+1, c+1] == piece and \
               board[r+2, c+2] == piece and board[r+3, c+3] == piece:
                return True

    #check forward diagonals ( \ )
    for c in range(cols - 3):
        for r in range(3, rows):
            if board[r, c] == piece and board[r-1, c+1] == piece and \
               board[r-2, c+2] == piece and board[r-3, c+3] == piece:
                return True

    return False



def drop_piece(board, piece, col_index):
    rows, cols = board.shape

    #start to scan from bottom since pieces fall
    for r in range(rows -1, -1,-1):
        if board[r, col_index] == "#":
            board[r, col_index] = piece
            return True

    return False

if __name__ == "__main__":
    create_board(10, 10)

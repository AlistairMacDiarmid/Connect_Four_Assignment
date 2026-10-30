"""
property-based tests for game properties using Hypothesis
"""

import unittest
import numpy as np
from hypothesis import given, strategies as st

from core.game_logic import create_board, random_cell_blocking, drop_piece, check_win
#TODO -  test the AI agent
from core.ai_agent import get_valid_locations, AIAgent


class BoardPropertiesTest(unittest.TestCase):
    """
    property tests for the board generation and random cell blocking invariants
    """

    @given(
        rows = st.integers(min_value=6, max_value=20),
        cols = st.integers(min_value=7, max_value=20)
    )
    def test_board_dimensions(self, rows: int, cols: int) -> None:
        board =  create_board(rows, cols)
        self.assertEqual(board.shape, (rows, cols))

    @given(
        rows = st.integers(min_value=6, max_value=20),
        cols = st.integers(min_value=7, max_value=20)
    )
    def test_board_valid_chars(self, rows: int, cols: int) -> None:
        """
        a newly created board should only contain '#' and '!'
        :param rows:
        :param cols:
        :return:
        """
        board = create_board(rows,cols)
        unique_tokens = set(board.flatten())
        self.assertTrue(unique_tokens.issubset({"#","!"}))

    @given(
        rows = st.integers(
        min_value=6, max_value=20),
        cols = st.integers(min_value=7, max_value=20)
    )
    def test_blocked_cell_count(self, rows: int, cols: int) -> None:
        """
        the blocked number of cells present in every board must be at least one, with no more than 10% of the total cells
        :param rows:
        :param cols:
        :return:
        """
        board = create_board(rows, cols)
        total_cells = rows * cols
        blocked_count = int(np.count_nonzero(board == "!"))
        max_allowed = max(1, int(total_cells * 0.10))
        self.assertGreaterEqual(blocked_count, 1)
        self.assertLessEqual(blocked_count, max_allowed)


class GamePieceDroppingTest(unittest.TestCase):
    @given(
        rows=st.integers(min_value=6, max_value=15),
        cols=st.integers(min_value=7, max_value=15),
        piece=st.sampled_from(["X", "O"]),
    )
    def test_drop_piece_preserves_blocked_cells(self, rows: int, cols: int, piece: str) -> None:
        """
        when a piece is dropped, it must never overwrite a blocked cell
        :param rows:
        :param cols:
        :param piece:
        :return:
        """
        board = create_board(rows, cols)
        initial_blocked_coords = set(zip(*np.where(board == "!")))

        #attempt to drop a piece in every col
        for c in range(cols):
            drop_piece(board, piece, c)

        after_blocked_coords = set(zip(*np.where(board == "!")))
        self.assertEqual(initial_blocked_coords, after_blocked_coords)

    @given(
        rows=st.integers(min_value=6, max_value=15),
        cols=st.integers(min_value=7, max_value=15),
        piece=st.sampled_from(["X", "O"]),
    )
    def test_piece_drops_lowest_available_row(self, rows: int, cols: int, piece: str) -> None:
         """
         when a piece is dropped, it must drop in the lowest available row
         :param rows:
         :param cols:
         :param piece:
         :return:
         """
         board = create_board(rows,cols)
         valid_cols = [c for c in range(cols) if '#' in board[:,c]]
         if not valid_cols:
             return

         col = valid_cols[0]
         empty_rows = [r for r in range(rows) if board[r,col] == "#"]
         expected_row = max(empty_rows)

         success = drop_piece(board, piece, col)
         self.assertTrue(success)
         self.assertEqual(board[expected_row, col], piece)


    @given(
        rows=st.integers(min_value=6, max_value=15),
        cols=st.integers(min_value=7, max_value=15),
        piece=st.sampled_from(["X", "O"]),
    )
    def test_full_col_drop(self,  rows: int, cols: int, piece: str) -> None:
        """
        attempting to drop a piece in a full column should fail
        :param rows:
        :param cols:
        :param piece:
        :return:
        """
        board = np.full((rows,cols), "#")
        #fill col at index 0 fully
        board[:,0] = piece
        board_prior = board.copy()

        success = drop_piece(board, piece, 0)
        self.assertFalse(success)
        np.testing.assert_array_equal(board, board_prior)



class WinConditionsTest(unittest.TestCase):
    @given(
        rows=st.integers(min_value=6, max_value=15),
        cols=st.integers(min_value=7, max_value=15),
        piece=st.sampled_from(["X", "O"]),
    )
    def test_empty_board(self, rows: int, cols: int, piece: str) -> None:
        """
        an empty board should never register a winner
        :param rows:
        :param cols:
        :param piece:
        :return:
        """
        board = np.full((rows,cols),"#")
        self.assertFalse(check_win(board, piece))


    @given(
        rows=st.integers(min_value=6, max_value=15),
        cols=st.integers(min_value=7, max_value=15),
        piece=st.sampled_from(["X", "O"]),
    )
    def test_horizontal_win_check(self, rows: int, cols: int, piece: str) -> None:
        """
        any four consecutive horizontal pieces should always trigger a win
        :param rows:
        :param cols:
        :param piece:
        :return:
        """
        board = np.full((rows,cols),"#")
        r = rows // 2
        c = 0 #cols >= 7, so c...c+3 is guaranteed to be in bounds
        for offset in range(4):
            board[r,c+offset] = piece

        self.assertTrue(check_win(board, piece))

    @given(
        rows=st.integers(min_value=6, max_value=15),
        cols=st.integers(min_value=7, max_value=15),
        piece=st.sampled_from(["X", "O"]),
    )
    def  test_vertical_win_check(self, rows: int, cols: int, piece: str) -> None:
        """
        any four consecutive vertical pieces should always trigger a win
        :param rows:
        :param cols:
        :param piece:
        :return:
        """
        board = np.full((rows,cols), "#")
        c = cols // 2
        r = 0 #rows >= 6, so r...r+3 is guaranteed to be in bounds
        for offset in range(4):
            board[r+offset,c] = piece

        self.assertTrue(check_win(board, piece))

    @given(
        rows=st.integers(min_value=6, max_value=15),
        cols=st.integers(min_value=7, max_value=15),
        piece=st.sampled_from(["X", "O"]),
    )
    def  test_diagonal_win_check(self, rows: int, cols: int, piece: str) -> None:
        """
        any four consecutive diagonal pieces should always trigger a win - both 45 and 135 degree diagonals
        :param rows:
        :param cols:
        :param piece:
        :return:
        """
        #45 degree check
        board_pos = np.full((rows,cols), "#")
        for i in range(4):
            board_pos[i,i] = piece
        self.assertTrue(check_win(board_pos, piece))


        #135 degree check
        board_neg = np.full((rows,cols), "#")
        for i in range(4):
            board_neg[3-i,i] = piece
        self.assertTrue(check_win(board_neg, piece))



#TODO - Add AI Agent test

if __name__ == "__main__":
    unittest.main()
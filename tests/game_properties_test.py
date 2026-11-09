"""
property-based tests for game properties using hypothesis.
"""

import unittest


import numpy as np
from hypothesis import given, settings, strategies as st

from core.game_logic import create_board, drop_piece, check_win, check_win_loop, get_winning_cells
from core.ai_agent import get_valid_locations, AIAgent, MCTSNode


class BoardPropertiesTest(unittest.TestCase):
    """
    property tests for the board generation and random cell blocking invariants.
    """

    @given(
        rows = st.integers(min_value=6, max_value=20),
        cols = st.integers(min_value=7, max_value=20)
    )
    def test_board_dimensions(self, rows: int, cols: int) -> None:
        """
        a newly created board should match the requested row and column dimensions.

        :param rows: integer number of rows on the board
        :param cols: integer number of columns on the board
        :return: none
        """
        board = create_board(rows, cols)
        self.assertEqual(board.shape, (rows, cols))

    @given(
        rows = st.integers(min_value=6, max_value=20),
        cols = st.integers(min_value=7, max_value=20)
    )
    def test_board_valid_chars(self, rows: int, cols: int) -> None:
        """
        a newly created board should only contain '#' and '!'.

        :param rows: integer number of rows on the board
        :param cols: integer number of columns on the board
        :return: none
        """
        board = create_board(rows, cols)
        unique_tokens = set(board.flatten())
        self.assertTrue(unique_tokens.issubset({"#", "!"}))

    @given(
        rows = st.integers(min_value=6, max_value=20),
        cols = st.integers(min_value=7, max_value=20)
    )
    def test_blocked_cell_count(self, rows: int, cols: int) -> None:
        """
        the blocked number of cells present in every board must be at least one, with no more than 10% of the total cells.

        :param rows: integer number of rows on the board
        :param cols: integer number of columns on the board
        :return: none
        """
        board = create_board(rows, cols)
        total_cells = rows * cols
        blocked_count = int(np.count_nonzero(board == "!"))
        max_allowed = max(1, int(total_cells * 0.10))
        self.assertGreaterEqual(blocked_count, 1)
        self.assertLessEqual(blocked_count, max_allowed)



class ValidLocationsPropertyTest(unittest.TestCase):
    """
    property tests for get_valid_locations col discovery.
    """
    @given(
        rows=st.integers(min_value=6, max_value=15),
        cols=st.integers(min_value=7, max_value=15),
    )
    def test_valid_locations_match_cols_with_empty_slots(self, rows: int, cols: int) -> None:
        """
        get_valid_locations must return the exact set of columns containing at least one "#".

        :param rows: integer number of rows on the board
        :param cols: integer number of columns on the board
        :return: none
        """
        board = create_board(rows, cols)
        valid_cols = get_valid_locations(board)

        for col in range(cols):
            has_empty_space = "#" in board[:, col]
            if has_empty_space:
                self.assertIn(col, valid_cols)
            else:
                self.assertNotIn(col, valid_cols)

    @given(
        rows=st.integers(min_value=6, max_value=15),
        cols=st.integers(min_value=7, max_value=15),
        piece=st.sampled_from(["X", "O"]),
    )
    def test_full_col_excluded_from_valid_locations(self, rows: int, cols: int, piece: str) -> None:
        """
        a col with no "#" cells remaining must never be included in valid locations.

        :param rows: integer number of rows on the board
        :param cols: integer number of columns on the board
        :param piece: player piece character ('X' or 'O')
        :return: none
        """
        board = np.full((rows, cols), "#")
        # fill the col with pieces so no empty space tokens are present
        board[:,0] = piece

        valid_cols = get_valid_locations(board)
        self.assertNotIn(0, valid_cols)
        self.assertEqual(len(valid_cols), cols-1)

class GamePieceDroppingTest(unittest.TestCase):
    """
    property tests for gravity-based piece dropping and blocked cell preservation.
    """

    @given(
        rows=st.integers(min_value=6, max_value=15),
        cols=st.integers(min_value=7, max_value=15),
        piece=st.sampled_from(["X", "O"]),
    )
    def test_drop_piece_preserves_blocked_cells(self, rows: int, cols: int, piece: str) -> None:
        """
        when a piece is dropped, it must never overwrite a blocked cell.

        :param rows: integer number of rows on the board
        :param cols: integer number of columns on the board
        :param piece: player piece character ('X' or 'O')
        :return: none
        """
        board = create_board(rows, cols)
        initial_blocked_coords = set(zip(*np.where(board == "!")))

        # attempt to drop a piece in every col
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
        when a piece is dropped, it must drop in the lowest available row.

        :param rows: integer number of rows on the board
        :param cols: integer number of columns on the board
        :param piece: player piece character ('X' or 'O')
        :return: none
        """
        board = create_board(rows, cols)
        valid_cols = [c for c in range(cols) if "#" in board[:, c]]
        if not valid_cols:
            return

        col = valid_cols[0]
        empty_rows = [r for r in range(rows) if board[r, col] == "#"]
        expected_row = max(empty_rows)

        success = drop_piece(board, piece, col)
        self.assertTrue(success)
        self.assertEqual(board[expected_row, col], piece)

    @given(
        rows=st.integers(min_value=6, max_value=15),
        cols=st.integers(min_value=7, max_value=15),
        piece=st.sampled_from(["X", "O"]),
    )
    def test_full_col_drop(self, rows: int, cols: int, piece: str) -> None:
        """
        attempting to drop a piece in a full column should fail.

        :param rows: integer number of rows on the board
        :param cols: integer number of columns on the board
        :param piece: player piece character ('X' or 'O')
        :return: none
        """
        board = np.full((rows, cols), "#")
        # fill col at index 0 fully
        board[:, 0] = piece
        board_prior = board.copy()

        success = drop_piece(board, piece, 0)
        self.assertFalse(success)
        np.testing.assert_array_equal(board, board_prior)


class WinConditionsTest(unittest.TestCase):
    """
    property tests for horizontal, vertical, and diagonal win condition checks.
    """

    @given(
        rows=st.integers(min_value=6, max_value=15),
        cols=st.integers(min_value=7, max_value=15),
        piece=st.sampled_from(["X", "O"]),
    )
    def test_empty_board(self, rows: int, cols: int, piece: str) -> None:
        """
        an empty board should never register a winner.

        :param rows: integer number of rows on the board
        :param cols: integer number of columns on the board
        :param piece: player piece character ('X' or 'O')
        :return: none
        """
        board = np.full((rows, cols), "#")
        self.assertFalse(check_win(board, piece))

    @given(
        rows=st.integers(min_value=6, max_value=15),
        cols=st.integers(min_value=7, max_value=15),
        piece=st.sampled_from(["X", "O"]),
    )
    def test_horizontal_win_check(self, rows: int, cols: int, piece: str) -> None:
        """
        any four consecutive horizontal pieces should always trigger a win.

        :param rows: integer number of rows on the board
        :param cols: integer number of columns on the board
        :param piece: player piece character ('X' or 'O')
        :return: none
        """
        board = np.full((rows, cols), "#")
        r = rows // 2
        c = 0  # cols >= 7, so c...c+3 is guaranteed to be in bounds
        for offset in range(4):
            board[r, c + offset] = piece

        self.assertTrue(check_win(board, piece))

    @given(
        rows=st.integers(min_value=6, max_value=15),
        cols=st.integers(min_value=7, max_value=15),
        piece=st.sampled_from(["X", "O"]),
    )
    def test_vertical_win_check(self, rows: int, cols: int, piece: str) -> None:
        """
        any four consecutive vertical pieces should always trigger a win.

        :param rows: integer number of rows on the board
        :param cols: integer number of columns on the board
        :param piece: player piece character ('X' or 'O')
        :return: none
        """
        board = np.full((rows, cols), "#")
        c = cols // 2
        r = 0  # rows >= 6, so r...r+3 is guaranteed to be in bounds
        for offset in range(4):
            board[r + offset, c] = piece

        self.assertTrue(check_win(board, piece))

    @given(
        rows=st.integers(min_value=6, max_value=15),
        cols=st.integers(min_value=7, max_value=15),
        piece=st.sampled_from(["X", "O"]),
    )
    def test_diagonal_win_check(self, rows: int, cols: int, piece: str) -> None:
        """
        any four consecutive diagonal pieces should always trigger a win - both 45 and 135 degree diagonals.

        :param rows: integer number of rows on the board
        :param cols: integer number of columns on the board
        :param piece: player piece character ('X' or 'O')
        :return: none
        """
        # 45 degree check
        board_pos = np.full((rows, cols), "#")
        for i in range(4):
            board_pos[i, i] = piece
        self.assertTrue(check_win(board_pos, piece))

        # 135 degree check
        board_neg = np.full((rows, cols), "#")
        for i in range(4):
            board_neg[3 - i, i] = piece
        self.assertTrue(check_win(board_neg, piece))


    @given(
        rows=st.integers(min_value=6, max_value=15),
        cols=st.integers(min_value=7, max_value=15),
        piece=st.sampled_from(["X", "O"]),
    )
    def test_get_winning_cells_returns_four_matching_coordinates(
        self, rows: int, cols: int, piece: str
    ) -> None:
        """
        when a win is present on the board, get_winning_cells must return 4 (row, col) coordinates
        that all contain the winning piece.

        :param rows: integer number of rows on the board
        :param cols: integer number of columns on the board
        :param piece: player piece character ('X' or 'O')
        :return: none
        """
        board = np.full((rows, cols), "#")
        r = rows // 2
        for offset in range(4):
            board[r, offset] = piece

        winning_coords = get_winning_cells(board, piece)
        self.assertEqual(len(winning_coords), 4)
        for row_idx, col_idx in winning_coords:
            self.assertEqual(board[row_idx, col_idx], piece)

    @given(
        rows=st.integers(min_value=6, max_value=15),
        cols=st.integers(min_value=7, max_value=15),
        piece=st.sampled_from(["X", "O"]),
        moves=st.lists(st.integers(min_value=0, max_value=14), min_size=0, max_size=30),
    )
    def test_vectorized_check_win_matches_loop_baseline(
        self, rows: int, cols: int, piece: str, moves: list[int]
    ) -> None:
        """
        the optimised vectorised check_win must always return the exact same result
        as the baseline loop-based check_win_loop on any board state.

        :param rows: integer number of rows on the board
        :param cols: integer number of columns on the board
        :param piece: player piece character ('X' or 'O')
        :param moves: list of random column indices to drop pieces into
        :return: none
        """
        board = create_board(rows, cols)
        current_piece = "X"
        for col in moves:
            drop_piece(board, current_piece, col % cols)
            current_piece = "O" if current_piece == "X" else "X"

        self.assertEqual(check_win(board, piece), check_win_loop(board, piece))


class MCTSPropertiesTest(unittest.TestCase):
    """
    properties testing for mcts node expansion, terminal detection, and ucb1 child selection.
    """
    @given(
        rows=st.integers(min_value=6, max_value=15),
        cols=st.integers(min_value=7, max_value=15),
        next_piece=st.sampled_from(["X", "O"]),
    )
    def test_node_expand_creates_valid_child_without_altering_parent(
            self, rows: int, cols: int, next_piece: str
    ) -> None:
        """
        expanding a mcts node must shrink the untried moves by 1, add 1 child node and not alter the parent node
        :param rows: integer number of rows on the board
        :param cols: integer number of columns on the board
        :param next_piece: player piece character dropped during expansion ('X' or 'O')
        :return: none
        """
        board = create_board(rows, cols)
        root = MCTSNode(board = board.copy(), parent = None, column=None, game_piece="X")
        prior_parent_board = root.board.copy()
        initial_untried_count = len(root.untried_moves)

        if initial_untried_count == 0:
            return

        child = root.expand(next_piece)

        #the parent board must remain unchanged
        np.testing.assert_array_equal(prior_parent_board, root.board)
        #check that the untried moves count has decreased by 1 and the children count increases by 1
        self.assertEqual(len(root.untried_moves), initial_untried_count - 1)
        self.assertEqual(len(root.children), 1)
        self.assertIs(child.parent, root)
        self.assertEqual(child.game_piece, next_piece)
        #check if the child board has one fewer "#" than the parent board
        self.assertEqual(int(np.count_nonzero(child.board == "#")), int(np.count_nonzero(root.board == "#")) - 1)

    @given(
        wins_a=st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False),
        wins_b=st.floats(min_value=15.0, max_value=25.0, allow_nan=False, allow_infinity=False),
        visits=st.integers(min_value=25, max_value=100),
    )
    def test_best_child_selects_higher_win_rate_given_equal_visits(
            self, wins_a: float, wins_b: float, visits: int
    ) -> None:
        """
        when two child nodes have the same visit count, best_child must select the one with more wins.

        :param wins_a: win score for child a
        :param wins_b: win score for child b (strictly greater than wins_a)
        :param visits: equal visit count assigned to both children
        :return: none
        """
        board = np.full((6, 7), "#")
        root = MCTSNode(board=board, parent=None, column=None, game_piece="X")
        child_a = root.expand("O")
        child_b = root.expand("O")

        root.visits = visits * 2
        child_a.visits = visits
        child_b.visits = visits
        child_a.wins = wins_a
        child_b.wins = wins_b

        chosen = root.best_child(c=1.414)
        self.assertIs(chosen, child_b)


class MCTSBackpropagationPropertiesTest(unittest.TestCase):
    """
    property tests for mcts backpropagation across ancestor node chains.
    """
    @given(
        depth=st.integers(min_value=1, max_value=6),
        winner=st.sampled_from(["X", "O", None]),
    )
    def test_backpropagate_updates_all_ancestors_correctly(
            self, depth: int, winner: str | None
    ) -> None:
        """
        backpropagate must increment visits by 1 for all ancestors and award 1.0, 0.5, or 0.0 wins.

        :param depth: number of expanded levels in the chain from root to leaf
        :param winner: simulation outcome ('X', 'O', or none for draw)
        :return: none
        """
        board = np.full((6,7), "#")
        agent = AIAgent(name="puter", game_piece="O", human_piece="X", difficulty="medium")

        #build the chain of nodes of length depth+1
        root = MCTSNode(board=board, parent = None, column = None, game_piece="X")
        chain = [root]
        current = root
        piece = "O"
        for _ in range(depth):
            current = current.expand(piece)
            chain.append(current)
            piece = "X" if piece == "O" else "O"

        leaf = chain[-1]
        agent.backpropagate(leaf, winner)

        for node in chain:
            self.assertEqual(node.visits, 1)
            if winner is None:
                self.assertEqual(node.wins, 0.5)
            elif winner == node.game_piece:
                self.assertEqual(node.wins, 1.0)
            else:
                self.assertEqual(node.wins, 0.0)



class AIMCTSPropertiesTest(unittest.TestCase):
    """
    property tests for end-to-end mcts search validity and immediate tactical win detection.
    """
    @settings(max_examples = 25,  deadline = None)
    @given(
        rows=st.integers(min_value=6, max_value=12),
        cols=st.integers(min_value=7, max_value=12),
    )
    def test_mcts_returns_valid_col_and_doesnt_mutate_board(self, rows: int, cols: int) -> None:
        """
        mcts_search must always return a playable column index without altering the input board.

        :param rows: integer number of rows on the board
        :param cols: integer number of columns on the board
        :return: none
        """
        board = create_board(rows, cols)
        valid_cols = get_valid_locations(board)
        if not valid_cols:
            return

        board_state_snap = board.copy()
        agent = AIAgent(name="computer", game_piece="O", human_piece="X", difficulty="medium", iterations = 50)

        chosen_col = agent.mcts_search(board)

        #check input board is not mutated
        np.testing.assert_array_equal(board, board_state_snap)
        #returned col must be a valid playable column
        self.assertIn(chosen_col, valid_cols)


    @settings(max_examples=20, deadline=None)
    @given(
        rows=st.integers(min_value=6, max_value=10),
        cols=st.integers(min_value=7, max_value=10),
        start_col=st.integers(min_value=0, max_value=3),
    )
    def test_mcts_finds_immediate_horizontal_winning_move(
        self, rows: int, cols: int, start_col: int
    ) -> None:
        """
        when the ai has 3 pieces in a horizontal row on the bottom with the 4th column open,
        mcts must select the winning 4th column.

        :param rows: integer number of rows on the board
        :param cols: integer number of columns on the board
        :param start_col: starting column index for the 3-in-a-row setup
        :return: none
        """
        board = np.full((rows, cols), "#")
        bottom_row = rows - 1

        # place 3 of the ai's pieces ('O') next to each other on the bottom row
        board[bottom_row, start_col] = "O"
        board[bottom_row, start_col + 1] = "O"
        board[bottom_row, start_col + 2] = "O"
        winning_col = start_col + 3

        # block the column to the left of start_col (if there is one) so winning_col is the unique winning move
        if start_col > 0:
            board[bottom_row, start_col - 1] = "!"

        agent = AIAgent(
            name="Computer",
            game_piece="O",
            human_piece="X",
            difficulty="medium",
            iterations=200,
        )

        chosen_col = agent.mcts_search(board)
        self.assertEqual(chosen_col, winning_col)


if __name__ == "__main__":
    unittest.main()

"""
game controller for the connect 4 gui.
connects the gamescreen view to the core connect 4 game logic and ai agent.
"""

import logging
import random
import numpy as np

from PyQt6.QtCore import QTimer
from core.ai_agent import AIAgent, get_valid_locations
from core.game_logic import check_win, create_board, drop_piece, get_winning_cells
from gui.views.game_screen import GameScreen

logger = logging.getLogger(__name__)


class GameController:
    """
    connects the gamescreen view to the core connect 4 game logic and ai agent.
    :param game_screen: the gamescreen instance to control
    """

    def __init__(self, game_screen: GameScreen) -> None:
        self.game_screen: GameScreen = game_screen
        self.board: np.ndarray | None = None
        self.mode: int = 1
        self.difficulty: str = "easy"
        self.current_piece: str = "X"
        self.total_moves: int = 0
        self.max_moves: int = 0
        self.game_over: bool = False
        self.ai_agent: AIAgent | None = None

        # listen for cell clicks
        self.game_screen.cell_clicked.connect(self.on_clicked_cell)
        logger.info("GameController initialised and connected to GameScreen")

    def start_game(self, mode: int, rows: int, cols: int, difficulty: str) -> None:
        """
        creates a fresh board, resets the counters, and initialises the game screen grid.
        :param mode: 1 for player vs player, 2 for player vs computer
        :param rows: number of board rows
        :param cols: number of board columns
        :param difficulty: ai difficulty level ('easy', 'medium', or 'hard')
        :return: none
        """
        self.mode = mode
        self.difficulty = difficulty
        self.board = create_board(rows, cols)

        # total playable slots is (total cell count - blocked cell count)
        blocked_cells = int(np.count_nonzero(self.board == "!"))
        self.max_moves = (rows * cols) - blocked_cells
        self.total_moves = 0
        self.current_piece = "X"
        self.game_over = False

        # create the ai agent if pvc selected
        if self.mode == 2:
            self.ai_agent = AIAgent(
                name="Computer",
                game_piece="O",
                human_piece="X",
                difficulty=self.difficulty,
            )
            logger.info("Initialised AIAgent for PvC match (difficulty=%s)", self.difficulty)
        else:
            self.ai_agent = None

        # build the initial button grid and set opening turn text
        self.game_screen.setup_board(self.board, self.current_piece)
        self.game_screen.set_status(
            "Player 1's Turn - Click a column to drop your piece"
        )
        logger.info(
            "Match started: mode=%d, size=%dx%d, blocked_cells=%d, max_playable_moves=%d",
            self.mode,
            rows,
            cols,
            blocked_cells,
            self.max_moves,
        )

    def current_player(self) -> str:
        """
        returns a readable string representation of the current player's name.
        :return: player display name
        :rtype: str
        """
        if self.mode == 1:
            return "Player 1" if self.current_piece == "X" else "Player 2"

        return (
            "Player"
            if self.current_piece == "X"
            else f"Computer ({self.difficulty})"
        )

    def on_clicked_cell(self, row: int, col: int) -> None:
        """
        handles a cell click event by attempting to drop a piece in the selected column.
        :param row: row index of the clicked cell
        :param col: column index of the clicked cell
        :return: none
        """
        if self.board is None or self.game_over:
            logger.debug(
                "Ignored click on cell (row=%d, col=%d): match is not active (game_over=%s)",
                row,
                col,
                self.game_over,
            )
            return

        # block the user attempting to click when it's the computer's turn
        if self.mode == 2 and self.current_piece == "O":
            logger.debug(
                "Ignored click on cell (row=%d, col=%d): waiting for AI turn",
                row,
                col,
            )
            return

        player_name = self.current_player()

        # attempt to drop the piece
        dropped = drop_piece(self.board, self.current_piece, col)
        if not dropped:
            logger.warning(
                "%s ('%s') clicked full column %d (row=%d); move rejected",
                player_name,
                self.current_piece,
                col + 1,
                row + 1,
            )
            self.game_screen.set_status(
                f"Column {col + 1} is full! {player_name} try again"
            )
            return

        logger.info(
            "Move #%d: %s placed '%s' in column %d (clicked row=%d)",
            self.total_moves + 1,
            player_name,
            self.current_piece,
            col + 1,
            row + 1,
        )

        self.advance_turn(col)

    def advance_turn(self, last_col: int) -> None:
        """
        updates the board ui, checks win/draw conditions, and advances the turn to the next player.
        :param last_col: 0-based column index where the last piece was dropped
        :return: none
        """
        if self.board is None:
            return

        self.total_moves += 1
        player_name = self.current_player()
        last_move_msg = (
            f"{player_name} played column {last_col + 1} ({self.current_piece})"
        )

        # check win condition once at least 7 total moves have been played
        if self.total_moves >= 7 and check_win(self.board, self.current_piece):
            self.game_over = True
            self.game_screen.update_board(self.board, None)
            winning_cells = get_winning_cells(self.board, self.current_piece)
            self.game_screen.highlight_winning_cells(winning_cells)
            logger.info(
                "Game Over: %s ('%s') won in %d total moves | Winning cells: %s",
                player_name,
                self.current_piece,
                self.total_moves,
                winning_cells,
            )
            self.game_screen.set_status(f"{last_move_msg} - {player_name} Wins!")
            return

        # check draw condition if no playable cells remain
        if self.total_moves >= self.max_moves:
            self.game_over = True
            self.game_screen.update_board(self.board, None)
            logger.info(
                "Game Over: Draw reached after %d/%d playable moves",
                self.total_moves,
                self.max_moves,
            )
            self.game_screen.set_status(f"{last_move_msg} - It's a Draw!")
            return

        # switch active piece for the next turn
        self.current_piece = "O" if self.current_piece == "X" else "X"
        next_player = self.current_player()

        # if playing vs computer and it is now 'O's turn, disable hover colour and trigger ai move
        if self.mode == 2 and self.current_piece == "O":
            self.game_screen.update_board(self.board, None)
            self.game_screen.set_status(
                f"{last_move_msg}  |  {next_player}'s Turn (O) - Thinking..."
            )
            logger.debug("Scheduling AI turn (%s) in 300ms", self.difficulty)
            QTimer.singleShot(300, self.play_ai_turn)
        else:
            self.game_screen.update_board(self.board, self.current_piece)
            self.game_screen.set_status(
                f"{last_move_msg}  |  Next: {next_player}'s Turn ({self.current_piece})"
            )
            logger.debug("Turn advanced to %s ('%s')", next_player, self.current_piece)

    def play_ai_turn(self) -> None:
        """
        executes the ai's turn by selecting a column and placing a piece on the board.
        :return: none
        """
        if self.board is None or self.game_over or self.ai_agent is None:
            return

        valid_cols = get_valid_locations(self.board)
        if not valid_cols:
            logger.warning("AI turn aborted: no valid columns available on the board")
            return

        logger.debug(
            "AI (%s) evaluating %d valid column(s): %s",
            self.ai_agent.difficulty,
            len(valid_cols),
            [c + 1 for c in valid_cols],
        )

        if self.ai_agent.difficulty == "easy":
            col = int(random.choice(valid_cols))
        else:
            col = self.ai_agent.mcts_search(self.board)

        drop_piece(self.board, self.current_piece, col)
        logger.info(
            "Move #%d: AI (%s) placed '%s' in column %d",
            self.total_moves + 1,
            self.ai_agent.difficulty,
            self.current_piece,
            col + 1,
        )
        self.advance_turn(col)

"""
player module
defines the human player class. handles terminal i/o, input validation and game logic.
"""

import logging
import numpy as np
from rich.console import Console
from core.game_logic import drop_piece

logger = logging.getLogger(__name__)
console = Console(force_terminal=True)


class Player:
    """
    represents a human player in the game.
    stores the player's name and the game piece they are playing. handles the interactive turn loop.
    """

    def __init__(self, name: str, game_piece: str | None = None) -> None:
        """
        initialises a new player instance with a name and optional game piece.

        :param name: display name of the player
        :param game_piece: game piece character ('X' or 'O')
        """
        self.name = name
        self.game_piece = game_piece

    def get_name(self) -> str:
        """
        retrieves the player's display name.

        :return: display name of the player
        :rtype: str
        """
        return self.name

    def play(self, board: np.ndarray) -> int:
        """
        prompts the player to enter a column number, validates it, and updates the board.

        loops until a valid column within bounds is chosen and successfully dropped
        via drop_piece. returns the 0-based column index.

        :param board: 2d numpy array representing the current game board
        :return: 0-based column index of the dropped piece
        :rtype: int
        """
        rows, cols = board.shape

        # infinite loop until the player enters a valid column number
        while True:
            console.print(
                f"\n[bold magenta]{self.name.lower()}'s turn ({self.game_piece})![/bold magenta]"
            )
            console.print(
                f"[bold cyan]enter a column number (1 to {cols}): [/bold cyan]",
                end="",
            )

            try:
                col_input = int(input().strip())
                # convert the column number from human input to a 0-based index
                col_index = col_input - 1

                # ensure the column number is within the board's dimensions
                if col_index < 0 or col_index >= cols:
                    logger.warning("Player '%s' entered out-of-bounds column %d", self.name, col_input)
                    console.print(
                        "[bold red]this is an invalid column number, try again :)[/bold red]\n"
                    )
                    continue

                # attempt to drop the piece. drop_piece() handles gravity and returns false if the column is full
                success = drop_piece(board, self.game_piece, col_index)

                if not success:
                    logger.warning("Player '%s' attempted to play in full column %d", self.name, col_input)
                    console.print(
                        "[bold red]this column is full, try again :)[/bold red]\n"
                    )
                else:
                    # if the piece was successfully dropped, return column index
                    logger.info("Player '%s' placed piece '%s' in column %d", self.name, self.game_piece, col_input)
                    return col_index
            except ValueError:
                logger.warning("Player '%s' entered non-integer input", self.name)
                # catch input error when user enters non-integer values
                console.print(
                    "[bold red]invalid input! please enter a valid whole number.[/bold red]\n"
                )

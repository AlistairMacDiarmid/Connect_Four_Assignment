"""
    Player Module
    Defines the human player class. Handles terminal I/O, input validation and game logic.
"""
import numpy as np
from rich.console import Console
from game_logic import drop_piece

console = Console(force_terminal=True)

class Player:
    """
    Represents a human player in the game.
    Stores the player's name and the game piece they are playing. Handles the interactive turn loop
    """
    def __init__(self,name, game_piece = None):
        self.name = name
        self.game_piece = game_piece

    def play(self, board: np.ndarray):
        """
        Prompts the player to enter a column number, validates it, and updates the board accordingly.

        :param board:
        :return:
        """
        rows, cols = board.shape

        #inifinite loop until the player enters a valid column number
        while True:
            console.print(f"\n[bold magenta]{self.name}'s turn ({self.game_piece})![/bold magenta]")
            console.print(f"[bold cyan]enter a column number (1 to {cols}): [/bold cyan]", end="")

            try:
                col_input = int(input().strip())
                #convert the column number from human input to a 0-based index
                col_index = col_input - 1

                #ensure the column number is within the board's dimensions
                if col_index < 0 or col_index >= cols:
                    console.print("[bold red]this is an invalid column number, try again :)[/bold red]\n")
                    continue


                #attempt to drop the piece. drop_piece() handles gravity and returns False if the column is full
                success = drop_piece(board, self.game_piece, col_index)

                if not success:
                    console.print("[bold red]this column is full, try again :)[/bold red]\n")
                else:
                    #if the piece was successfully dropped, exit the loop
                    break
            except ValueError:
                #catch a TypeError - user types a letter or leaves it blank
                console.print("[bold red]invalid input! please enter a valid whole number.[/bold red]\n")
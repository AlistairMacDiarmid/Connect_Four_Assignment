import time
import random
from rich.console import Console
from game_logic import  drop_piece, check_win


console = Console(force_terminal=True)

class AIAgent:
    def __init__(self, name, game_piece):
        self.name = name
        self.game_piece = game_piece

    def get_valid_locations(self, board):
        valid_locations = []
        cols = board.shape[1]

        for col in range (cols):
            if "#" in board[:,col]:
                valid_locations.append(col)

        return valid_locations



    def play(self, board):

        #little delay so the computer doesnt play their turn instantly
        time.sleep(1)

        valid_locations = self.get_valid_locations(board)

        if valid_locations:
            col = int(random.choice(valid_locations))
            drop_piece(board, self.game_piece, col)
            console.print(f"[bold green]{self.name} played column {col + 1}[/bold green]")






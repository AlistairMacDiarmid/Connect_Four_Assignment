from rich.console import Console
from game_logic import drop_piece

console = Console(force_terminal=True)

class Player:
    def __init__(self,name, game_piece = None):
        self.name = name
        self.game_piece = game_piece

    def play(self, board):
        rows, cols = board.shape

        while True:
            console.print(f"\n[bold magenta]{self.name}'s turn ({self.game_piece})![/bold magenta]")
            console.print(f"[bold cyan]enter a column number (1 to {cols}): [/bold cyan]", end="")

            try:
                col_input = int(input().strip())
                col_index = col_input - 1

                if col_index < 0 or col_index >= cols:
                    console.print("[bold red]this is an invalid column number, try again :)[/bold red]\n")
                    continue

                success = drop_piece(board, self.game_piece, col_index)

                if not success:
                    console.print("[bold red]this column is full, try again :)[/bold red]\n")
                else:
                    break
            except ValueError:
                console.print("[bold red]invalid input! please enter a valid whole number.[/bold red]\n")
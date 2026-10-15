import os
import numpy as np
from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from Player import Player
from game_logic import create_board, check_win



# https://coolors.co/palette/ffe5ec-ffc2d1-ffb3c6-ff8fab-fb6f92


console = Console(force_terminal=True)


def intro_text():


  centered_message = Align.center(
      "[bold cyan]    CONNECT 4![/bold cyan]\n[dim]Player vs Player\nPlayer vs"
      " Computer[/dim]"
  )


  console.print(
      Panel(
          centered_message,
          title="Assignment",
          expand=True,
          border_style="#ffb3c6",
      )
  )


def get_game_mode():


  prompt_message = Align.center(
      "[#fdc500]Select Game Mode:[/#fdc500]\n\n"
      "[green][1][/green] Player vs Player\n"
      "[blue][2][/blue] Player vs Computer"
  )


  console.print(
      Panel(
          prompt_message,
          title="Menu",
          expand=True,
          border_style="#ff8fab",
      )
  )

  console.print()


  while True:
      try:
          console.print("[bold magenta]enter your game mode choice (1 or 2): [/bold magenta]", end="")
          choice = input().strip()

          if choice in ['1', '2']:
              return int(choice)
          else:
              console.print(
                  "[bold red]error: invalid choice. please enter 1 or 2.[/bold red]\n"
              )

      except ValueError:
          console.print(
              "[bold red]invalid input! please enter 1 or 2.[/bold red]\n"
          )
          continue



def get_board_dimensions():

  board_prompt_msg = Align.center(
      "[#fdc500]what size of board do u wish to play with?[/#fdc500]\n\n"
      "[dim](standard Connect 4 is 6 rows by 7 columns (minimum size is 6x7)[/dim]"
  )

  console.print()
  console.print(
      Panel(
          board_prompt_msg,
          title="Board Configuration",
          expand=True,
          border_style="#ff8fab",
      )
  )

  console.print()


  while True:
    try:
      console.print(
          "[bold cyan]enter number of rows (min 6): [/bold cyan]", end=""
      )
      rows = int(input().strip())
      if rows >= 6:
        break
      console.print(
          "[bold red]error: the minimum number of rows is 6[/bold red]\n"
      )
    except ValueError:
      console.print(
          "[bold red]invalid input! please enter a valid number.[/bold red]\n"
      )


  while True:
    try:
      console.print(
          "[bold cyan]enter number of columns (min 7): [/bold cyan]", end=""
      )
      cols = int(input().strip())
      if cols >= 7:
        break
      console.print(
          "[bold red]error: the minimum number of columns is 7[/bold red]\n"
      )
    except ValueError:
      console.print(
          "[bold red]invalid input! please enter a valid number.[/bold red]\n"
      )

  return rows, cols


def display_board(board):
    os.system('cls' if os.name == 'nt' else 'clear')

    rows, cols = board.shape

    info_text = Align.center(
        f"dimensions: [bold cyan]{rows} rows[/bold cyan] × [bold cyan]{cols} columns[/bold cyan]\n"
    )

    grid_rows = []
    for row in range(rows):
        formatted_cells = []
        for col in range(cols):
            cell = board[row, col]

            if cell == "X":
                formatted_cells.append(f"[bold medium_purple1 ]{cell}[/bold medium_purple1]")
            elif cell == "O":
                formatted_cells.append(f"[bold bright_yellow]{cell}[/bold bright_yellow]")
            elif cell == "!":
                formatted_cells.append(f"[bold red]{cell}[/bold red]")
            else:
                formatted_cells.append(f"[dim cyan]{cell}[/dim cyan]")

        row_str = " ".join(formatted_cells)
        grid_rows.append(Align.center(row_str))

    board_panel_content = Group(info_text, "", *grid_rows)

    console.print(
        Panel(
            board_panel_content,
            title="Connect 4 board",
            expand=True,
            border_style="#ff8fab",
        )
    )


def main():
    """
    main entry point to run the Connect 4 application.
    """
    intro_text()
    mode = get_game_mode()

    if mode == 1:
        console.print("\n[bold green]starting player vs player mode...[/bold green]")
        rows, cols = get_board_dimensions()


        board = create_board(rows, cols)
        display_board(board)


        player1 = Player(name="Player 1", game_piece="X")
        player2 = Player(name="Player 2", game_piece="O")

        max_possible_moves = (rows * cols) - int(np.count_nonzero(board == "!"))
        total_moves = 0
        current_player = player1
        game_over = False

        while not game_over:
            current_player.play(board)
            total_moves += 1

            display_board(board)

            if total_moves >= 7:
                if check_win(board, current_player.game_piece):
                    console.print(f"\n[bold green]{current_player.name} wins![/bold green]")
                    game_over = True
                    break

            if total_moves >= max_possible_moves:
                console.print("\n[bold red]it's a draw![/bold red]")
                game_over = True
                break

            #switch turns
            current_player = player2 if current_player == player1 else player1

    else:
        console.print("\n[bold green]starting player vs computer mode...[/bold green]")


if __name__ == "__main__":
    main()


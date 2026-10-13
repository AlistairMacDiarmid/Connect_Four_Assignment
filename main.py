import os
import random
import numpy as np
from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel

# Color palette reference:
# https://coolors.co/palette/ffe5ec-ffc2d1-ffb3c6-ff8fab-fb6f92

# Initialise Rich console for styled terminal output
console = Console(force_terminal=True)


def intro_text():
  """Displays the welcome/intro banner."""
  # Format and centre the title and game subtitle
  centered_message = Align.center(
      "[bold cyan]    CONNECT 4![/bold cyan]\n[dim]Player vs Player\nPlayer vs"
      " Computer[/dim]"
  )

  # Display the intro panel
  console.print(
      Panel(
          centered_message,
          title="Assignment",
          expand=True,
          border_style="#ffb3c6",
      )
  )


def get_game_mode():
  """Prompts the user to select a game mode and returns the choice (1 or 2)."""
  prompt_message = Align.center(
      "[#fdc500]Select Game Mode:[/#fdc500]\n\n"
      "[green][1][/green] Player vs Player\n"
      "[blue][2][/blue] Player vs Computer"
  )

  # Display menu panel
  console.print(
      Panel(
          prompt_message,
          title="Menu",
          expand=True,
          border_style="#ff8fab",
      )
  )

  console.print()

  # Prompt until a valid choice is entered
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
  """Prompts the user for valid board dimensions (min 6 rows, min 7 cols)."""
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

  # Get and validate rows (min 6)
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

  # Get and validate columns (min 7)
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


def build_board(rows: int, cols: int):
    """
    Initialises and renders the game board with randomly blocked cells.
    """

    # initialise board with '#' placeholder
    board = np.full((rows, cols), "#")

    # Add randomly blocked cells to the board
    board = random_cell_blocking(board, block_char="X")

    # clear terminal
    os.system('cls' if os.name == 'nt' else 'clear')

    info_text = Align.center(
        "[bold green]Connect 4 board initialised![/bold green]\n"
        f"dimensions: [bold cyan]{rows} rows[/bold cyan] × [bold cyan]{cols} columns[/bold cyan]\n"
    )

    # Format each row into a centered string for display
    grid_rows = []
    for row in range(rows):
        row_str = " ".join(f"[cyan]{board[row, col]}[/cyan]" for col in range(cols))
        grid_rows.append(Align.center(row_str))

    board_panel_content = Group(info_text, "", *grid_rows)

    # Print board inside a styled panel
    console.print(
        Panel(
            board_panel_content,
            title="Connect 4 board",
            expand=True,
            border_style="#ff8fab",
        )
    )

    return board


def random_cell_blocking(board, block_char="X"):
    """
    Randomly blocks up to 10% of cells on the board using block_char.
    """

    rows, cols = board.shape
    total_cells = rows * cols

    # Pick a random percentage between 1% and 10%
    cell_block_percent = random.randint(1, 10) / 100
    max_blocked = int(total_cells * cell_block_percent)

    # find all empty '#' cells
    empty_cells = list(zip(*np.where(board == "#")))

    if not empty_cells:
        return board

    #determine how many cells to block (at least 1, up to max_blocked)
    upper_bound = min(max_blocked + 1, len(empty_cells) + 1)
    if upper_bound <= 1:
        return board

    num_to_block = np.random.randint(1, upper_bound)

    #randomly pick coordinates to block
    chosen_indices = np.random.choice(
        len(empty_cells), size=num_to_block, replace=False
    )

    # Place the blocking character in the chosen cells
    for idx in chosen_indices:
        r, c = empty_cells[idx]
        board[r, c] = block_char

    return board


def main():
  """
  main entry point to run the Connect 4 application.
  """

  # show title screen
  intro_text()

  # select game mode
  mode = get_game_mode()

  if mode == 1:
    console.print("\n[bold green]starting player vs player mode...[/bold green]")
    rows, cols = get_board_dimensions()
    board = build_board(rows, cols)
  else:
    console.print("\n[bold green]starting player vs computer mode...[/bold green]")


if __name__ == "__main__":
  main()

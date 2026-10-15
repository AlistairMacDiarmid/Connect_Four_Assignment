"""
Connect 4 - application controller and terminal UI
Handle the game loop state, player turns, and Rich-formatted terminal rendering.
"""


import os
from typing import Tuple

import numpy as np
from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel

from Player import Player
from game_logic import create_board, check_win
from ai_agent import AIAgent

# https://coolors.co/palette/ffe5ec-ffc2d1-ffb3c6-ff8fab-fb6f92

console = Console(force_terminal=True)


def intro_text() -> None:
    """
    displays the introductory message for the Connect 4
    :return: None
    """

    #use Align.center to align the text in the centre (horizontally) of the terminal
    centered_message = Align.center(
        "[bold cyan]    CONNECT 4![/bold cyan]\n[dim]Player vs Player\nPlayer vs"
        " Computer[/dim]"
    )

    #use Panel to add a border to the message
    console.print(
        Panel(
            centered_message,
            title="Assignment",
            expand=True,
            border_style="#ffb3c6",
        )
    )


def get_game_mode() -> int | None:
    """
    prompts the user to select the game mode (player vs player or player vs computer)
    :return: int representing the game mode (1 or 2)
    """
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

    #use infinite loop to keep the user inputting until a valid choice is made
    while True:
        try:
            console.print(
                "[bold magenta]enter your game mode choice (1 or 2): [/bold magenta]",
                end="",
            )
            choice = input().strip()
            #use string matching to validate user input then return as integer
            if choice in ["1", "2"]:
                return int(choice)
            else:
                console.print(
                    "[bold red]error: invalid choice. please enter 1 or 2.[/bold red]\n"
                )

        except ValueError:
            console.print("[bold red]invalid input! please enter 1 or 2.[/bold red]\n")
            continue


def get_board_dimensions() -> Tuple[int, int]:
    """
    prompts the user for valid board dimensions
    :return: Tuple containing (rows, cols)
    """
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

    #use infinite loop to keep the user inputting until a valid choice is made - For row count
    while True:
        try:
            console.print(
                "[bold cyan]enter number of rows (min 6): [/bold cyan]", end=""
            )
            rows = int(input().strip())
            #enfoce minimum row count of 6
            if rows >= 6:
                break
            console.print(
                "[bold red]error: the minimum number of rows is 6[/bold red]\n"
            )
        except ValueError:
            console.print(
                "[bold red]invalid input! please enter a valid number.[/bold red]\n"
            )

    #use infinite loop to keep the user inputting until a valid choice is made - For column count
    while True:
        try:
            console.print(
                "[bold cyan]enter number of columns (min 7): [/bold cyan]", end=""
            )
            cols = int(input().strip())
            #enfoce minimum column count of 7
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


def display_board(board: np.ndarray) -> None:
    """
    renders the numpy board array to the terminal using rich styling
    :param board: numpy array representing the game state
    :return: None
    """
    #clear the terminal so the game board is displayed smoothly
    os.system("cls" if os.name == "nt" else "clear")

    rows, cols = board.shape

    info_text = Align.center(
        f"dimensions: [bold cyan]{rows} rows[/bold cyan] × [bold cyan]{cols} columns[/bold cyan]\n"
    )

    grid_rows = []
    #iterate through the 2d numpy array to map the characters to rich styling strings
    for row in range(rows):
        formatted_cells = []
        for col in range(cols):
            cell = board[row, col]
            #apply colour coding for cell ownership/state
            if cell == "X":
                formatted_cells.append(
                    f"[bold medium_purple1 ]{cell}[/bold medium_purple1]"
                )
            elif cell == "O":
                formatted_cells.append(
                    f"[bold bright_yellow]{cell}[/bold bright_yellow]"
                )
            elif cell == "!":
                formatted_cells.append(f"[bold red]{cell}[/bold red]")
            else:
                formatted_cells.append(f"[dim cyan]{cell}[/dim cyan]")

        #join row list into a single string - with spaces between columns
        row_str = " ".join(formatted_cells)
        grid_rows.append(Align.center(row_str))

    #use Group to stack the subtitle and the board rows vertically inside the Panel
    board_panel_content = Group(info_text, "", *grid_rows)

    console.print(
        Panel(
            board_panel_content,
            title="Connect 4 board",
            expand=True,
            border_style="#ff8fab",
        )
    )


def run_game_loop(board: np.ndarray, player1: Player | AIAgent, player2: Player | AIAgent) -> None:
    """
    executes the alternating turn loop until a win or draw occurs
    :param board: numpy array representing the game state
    :param player1: instance of Player or AIAgent
    :param player2: instance of Player or AIAgent
    :return: None
    """
    rows, cols = board.shape

    #calculate the total playable cells by subtracting the number of "!" cells from the total number of cells - "!" is the blocked cell char
    max_possible_moves = (rows * cols) - int(np.count_nonzero(board == "!"))
    total_moves = 0
    current_player = player1
    game_over = False

    while not game_over:
        #trigger active players turn logic.
        current_player.play(board)
        total_moves += 1

        #refresh UI after a turn is processed
        display_board(board)

        #only check for a win after 7 total turns, as mathematically it's impossible for someone to win before this turn count
        if total_moves >= 7:
            if check_win(board, current_player.game_piece):
                console.print(
                    f"\n[bold green]{current_player.name} wins![/bold green]"
                )
                game_over = True
                break

        #draw condition - if no more moves are possible, the game is a draw. Done by checking if the total number of moves is equal to the maximum possible moves
        if total_moves >= max_possible_moves:
            console.print("\n[bold red]it's a draw![/bold red]")
            game_over = True
            break

        #toggle the active player after each turn
        current_player = player2 if current_player == player1 else player1


def main() -> None:
    """
    main entry point to run the Connect 4 application.
    """

    #UI initialisation
    intro_text()
    mode = get_game_mode()

    #generate the board
    rows, cols = get_board_dimensions()
    board = create_board(rows, cols)

    #show the initial board state
    display_board(board)

    #player instantiation based on game mode selection
    if mode == 1:
        console.print("\n[bold green]starting player vs player mode...[/bold green]")
        player1 = Player(name="Player 1", game_piece="X")
        player2 = Player(name="Player 2", game_piece="O")
    else:
        console.print("\n[bold green]starting player vs computer mode...[/bold green]")
        player1 = Player(name="Player", game_piece="X")
        player2 = AIAgent(name="Computer", game_piece="O")

    #game loop
    run_game_loop(board, player1, player2)


if __name__ == "__main__":
    main()
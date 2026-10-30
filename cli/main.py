"""
connect 4 - application controller and terminal ui
handle the game loop state, player turns, and rich-formatted terminal rendering.
"""

import os
import sys
from pathlib import Path
import subprocess
from typing import Tuple

import numpy as np
from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel

from core.player import Player
from core.ai_agent import AIAgent
from core.game_logic import check_win, create_board
import logging
from core.logger import setup_log


console = Console(force_terminal=True)
logger = logging.getLogger(__name__)

def intro_text() -> None:
    """
    displays the introductory message for connect 4 inside a rich panel.

    :return: None
    """
    centered_message = Align.center(
        "[bold cyan]connect 4![/bold cyan]\n[cyan]player vs player\nplayer vs computer[/cyan]"
    )

    console.print(
        Panel(
            centered_message,
            title="assignment",
            expand=True,
            border_style="#ff8fab",
        )
    )


def get_game_mode() -> int | None:
    """
    prompts the user to select the game mode.

    displays a menu allowing selection between player vs player (1) and
    player vs computer (2). validates the choice and re-prompts until a
    valid integer is entered.

    :return: integer representing the selected mode (1 or 2)
    :rtype: int | None
    """
    prompt_message = Align.center(
        "[cyan]select game mode:[/cyan]\n\n"
        "[cyan][1][/cyan] player vs player\n"
        "[cyan][2][/cyan] player vs computer"
    )

    console.print(
        Panel(
            prompt_message,
            title="menu",
            expand=True,
            border_style="#ff8fab",
        )
    )
    console.print()

    # infinite loop until a valid mode choice is entered
    while True:
        try:
            console.print(
                "[deep_pink4]enter your game mode choice (1 or 2): [/deep_pink4]",
                end="",
            )
            choice = input().strip()
            if choice in ["1", "2"]:
                return int(choice)
            else:
                console.print(
                    "[bold red]error: invalid choice. please enter 1 or 2.[/bold red]\n"
                )
        except ValueError:
            console.print("[bold red]invalid input! please enter 1 or 2.[/bold red]\n")
            continue


def get_ai_difficulty() -> str:
    """
    prompts the user to select the ai difficulty level.

    displays a selection menu for easy (random moves) and medium (mcts engine),
    validates user input, and re-prompts if an invalid choice is entered.

    :return: string representing the selected difficulty ("easy" or "medium")
    :rtype: str
    """
    prompt_message = Align.center(
        "[cyan]select ai difficulty:[/cyan]\n\n"
        "[cyan][1][/cyan] easy (random moves)\n"
        "[cyan][2][/cyan] medium (mcts engine)"
    )

    console.print(
        Panel(
            prompt_message,
            title="difficulty configuration",
            expand=True,
            border_style="#ff8fab",
        )
    )
    console.print()

    # infinite loop until a valid difficulty choice is entered
    while True:
        try:
            console.print(
                "[deep_pink4]enter difficulty choice (1 or 2): [/deep_pink4]",
                end="",
            )
            choice = input().strip()
            if choice == "1":
                return "easy"
            elif choice == "2":
                return "medium"
            else:
                console.print(
                    "[bold red]error: invalid choice. please enter 1 or 2.[/bold red]\n"
                )
        except ValueError:
            console.print("[bold red]invalid input! please enter 1 or 2.[/bold red]\n")
            continue


def get_board_dimensions() -> Tuple[int, int]:
    """
    prompts the user for valid board dimensions.

    requests row count (minimum 6) and column count (minimum 7) from the user,
    validating that input values are integers meeting the minimum size constraints.

    :return: tuple of (rows, cols) defining the board dimensions
    :rtype: Tuple[int, int]
    """
    board_prompt_msg = Align.center(
        "[cyan]what size of board do u wish to play with?[/cyan]\n\n"
        "(standard connect 4 is 6 rows by 7 columns - minimum size is 6x7)"
    )

    console.print()
    console.print(
        Panel(
            board_prompt_msg,
            title="board configuration",
            expand=True,
            border_style="#ff8fab",
        )
    )
    console.print()

    # infinite loop until a valid row count (min 6) is entered
    while True:
        try:
            console.print(
                "[deep_pink4]enter number of rows (min 6): [/deep_pink4]", end=""
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

    # infinite loop until a valid column count (min 7) is entered
    while True:
        try:
            console.print(
                "[deep_pink4]enter number of columns (min 7): [/deep_pink4]", end=""
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


def display_board(board: np.ndarray, last_move: str | None = None) -> None:
    """
    renders the numpy board array to the terminal using rich styling.

    clears the terminal screen, prints dimension details and the last played move
    if provided, color-codes tokens and blocked cells, and displays column numbers.

    :param board: 2d numpy array representing the current game board
    :param last_move: optional description string of the most recent move
    :return: None
    """
    # clear the terminal so the game board updates smoothly
    command = "cls" if os.name == "nt" else "clear"
    subprocess.run(command, shell=True)

    rows, cols = board.shape

    info_txt_lines = [
        f"dimensions: [cyan]{rows} rows[/cyan] × [cyan]{cols} columns[/cyan]"
    ]

    # append last move info if available
    if last_move:
        info_txt_lines.append(f"[cyan]last move: {last_move}[/cyan]")

    info_text = Align.center("\n".join(info_txt_lines) + "\n")

    grid_rows = []
    # iterate through 2d numpy array to apply rich styles to each cell
    for row in range(rows):
        formatted_cells = []
        for col in range(cols):
            cell = board[row, col]
            if cell == "X":
                formatted_cells.append(
                    f"[bold medium_purple1]{cell}[/bold medium_purple1]"
                )
            elif cell == "O":
                formatted_cells.append(
                    f"[bold bright_yellow]{cell}[/bold bright_yellow]"
                )
            elif cell == "!":
                formatted_cells.append(f"[bold red]{cell}[/bold red]")
            else:
                formatted_cells.append(f"[dim cyan]{cell}[/dim cyan]")

        row_str = " ".join(formatted_cells)
        grid_rows.append(Align.center(row_str))

    # column numbers and divider at bottom of board display
    divider_str = " ".join(["-"] * cols)
    grid_rows.append(Align.center(f"[dim cyan]{divider_str}[/dim cyan]"))
    col_numbers = [f"[bold white]{c}[/bold white]" for c in range(1, cols + 1)]
    grid_rows.append(Align.center(" ".join(col_numbers)))

    board_panel_content = Group(info_text, "", *grid_rows)

    console.print(
        Panel(
            board_panel_content,
            title="connect 4 board",
            expand=True,
            border_style="#ff8fab",
        )
    )


def run_game_loop(
    board: np.ndarray, player1: Player | AIAgent, player2: Player | AIAgent
) -> None:
    """
    executes the alternating turn loop until a win or draw occurs.

    renders the current board and last move at the start of each turn, prompts
    the active player or ai to make a move, tracks total moves, and checks for
    win or draw conditions after every turn.

    :param board: 2d numpy array representing the game board
    :param player1: player or aiagent instance representing the first player
    :param player2: player or aiagent instance representing the second player
    :return: None
    """
    rows, cols = board.shape

    # calculate total playable cells by subtracting blocked cells ("!")
    max_possible_moves = (rows * cols) - int(np.count_nonzero(board == "!"))
    total_moves = 0
    current_player = player1
    game_over = False
    last_move_txt = None

    # alternating turn loop
    while not game_over:
        display_board(board, last_move_txt)
        col = current_player.play(board)

        # format difficulty indicator if current player is an ai agent
        ai_difficulty = (
            f" ({current_player.difficulty.lower()})"
            if isinstance(current_player, AIAgent)
            else ""
        )
        col_num = col + 1 if col is not None else "?"
        piece_color = (
            "medium_purple1"
            if current_player.game_piece == "X"
            else "bright_yellow"
        )
        player_name = current_player.name.lower()
        last_move_txt = (
            f"{player_name}{ai_difficulty} played column {col_num} "
            f"([{piece_color}]{current_player.game_piece}[/{piece_color}])"
        )

        total_moves += 1

        # check win condition once minimum 7 moves have occurred
        if total_moves >= 7:
            if check_win(board, current_player.game_piece):
                logger.info("Game Over: %s won the game in %d total moves", player_name, total_moves)
                display_board(board, last_move=last_move_txt)
                console.print(
                    f"\n[bold cyan]{player_name} wins![/bold cyan]"
                )
                game_over = True
                break

        # check draw condition if all playable cells are filled
        if total_moves >= max_possible_moves:
            logger.info("Game Over: Game ended in a draw after %d total moves", total_moves)
            display_board(board, last_move=last_move_txt)
            console.print("\n[cyan]it's a draw![/cyan]")
            game_over = True
            break

        # switch active player
        current_player = player2 if current_player == player1 else player1


def main() -> None:
    """
    main entry point to run the connect 4 application.

    initialises the game by showing the intro banner, querying game mode,
    ai difficulty (if playing vs computer), and board dimensions. creates
    the board and player instances and begins the game loop.

    :return: None
    """
    setup_log()
    logger.info("NEW CONNECT FOUR SESSION STARTED")
    intro_text()
    mode = get_game_mode()
    mode_name = "Player vs Player" if mode == 1 else "Player vs Computer"
    logger.info("Selected game mode: %s", mode_name)

    ai_difficulty = "medium"
    if mode == 2:
        ai_difficulty = get_ai_difficulty()
        logger.info("Selected AI difficulty: %s", ai_difficulty)

    rows, cols = get_board_dimensions()
    logger.info("Board dimensions chosen: %dx%d", rows, cols)
    board = create_board(rows, cols)

    # initialise players based on chosen game mode
    if mode == 1:
        player1 = Player(name="player 1", game_piece="X")
        player2 = Player(name="player 2", game_piece="O")
    else:
        player1 = Player(name="player", game_piece="X")
        player2 = AIAgent(
            name="computer",
            game_piece="O",
            human_piece="X",
            difficulty=ai_difficulty,
        )

    run_game_loop(board, player1, player2)


if __name__ == "__main__":
    main()

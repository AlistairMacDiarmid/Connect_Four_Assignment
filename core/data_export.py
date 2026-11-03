"""
game data storage and exporter module
records completed match statistics and move histories in a csv file
"""

import csv
import logging
from datetime import datetime
from pathlib import Path

import numpy as np


logger = logging.getLogger(__name__)

COL_NAMES = [
    "timestamp",
    "interface",
    "game_mode",
    "ai_difficulty",
    "board_size",
    "blocked_cells",
    "winner",
    "total_moves",
    "move_history",
]

def export_match_data(
    interface: str,
    mode: int,
    difficulty: str,
    board: np.ndarray,
    winner: str,
    total_moves: int,
    move_history: list[int],
    file_path: str = "data/match_history.csv",
) -> Path:
    """
    stores and exports completed match data as a row in a csv file.

    :param interface: string identifier for the ui used ('CLI' or 'GUI')
    :param mode: integer game mode (1 for pvp, 2 for pvc)
    :param difficulty: ai difficulty setting ('easy' or 'medium')
    :param board: final 2d numpy array game board
    :param winner: display name of the winning player, or 'Draw'
    :param total_moves: total number of pieces dropped during the match
    :param move_history: list of 1-based column numbers played in chronological order
    :param file_path: relative or absolute path to the target csv file
    :return: resolved path to the exported csv file
    :rtype: Path
    """
    output_path = Path(file_path)
    if not output_path.is_absolute():
        project_root = Path(__file__).resolve().parent.parent
        output_path = project_root / output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    exists = output_path.exists()

    rows, cols = board.shape
    blocked_cells = int(np.count_nonzero(board == "!"))
    mode_str  = "PvP" if mode == 1 else "PvC"
    ai_difficulty_str = difficulty if mode == 2 else "N/A"
    moves_str = "->".join(str(col) for col in move_history)

    row_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "interface": interface,
        "game_mode": mode_str,
        "ai_difficulty": ai_difficulty_str,
        "board_size": f"{rows}x{cols}",
        "blocked_cells": blocked_cells,
        "winner": winner,
        "total_moves": total_moves,
        "move_history": moves_str,
    }

    with output_path.open(mode="a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=COL_NAMES)
        if not exists:
            writer.writeheader()
        writer.writerow(row_data)

    logger.info("Exported match data to %s (winner=%s, moves=%d)", output_path, winner, total_moves)
    return output_path
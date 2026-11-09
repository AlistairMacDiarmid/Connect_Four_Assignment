"""
benchmark script comparing computation time and memory usage between:
1. check_win_loops (baseline nested python loops)
2. check_win (optimised numpy vectorised slicing)
"""

import random
import time
import tracemalloc
from typing import Callable

import numpy as np

from core.game_logic import check_win, check_win_loop, create_board, drop_piece


def generate_a_midgame_board(rows: int, cols: int, num_moves: int, seed: int = 28) -> np.ndarray:
    """
    creates a reproducible mid-game board with random pieces dropped so the win checks scan a realistic board state.
    :param rows: integer number of rows on the board
    :param cols: integer number of columns on the board
    :param num_moves: integer number of moves to drop pieces onto the board
    :param seed: integer seed for random number generator
    :return: numpy array representing the board state
    """

    random.seed(seed)
    np.random.seed(seed)
    board = create_board(rows, cols)
    game_piece = "X"

    for _ in range(num_moves):
        col = np.random.randint(cols)
        drop_piece(board, game_piece, col)
        game_piece = "O" if game_piece == "X" else "X"

    return board


def benchmark_function(func: Callable[[np.ndarray, str], bool],board: np.ndarray,iterations: int = 20_000,) -> tuple[float, int]:
    """
    measures total execution time in milliseconds and peak memory usage in bytes for a win-check function.

    :param func: win-check callable accepting (board, piece) and returning a boolean
    :param board: 2d numpy array representing the mid-game board to test against
    :param iterations: number of loop iterations to execute (each iteration checks both 'X' and 'O')
    :return: tuple of (elapsed_time_ms, peak_memory_bytes)
    :rtype: tuple[float, int]
    """
    # warm-up call before starting timers and memory tracing
    func(board, "X")

    tracemalloc.start()
    start_time = time.perf_counter()

    for _ in range(iterations):
        func(board, "X")
        func(board, "O")

    elapsed = (time.perf_counter() - start_time) * 1000.0
    peak_mem = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

    return elapsed, peak_mem


def run_benchmark() -> None:
    """
    runs the win-check benchmark across standard, medium, and large board presets and prints results.

    :return: none
    """
    board_configs = [
        ("standard", 6,7,12),
        ("medium", 10,11,30),
        ("large", 20,20,60),

    ]
    iterations = 10_000


    for label, rows, cols, moves in board_configs:
        board = generate_a_midgame_board(rows, cols, moves)

        #run benchmarks
        loop_ms, loop_mem = benchmark_function(check_win_loop, board, iterations)
        vec_ms, vec_mem = benchmark_function(check_win, board, iterations)

        if vec_ms > 0:
            speedup = round(loop_ms / vec_ms, 2)
        else:
            speedup = 0.0

        print("Board:", label)
        print("  Method: Python Nested Loops | Time:", loop_ms, "ms | Memory:", loop_mem, "bytes | Speedup: 1.0x")
        print("  Method: NumPy Vectorised    | Time:", vec_ms, "ms | Memory:", vec_mem, "bytes | Speedup:", speedup,
              "x")
        print()



if __name__ == "__main__":
    run_benchmark()
"""
ai agent module
implements computer player logic using random move selection and monte carlo tree search (mcts).
"""

from __future__ import annotations

import logging
import math
import random
import time
from typing import List, Optional

import numpy as np
from rich.console import Console
from core.game_logic import drop_piece, check_win

logger = logging.getLogger(__name__)
console = Console(force_terminal=True)


def get_valid_locations(board: np.ndarray) -> list[int]:
    """
    finds all columns on the board that have at least one empty slot.

    :param board: 2d numpy array representing the current board state
    :return: list of 0-based column indices that can accept a piece
    :rtype: list[int]
    """
    valid_locations = []
    cols = board.shape[1]

    # iterate through all columns and collect those with an available slot ('#')
    for col in range(cols):
        if "#" in board[:, col]:
            valid_locations.append(col)

    return valid_locations


class MCTSNode:
    """
    represents a node in the monte carlo tree search tree.

    tracks board state, visit counts, win score, untried moves, and child nodes.
    """

    def __init__(
        self,
        board: np.ndarray,
        parent: Optional[MCTSNode],
        column: Optional[int],
        game_piece: str = "O",
    ) -> None:
        """
        initialises an mcts node with board state, parent pointer, move column, and piece.

        :param board: 2d numpy array representing the board at this node
        :param parent: parent mcts node, or none for the root node
        :param column: column index that led to this node state, or none for root
        :param game_piece: piece character ('X' or 'O') placed to reach this node
        """
        self.board = board
        self.parent = parent
        self.column = column
        self.game_piece = game_piece
        self.visits = 0
        self.wins = 0.0
        self.untried_moves = get_valid_locations(self.board)
        random.shuffle(self.untried_moves)
        self.children: List[MCTSNode] = []

    def is_terminal(self, human_piece: str) -> bool:
        """
        determines whether the current node represents a terminal game state (win or draw).

        :param human_piece: string character representing the human opponent's piece
        :return: true if either player has won or no valid moves remain, otherwise false
        :rtype: bool
        """
        opponents_piece = (
            human_piece
            if self.game_piece != human_piece
            else ("O" if human_piece == "X" else "X")
        )
        if check_win(self.board, self.game_piece) or check_win(
            self.board, opponents_piece
        ):
            return True
        return len(get_valid_locations(self.board)) == 0

    def is_fully_expanded(self) -> bool:
        """
        checks whether all possible child moves from this node have been expanded.

        :return: true if untried moves list is empty, otherwise false
        :rtype: bool
        """
        return len(self.untried_moves) == 0

    def expand(self, next_game_piece: str) -> MCTSNode:
        """
        expands an untried move by creating and returning a new child mcts node.

        :param next_game_piece: string character of the player whose turn it is next
        :return: newly created child mcts node
        :rtype: MCTSNode
        """
        col = self.untried_moves.pop()

        # copy board and drop piece
        new_board = self.board.copy()
        drop_piece(new_board, next_game_piece, col)

        child_node = MCTSNode(
            board=new_board,
            parent=self,
            column=col,
            game_piece=next_game_piece,
        )

        self.children.append(child_node)
        return child_node

    def best_child(self, c: float = 1.414) -> MCTSNode:
        """
        selects the best child node using the upper confidence bound 1 (ucb1) formula.

        :param c: exploration parameter balancing exploitation and exploration
        :return: child mcts node with the highest ucb1 score
        :rtype: MCTSNode
        """
        for child in self.children:
            if child.visits == 0:
                return child

        def ucb(child: MCTSNode) -> float:
            exploit = child.wins / child.visits
            explore = c * math.sqrt(math.log(self.visits) / child.visits)
            return exploit + explore

        return max(self.children, key=ucb)


class AIAgent:
    """
    represents an ai opponent supporting easy (random) and medium (mcts) difficulty levels.
    """

    def __init__(
        self,
        name: str,
        game_piece: str,
        human_piece: str = "X",
        difficulty: str = "medium",
        iterations: int = 1500,
    ) -> None:
        """
        initialises the ai agent with identity, game pieces, difficulty, and search iterations.

        :param name: display name of the ai agent
        :param game_piece: game piece character used by the ai ('X' or 'O')
        :param human_piece: game piece character used by the human opponent
        :param difficulty: difficulty setting ('easy' or 'medium')
        :param iterations: number of mcts iterations to execute per move in medium mode
        """
        self.name = name
        self.game_piece = game_piece
        self.human_piece = human_piece
        self.difficulty = difficulty.lower()
        self.iterations = iterations

    def get_difficulty(self) -> str:
        """
        returns the current difficulty level of the ai agent.

        :return: difficulty level string in lowercase ('easy' or 'medium')
        :rtype: str
        """
        return self.difficulty

    def play(self, board: np.ndarray) -> int | None:
        """
        determines and executes a move on the board according to the chosen difficulty.

        in easy mode, selects randomly from available valid columns. in medium mode,
        runs monte carlo tree search. drops the piece on the board and returns the column.

        :param board: 2d numpy array representing the current game board
        :return: 0-based column index played, or none if no valid moves exist
        :rtype: int | None
        """
        valid_locations = get_valid_locations(board)
        if not valid_locations:
            logger.warning("AI '%s' found no valid locations available", self.name)
            return None

        console.print(
            f"\n[bold bright_yellow]{self.name.lower()}'s turn ({self.game_piece})[/bold bright_yellow] [cyan]– thinking...[/cyan]"
        )

        time.sleep(2)

        if self.difficulty == "easy":
            # easy mode just chooses a random valid column to play its piece
            col = int(random.choice(valid_locations))
            logger.info("AI '%s' (easy) selected random column %d", self.name, col + 1)
        else:
            # medium mode runs monte carlo tree search
            logger.info("AI '%s' (%s) running MCTS with %d iterations", self.name, self.difficulty, self.iterations)
            col = self.mcts_search(board)
            logger.info("AI '%s' selected column %d via MCTS", self.name, col + 1)

        drop_piece(board, self.game_piece, col)
        logger.info("AI '%s' placed piece '%s' in column %d", self.name, self.game_piece, col + 1)
        return col

    def mcts_search(self, board: np.ndarray) -> int:
        """
        runs the 4-phase monte carlo tree search algorithm to select the best move.

        phases: selection, expansion, simulation, and backpropagation.

        :param board: 2d numpy array representing current game board
        :return: 0-based column index with the most visits
        :rtype: int
        """
        # root node which represents the current board state
        root = MCTSNode(
            board=board.copy(),
            parent=None,
            column=None,
            game_piece=self.human_piece,
        )

        for _ in range(self.iterations):
            node = root
            current_piece_turn = self.game_piece

            # phase 1 - selection
            while node.is_fully_expanded() and not node.is_terminal(
                self.human_piece
            ):
                node = node.best_child(c=1.414)
                current_piece_turn = (
                    self.human_piece
                    if node.game_piece != self.human_piece
                    else self.game_piece
                )

            # phase 2 - expansion
            if not node.is_fully_expanded() and not node.is_terminal(
                self.human_piece
            ):
                node = node.expand(current_piece_turn)

            # phase 3 - simulation
            winner = self.simulate_random_rollout(node)

            # phase 4 - backpropagation
            self.backpropagate(node, winner)

        if not root.children:
            valid = get_valid_locations(board)
            return random.choice(valid)

        # pick the most robust child - the one with the most visits
        robust_child = max(root.children, key=lambda child: child.visits)
        return robust_child.column

    def simulate_random_rollout(self, node: MCTSNode) -> str | None:
        """
        simulates a random rollout game from the given node until a win or draw occurs.

        :param node: mcts node from which simulation starts
        :return: winning piece character ('X' or 'O'), or none in case of a draw
        :rtype: str | None
        """
        if check_win(node.board, node.game_piece):
            return node.game_piece

        simulation_board = node.board.copy()
        turn = (
            self.game_piece
            if node.game_piece == self.human_piece
            else self.human_piece
        )
        other_turn = node.game_piece

        while True:
            valid = get_valid_locations(simulation_board)
            if not valid:
                # draw condition - no valid moves left
                return None

            col = random.choice(valid)
            drop_piece(simulation_board, turn, col)

            if check_win(simulation_board, turn):
                return turn

            turn, other_turn = other_turn, turn

    def backpropagate(self, node: MCTSNode | None, winner: str | None) -> None:
        """
        propagates simulation results up the tree from leaf node to root.

        updates visit count and increments wins (1 for win, 0.5 for draw, 0 for loss).

        :param node: leaf mcts node where simulation started
        :param winner: winning piece character ('X' or 'O'), or none for draw
        :return: None
        """
        while node is not None:
            node.visits += 1
            if winner is None:
                node.wins += 0.5
            elif winner == node.game_piece:
                node.wins += 1
            node = node.parent

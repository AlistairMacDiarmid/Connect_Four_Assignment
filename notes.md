# <u>Notes</u>

---

## Creating the AI

- minimax and alpha-beta pruning
- deep Q networks and PPO 
- heuristics and optimisations

---
### Minimax and Alpha-Beta Pruning

- minimax algorithm
- alpha-beta pruning technique

https://www.deepexploration.org/blog/minimax-algorithm-for-connect-4


Minimax is an algorithm used for turn-based games. the algorithm splits the game into two opposing forces:
    1. The maximizer (the AI): seeks the path which results in the highest positive score (+100000 for an AI win)
    2. The minimizer (the player): seeks the path which results in the lowest negative score (-100000 for a player win)

Minimax operates under the strict assumption that the game opponent is perfectly rational. This means the AI will never choose a path which relies on the
human making a mistake. As the AI evaluates future boards, it will assume the minimizer wil always choose the response that is mathematically most devastating to the AI.

Minimax is a recursive algorithm. It evaluates the score of each possible move, 
and then recursively evaluates the score of each possible response to that move. 
This process continues until a terminal state is reached (a win, loss, or draw). The AI then chooses the move which results in the highest score.


### The Curse of Dimensionality

Since the user can dictate the size of the board, the dynamic sizing introduces severe computational challenges. The number states the Minimax algorithm 
must evaluate grows exponentially based on two factors:

- <b>Branching Factor (b)</b>: the number of legal moves available on a turn (equal to the number of unfilled columns)
- <b>Serach Depth (d)</b>: how many turns ahead the AI attempts to look

| Board Setup           | Look-Ahead Depth | Boards Evaluated         |
| :-------------------- | :--------------- | :----------------------- |
| 7 columns (Standard)  | 5 moves ahead    | 7^5 = 16,807 states      |
| 7 columns (Standard)  | 7 moves ahead    | 7^7 = 823,543 states     |
| 10 columns (Custom)   | 7 moves ahead    | 10^7 = 10,000,000 states |


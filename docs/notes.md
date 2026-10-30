# Connect Four Assignment Notes







#### Terminal Based Colour Coding – Using the Rich package – https://rich.readthedocs.io/en/stable/introduction.html

<i> subject to change </i>


- Borders & Titles: Pink (#ff8fab)
- Prompts: Deep pink (deep_pink4)
- Information & Subtitles: Cyan (cyan)
- Piece One (X): Purple (medium_purple1)
- Piece Two (O): Bright Yellow (bright_yellow)
- Blank Cells (#): Dimmed Cyan (dim cyan)
- Blocked Cells (!): Bold Red (bold red)






#### TODO:
- when the computer is playing their turn, no info is displayed informing the player, add a message to the terminal the computer is playing their turn
- add a message to the top of the board of the most recent move for both the player and the computers moves 
- change colour of the winning line game pieces to be bright green 
- add column numbers to the bottom of the board to make it easier to read. ✔
- add replay functionality via a prompt. 




## The AI Agent to play against
---
### Monte Carlo Tree Search (MCTS)

For explanation scenario, a standard board size of 6x7 is used
### Phase 1: Exploration
The AI checks all 7 columns. In this example, column 1 has 0 visits so far (has no game pieces droppped in its column). For this reason, it scores infinity for its UCB1 Score. 
MCTS will always try every untried column at least once before doubling down.

### Phase 2: Expansion
The AI then imagines dropping a game piece into column 1. It then adds this hypothetical board state to its mental tree in order to test what happens next

### Phase 3: Simulation
The AI then simulates a random game from this hypothetical board state. It does this by dropping random pieces for both players until the practice game ends. 

### Phase 4: Backpropagation
After the simulation ends, the AI walks backwards from the leaf to the root, while incrementing the visit counts (+1) and updating win scores (+1 for the player who made the move which won, or +0.5 for a draw)
for every node in the ancestory path. 

### Picking the most robust child – the one with the most visits
After all iterations (after n simulated practice games) are complete, the AI ignores the UCB1 score and looks directly at the children attached to the root node, and picks the 
column with the highest visit counts – This column is picked as its survived the most simulated stress tests.

## References & Resources

For Monte Carlo Tree Search Implementation:
1. Olin College Connect 4 MCTS Study (Asymmetric tree growth, Connect 4 state-space complexity):
   https://mcts.netlify.app/
2. AI-Boson MCTS Python Tutorial (Object-oriented Node design, lazy expansion via untried_moves, tree_policy):
   https://ai-boson.github.io/mcts/
3. GeeksforGeeks MCTS in Machine Learning (Four-phase loop, UCB1 equation, zero-sum perspective backpropagation):
   https://www.geeksforgeeks.org/machine-learning/monte-carlo-tree-search-mcts-in-machine-learning/
4. Multi-Armed Bandit UCB1 Analysis ("Optimism in the face of uncertainty", confidence-bound convergence):
   https://github.com/kfoofw/bandit_simulations/blob/master/python/multiarmed_bandits/analysis/ucb.md
---

# Hypothesis Testing

https://hypothesis.readthedocs.io/en/latest/tutorial/builtin-strategies.html












##### Random Tid Bits
- mac venv activate command: `source venv/bin/activate` 
- windows  `venv\Scripts\activate`

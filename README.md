# Connect_Four_Assignment

Advanced Python programming Assignment. The assignment is Connect Four.

## Project Directory Overview

```text
Assignment/
├── cli_main.py                      # Top-level entry point for the terminal CLI
├── gui_main.py                      # Top-level entry point for the PyQt6 GUI
├── requirements.txt                 # Third-party package dependencies
├── core/                            # Shared game engine, AI, logging, and CSV data export
│   ├── game_logic.py                # Board creation, random blockers, gravity, and win detection
│   ├── player.py                    # Human terminal player class and input validation
│   ├── ai_agent.py                  # MCTSNode and AIAgent (Easy random & Medium MCTS)
│   ├── data_export.py               # CSV match history storage and retrieval
│   └── logger.py                    # Centralised file logging configuration
├── cli/                             # Terminal User Interface
│   └── main.py                      # Terminal prompts, board rendering, and CLI game loop
├── gui/                             # Graphical User Interface (PyQt6)
│   ├── __main__.py                  # GUI application bootstrapper
│   ├── main_window.py               # QMainWindow & QStackedWidget navigation manager
│   ├── controllers/
│   │   └── game_controller.py       # MVC controller linking GameScreen to core logic & AI
│   ├── views/
│   │   ├── title_screen.py          # Landing screen (Play / Exit)
│   │   ├── gamemode_select_screen.py# Mode selection screen (PvP / PvC)
│   │   ├── game_setup_screen.py     # Board dimension & AI difficulty configuration screen
│   │   └── game_screen.py           # Interactive board grid, colour key, & match history panel
│   └── assets/
│       ├── styles.qss               # External Qt stylesheet & dynamic property selectors
│       └── fonts/                   # Bundled retro/pixel TrueType fonts (.ttf)
├── tests/                           # Automated test suite
│   └── game_properties_test.py      # Hypothesis property-based test suite
├── benchmarks/                      # Performance & memory profiling
│   └── benchmark_check_win.py       # Loop vs. NumPy vectorised check_win benchmark
├── data/
│   └── match_history.csv            # CSV log of completed CLI & GUI matches
└── logs/
    ├── game.log                     # CLI runtime log file
    └── gui_game.log                 # GUI runtime log file
```

## Project Dependencies

```pip-requirements
numpy==2.5.4
rich==15.0.0
hypothesis==6.170.14
PyQt6==6.12.0
pyqt6-sip==13.13.0
```

## How to run the project

1.  Install the required dependencies by running `pip install -r requirements.txt`.
2.  Navigate to the project directory.
3.  Run the CLI version of the game by executing `python cli_main.py`.
4.  Run the GUI version of the game by executing `python gui_main.py`.
5.  Run the property-based test suite by executing `python -m unittest tests/game_properties_test.py -v` (or `pytest -v --hypothesis-show-statistics`).
6.  Run the win-check optimisation benchmark by executing `python -m benchmarks.benchmark_check_win`.

## Project Modules

### CLI (`rich` Terminal Rendering)

The command line interface (CLI) version of the game makes use of the package `rich` to create a visually appealing experience for the player. The standard Python terminal output is basic monochromatic text, whereas `rich` allows for colourful text, tables, and other rich text formatting.

Why `rich` was used:

-   By assigning consistent colour roles across the interface—pink `(#ff8fab)` for structural Panel borders and titles, `deep_pink4` for user input prompts, `cyan` for game metadata, `bold red` for blocked cells (`!`), and high-contrast player tokens (`bold navy_blue` / `bold medium_purple1` for `X` and `bold bright_yellow` for `O`)—players can distinguish playable slots (`dim cyan #`) from obstacles and opponent pieces at a glance.
-   The terminal width varies across environments, so using `Align.center` and `Panel(..., expand=True)` allows for the dynamic board sizes to remain horizontally centered and cleanly framed without the need for manual string padding. By using `Group`, it allows for the stacking of metadata headers (the board dimensions and last move tracking) and the rendered NumPy grid inside a single unified container.
-   Initialising `Console(force_terminal=True)` guarantees consistent TrueColor/256-colour rendering and box-drawing characters across Windows PowerShell, macOS, Linux, and IDE integrated terminals, while also enabling headless output capture `(console.record = True)` during automated testing.

#### `cli/main.py`

-   `intro_text() -> None`
    
    -   Prints the centered welcome banner inside a pink-bordered `Rich` `Panel`.
-   `get_game_mode() -> int | None`
    
    -   Prompts the user to select a game mode (`1` for player vs player, `2` for player vs computer) and returns the selected mode. If the user enters an invalid input, the function will prompt the user again until a valid input is provided.
-   `get_ai_difficulty() -> str`
    
    -   Prompts the user to select an AI difficulty level (`1` for easy, `2` for medium) and returns the selected difficulty. If the user enters an invalid input, the function will prompt the user again until a valid input is provided.
-   `get_board_dimensions() -> tuple[int, int]`
    
    -   Prompts the user to enter the dimensions of the game board (rows must be a minimum of 6, and columns must be a minimum of 7) and returns a tuple containing the number of rows and columns. If the user enters invalid input, the function will prompt the user again until valid input is provided.
-   `display_board(board: np.ndarray, last_move: str | None = None, winning_cells: list[tuple[int, int]] | None = None) -> None`
    
    -   Clears the terminal screen (`cls` on Windows and `clear` on macOS/Linux), formats each board cell with its own `Rich` colour tag (`bold bright_green` for coordinates in `winning_cells`, `bold navy_blue` for `X`, `bold bright_yellow` for `O`, `bold red` for `!`, and `dim cyan` for `#`), adds a bottom divider and 1-based column numbers, and prints the board inside a `Rich` `Panel`.
    -   Converts `winning_cells` into a set (`winning_set`) before iterating over the grid so membership checks `(row, col) in winning_set` are $O(1)$.
-   `run_game_loop(board: np.ndarray, player1: Player | AIAgent, player2: Player | AIAgent) -> None`
    
    -   Alternates turns between `player1` and `player2`, tracks the `total_moves` and 1-based `move_history`, checks for a win after `total_moves >= 7`, highlights the winning four cells in green via `get_winning_cells()`, checks for a draw once `total_moves >= max_possible_moves`, and exports the completed match data via `export_match_data(interface="CLI", ...)`.
    -   The `max_possible_moves` is calculated with `(rows * cols) - int(np.count_nonzero(board == "!"))`, since blocked cells can never be filled by players; without subtracting them, a full board would never trigger the draw check.
-   `main() -> None`
    
    -   Initialises `setup_log()`, runs the setup prompts, instantiates `Player` / `AIAgent` objects, and starts `run_game_loop()`.

### Core

#### `core/game_logic.py`

This module contains the mathematical and grid manipulation engine for the game. This module is completely independent of any UI.

-   `create_board(rows: int, cols: int) -> np.ndarray`
    
    -   Allocates a 2D NumPy array of shape (`rows`, `cols`) filled with `"#"`, applies random obstacle cells `"!"` via `random_cell_blocking()`, logs the board size and blocker count, and returns the board.
-   `random_cell_blocking(board: np.ndarray, block_char: str = "!") -> np.ndarray`
    
    -   Picks a random percentage between `1%` and `10%` of the total cells (`max(1, int(total_cells * block_percent))`), selects the unique flat indices using `np.random.choice(..., replace=False)`, converts each 1D index into 2D coordinates using (`i // cols`, `i % cols`), and places the `block_char` (`"!"`).
    -   Using `replace=False` was imperative as without it, duplicate random indices would overwrite the same cell and would occasionally result in fewer blocked cells than was intended. The use of `max(1, ...)` guarantees that at least one blocked cell will be present—this matters as on the smallest board (`6x7`), the blocked cell percentage could result in `0.42`, which rounds down to `0`, resulting in no blocked cells being present.
-   `check_win_loop(board: np.ndarray, piece: str) -> bool`
    
    -   This was the baseline win detection check which was implemented; it used 4 pairs of nested `for` loops to scan horizontal, vertical, back diagonal, and forward diagonal lines of four consecutive `piece` tokens.
-   `check_win(board: np.ndarray, piece: str) -> bool`
    
    -   This is the optimised win check using NumPy vectorised boolean array slicing and bitwise `&` across four shifted 2D views which are evaluated with `np.any()`.
-   `get_winning_cells(board: np.ndarray, piece: str) -> list[tuple[int, int]]`
    
    -   Scans the board in all 4 directions and returns a list of the four `(row, col)` coordinate tuples which form the winning line—or `[]` if no win exists. Used by both the CLI and GUI for highlighting the winning pieces in green.
-   `drop_piece(board: np.ndarray, piece: str, col_index: int) -> bool`
    
    -   Simulates dropping a piece into the board at the specified column index, returning `True` if the move was successful and `False` if the column was full.
    -   Works by iterating backwards from the bottom row (`rows - 1` down to `0`) and placing the `piece` into the first empty cell (`"#"`) it encounters. It was done this way as blocked cells can appear at any height, and pieces are not just placed on top of the blocked cell—they go through if any playable cells exist underneath. Scanning from `rows - 1` upwards ensures pieces fill empty slots from the bottom up, whilst skipping over blocked cells without overwriting them.

#### `core/player.py`

This module represents a human player within the CLI version of the game.

-   `__init__(self, name: str, game_piece: str | None = None) -> None`
    
    -   Initialises a new player instance with the specified name and game piece.
-   `get_name(self) -> str`
    
    -   Returns the name of the player.
-   `play(self, board: np.ndarray) -> int`
    
    -   Prompts the player to select a column to drop their piece into. The player enters their column index as a 1-based value and the function converts it to 0-based, checks bounds, calls `drop_piece()`, and loops until a valid column is entered. It returns the 0-based column index the player played.
    -   This class performs blocking `input()` calls and prints using the `Rich` library; for this reason it is only used by the CLI version of the game.

#### `core/ai_agent.py`

This module implements the computer opponent, and supports both `easy` (random selection) and `medium` (Monte Carlo Tree Search with UCB1) difficulty levels. The `medium` difficulty algorithm is discussed in more detail further down in the document.

**Standalone Function**

-   `get_valid_locations(board: np.ndarray) -> list[int]`
    -   Returns a list of 0-based column indices which contain at least one empty cell using `"#" in board[:, col]`.
    -   Since we cannot just check the top cell due to the blocked cell mechanic (`board[0, col] == "#"`), if the top cell is a blocked cell and there are empty cells below it, the column would falsely be considered invalid. Slicing the entire column `board[:, col]` avoids this bug happening.

**Class `MCTSNode`** This class represents a node in the Monte Carlo Tree Search (MCTS) tree used by the AI agent to make decisions.

-   `__init__(self, board: np.ndarray, parent: Optional[MCTSNode], column: Optional[int], game_piece: str = "O") -> None`
    
    -   Stores the node's board snapshot, parent pointer, the column move which created this node, the `game_piece` that was dropped to reach this state, `visits = 0`, `wins = 0.0`, `untried_moves = get_valid_locations(self.board)`, and `children = []`.
    -   Makes use of `random.shuffle(self.untried_moves)` immediately after initialising `untried_moves` to ensure that the order of untried moves is randomised. This is due to the `expand()` function using `.pop()` which removes from the end of the list, which would otherwise always result in expanding columns from right to left, introducing right-side positional bias if iterations are low.
-   `is_terminal(self, human_piece: str) -> bool`
    
    -   Checks if the node's board state is game-over—either `self.game_piece` won, the opponent's piece won, or `get_valid_locations(self.board)` is empty.
-   `is_fully_expanded(self) -> bool`
    
    -   Returns `True` once `len(self.untried_moves) == 0`—this is when every legal column from this state has been expanded into a child node.
-   `expand(self, next_game_piece: str) -> MCTSNode`
    
    -   Pops one column from `self.untried_moves`, clones `self.board`, drops `next_game_piece` into that column, wraps the resulting board in a new child `MCTSNode`, appends it to `self.children`, and returns the child.
    -   Makes use of NumPy's `copy()` method to clone the board instead of `copy.deepcopy()` to keep the node expansion process fast and avoid mutating the parent node's board.
-   `best_child(self, c: float = 1.414) -> MCTSNode`
    
    -   Applies the UCB1 formula ($frac{w_i}{n_i} + c sqrt{frac{ln N}{n_i}}$) to select the child node that best balances exploitation and exploration.
    -   Avoids `ZeroDivisionError` by checking `if child.visits == 0: return child` before calculating `child.wins / child.visits`.

**Class `AIAgent`**

-   `__init__(self, name: str, game_piece: str, human_piece: str = "X", difficulty: str = "medium", iterations: int = 1500) -> None`
    
    -   Configures the AI's display name, its game piece (`"O"`), the human player's game piece (`"X"`), the AI's difficulty level (`"easy"` or `"medium"`), and the number of iterations for the Monte Carlo Tree Search algorithm (`default = 1500`).
-   `get_difficulty(self) -> str`
    
    -   Returns `self.difficulty`.
-   `play(self, board: np.ndarray) -> int | None`
    
    -   Used by the CLI game loop. Prints `thinking...` to indicate the AI is thinking about its turn, sleeps for 2 seconds to simulate thinking time and allow the human player to read the board update, picks a column via `random.choice` (for `easy` difficulty) or `self.mcts_search(board)` (for `medium` difficulty), drops the piece on the board, and returns the 0-based column index.
    -   Since this uses `time.sleep()` and prints to the console, the GUI version does not call this. Instead, the GUI uses `QTimer.singleShot(300, self.play_ai_turn)` and calls `ai_agent.mcts_search(board)` directly so the Qt event loop isn't blocked by `time.sleep()`.
-   `mcts_search(self, board: np.ndarray) -> int`
    
    -   Executes `self.iterations` cycles of the Monte Carlo Tree Search (MCTS) algorithm (`Selection` -> `Expansion` -> `Simulation` -> `Backpropagation`) starting from the root node, then returns the column of the root child with the highest `visits` count (this is the most robust child).
-   `simulate_random_rollout(self, node: MCTSNode) -> str | None`
    
    -   Plays a fast simulated game on `node.board.copy()` by randomly selecting valid columns for alternating players until a win—returns the winning game piece `"O"` or `"X"`, or `None` if the game is a draw.
-   `backpropagate(self, node: MCTSNode | None, winner: str | None) -> None`
    
    -   Walks up the parent pointers from the expanded leaf node to `root`, increments `node.visits += 1`, and adds `+0.5` to `node.wins` on a draw or `+1.0` to `node.wins` when `winner == node.game_piece`.
    -   Since it is a two-player alternating tree, each level belongs to a different player, so awarding `+1.0` only when `winner == node.game_piece` ensures that when `parent.best_child()` is called at the human turn node, it chooses a move that maximises the human's win rate, preventing the AI from assuming the human will cooperate with its game move.

#### `core/data_export.py`

This module persists completed match statistics and move histories to `data/match_history.csv` and loads recent matches for display in the GUI.

-   `export_match_data(interface: str, mode: int, difficulty: str, board: np.ndarray, winner: str, total_moves: int, move_history: list[int], file_path: str = "data/match_history.csv") -> Path`
    
    -   Appends a single completed match record to `data/match_history.csv` using `csv.DictWriter`. Automatically creates the `data/` directory and writes the CSV header row `COL_NAMES` if the file does not exist yet.
    -   Resolves relative `file_path` strings against `Path(__file__).resolve().parent.parent` so the CSV file is always written to the top-level `data/` folder regardless of the current working directory.
    -   Formats `move_history` using `"->".join(...)` instead of `",".join(...)` to make the move history more readable in the CSV file.
-   `load_recent_matches(limit: int = 10, file_path: str = "data/match_history.csv") -> list[dict[str, str]]`
    
    -   Reads `data/match_history.csv` using `csv.DictReader` and returns a list of the most recent `limit` matches ordered from newest to oldest using `list(reversed(rows[-limit:]))`. If the file does not yet exist, it returns an empty list.

#### `core/logger.py`

This module is the centralised file logging configuration for both the CLI and GUI versions of the game.

-   `setup_logging(log_file: str = "logs/game.log", level: int = logging.INFO) -> None` (has an alias of `setup_log`)
    -   Configures Python's root logger to write timestamped log entries `%(asctime)s [%(levelname)s] [%(name)s]: %(message)s` to `log_file`.
    -   Logs exclusively to a `FileHandler` so log messages never break the `Rich` terminal UI panels in the CLI version of the game.
    -   Checks `root_logger.handlers` for an existing `FileHandler` with the same `baseFilename` before attaching a new one to avoid duplicate log entries if `setup_log()` is invoked multiple times.

### GUI

For the GUI version of the game, I decided to use the `PyQt6` library over alternatives like `pygame` and `tkinter`. There were a few key reasons behind this:

-   Having prior experience with **Java Swing** and `PyQt6`, an object-oriented, widget-based toolkit was far more intuitive than `pygame`'s frame-by-frame rendering loop. Much like attaching an `ActionListener` to a `JButton` in Swing, `PyQt6` uses a native **Signal and Slot** mechanism (`pyqtSignal` and `.clicked.connect(...)`). Instead of constantly polling mouse $(x, y)$ coordinates to calculate which column was clicked, each cell in `GameScreen` is a discrete widget that emits an event only when interacted with, routing directly to `GameController` to trigger `drop_piece()` or an MCTS turn.
    
-   Similar to Swing's `CardLayout`, `PyQt6` provides `QStackedWidget` inside `QMainWindow` (`gui/main_window.py`). This allowed the application to manage clean, single-window view transitions (`TitleScreen` $rightarrow$ `GameModeSelectScreen` $rightarrow$ `SetupScreen` $rightarrow$ `GameScreen`) without spawning separate OS windows or manually clearing and redrawing a canvas between menus.
    
-   Unlike `tkinter`, which I think looks dated, `PyQt6` provides responsive widgets (`QPushButton`, `QSpinBox`, `QCheckBox`, `QGroupBox`, `QListWidget`, and `QGridLayout`) out of the box. In `GameScreen`, `QGridLayout` automatically manages geometry and stretch factors to construct variable-sized Connect 4 boards alongside the colour legend and live CSV match history panel without manual pixel arithmetic.
    
-   A standout advantage of `PyQt6` over `tkinter` and `pygame` is its support for external Qt Style Sheets (`gui/assets/styles.qss`), which mirror web CSS syntax. This decoupled all visual styling—hover effects, borders, and bundled custom fonts (`gui/assets/fonts/`)—from the Python view classes. By binding a dynamic Qt property (`cell_state`) to board cells (updating a button's state to `"empty_x"`, `"empty_o"`, `"empty_disabled"`, `"x"`, `"o"`, `"blocked"`, or `"win"` and re-polishing the widget), the grid dynamically updates its colours—including active-player hover previews and highlighting the winning 4-in-a-row line in bright green—purely through stylesheet selectors.
    

#### `gui/main_window.py`

The top-level window manager containing a `QStackedWidget` for navigating between all four GUI screens within a single window.

-   `__init__(self) -> None`
    
    -   Constrains the maximum window size to `QApplication.primaryScreen().geometry().size()`, opens in fullscreen, loads custom fonts and the stylesheet (`gui/assets/styles.qss`), creates `TitleScreen`, `GameModeSelectScreen`, `SetupScreen`, `GameScreen`, and `GameController`, registers the views in `self.stack`, and connects navigation signals.
-   `load_custom_fonts(self) -> None`
    
    -   Recursively loads all `.ttf` font files (`VT323`, `Geist Pixel`) from `gui/assets/fonts/` into `QFontDatabase` so they can be referenced by name in `styles.qss` on any machine without system-wide installation.
-   `load_stylesheet(self) -> None`
    
    -   Reads `gui/assets/styles.qss` and applies it to `MainWindow` via `self.setStyleSheet(...)`.
-   `connect_signals(self) -> None`
    
    -   Wires `pyqtSignal` events from all four screen views to the navigation slot methods on `MainWindow`.
-   **Navigation Slots (`on_play_clicked`, `on_exit_clicked`, `on_mode_back_clicked`, `on_setup_back_clicked`, `on_game_back_clicked`, `on_mode_selected`, `on_start_game`):**
    
    -   `on_play_clicked(self) -> None`
        
        -   Logs the transition and switches the active widget in `self.stack` from `TitleScreen` to `GameModeSelectScreen`.
    -   `on_exit_clicked(self, source_screen: str = "TitleScreen") -> None`
        
        -   Logs which screen emitted the exit request (`TitleScreen` or `GameScreen`) and cleanly closes the main application window via `self.close()`.
    -   `on_mode_back_clicked(self) -> None`
        
        -   Logs the transition and navigates back from `GameModeSelectScreen` to `TitleScreen`.
    -   `on_setup_back_clicked(self) -> None`
        
        -   Logs the transition and navigates back from `SetupScreen` to `GameModeSelectScreen`.
    -   `on_game_back_clicked(self) -> None`
        
        -   Logs that the user left the active match and navigates back from `GameScreen` to `SetupScreen`.
    -   `on_mode_selected(self, mode: int) -> None`
        
        -   Stores the chosen game mode (`1` for Player vs Player, `2` for Player vs Computer), calls `self.setup_screen.config_mode(mode)` to enable or disable the AI difficulty checkboxes accordingly, and switches `self.stack` to `SetupScreen`.
    -   `on_start_game(self, rows: int, cols: int, difficulty: str) -> None`
        
        -   Logs the match configuration, delegates board creation and match initialisation to `self.game_controller.start_game(mode=self.selected_mode, rows=rows, cols=cols, difficulty=difficulty)`, and switches `self.stack` to `GameScreen`.

#### `gui/controllers/game_controller.py`

This module is the MVC controller which bridges the `GameScreen` with `core/game_logic.py`, `core/ai_agent.py`, and `core/data_export.py`.

**Class `GameController`**

-   `__init__(self, game_screen: GameScreen) -> None`
    
    -   Stores match state (`board`, `mode`, `difficulty`, `current_piece`, `total_moves`, `max_moves`, `game_over`, `ai_agent`, `move_history`) and connects `game_screen.cell_clicked` to `self.on_clicked_cell`.
-   `start_game(self, mode: int, rows: int, cols: int, difficulty: str) -> None`
    
    -   Generates a new board via `create_board(rows, cols)`, calculates `self.max_moves = (rows * cols) - blocked_cells`, creates `AIAgent` if `mode == 2`, builds the button grid on `GameScreen`, loads the recent match history sidebar (`refresh_match_history`), and sets the opening status message.
-   `current_player(self) -> str`
    
    -   Returns the human-readable display name for whoever's turn it is (`"Player 1"` / `"Player 2"` in PvP, or `"Player"` / `"Computer (easy|medium)"` in PvC).
-   `on_clicked_cell(self, row: int, col: int) -> None`
    
    -   Handles human clicks on any cell button in column `col`. Ignores clicks if `self.game_over` is `True` or if it is currently the computer's turn (`self.mode == 2 and self.current_piece == "O"`). Calls `drop_piece(self.board, self.current_piece, col)`; if the column is full, displays a warning in the status bar, otherwise calls `self.advance_turn(col)`.
    -   Even though the user clicks a specific `(row, col)` button, `drop_piece` always drops the piece into `col` with gravity. The input guard `if self.mode == 2 and self.current_piece == "O": return` is essential to prevent the human from dropping pieces on behalf of the AI during the `QTimer` delay.
-   `advance_turn(self, last_col: int) -> None`
    
    -   Increments `self.total_moves`, appends `last_col + 1` to `self.move_history`, checks for a win (when `total_moves >= 7`) or draw (`total_moves >= max_moves`), highlights winning cells, exports match data to CSV and refreshes the sidebar on game over, or switches `self.current_piece` (`"X" <-> "O"`) and schedules `self.play_ai_turn` via `QTimer.singleShot(300, self.play_ai_turn)` when it is the AI's turn.
    -   When transitioning to the AI's turn (or when the game ends), `update_board(self.board, None)` is called with `active_piece=None` so empty cells switch to the `empty_disabled` QSS state and don't show a human hover preview while the AI is "thinking".
-   `play_ai_turn(self) -> None`
    
    -   Executed asynchronously by `QTimer.singleShot`. Picks a column using `random.choice` (`easy`) or `self.ai_agent.mcts_search(self.board)` (`medium`), calls `drop_piece`, and calls `self.advance_turn(col)`.
-   `refresh_match_history(self) -> None`
    
    -   Calls `load_recent_matches(limit=10)` and passes the records to `self.game_screen.update_match_history(recent_matches)`.

### Views

#### `gui/views/title_screen.py`

The initial landing view (`TitleScreen(QWidget)`) displaying the `"CONNECT 4"` title, subtitle, and `"Play"` / `"Exit"` buttons.

-   Signals: `play_btn_clicked = pyqtSignal()`, `exit_btn_clicked = pyqtSignal()`.
    
-   Methods: `__init__`, `initUI` (builds centered `QVBoxLayout` and forwards button clicks to custom signals).
    

---

#### `gui/views/gamemode_select_screen.py`

Mode selection view (`GameModeSelectScreen(QWidget)`) allowing the player to choose `"Player vs Player"`, `"Player vs Computer"`, or `"Back"`.

-   Signals: `mode_selected = pyqtSignal(int)` (emits `1` for PvP, `2` for PvC), `back_btn_clicked = pyqtSignal()`.
    
-   Methods: `__init__`, `initUI`.
    

---

#### `gui/views/game_setup_screen.py`

Match configuration view (`SetupScreen(QWidget)`) for selecting board dimensions and AI difficulty.

-   Signals: `start_game_clicked = pyqtSignal(int, int, str)` (emits `(rows, cols, difficulty)`), `back_btn_clicked = pyqtSignal()`.
    
-   Methods:
    
    -   `initUI(self) -> None`: Creates `QSpinBox` controls for rows (`setRange(6, 20)`) and columns (`setRange(7, 20)`), an `"AI Difficulty"` `QGroupBox` containing `"Easy (Random Moves)"` and `"Medium (MCTS Engine)"` checkboxes inside an exclusive `QButtonGroup`, and `"Back"` / `"Start"` buttons.
        
    -   `config_mode(self, mode: int) -> None`: Enables `self.ai_group` only when `mode == 2` (PvC) and greys it out when `mode == 1` (PvP).
        
    -   `start_game(self) -> None`: Reads `rows_spin.value()`, `cols_spin.value()`, and the checked difficulty checkbox, and emits `start_game_clicked`.
        

---

#### `gui/views/game_screen.py`

The main interactive gameplay view (`GameScreen(QWidget)`) containing the top status bar, the dynamic `QGridLayout` of board cell buttons, and the right-hand sidebar (`Key` legend, `Recent Match History` list, and `Back` / `Exit` buttons).

-   Signals: `cell_clicked = pyqtSignal(int, int)`, `back_btn_clicked = pyqtSignal()`, `exit_btn_clicked = pyqtSignal()`.
-   Methods:
    -   `__init__(self, parent: QWidget | None = None) -> None`: Builds the root layout, top `#status_lbl`, expanding `self.grid_layout`, and the right-hand `self.key_layout` which holds `QGroupBox("Key")`, `QGroupBox("Recent Match History")` (`self.history_list`), and the `Back` / `Exit` buttons.
        
    -   `setup_board(self, board: np.ndarray, active_piece: str | None = "X") -> None`: Clears and schedules deletion — using `deleteLater()` — of any widgets from a previous match, sets equal row/column stretch factors using `setRowStretch(r, 1)` and `setColumnStretch(c, 1)`, creates a `QPushButton` (`#board_cell`) for every `(r, c)` coordinate, styles it using `style_cell_button()`, and connects its `clicked` signal to emit `(r, c)`.
        
        -   Each button uses `QSizePolicy.Policy.Ignored` and `setMinimumSize(0, 0)` so that even a $20 times 20$ grid of 400 buttons shrinks smoothly to fit inside the window without forcing the layout wider than the monitor.
    -   `update_board(self, board: np.ndarray, active_piece: str | None = "X") -> None`: Iterates over the existing grid buttons in place and updates their QSS states via `style_cell_button()` without destroying/recreating widgets on every turn.
        
    -   `style_cell_button(self, cell_btn: QPushButton, char: str, active_piece: str | None = "X") -> None`: Maps the board characters (`"#"`, `"!"`, `"X"`, `"O"`) and `active_piece` to a QSS `cell_state` string (`"empty_x"`, `"empty_o"`, `"empty_disabled"`, `"blocked"`, `"x"`, `"o"`) and calls `apply_cell_state()`.
        
    -   `highlight_winning_cells(self, winning_cells: list[tuple[int, int]]) -> None`: Sets the 4 winning `(row, col)` buttons to `cell_state="win"` (bright green).
        
    -   `apply_cell_state(self, cell_btn: QPushButton, state: str) -> None`: Updates the dynamic property `cell_btn.setProperty("cell_state", state)` and calls `style.unpolish(cell_btn)` + `style.polish(cell_btn)` when the state changes.
        
        -   Since PyQt does not automatically re-evaluate QSS property selectors (`QPushButton#board_cell[cell_state="..."]`) when `setProperty()` is called at runtime unless `unpolish()` and `polish()` are called on the widget's `QStyle`, checking `if cell_btn.property("cell_state") != state:` first avoids redundant repolishing on unchanged cells.
    -   `set_status(self, message: str) -> None`: Updates `self.status_lbl` text and turns the text green when `"wins!"` appears in the message.
        
    -   `create_legend_row(self, colour: str, lbl_txt: str) -> QHBoxLayout`: Helper that builds a `QFrame` colour swatch (`#legend_swatch`) using a dynamic property `swatch_colour` alongside the text detailing what that swatch correlates to.
        
    -   `update_match_history(self, matches: list[dict[str, str]]) -> None`: Clears `self.history_list` and populates it with formatted multi-line summaries of the recent matches from `data/match_history.csv`.
        

### Tests

Testing is done via automated property-based testing using `unittest` and `hypothesis` to verify invariants across randomised board dimensions, piece tokens, move sequences, and MCTS tree structures. More information about the reason Hypothesis was used can be found further down in the document.

#### `tests/game_properties_test.py`

-   Test Classes:
    -   `BoardPropertiesTest`: Tests `test_board_dimensions`, `test_board_valid_chars`, and `test_blocked_cell_count`.
        
    -   `ValidLocationsPropertyTest`: Tests `test_valid_locations_match_cols_with_empty_slots` and `test_full_col_excluded_from_valid_locations`.
        
    -   `GamePieceDroppingTest`: Tests `test_drop_piece_preserves_blocked_cells`, `test_piece_drops_lowest_available_row`, and `test_full_col_drop`.
        
    -   `WinConditionsTest`: Tests `test_empty_board`, `test_horizontal_win_check`, `test_vertical_win_check`, `test_diagonal_win_check`, `test_get_winning_cells_returns_four_matching_coordinates`, and `test_vectorized_check_win_matches_loop_baseline`.
        
    -   `MCTSPropertiesTest`: Tests `test_node_expand_creates_valid_child_without_altering_parent` and `test_best_child_selects_higher_win_rate_given_equal_visits`.
        
    -   `MCTSBackpropagationPropertiesTest`: Tests `test_backpropagate_updates_all_ancestors_correctly`.
        
    -   `AIMCTSPropertiesTest`: Tests `test_mcts_returns_valid_col_and_doesnt_mutate_board` and `test_mcts_finds_immediate_horizontal_winning_move`.
        
    -   This test uses `@settings(max_examples=25, deadline=None)` (and `max_examples=20`) since running full MCTS searches across 100 boards would exceed Hypothesis's default 200ms per-example deadline.
        

### Benchmarking

#### `benchmarks/benchmark_check_win.py`

This benchmarks the execution time and peak memory allocation between the baseline nested-loop `check_win_loop` and the optimised NumPy vectorised `check_win` across three board sizes: `standard` ($6 times 7$), `medium` ($10 times 11$), and `large` ($20 times 20$).

-   Functions:
    
    -   `generate_a_midgame_board(rows: int, cols: int, num_moves: int, seed: int = 28) -> np.ndarray`: Seeds both `random` and `np.random` with the given `seed`, creates a board of `rows, cols`, and drops `num_moves` alternating game pieces so both win check functions are benchmarked on identical, realistic mid-game boards rather than empty arrays.
        
    -   `benchmark_function(func: Callable[[np.ndarray, str], bool], board: np.ndarray, iterations: int = 20_000) -> tuple[float, int]`: Runs one warm-up call, starts `tracemalloc` and `time.perf_counter()`, executes `func(board, "X")` and `func(board, "O")` inside a loop of `iterations`, and returns `(elapsed_ms, peak_memory_bytes)`.
        
    -   `run_benchmark() -> None`: Iterates over the `standard` ($6 times 7$), `medium` ($10 times 11$), and `large` ($20 times 20$) board configurations, executes `benchmark_function()` for both `check_win_loop` and `check_win`, computes the speedup ratio (`round(loop_ms / vec_ms, 2)`), and prints the comparison summary to the console.
        

## AI Agent

The AI agent implemented contains two difficulty levels: `easy` and `medium`. `easy` difficulty uses the simple method of selecting a random column using `random.choice(get_valid_locations(board))`. `medium` uses Monte Carlo Tree Search (MCTS) which is guided by the Upper Confidence Bound 1 (UCB1) formula across `1,500` simulated iterations per turn. This section will cover the implementation details of the MCTS algorithm along with justification for the choice of UCB1, and the reasoning behind why this algorithm was chosen compared to other alternatives.

The references used when implementing the Monte Carlo Tree Search are as follows:

1.  Olin College Connect 4 MCTS Study (Asymmetric tree growth, Connect 4 state-space complexity): [https://mcts.netlify.app/](https://mcts.netlify.app/)
2.  AI-Boson MCTS Python Tutorial (Object-oriented Node design, lazy expansion via `untried_moves`, `tree_policy`): [https://ai-boson.github.io/mcts/](https://ai-boson.github.io/mcts/)
3.  GeeksforGeeks MCTS in Machine Learning (Four-phase loop, UCB1 equation, zero-sum perspective backpropagation): [https://www.geeksforgeeks.org/machine-learning/monte-carlo-tree-search-mcts-in-machine-learning/](https://www.geeksforgeeks.org/machine-learning/monte-carlo-tree-search-mcts-in-machine-learning/)
4.  Multi-Armed Bandit UCB1 Analysis ("Optimism in the face of uncertainty", confidence-bound convergence): [https://github.com/kfoofw/bandit_simulations/blob/master/python/multiarmed_bandits/analysis/ucb.md](https://github.com/kfoofw/bandit_simulations/blob/master/python/multiarmed_bandits/analysis/ucb.md)
5.  [https://en.wikipedia.org/wiki/Monte_Carlo_tree_search](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search)

### Monte Carlo Tree Search (MCTS)

Monte Carlo Tree Search (MCTS) is a heuristic search algorithm used for decision-making in turn-based games with large state spaces, where evaluating every possible future board configuration is computationally infeasible. Instead of relying on a hand-crafted board evaluation function like traditional Minimax, MCTS estimates the value of each legal move by iteratively building an asymmetric search tree and running hundreds of fast, randomised simulated games from the current state to a terminal win, loss, or draw. Across four repeating phases (Selection, Expansion, Simulation, Backpropagation) the algorithm uses the Upper Confidence Bound 1 (UCB1) formula to balance exploitation (focusing simulations on columns with high historical win rates) and exploration (testing under-visited columns so potential threats or winning lines aren't missed). Once the simulation budget is exhausted, the AI selects the root move with the highest visit count as its final action.

#### Why MCTS was used over other algorithms

Initially I was going to go with minimax (with alpha-beta pruning), but after doing some research, I came to the conclusion that another algorithm would be better suited for this game. Minimax (with Alpha-beta pruning) relies on a hand-crafted heuristic evaluation function to score non-terminal board states at a fixed depth cutoff. As this game has the mechanism of dynamic board dimensions and randomly placed obstacle cells scattered across up to 10% of the board grid, the static positional weight tables used in minimax break down whenever an obstacle blocks a line or the board geometry changes. Furthermore, with the board geometry being dynamic, larger boards cause the branching factor to grow exponentially, leading to Minimax's exponential time complexity $O (b^d)$ becoming too slow for real-time play. Whereas MCTS is domain-agnostic and evaluates board states dynamically through full simulated rollouts, naturally adapting to arbitrary grid dimensions and blocked cells without needing hardcoded positional heuristics.

#### How the MCTS algorithm works

My explanation of MCTS is going to assume a standard board size of $6 times 7$, and 1500 iterations of the 4-stage loop which starts from the current board state (`root`)

##### UCB1 Formula

During tree traversal, child nodes are scored using the Upper Confidence Bound 1 (UCB1) equation to balance exploitation (picking moves with high empirical win rates) and exploration (testing moves that have rarely been visited): $$UCB1(i) = bar{X}_i + c sqrt{frac{ln N}{n_i}}$$

-   $bar{X}_i$ = average reward of child node $i$ (`child.wins / child.visits`)
-   $c$ = exploration parameter ($sqrt{2} approx 1.414$)
-   $N$ = total number of visits to the parent node (`self.visits`)
-   $n_i$ = number of visits to child node $i$ (`child.visits`)

##### Stage 1: Selection (Exploration)

Starting at the `root` node, the AI checks all playable columns. If a node is already fully expanded (`len(untried_moves) == 0`) and non-terminal, it uses `best_child(c=1.414)` to select the child with the highest UCB1 score. Any unvisited column has $n_i = 0$ visits (which scores $infty$ in UCB1), guaranteeing that MCTS tries every untried column at least once before doubling down on promising branches.

##### Stage 2: Expansion

Once selection reaches a non-terminal node that still has `untried_moves`, the AI pops one untried column (`col = self.untried_moves.pop()`), clones the board via `self.board.copy()`, imagines dropping a game piece into that column, and attaches this hypothetical board state as a new child `MCTSNode` in its search tree.

##### Stage 3: Simulation (Rollout)

From the newly expanded child node, the AI simulates a full practice game (`simulate_random_rollout`) by randomly dropping alternating pieces for both players (`"X"` and `"O"`) into valid columns until either player achieves 4-in-a-row or the board fills up in a draw.

##### Stage 4: Backpropagation

After the simulated rollout ends, the AI walks backwards from the expanded leaf node up to the `root` (`while node is not None:`), incrementing the visit count (`node.visits += 1`) and updating the win score for every ancestor along the path:

-   `+1.0` if the rollout winner matches the player who moved to create that node (`winner == node.game_piece`)
-   `+0.5` if the rollout ended in a draw (`winner is None`)
-   `+0.0` if the opponent won

##### Final Decision – Picking the Most Robust Child

Once all `1,500` simulated games are complete, the AI ignores the UCB1 formula, inspects the immediate children of the `root` node, and selects the column with the highest visit count:

```python
robust_child = max(root.children, key=lambda child: child.visits)
return robust_child.column
```

This column is chosen because it has survived the greatest number of simulated stress tests.

## Hypothesis Testing

Unlike standard example-based unit tests where you manually hardcode 1 or 2 board sizes (such as a single $6 times 7$ grid) and assert a single output, Property-Based Testing uses the `hypothesis` library on top of Python's `unittest.TestCase` framework to automatically generate 100+ randomised inputs per test method.

Since this game features dynamic board dimensions, randomly placed blocked cells and a stochastic MCTS, hardcoding board states could have led to missed edge cases (blocked cell at row 0, or an asymmetric board aspect ratio). So instead of testing isolated examples, Hypothesis was used to test invariants (properties). Invariants are rules that must hold true across all valid board dimensions, piece tokens, move sequences, and MCTS tree states.

References used when implementing Hypothesis strategies:

-   Hypothesis Built-in Strategies Documentation: [https://hypothesis.readthedocs.io/en/latest/tutorial/builtin-strategies.html](https://hypothesis.readthedocs.io/en/latest/tutorial/builtin-strategies.html)
-   [https://semaphore.io/blog/property-based-testing-python-hypothesis-pytest](https://semaphore.io/blog/property-based-testing-python-hypothesis-pytest)

### Core Hypothesis Features Used in the Test Suite

-   `@given(...)` Decorator: Wraps each `unittest.TestCase` method and automatically feeds it randomised test parameters across 100+ runs.
    
-   Built-in Strategies (`strategies as st`):
    
    -   `st.integers(min_value=..., max_value=...)`: Generates variable board dimensions (e.g., `6..20` rows and `7..20` columns), MCTS tree depths (`1..6`), visit counts (`25..100`), and starting column offsets (`0..3`).
    -   `st.sampled_from(["X", "O"])` and `st.sampled_from(["X", "O", None])`: Randomly tests invariants for both player tokens as well as draw outcomes (`None`).
    -   `st.floats(min_value=..., max_value=..., allow_nan=False, allow_infinity=False)`: Generates realistic floating-point win scores (`wins_a` vs `wins_b`) to verify UCB1 tie-breaking when visit counts are equal.
    -   `st.lists(st.integers(min_value=0, max_value=14), min_size=0, max_size=30)`: Generates random sequences of column drops to simulate realistic mid-game boards.
-   `@settings(max_examples=..., deadline=None)`: Applied to full `AIMCTSPropertiesTest` methods (`max_examples=25` and `max_examples=20`) so that running 50 to 200 MCTS simulation rollouts per generated board does not trigger Hypothesis's default 200ms per-example timeout.
    
-   Automatic Shrinking: If any property fails on a large board (e.g., $18 times 19$), Hypothesis automatically shrinks the failing input down to the smallest possible `(rows, cols)` dimensions and move sequence that still reproduce the bug.
    

---

### Invariants Verified Across the 7 Test Classes

1.  `BoardPropertiesTest` (Board Generation & Obstacles)
    
    -   `test_board_dimensions`: `create_board(rows, cols)` always produces a 2D NumPy array matching the exact `(rows, cols)` shape (`6..20` $times$ `7..20`).
    -   `test_board_valid_chars`: A newly created board only ever contains empty slots (`"#"`) and blocked cells (`"!"`).
    -   `test_blocked_cell_count`: Every generated board contains at least `1` blocked cell (`"!"`), and never exceeds `10%` of the total board area (`int(rows * cols * 0.10)`).
2.  `ValidLocationsPropertyTest` (Column Discovery)
    
    -   `test_valid_locations_match_cols_with_empty_slots`: `get_valid_locations(board)` returns the exact set of column indices that contain at least one `"#"` character.
    -   `test_full_col_excluded_from_valid_locations`: Any column completely filled with pieces (`board[:, 0] = piece`) is strictly excluded from `get_valid_locations(board)`, reducing the valid column count to `cols - 1`.
3.  `GamePieceDroppingTest` (Gravity & Obstacle Preservation)
    
    -   `test_drop_piece_preserves_blocked_cells`: Dropping pieces across all columns never overwrites or alters the `(row, col)` coordinates of any `"!"` blocker cells.
    -   `test_piece_drops_lowest_available_row`: Dropping a piece into a valid column always places it at `max(empty_rows)` (the bottom-most available `"#"` slot) and returns `True`.
    -   `test_full_col_drop`: Attempting to drop a piece into a full column returns `False` and leaves the board array completely unchanged (`np.testing.assert_array_equal`).
4.  `WinConditionsTest` (Win Detection, Winning Coordinates & Optimisation Equivalence)
    
    -   `test_empty_board`: An empty board filled with `"#"` never triggers `check_win(board, piece)`.
    -   `test_horizontal_win_check` & `test_vertical_win_check`: Placing 4 consecutive matching pieces horizontally or vertically always causes `check_win()` to return `True` regardless of board size.
    -   `test_diagonal_win_check`: Placing 4 consecutive pieces along either a 45-degree (`board_pos[i, i]`) or 135-degree (`board_neg[3 - i, i]`) diagonal always triggers a win.
    -   `test_get_winning_cells_returns_four_matching_coordinates`: When a 4-in-a-row win exists, `get_winning_cells(board, piece)` returns a list of 4 `(row, col)` coordinates, and every returned coordinate contains `piece`.
    -   `test_vectorized_check_win_matches_loop_baseline`: Across any random sequence of moves (`0..30` drops) and board dimensions (`6..15` $times$ `7..15`), the optimised NumPy vectorised `check_win(board, piece)` always returns the exact same boolean result as the baseline loop implementation `check_win_loop(board, piece)`.
5.  `MCTSPropertiesTest` (Node Expansion & UCB1 Selection)
    
    -   `test_node_expand_creates_valid_child_without_altering_parent`: Calling `root.expand(next_piece)` leaves the parent board array untouched in memory, decreases `len(root.untried_moves)` by `1`, adds `1` child to `root.children`, links `child.parent` to `root`, and reduces the child board's `"#"` count by `1`.
    -   `test_best_child_selects_higher_win_rate_given_equal_visits`: When two child nodes have the exact same visit count (`visits`), `best_child(c=1.414)` always selects the child with the strictly higher win score (`wins_b > wins_a`) because their exploration bonuses are identical.
6.  `MCTSBackpropagationPropertiesTest` (Ancestry Score Updates)
    
    -   `test_backpropagate_updates_all_ancestors_correctly`: Across any tree depth (`1..6`), calling `agent.backpropagate(leaf, winner)` increments `visits` by `+1` for every node in the chain and assigns `+0.5` for draws (`None`), `+1.0` when `winner == node.game_piece`, and `+0.0` when the opponent won.
7.  `AIMCTSPropertiesTest` (End-to-End Search & Tactical Win Finding)
    
    -   `test_mcts_returns_valid_col_and_doesnt_mutate_board`: Running `agent.mcts_search(board)` returns a valid column index from `get_valid_locations(board)` without mutating the original board passed into the search.
    -   `test_mcts_finds_immediate_horizontal_winning_move`: Given 200 iterations on any board size (`6..10` $times$ `7..10`) where the AI (`"O"`) already has 3 horizontal pieces in a row on the bottom (`start_col` to `start_col + 2`, with `start_col - 1` blocked by `"!"`), `mcts_search()` reliably selects the winning 4th column (`start_col + 3`).

## Code Optimisation & Benchmarking (`check_win`)

References:

-   [https://medium.com/@amit25173/what-is-a-numpy-mask-and-why-use-it-cb567e77fb7f](https://medium.com/@amit25173/what-is-a-numpy-mask-and-why-use-it-cb567e77fb7f)
-   [https://www.geeksforgeeks.org/python/what-makes-python-a-slow-language/](https://www.geeksforgeeks.org/python/what-makes-python-a-slow-language/)
-   [https://jakevdp.github.io/blog/2014/05/09/why-python-is-slow/](https://jakevdp.github.io/blog/2014/05/09/why-python-is-slow/)

When it came to optimising parts of the code, one major choke point was the win check. This was due to a single AI turn using MCTS running 1500 iterations, which means in every single iteration:

-   `check_win()` is called inside `MCTSNode.is_terminal()` during the Selection and Expansion phases to check whether a node already contains a win line.
-   `check_win()` is also called again after every single random piece drop inside `simulate_random_rollout()` until the simulated game finishes (the dynamic board sizing mechanic means the number of moves grows exponentially). This results in `check_win` being executed between 30,000 and 100,000+ times per AI turn.

### Optimising the `check_win` Function

The initial win-detection mechanism `check_win_loop` relied on four pairs of nested Python for loops to scan the grid cell-by-cell across all four directional axes. While this was the straightforward easy-to-read approach, iterating cell-by-cell in pure Python incurs heavy bytecode loop overhead and repeated scalar array indexing (`board[r, c]`), which means the `check_win_loop` scales poorly when board dimensions increase from $6 times 7$ up to $20 times 20$.

To fix this, `check_win` was rewritten using NumPy boolean masks and shifted 2D array slicing, pushing the entire win check into compiled C operations.

#### How the optimised `win_check` works

-   Firstly, it creates a 2D boolean mask of the board in a single compiled C operation `mask = board == piece`
-   Instead of looping through columns one by one, NumPy takes 4 shifted views of `mask` (offset by `0`, `1`, `2`, and `3` columns, reducing the 7 columns down to 4 overlapping windows of width 4) and combines them using bitwise AND (`&`). A position in the result is only `True` (`T`) if all 4 shifted slices are `True` at that exact same index:
-   It then checks all four win directions by shifting 2D views of `mask` by `0`,`1`,`2`, and `3` steps and combining them with bitwise AND (`&`) and `np.any()`
    -   Horizontal: `np.any(mask[:, :-3] & mask[:, 1:-2] & mask[:, 2:-1] & mask[:, 3:])`
    -   Vertical:`np.any(mask[:-3, :] & mask[1:-2, :] & mask[2:-1, :] & mask[3:, :])`
    -   Negative / Back-Slash Diagonal:`np.any(mask[:-3, :-3] & mask[1:-2, 1:-2] & mask[2:-1, 2:-1] & mask[3:, 3:])`
    -   Positive / Forward-Slash Diagonal:`np.any(mask[3:, :-3] & mask[2:-1, 1:-2] & mask[1:-2, 2:-1] & mask[:-3, 3:])`

#### Optimisation Benefit

Running [`benchmarks/benchmark_check_win.py`](benchmarks/benchmark_check_win.py) across `10,000` iterations (`20,000` calls per board size, checking both `"X"` and `"O"` on reproducible mid-game boards with `seed=28`) produced the following results:

```text
Board: standard
  Method: Python Nested Loops | Time: 6488.541199942119 ms | Memory: 226 bytes | Speedup: 1.0x
  Method: NumPy Vectorised    | Time: 2981.997200055048 ms | Memory: 1722 bytes | Speedup: 2.18 x

Board: medium
  Method: Python Nested Loops | Time: 14877.366399974562 ms | Memory: 226 bytes | Speedup: 1.0x
  Method: NumPy Vectorised    | Time: 2829.852299997583 ms | Memory: 1958 bytes | Speedup: 5.26 x

Board: large
  Method: Python Nested Loops | Time: 10915.465499972925 ms | Memory: 226 bytes | Speedup: 1.0x
  Method: NumPy Vectorised    | Time: 1327.1257999585941 ms | Memory: 3028 bytes | Speedup: 8.22 x
```

Board Preset

Dimensions

Moves Dropped

Method

Total Time (`10,000` iters)

Peak Memory (`tracemalloc`)

Speedup

`standard`

$6 times 7$

`12`

Python Nested Loops (`check_win_loop`)

`6,488.54 ms`

`226 bytes`

`1.00x`

`standard`

$6 times 7$

`12`

NumPy Vectorised (`check_win`)

`2,982.00 ms`

`1,722 bytes`

`2.18x`

`medium`

$10 times 11$

`30`

Python Nested Loops (`check_win_loop`)

`14,877.37 ms`

`226 bytes`

`1.00x`

`medium`

$10 times 11$

`30`

NumPy Vectorised (`check_win`)

`2,829.85 ms`

`1,958 bytes`

`5.26x`

`large`

$20 times 20$

`60`

Python Nested Loops (`check_win_loop`)

`10,915.47 ms`

`226 bytes`

`1.00x`

`large`

$20 times 20$

`60`

NumPy Vectorised (`check_win`)

`1,327.13 ms`

`3,028 bytes`

`8.22x`

Key Takeaways from the Benchmark:

-   Scaling Speedup (`2.18x` up to `8.22x`): On a standard $6 times 7$ board, the vectorised implementation is more than twice as fast (`2.18x`, cutting execution time from `6.49s` down to `2.98s`). As the grid grows, Python's nested loop overhead compounds rapidly, whereas NumPy's C-level array slicing scales far better—achieving a `5.26x` speedup on the $10 times 11$ board and an `8.22x` speedup on the $20 times 20$ board (Note: on the `large` 60-move board, one player triggers an early return before all 4 directional axes are exhausted, which is why total time is lower than `medium` while the relative gap between NumPy and Python loops widens to `8.22x`).
-   Time vs. Memory Trade-Off: `check_win_loop` uses a constant `226 bytes` of peak memory across all board sizes because it only inspects individual scalar cells one at a time. The vectorised `check_win` allocates temporary boolean arrays (`mask` and the intermediate bitwise `&` slices), increasing peak memory from `1,722 bytes` ($approx 1.7text{ KB}$) on a $6 times 7$ board to `3,028 bytes` ($approx 3.0text{ KB}$) on a $20 times 20$ board. Trading less than `3 KB` of short-lived heap memory for up to an `8.22x` reduction in CPU time makes the `1,500`-iteration MCTS AI noticeably more responsive during gameplay.
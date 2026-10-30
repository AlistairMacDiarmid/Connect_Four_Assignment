"""
main window controller for the connect 4 gui.
manages top-level window configuration, font/stylesheet loading, stacked view navigation, and view signals.
"""

import logging
from pathlib import Path

from PyQt6 import QtCore
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QApplication
from PyQt6.QtGui import QIcon, QFontDatabase

from gui.views.title_screen import TitleScreen
from gui.views.gamemode_select_screen import GameModeSelectScreen
from gui.views.game_setup_screen import SetupScreen

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    top-level application window hosting a qstackedwidget to switch between views.
    handles navigation signals between the title, mode selection, and game setup screens.
    """

    def __init__(self) -> None:
        """
        initialises the main window, loads fonts and stylesheet, creates view widgets, and wires up signals.
        """
        super().__init__()
        self.setWindowTitle("CONNECT FOUR")
        self.showMaximized()

        # set window icon from bundled svg asset if present
        icon_path = Path(__file__).parent / "img" / "noun_connectfour_7354744.svg"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # load custom bundled fonts and external .qss stylesheet
        self._load_custom_fonts()
        self._load_stylesheet()

        # default to player vs player (1) until changed in mode selection
        self.selected_mode: int = 1

        # central stacked widget to manage screen transitions
        self.stack: QStackedWidget = QStackedWidget()
        self.setCentralWidget(self.stack)

        # instantiate screen views
        self.title_screen: TitleScreen = TitleScreen()
        self.mode_screen: GameModeSelectScreen = GameModeSelectScreen()
        self.setup_screen: SetupScreen = SetupScreen()

        # register screens in the stacked widget
        self.stack.addWidget(self.title_screen)
        self.stack.addWidget(self.mode_screen)
        self.stack.addWidget(self.setup_screen)

        self.connect_signals()
        logger.info("MainWindow initialised with title, mode select, and setup screens")

    def _load_custom_fonts(self) -> None:
        """
        loads all bundled true-type fonts from gui/assets/fonts into the qt font database.

        :return: none
        """
        fonts_dir = Path(__file__).parent / "assets" / "fonts"
        for font_file in fonts_dir.rglob("*.ttf"):
            QFontDatabase.addApplicationFont(str(font_file))
        logger.info("Loaded custom fonts from %s", fonts_dir)

    def _load_stylesheet(self) -> None:
        """
        loads and applies the external qss stylesheet from gui/assets/styles.qss to the main window.

        :return: none
        """
        style_path = Path(__file__).parent / "assets" / "styles.qss"
        if style_path.exists():
            self.setStyleSheet(style_path.read_text(encoding="utf-8"))
            logger.info("Loaded stylesheet from %s", style_path)

    def connect_signals(self) -> None:
        """
        connects custom pyqt signals from child screens to navigation and handler slots.

        :return: none
        """
        # title screen signals
        self.title_screen.play_btn_clicked.connect(self.on_play_clicked)
        self.title_screen.exit_btn_clicked.connect(self.on_exit_clicked)

        # game mode select signals
        self.mode_screen.mode_selected.connect(self.on_mode_selected)
        self.mode_screen.back_btn_clicked.connect(self.on_mode_back_clicked)

        # game setup signals
        self.setup_screen.back_btn_clicked.connect(self.on_setup_back_clicked)
        self.setup_screen.start_game_clicked.connect(self.on_start_game)

    def on_play_clicked(self) -> None:
        """
        navigates from the title screen to the game mode selection screen.

        :return: none
        """
        logger.info("Play clicked on title screen; navigating to game mode selection")
        self.stack.setCurrentWidget(self.mode_screen)

    def on_exit_clicked(self) -> None:
        """
        logs the exit request from the title screen and closes the main window.

        :return: none
        """
        logger.info("Exit clicked on title screen; closing main window")
        self.close()

    def on_mode_back_clicked(self) -> None:
        """
        navigates back from the game mode selection screen to the title screen.

        :return: none
        """
        logger.info("Back clicked on game mode screen; returning to title screen")
        self.stack.setCurrentWidget(self.title_screen)

    def on_setup_back_clicked(self) -> None:
        """
        navigates back from the game setup screen to the game mode selection screen.

        :return: none
        """
        logger.info("Back clicked on setup screen; returning to game mode selection")
        self.stack.setCurrentWidget(self.mode_screen)

    def on_mode_selected(self, mode: int) -> None:
        """
        handles game mode selection, updates setup screen options, and navigates to setup.

        :param mode: integer representing the selected mode (1 for pvp, 2 for pvc)
        :return: none
        """
        self.selected_mode = mode
        mode_str = "Player vs Player" if mode == 1 else "Player vs Computer"
        logger.info("Selected game mode: %s (mode=%d)", mode_str, mode)

        # enable or disable ai difficulty options based on selected game mode
        self.setup_screen.config_mode(mode)
        self.stack.setCurrentWidget(self.setup_screen)

    def on_start_game(self, rows: int, cols: int, difficulty: str) -> None:
        """
        handles the start game signal from the setup screen with chosen configuration parameters.

        :param rows: number of rows for the game board
        :param cols: number of columns for the game board
        :param difficulty: selected ai difficulty string ("easy" or "medium")
        :return: none
        """
        mode_str = "Player vs Player" if self.selected_mode == 1 else "Player vs Computer"
        logger.info(
            "Starting game: mode=%s (%d), board=%dx%d, difficulty=%s",
            mode_str,
            self.selected_mode,
            rows,
            cols,
            difficulty,
        )
        # temporary debug print until main game board view is implemented
        print(
            f"Starting game: mode={mode_str} ({self.selected_mode}), "
            f"board={rows}x{cols}, difficulty={difficulty}"
        )

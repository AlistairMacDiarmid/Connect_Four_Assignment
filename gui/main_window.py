"""
main window controller for the connect 4 gui.
manages top-level window configuration, font/stylesheet loading, stacked view navigation, and view signals.
"""

import logging
from pathlib import Path

from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QApplication
from PyQt6.QtGui import QFontDatabase

from gui.views.game_screen import GameScreen
from gui.views.title_screen import TitleScreen
from gui.views.gamemode_select_screen import GameModeSelectScreen
from gui.views.game_setup_screen import SetupScreen
from gui.controllers.game_controller import GameController

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    top-level application window hosting a qstackedwidget to switch between views.
    handles navigation signals between the title, mode selection, game setup, and game board screens.
    """

    def __init__(self) -> None:
        """
        initialises the main window, loads fonts and stylesheet, creates view widgets, and wires up signals.
        """
        super().__init__()
        self.setWindowTitle("CONNECT FOUR")

        # constrain maximum window size to a single monitor's geometry so it never spills onto a second screen
        screen = QApplication.primaryScreen()
        screen_size = screen.geometry().size()
        self.setMaximumSize(screen_size)
        logger.info(
            "Constrained MainWindow maximum size to (%dx%d)",
            screen_size.width(),
            screen_size.height(),
        )

        self.showFullScreen()

        # load custom bundled fonts and external .qss stylesheet
        self.load_custom_fonts()
        self.load_stylesheet()

        # default to player vs player (1) until changed in mode selection
        self.selected_mode: int = 1

        # central stacked widget to manage screen transitions
        self.stack: QStackedWidget = QStackedWidget()
        self.setCentralWidget(self.stack)

        # instantiate screen views and game controller
        self.title_screen: TitleScreen = TitleScreen()
        self.mode_screen: GameModeSelectScreen = GameModeSelectScreen()
        self.setup_screen: SetupScreen = SetupScreen()
        self.game_screen: GameScreen = GameScreen()
        self.game_controller: GameController = GameController(self.game_screen)

        # register screens in the stacked widget
        self.stack.addWidget(self.title_screen)
        self.stack.addWidget(self.mode_screen)
        self.stack.addWidget(self.setup_screen)
        self.stack.addWidget(self.game_screen)

        self.connect_signals()
        logger.info(
            "MainWindow initialised with TitleScreen, GameModeSelectScreen, SetupScreen, and GameScreen"
        )

    def load_custom_fonts(self) -> None:
        """
        loads all bundled true-type fonts from gui/assets/fonts into the qt font database.

        :return: none
        """
        fonts_dir = Path(__file__).parent / "assets" / "fonts"
        if not fonts_dir.exists():
            logger.warning("Custom fonts directory not found at %s", fonts_dir)
            return

        loaded_count = 0
        for font_file in fonts_dir.rglob("*.ttf"):
            font_id = QFontDatabase.addApplicationFont(str(font_file))
            if font_id != -1:
                loaded_count += 1
            else:
                logger.warning("Failed to load font file: %s", font_file)

        logger.info("Loaded %d custom font file(s) from %s", loaded_count, fonts_dir)

    def load_stylesheet(self) -> None:
        """
        loads and applies the external qss stylesheet from gui/assets/styles.qss to the main window.

        :return: none
        """
        style_path = Path(__file__).parent / "assets" / "styles.qss"
        if style_path.exists():
            self.setStyleSheet(style_path.read_text(encoding="utf-8"))
            logger.info("Loaded QSS stylesheet from %s", style_path)
        else:
            logger.warning("QSS stylesheet not found at %s", style_path)

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

        # game screen signals
        self.game_screen.back_btn_clicked.connect(self.on_game_back_clicked)
        logger.debug("Connected navigation signals for all views in MainWindow")

    def on_play_clicked(self) -> None:
        """
        navigates from the title screen to the game mode selection screen.

        :return: none
        """
        logger.info("Navigation: TitleScreen -> GameModeSelectScreen")
        self.stack.setCurrentWidget(self.mode_screen)

    def on_exit_clicked(self) -> None:
        """
        logs the exit request from the title screen and closes the main window.

        :return: none
        """
        logger.info("Exit clicked on TitleScreen; closing application window")
        self.close()

    def on_mode_back_clicked(self) -> None:
        """
        navigates back from the game mode selection screen to the title screen.

        :return: none
        """
        logger.info("Navigation: GameModeSelectScreen -> TitleScreen")
        self.stack.setCurrentWidget(self.title_screen)

    def on_setup_back_clicked(self) -> None:
        """
        navigates back from the game setup screen to the game mode selection screen.

        :return: none
        """
        logger.info("Navigation: SetupScreen -> GameModeSelectScreen")
        self.stack.setCurrentWidget(self.mode_screen)

    def on_game_back_clicked(self) -> None:
        """
        navigates back from the game board screen to the game setup screen.

        :return: none
        """
        logger.info("Navigation: GameScreen -> SetupScreen (left active match)")
        self.stack.setCurrentWidget(self.setup_screen)

    def on_mode_selected(self, mode: int) -> None:
        """
        handles game mode selection, updates setup screen options, and navigates to setup.

        :param mode: integer representing the selected mode (1 for pvp, 2 for pvc)
        :return: none
        """
        self.selected_mode = mode
        mode_str = "Player vs Player" if mode == 1 else "Player vs Computer"
        logger.info(
            "Navigation: GameModeSelectScreen -> SetupScreen (selected mode=%d: %s)",
            mode,
            mode_str,
        )

        # enable or disable ai difficulty options based on selected game mode
        self.setup_screen.config_mode(mode)
        self.stack.setCurrentWidget(self.setup_screen)

    def on_start_game(self, rows: int, cols: int, difficulty: str) -> None:
        """
        creates the board with the chosen dimensions, populates the game screen, and navigates to it.

        :param rows: number of rows for the game board
        :param cols: number of columns for the game board
        :param difficulty: selected ai difficulty string ("easy" or "medium")
        :return: none
        """
        mode_str = "Player vs Player" if self.selected_mode == 1 else "Player vs Computer"
        logger.info(
            "Navigation: SetupScreen -> GameScreen | Starting match: mode=%s (%d), board=%dx%d, difficulty=%s",
            mode_str,
            self.selected_mode,
            rows,
            cols,
            difficulty,
        )

        # start a new match via the game controller and switch to the game screen
        self.game_controller.start_game(
            mode=self.selected_mode,
            rows=rows,
            cols=cols,
            difficulty=difficulty,
        )
        self.stack.setCurrentWidget(self.game_screen)

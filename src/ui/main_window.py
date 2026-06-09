from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from PyQt6.QtCore import Qt
from src.ui.setup_screen import SetupScreen
from src.ui.game_screen import GameScreen
from src.engine.game import Game
from src.runner.player_config import PlayerConfig
from src.runner.player_factory import build_mcts

DIFFICULTY_PRESETS: dict[str, PlayerConfig] = {
    "easy": PlayerConfig(
        name="MCTS-Easy",
        iterations=500,
        selection="uct",
        simulation="random",
        backpropagation="standard",
    ),
    "medium": PlayerConfig(
        name="MCTS-Medium",
        iterations=2000,
        selection="uct",
        simulation="random",
        backpropagation="standard",
    ),
    "hard": PlayerConfig(
        name="MCTS-Solver-Hard",
        iterations=2000,
        selection="uct",
        simulation="random",
        backpropagation="solver",
    ),
}

DEFAULT_PLAYER = DIFFICULTY_PRESETS["medium"]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Close Twins Avoidance")
        self.setMinimumSize(800, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.setup_screen = SetupScreen()
        self.setup_screen.game_started.connect(self.start_game)
        self.stack.addWidget(self.setup_screen)

        self.game_screen = GameScreen()
        self.game_screen.game_ended.connect(self.on_game_ended)
        self.stack.addWidget(self.game_screen)

        self.stack.setCurrentWidget(self.setup_screen)

    def start_game(self, mode, alphabet_size, max_length, difficulty="medium"):
        alphabet = [chr(ord('a') + i) for i in range(alphabet_size)]
        engine = Game(alphabet, max_length)

        config = DIFFICULTY_PRESETS.get(difficulty, DEFAULT_PLAYER)
        ai_pointer = build_mcts(config)
        ai_inserter = build_mcts(config)

        self.stack.setCurrentWidget(self.game_screen)
        self.game_screen.start_game(engine, mode, ai_pointer, ai_inserter)

    def on_game_ended(self, status, history):
        self.game_screen.cleanup()
        self.setup_screen.reset()
        self.stack.setCurrentWidget(self.setup_screen)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            if self.stack.currentWidget() == self.game_screen:
                reply = QMessageBox.question(
                    self,
                    "Exit Game",
                    "Exit current game?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.Yes:
                    self.game_screen.cleanup()
                    self.setup_screen.reset()
                    self.stack.setCurrentWidget(self.setup_screen)

from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from PyQt6.QtCore import Qt
from src.ui.setup_screen import SetupScreen
from src.ui.game_screen import GameScreen
from src.engine.game import Game
import random


class SimpleAI:
    def get_best_move(self, engine):
        legal_moves = engine.get_legal_moves()
        return random.choice(legal_moves) if legal_moves else None


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
    
    def start_game(self, mode, alphabet_size, max_length):
        alphabet = [chr(ord('a') + i) for i in range(alphabet_size)]
        engine = Game(alphabet, max_length)
        
        ai_pointer = SimpleAI()
        ai_inserter = SimpleAI()
        
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
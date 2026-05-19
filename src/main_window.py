from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox, QFileDialog
from PyQt6.QtCore import Qt
from src.setup_screen import SetupScreen
from src.game_screen import GameScreen
from src.engine.game import Game
import json
from datetime import datetime


class SimpleAI:
    """Wrapper for AI that uses get_legal_moves"""
    def __init__(self):
        pass
    
    def get_best_move(self, engine):
        import random
        legal_moves = engine.get_legal_moves()
        return random.choice(legal_moves) if legal_moves else None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Close Twins Avoidance")
        self.setMinimumSize(800, 600)
        
        # Stacked widget
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Setup screen
        self.setup_screen = SetupScreen()
        self.setup_screen.game_started.connect(self.start_game)
        self.stack.addWidget(self.setup_screen)
        
        # Game screen
        self.game_screen = GameScreen()
        self.game_screen.game_ended.connect(self.on_game_ended)
        self.stack.addWidget(self.game_screen)
        
        self.stack.setCurrentWidget(self.setup_screen)
    
    def start_game(self, mode, alphabet_size, max_length):
        """Initialize and start game with real Game engine"""
        # Create alphabet
        alphabet = [chr(ord('a') + i) for i in range(alphabet_size)]
        
        # Create engine
        engine = Game(alphabet, max_length)
        
        # Create AI players
        ai_pointer = SimpleAI()
        ai_inserter = SimpleAI()
        
        # Switch to game screen
        self.stack.setCurrentWidget(self.game_screen)
        self.game_screen.start_game(engine, mode, ai_pointer, ai_inserter)
    
    def on_game_ended(self, status, history):
        # Return to setup
        self.game_screen.cleanup()
        self.setup_screen.reset()
        self.stack.setCurrentWidget(self.setup_screen)
    
    def save_history(self, history):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Game History",
            f"game_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )
        
        if filename:
            data = {
                'timestamp': datetime.now().isoformat(),
                'moves': [{'player': move[0], 'action': move[1]} for move in history]
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
    
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
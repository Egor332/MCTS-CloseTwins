from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QKeyEvent
from src.domain import GameMode, GameStatus, Role
from typing import Optional


class GameScreen(QWidget):
    game_ended = pyqtSignal(GameStatus, list)
    
    def __init__(self):
        super().__init__()
        self.engine = None
        self.mode = None
        self.cursor_position = 0
        self.waiting_for_input = False
        self.cursor_visible = True
        self.move_history = []
        self.ai_timer = QTimer()
        self.ai_timer.timeout.connect(self.process_ai_move)
        self.cursor_timer = QTimer()
        self.cursor_timer.timeout.connect(self.toggle_cursor)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Monospace", 14))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #666;")
        
        # Word display
        self.word_label = QLabel("")
        self.word_label.setFont(QFont("Monospace", 36, QFont.Weight.Bold))
        self.word_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.word_label.setMinimumHeight(100)
        self.word_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                padding: 20px;
                border: none;
            }
        """)
        
        # Info label
        self.info_label = QLabel("")
        self.info_label.setFont(QFont("Monospace", 11))
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #999;")
        
        layout.addStretch()
        layout.addWidget(self.status_label)
        layout.addWidget(self.word_label)
        layout.addWidget(self.info_label)
        layout.addStretch()
        
        self.setLayout(layout)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def start_game(self, engine, mode: GameMode, ai_pointer, ai_inserter):
        self.engine = engine
        self.mode = mode
        self.ai_pointer = ai_pointer
        self.ai_inserter = ai_inserter
        self.cursor_position = 0
        self.move_history = []
        
        # Clean up end buttons if they exist
        if hasattr(self, 'end_button_layout'):
            while self.end_button_layout.count():
                item = self.end_button_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.layout().removeItem(self.end_button_layout)
            del self.end_button_layout
        
        # Reset status label style
        self.status_label.setStyleSheet("color: #666;")
        
        # INSERTER always starts - POINTER chooses position 0 first
        self.engine.apply_index(0)
        self.move_history.append(('POINTER (initial)', 'chose position 0'))
        
        if mode == GameMode.HUMAN_INSERTER:
            self.status_label.setText("Your turn - Type letter")
            self.show_cursor_for_input()
        elif mode == GameMode.HUMAN_POINTER:
            # AI inserts first letter
            self.status_label.setText("AI inserting letter...")
            self.ai_timer.start(500)
        else:  # AI vs AI
            self.status_label.setText("AI vs AI")
            self.ai_timer.start(500)
        
        self.update_display()
    
    def update_display(self):
        word = self.engine.get_current_word()
        turn = self.engine.turn
        pending = self.engine.choosen_index
        
        # Build display - underscore always shown, square blinks on top
        if self.waiting_for_input:
            if turn == Role.POINTER:
                # Blinking square on underscore at cursor position
                if self.cursor_visible:
                    display = word[:self.cursor_position] + "█" + word[self.cursor_position:]
                else:
                    display = word[:self.cursor_position] + "_" + word[self.cursor_position:]
            else:
                # Blinking square on underscore at pending position
                if self.cursor_visible:
                    display = word[:pending] + "█" + word[pending:]
                else:
                    display = word[:pending] + "_" + word[pending:]
        else:
            if turn == Role.INSERTER and pending is not None:
                # Show underscore at pending position
                display = word[:pending] + "_" + word[pending:]
            else:
                display = word if word else "_"
        
        self.word_label.setText(display)
        
        # Update info
        max_len = self.engine.get_max_length()
        alphabet = sorted(self.engine.get_alphabet())
        self.info_label.setText(f"Length: {len(word)}/{max_len} | Alphabet: {', '.join(alphabet)}")
    
    def show_cursor_for_input(self):
        self.waiting_for_input = True
        self.cursor_visible = True
        self.cursor_timer.start(500)
        self.update_display()
    
    def hide_cursor(self):
        self.waiting_for_input = False
        self.cursor_timer.stop()
        self.cursor_visible = False
        self.update_display()
    
    def toggle_cursor(self):
        self.cursor_visible = not self.cursor_visible
        self.update_display()
    
    def cleanup(self):
        self.ai_timer.stop()
        self.cursor_timer.stop()
    
    def keyPressEvent(self, event: QKeyEvent):
        if not self.waiting_for_input:
            return
        
        key = event.key()
        turn = self.engine.turn
        
        # POINTER role - arrows + enter
        if turn == Role.POINTER and self.mode == GameMode.HUMAN_POINTER:
            word_len = len(self.engine.get_current_word())
            
            if key == Qt.Key.Key_Left:
                self.cursor_position = max(0, self.cursor_position - 1)
                self.update_display()
            elif key == Qt.Key.Key_Right:
                self.cursor_position = min(word_len, self.cursor_position + 1)
                self.update_display()
            elif key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
                self.confirm_position()
        
        # INSERTER role - type letter
        elif turn == Role.INSERTER and self.mode == GameMode.HUMAN_INSERTER:
            text = event.text().lower()
            if text and text in self.engine.get_alphabet():
                self.insert_letter(text)
    
    def confirm_position(self):
        """Human POINTER confirms position"""
        self.hide_cursor()
        
        try:
            self.engine.apply_index(self.cursor_position)
            self.move_history.append(('POINTER', f"chose position {self.cursor_position}"))
            self.status_label.setText("AI inserting letter...")
            self.update_display()
            self.ai_timer.start(1000)
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.show_cursor_for_input()
    
    def insert_letter(self, letter: str):
        """Human INSERTER inserts letter"""
        self.hide_cursor()
        
        try:
            pending = self.engine.choosen_index
            self.engine.apply_letter(letter)
            self.move_history.append(('INSERTER', f"inserted '{letter}' at {pending}"))
            self.update_display()
            
            if self.engine.game_status != GameStatus.ONGOING:
                self.end_game()
                return
            
            self.cursor_position = 0
            self.status_label.setText("AI choosing position...")
            self.ai_timer.start(1000)
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.show_cursor_for_input()
    
    def process_ai_move(self):
        self.ai_timer.stop()
        turn = self.engine.turn
        
        try:
            if turn == Role.POINTER:
                index = self.ai_pointer.get_best_move(self.engine)
                self.engine.apply_index(index)
                self.move_history.append(('POINTER (AI)', f"chose position {index}"))
                self.update_display()
                
                if self.mode == GameMode.HUMAN_INSERTER:
                    self.status_label.setText("Your turn - Type letter")
                    self.show_cursor_for_input()
                else:
                    self.status_label.setText("AI inserting letter...")
                    self.ai_timer.start(500)
            
            else:  # INSERTER
                letter = self.ai_inserter.get_best_move(self.engine)
                pending = self.engine.choosen_index
                self.engine.apply_letter(letter)
                self.move_history.append(('INSERTER (AI)', f"inserted '{letter}' at {pending}"))
                self.update_display()
                
                if self.engine.game_status != GameStatus.ONGOING:
                    QTimer.singleShot(500, self.end_game)
                    return
                
                if self.mode == GameMode.HUMAN_POINTER:
                    self.cursor_position = 0
                    self.status_label.setText("Your turn - Choose position")
                    self.show_cursor_for_input()
                else:
                    self.status_label.setText("AI choosing position...")
                    self.ai_timer.start(500)
        
        except Exception as e:
            self.status_label.setText(f"AI Error: {str(e)}")
    
    def end_game(self):
        self.ai_timer.stop()
        self.hide_cursor()
        
        status = self.engine.game_status
        word = self.engine.get_current_word()
        
        # Determine winner
        if status == GameStatus.P2_WINS_LIMIT:
            if self.mode == GameMode.HUMAN_INSERTER:
                message = "You Won!"
            elif self.mode == GameMode.HUMAN_POINTER:
                message = "You Lost!"
            else:
                message = "Inserter Won!"
        else:
            if self.mode == GameMode.HUMAN_POINTER:
                message = "You Won!"
            elif self.mode == GameMode.HUMAN_INSERTER:
                message = "You Lost!"
            else:
                message = "Pointer Won!"
        
        # Update status label
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #000; font-size: 18px; font-weight: bold;")
        
        # Show end game buttons
        self.show_end_buttons()
    
    def show_end_buttons(self):
        """Show buttons at end of game"""
        from PyQt6.QtWidgets import QPushButton, QHBoxLayout
        
        # Create buttons
        button_layout = QHBoxLayout()
        
        back_btn = QPushButton("Back to Menu")
        back_btn.setFont(QFont("Monospace", 11))
        back_btn.setMinimumHeight(50)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #666;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        back_btn.clicked.connect(self.return_to_menu)
        
        play_again_btn = QPushButton("Play Again")
        play_again_btn.setFont(QFont("Monospace", 12, QFont.Weight.Bold))
        play_again_btn.setMinimumHeight(50)
        play_again_btn.setStyleSheet("""
            QPushButton {
                background-color: #000;
                color: #fff;
                border: none;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #333;
            }
        """)
        play_again_btn.clicked.connect(self.play_again)
        
        save_btn = QPushButton("Download History")
        save_btn.setFont(QFont("Monospace", 11))
        save_btn.setMinimumHeight(50)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #666;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        save_btn.clicked.connect(self.save_history_to_file)
        
        button_layout.addWidget(back_btn)
        button_layout.addWidget(play_again_btn)
        button_layout.addWidget(save_btn)
        
        # Add to main layout
        self.layout().addLayout(button_layout)
        self.end_button_layout = button_layout
    
    def return_to_menu(self):
        """Return to setup screen"""
        self.game_ended.emit(self.engine.game_status, self.move_history)
    
    def play_again(self):
        """Restart game with same settings"""
        # Clean up current buttons
        if hasattr(self, 'end_button_layout'):
            while self.end_button_layout.count():
                item = self.end_button_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.layout().removeItem(self.end_button_layout)
            del self.end_button_layout
        
        # Reset status label style
        self.status_label.setStyleSheet("color: #666;")
        
        # Start new game with same settings
        from src.engine.game import Game
        alphabet = self.engine.get_alphabet()
        max_length = self.engine.get_max_length()
        new_engine = Game(alphabet, max_length)
        
        self.start_game(new_engine, self.mode, self.ai_pointer, self.ai_inserter)
    
    def save_history_to_file(self):
        """Save game history as text file"""
        from PyQt6.QtWidgets import QFileDialog
        from datetime import datetime
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Game History",
            f"game_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt)"
        )
        
        if filename:
            with open(filename, 'w') as f:
                f.write("Game History\n" + "=" * 40 + "\n\n")
                
                current_word = ""
                for i, (player, action) in enumerate(self.move_history, 1):
                    if "chose position" in action:
                        pos = action.split()[-1]
                        f.write(f"{i}. {player} chose position {pos}\n")
                    elif "inserted" in action:
                        parts = action.split("'")
                        letter = parts[1] if len(parts) > 1 else "?"
                        pos_part = action.split("at ")[-1]
                        pos = int(pos_part) if pos_part.isdigit() else 0
                        current_word = current_word[:pos] + letter + current_word[pos:]
                        f.write(f"{i}. {player} inserted '{letter}' → {current_word}\n")
                
                f.write("\n" + "=" * 40 + "\n")
                f.write(f"Final word: {self.engine.get_current_word()}\n")
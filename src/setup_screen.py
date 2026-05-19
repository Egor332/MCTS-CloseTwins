from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QSpinBox, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from src.domain import GameMode


class SetupScreen(QWidget):
    game_started = pyqtSignal(GameMode, int, int)  # mode, alphabet_size, max_length
    
    def __init__(self):
        super().__init__()
        self.selected_mode = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("Close Twins Avoidance")
        title.setFont(QFont("Monospace", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Mode selection buttons
        self.inserter_btn = self._create_mode_button("Play as Inserter")
        self.pointer_btn = self._create_mode_button("Play as Pointer")
        self.ai_btn = self._create_mode_button("AI vs AI")
        
        self.inserter_btn.clicked.connect(lambda: self.on_mode_selected(GameMode.HUMAN_INSERTER))
        self.pointer_btn.clicked.connect(lambda: self.on_mode_selected(GameMode.HUMAN_POINTER))
        self.ai_btn.clicked.connect(lambda: self.on_mode_selected(GameMode.AI_VS_AI))
        
        # Instructions button
        help_btn = QPushButton("Instructions")
        help_btn.setFont(QFont("Monospace", 10))
        help_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #666;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #404040;
            }
        """)
        help_btn.clicked.connect(self.show_instructions)
        
        # Settings panel (hidden initially)
        self.settings_panel = QWidget()
        settings_layout = QVBoxLayout()
        
        settings_title = QLabel("Game Settings")
        settings_title.setFont(QFont("Monospace", 14, QFont.Weight.Bold))
        settings_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Alphabet size
        alphabet_layout = QHBoxLayout()
        alphabet_label = QLabel("Alphabet size:")
        alphabet_label.setFont(QFont("Monospace", 11))
        self.alphabet_spin = QSpinBox()
        self.alphabet_spin.setRange(2, 26)
        self.alphabet_spin.setValue(4)
        self.alphabet_spin.setFont(QFont("Monospace", 11))
        alphabet_layout.addWidget(alphabet_label)
        alphabet_layout.addWidget(self.alphabet_spin)
        
        # Max length
        length_layout = QHBoxLayout()
        length_label = QLabel("Max word length:")
        length_label.setFont(QFont("Monospace", 11))
        self.length_spin = QSpinBox()
        self.length_spin.setRange(3, 30)
        self.length_spin.setValue(10)
        self.length_spin.setFont(QFont("Monospace", 11))
        length_layout.addWidget(length_label)
        length_layout.addWidget(self.length_spin)
        
        # Start button
        self.start_btn = QPushButton("Start Game")
        self.start_btn.setFont(QFont("Monospace", 12, QFont.Weight.Bold))
        self.start_btn.setMinimumHeight(50)
        self.start_btn.setStyleSheet("""
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
        self.start_btn.clicked.connect(self.start_game)
        
        # Back button
        back_btn = QPushButton("Back")
        back_btn.setFont(QFont("Monospace", 10))
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #666;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #404040;
            }
        """)
        back_btn.clicked.connect(self.back_to_mode_selection)
        
        settings_layout.addWidget(settings_title)
        settings_layout.addSpacing(20)
        settings_layout.addLayout(alphabet_layout)
        settings_layout.addLayout(length_layout)
        settings_layout.addSpacing(20)
        settings_layout.addWidget(self.start_btn)
        settings_layout.addWidget(back_btn)
        self.settings_panel.setLayout(settings_layout)
        self.settings_panel.hide()
        
        # Main layout assembly
        layout.addWidget(title)
        layout.addSpacing(30)
        layout.addWidget(self.inserter_btn)
        layout.addWidget(self.pointer_btn)
        layout.addWidget(self.ai_btn)
        layout.addSpacing(20)
        layout.addWidget(help_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(30)
        layout.addWidget(self.settings_panel)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def _create_mode_button(self, text):
        btn = QPushButton(text)
        btn.setFont(QFont("Monospace", 12, QFont.Weight.Bold))
        btn.setMinimumHeight(50)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #000;
                color: #fff;
                border: none;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #404040;
            }
        """)
        return btn
    
    def on_mode_selected(self, mode):
        self.selected_mode = mode
        
        # Hide mode buttons
        self.inserter_btn.hide()
        self.pointer_btn.hide()
        self.ai_btn.hide()
        
        # Show settings
        self.settings_panel.show()
    
    def back_to_mode_selection(self):
        self.selected_mode = None
        self.settings_panel.hide()
        self.inserter_btn.show()
        self.pointer_btn.show()
        self.ai_btn.show()
    
    def start_game(self):
        alphabet_size = self.alphabet_spin.value()
        max_length = self.length_spin.value()
        self.game_started.emit(self.selected_mode, alphabet_size, max_length)
    
    def show_instructions(self):
        instructions = """
OBJECTIVE:
- INSERTER: Build a word to max length without creating twins
- POINTER: Force INSERTER to create twins

TWINS: Any repeated substring (e.g., "aa", "abab", "123123")

CONTROLS:

As INSERTER:
• Arrow Keys: Move cursor
• Enter: Confirm position
• Wait for AI to insert letter

As POINTER:
• Type letter on keyboard when cursor appears
• Wait for AI to choose position

AI vs AI:
• Watch the game unfold automatically
        """
        
        QMessageBox.information(self, "Instructions", instructions.strip())
    
    def reset(self):
        """Reset to initial state"""
        self.selected_mode = None
        self.settings_panel.hide()
        self.inserter_btn.show()
        self.pointer_btn.show()
        self.ai_btn.show()
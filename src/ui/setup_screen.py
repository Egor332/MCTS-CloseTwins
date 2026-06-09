from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpinBox, QComboBox, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from src.domain import GameMode
from src.ui.components import create_button, create_label, UIConfig


class SetupScreen(QWidget):
    game_started = pyqtSignal(GameMode, int, int, str)
    
    def __init__(self):
        super().__init__()
        self.selected_mode = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = create_label("Close Twins Avoidance", style_type="title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont(*UIConfig.FONT_MONO_TITLE))
        
        # Mode buttons
        self.inserter_btn = create_button("Play as Inserter", style_type="primary")
        self.pointer_btn = create_button("Play as Pointer", style_type="primary")
        self.ai_btn = create_button("AI vs AI", style_type="primary")
        
        self.inserter_btn.clicked.connect(lambda: self.on_mode_selected(GameMode.HUMAN_INSERTER))
        self.pointer_btn.clicked.connect(lambda: self.on_mode_selected(GameMode.HUMAN_POINTER))
        self.ai_btn.clicked.connect(lambda: self.on_mode_selected(GameMode.AI_VS_AI))
        
        # Help button
        help_btn = create_button("Instructions", style_type="secondary", font_size="sm")
        help_btn.clicked.connect(self.show_instructions)
        
        # Settings panel
        self.settings_panel = QWidget()
        settings_layout = QVBoxLayout()
        
        settings_title = create_label("Game Settings", style_type="title")
        settings_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Alphabet size
        alphabet_layout = QHBoxLayout()
        alphabet_label = create_label("Alphabet size:", style_type="normal")
        self.alphabet_spin = QSpinBox()
        self.alphabet_spin.setRange(2, 26)
        self.alphabet_spin.setValue(4)
        self.alphabet_spin.setFont(QFont(*UIConfig.FONT_MONO_MD))
        alphabet_layout.addWidget(alphabet_label)
        alphabet_layout.addWidget(self.alphabet_spin)
        
        # Max length
        length_layout = QHBoxLayout()
        length_label = create_label("Max word length:", style_type="normal")
        self.length_spin = QSpinBox()
        self.length_spin.setRange(3, 30)
        self.length_spin.setValue(10)
        self.length_spin.setFont(QFont(*UIConfig.FONT_MONO_MD))
        length_layout.addWidget(length_label)
        length_layout.addWidget(self.length_spin)
        
        # Difficulty
        difficulty_layout = QHBoxLayout()
        difficulty_label = create_label("AI difficulty:", style_type="normal")
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Easy", "Medium", "Hard"])
        self.difficulty_combo.setCurrentIndex(1)
        self.difficulty_combo.setFont(QFont(*UIConfig.FONT_MONO_MD))
        difficulty_layout.addWidget(difficulty_label)
        difficulty_layout.addWidget(self.difficulty_combo)
        
        # Buttons
        self.start_btn = create_button("Start Game", style_type="primary")
        self.start_btn.clicked.connect(self.start_game)
        
        back_btn = create_button("Back", style_type="secondary", font_size="sm", min_height=40)
        back_btn.clicked.connect(self.back_to_mode_selection)
        
        settings_layout.addWidget(settings_title)
        settings_layout.addSpacing(20)
        settings_layout.addLayout(alphabet_layout)
        settings_layout.addLayout(length_layout)
        settings_layout.addLayout(difficulty_layout)
        settings_layout.addSpacing(20)
        settings_layout.addWidget(self.start_btn)
        settings_layout.addWidget(back_btn)
        self.settings_panel.setLayout(settings_layout)
        self.settings_panel.hide()
        
        # Main assembly
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
    
    def on_mode_selected(self, mode):
        self.selected_mode = mode
        self.inserter_btn.hide()
        self.pointer_btn.hide()
        self.ai_btn.hide()
        self.difficulty_combo.setVisible(mode != GameMode.AI_VS_AI)
        self.settings_panel.show()
    
    def back_to_mode_selection(self):
        self.selected_mode = None
        self.settings_panel.hide()
        self.inserter_btn.show()
        self.pointer_btn.show()
        self.ai_btn.show()
    
    def start_game(self):
        difficulty = self.difficulty_combo.currentText().lower()
        self.game_started.emit(
            self.selected_mode,
            self.alphabet_spin.value(),
            self.length_spin.value(),
            difficulty,
        )
    
    def show_instructions(self):
        msg = """Try to build a word without creating twins* or force your opponent to create them!

CONTROLS:

As Inserter: type one of the letters from the alphabet.

As Pointer: use arrow keys to move the cursor and press Enter to confirm.

AI vs AI: both AIs will play against each other, you can watch the game unfold!


*twins - any repeated substring (e.g., "aa", "abab", "123123")"""
        QMessageBox.information(self, "Instructions", msg)
    
    def reset(self):
        self.selected_mode = None
        self.settings_panel.hide()
        self.inserter_btn.show()
        self.pointer_btn.show()
        self.ai_btn.show()
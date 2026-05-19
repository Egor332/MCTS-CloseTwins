from PyQt6.QtWidgets import QPushButton, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class UIConfig:
    # Colors
    PRIMARY_BG = "#000"
    PRIMARY_TEXT = "#fff"
    SECONDARY_BG = "transparent"
    SECONDARY_BORDER = "#666"
    HOVER_BG = "#404040"
    TEXT_COLOR = "#666"
    MUTED_COLOR = "#999"
    
    # Fonts
    FONT_MONO_SM = ("Monospace", 10)
    FONT_MONO_MD = ("Monospace", 11)
    FONT_MONO_LG = ("Monospace", 12, QFont.Weight.Bold)
    FONT_MONO_XL = ("Monospace", 14, QFont.Weight.Bold)
    FONT_MONO_TITLE = ("Monospace", 24, QFont.Weight.Bold)
    FONT_MONO_DISPLAY = ("Monospace", 36, QFont.Weight.Bold)


def create_button(text, style_type="primary", font_size="lg", min_height=50):
    btn = QPushButton(text)
    
    font_configs = {
        "sm": UIConfig.FONT_MONO_SM,
        "md": UIConfig.FONT_MONO_MD,
        "lg": UIConfig.FONT_MONO_LG,
    }
    
    font_config = font_configs.get(font_size, UIConfig.FONT_MONO_LG)
    btn.setFont(QFont(*font_config))
    btn.setMinimumHeight(min_height)
    
    if style_type == "primary":
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {UIConfig.PRIMARY_BG};
                color: {UIConfig.PRIMARY_TEXT};
                border: none;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: {UIConfig.HOVER_BG};
            }}
        """)
    else:  # secondary
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {UIConfig.SECONDARY_BG};
                border: 1px solid {UIConfig.SECONDARY_BORDER};
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: {UIConfig.HOVER_BG};
            }}
        """)
    
    return btn


def create_label(text, style_type="normal", alignment=None):
    label = QLabel(text)
    
    if style_type == "title":
        label.setFont(QFont(*UIConfig.FONT_MONO_TITLE))
        label.setStyleSheet(f"color: {UIConfig.TEXT_COLOR};")
    elif style_type == "display":
        label.setFont(QFont(*UIConfig.FONT_MONO_DISPLAY))
        label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                padding: 20px;
                border: none;
            }
        """)
    elif style_type == "muted":
        label.setFont(QFont(*UIConfig.FONT_MONO_MD))
        label.setStyleSheet(f"color: {UIConfig.MUTED_COLOR};")
    else:  # normal
        label.setFont(QFont(*UIConfig.FONT_MONO_MD))
        label.setStyleSheet(f"color: {UIConfig.TEXT_COLOR};")
    
    if alignment:
        label.setAlignment(alignment)
    
    return label
"""Koyu gri tema. Yazılar beyaz, arka planlar nötr gri, vurgular orta tonlu.

Tüm renkler bu dosyadan gelir; bir rengi değiştirmek için yalnızca burayı düzenleyin.
"""


class C:
    BG = "#1F2125"
    PANEL = "#272A30"
    PANEL_ALT = "#2B2F36"
    INPUT = "#2E3238"
    BORDER = "#3C4149"
    BORDER_HOVER = "#585F69"
    TEXT = "#FFFFFF"
    TEXT_SOFT = "#E3E6EA"
    TEXT_MUTED = "#A3AAB3"
    TEXT_DISABLED = "#6E757F"
    HEADING = "#D5DCE4"
    ACCENT = "#7893AE"
    ACCENT_HOVER = "#93AAC2"
    ACCENT_DIM = "#4A5D71"
    SUCCESS = "#6F9F8A"
    SUCCESS_DIM = "#3A5248"
    DANGER = "#B57377"
    DANGER_DIM = "#4F3436"
    WARN = "#B49A6C"
    SELECTION = "#3A4150"


RADIUS = 8
INPUT_HEIGHT = 36
FONT_FAMILY = "'Inter', 'Segoe UI', 'SF Pro Text', 'Noto Sans', sans-serif"

HINT_STYLE = (
    f"color: {C.TEXT_MUTED};"
    "font-style: italic;"
    "font-weight: 500;"
    "padding-bottom: 2px;"
)

DARK_STYLE = f"""
QMainWindow, QDialog {{
    background-color: {C.BG};
}}
QWidget {{
    background-color: {C.BG};
    color: {C.TEXT};
    font-family: {FONT_FAMILY};
}}
QFrame {{
    background-color: {C.PANEL};
    border-radius: {RADIUS}px;
    border: 1px solid {C.BORDER};
}}
QLabel {{
    background: transparent;
    border: none;
    color: {C.TEXT};
}}
QLabel:disabled {{
    color: {C.TEXT_DISABLED};
}}
QComboBox, QLineEdit, QTextEdit {{
    background-color: {C.INPUT};
    border: 1px solid {C.BORDER};
    padding: 6px 12px;
    border-radius: {RADIUS}px;
    color: {C.TEXT};
    selection-background-color: {C.ACCENT_DIM};
    selection-color: {C.TEXT};
    min-height: {INPUT_HEIGHT - 12}px;
}}
QComboBox:hover, QLineEdit:hover, QTextEdit:hover {{
    border: 1px solid {C.BORDER_HOVER};
}}
QComboBox:focus, QLineEdit:focus, QTextEdit:focus {{
    border: 1px solid {C.ACCENT};
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox QAbstractItemView {{
    background-color: {C.INPUT};
    selection-background-color: {C.ACCENT_DIM};
    selection-color: {C.TEXT};
    color: {C.TEXT};
    border: 1px solid {C.BORDER};
    outline: none;
}}
QPushButton {{
    background-color: {C.PANEL_ALT};
    border: 1px solid {C.BORDER};
    padding: 6px 14px;
    border-radius: {RADIUS}px;
    color: {C.TEXT};
    font-weight: 600;
    text-align: center;
}}
QPushButton:hover {{
    background-color: {C.SELECTION};
    border: 1px solid {C.BORDER_HOVER};
}}
QPushButton:pressed {{
    background-color: {C.PANEL};
    color: {C.TEXT_MUTED};
}}
QPushButton:checked {{
    background-color: {C.ACCENT_DIM};
    border: 1px solid {C.ACCENT};
    color: {C.TEXT};
}}
QPushButton:disabled {{
    background-color: {C.PANEL};
    border: 1px solid {C.BORDER};
    color: {C.TEXT_DISABLED};
}}
QTableWidget, QListWidget {{
    background-color: {C.PANEL};
    alternate-background-color: {C.PANEL_ALT};
    gridline-color: {C.BORDER};
    selection-background-color: {C.SELECTION};
    selection-color: {C.TEXT};
    color: {C.TEXT};
    border: 1px solid {C.BORDER};
    border-radius: {RADIUS}px;
    outline: none;
}}
QTableWidget::item, QListWidget::item {{
    padding: 6px;
}}
QTableWidget::item:selected, QListWidget::item:selected {{
    background-color: {C.SELECTION};
    color: {C.TEXT};
}}
QHeaderView::section {{
    background-color: {C.INPUT};
    padding: 8px;
    border: 1px solid {C.BORDER};
    font-weight: bold;
    color: {C.HEADING};
}}
QProgressBar {{
    border: 1px solid {C.BORDER};
    border-radius: {RADIUS}px;
    text-align: center;
    background-color: {C.BG};
    color: {C.TEXT};
    font-weight: bold;
}}
QProgressBar::chunk {{
    background-color: {C.SUCCESS};
    border-radius: {RADIUS - 1}px;
}}
QSpinBox {{
    background-color: {C.INPUT};
    border: 1px solid {C.BORDER};
    padding: 6px;
    border-radius: {RADIUS}px;
    color: {C.TEXT};
    min-height: {INPUT_HEIGHT - 12}px;
}}
QSpinBox:hover {{
    border: 1px solid {C.BORDER_HOVER};
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {C.SELECTION};
    border-radius: 3px;
    margin: 1px;
}}
QCheckBox {{
    background: transparent;
    border: none;
    color: {C.TEXT};
    font-weight: 500;
}}
QCheckBox:disabled {{
    color: {C.TEXT_DISABLED};
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid {C.BORDER_HOVER};
    background-color: {C.INPUT};
}}
QCheckBox::indicator:hover {{
    border: 1px solid {C.ACCENT};
}}
QCheckBox::indicator:checked {{
    background-color: {C.SUCCESS};
    border: 1px solid {C.SUCCESS};
}}
QSlider::groove:horizontal {{
    border: 1px solid {C.BORDER};
    height: 6px;
    background: {C.INPUT};
    margin: 2px 0;
    border-radius: 3px;
}}
QSlider::handle:horizontal {{
    background: {C.ACCENT};
    border: 1px solid {C.ACCENT_HOVER};
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}}
QSlider::handle:horizontal:hover {{
    background: {C.ACCENT_HOVER};
}}
QGroupBox {{
    border: 1px solid {C.BORDER};
    border-radius: {RADIUS}px;
    margin-top: 1.2ex;
    font-weight: bold;
    padding: 12px;
    background-color: {C.PANEL};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 8px;
    background-color: {C.BG};
    color: {C.HEADING};
    border-radius: 4px;
}}
QMenu {{
    background-color: {C.PANEL};
    border: 1px solid {C.BORDER_HOVER};
    color: {C.TEXT};
}}
QMenu::item:selected {{
    background-color: {C.ACCENT_DIM};
    color: {C.TEXT};
}}
QScrollBar:vertical, QScrollBar:horizontal {{
    background-color: {C.BG};
    border: none;
    width: 8px;
    height: 8px;
}}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
    background-color: {C.BORDER};
    border-radius: 4px;
}}
QScrollBar::handle:hover {{
    background-color: {C.ACCENT};
}}
QToolTip {{
    background-color: {C.PANEL_ALT};
    color: {C.TEXT};
    border: 1px solid {C.BORDER_HOVER};
}}
"""

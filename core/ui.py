"""Ortak arayüz parçaları: butonlar, akış düzeni, kaydırılabilir kapsayıcı."""
from PyQt5.QtCore import Qt, QSize, QRect, QPoint
from PyQt5.QtWidgets import (
    QApplication, QPushButton, QSizePolicy, QScrollArea, QFrame, QLayout,
)

from core.theme import C, RADIUS, INPUT_HEIGHT, FONT_FAMILY


class UIScale:
    BUTTON_HEIGHT = 36
    BUTTON_MIN_WIDTH = 100
    ICON_SIZE = 18
    INPUT_HEIGHT = INPUT_HEIGHT
    PADDING = 8
    RADIUS = RADIUS
    FONT_FAMILY = FONT_FAMILY


# Buton rolleri: (arka plan, yazı, kenar)
ROLES = {
    "primary": (C.ACCENT_DIM, C.TEXT, C.ACCENT),
    "success": (C.SUCCESS_DIM, C.TEXT, C.SUCCESS),
    "danger": (C.DANGER_DIM, C.TEXT, C.DANGER),
    "neutral": (C.PANEL_ALT, C.TEXT, C.BORDER),
}


def role_style(role: str) -> str:
    bg, fg, border = ROLES.get(role, ROLES["neutral"])
    return f"background-color: {bg}; color: {fg}; border: 1px solid {border}; font-weight: bold;"


class ModernButton(QPushButton):
    """Yüksekliği yazı boyutuna göre ayarlanan standart buton."""

    def __init__(self, text="", icon=None, tooltip="", parent=None, role=None):
        super().__init__(text, parent)
        if icon:
            self.setIcon(icon)
            self.setIconSize(QSize(UIScale.ICON_SIZE, UIScale.ICON_SIZE))
        if tooltip:
            self.setToolTip(tooltip)
        if role:
            self.setStyleSheet(role_style(role))

        fm = self.fontMetrics()
        self.setMinimumHeight(max(UIScale.BUTTON_HEIGHT, fm.height() + 14))
        self.setMinimumWidth(UIScale.BUTTON_MIN_WIDTH)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


class FlowLayout(QLayout):
    """Alanı daraldığında öğeleri alt satıra saran düzen."""

    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.item_list = []

    def addItem(self, item):
        self.item_list.append(item)

    def count(self):
        return len(self.item_list)

    def itemAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())
        m = self.contentsMargins()
        return size + QSize(m.left() + m.right(), m.top() + m.bottom())

    def _do_layout(self, rect, test_only):
        x, y = rect.x(), rect.y()
        line_height = 0
        spacing = self.spacing()
        for item in self.item_list:
            wid = item.widget()
            space_x = spacing + wid.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
            space_y = spacing + wid.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        return y + line_height - rect.y()


def format_sayi(sayi) -> str:
    """1234567 -> 1.234.567 (Türkçe binlik ayracı)."""
    return f"{int(sayi):,}".replace(",", ".")


def create_scrollable_container(child_widget) -> QScrollArea:
    """Modu şeffaf bir QScrollArea içine alır; küçük ekranlarda taşmayı önler."""
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
    scroll.setWidget(child_widget)
    return scroll


def enable_high_dpi():
    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

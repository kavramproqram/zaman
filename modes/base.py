"""Tüm modların temel sınıfı."""
from PyQt5.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget

from core.theme import C


class ModeBase(QWidget):
    TITLE = "Mod"

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.build_ui()

    def build_ui(self):
        """Arayüzü kurar. Alt sınıflar doldurur."""

    def update_display(self):
        """Yalnızca mod görünürken her saniye çağrılır."""

    def tick(self):
        """Görünürlükten bağımsız, her saniye çağrılır (arka plan işleri için)."""

    def on_shown(self):
        """Mod sekmesi seçildiğinde çağrılır."""


def make_error_mode(name: str, error_text: str):
    """Yüklenemeyen bir modun yerine geçen, hatayı gösteren sekme üretir."""

    class ErrorMode(ModeBase):
        TITLE = f"{name} (yüklenemedi)"

        def build_ui(self):
            layout = QVBoxLayout(self)
            label = QLabel(f"'{name}' modu yüklenemedi. Aşağıdaki hatayı düzeltin:")
            label.setStyleSheet(f"color: {C.WARN}; font-weight: bold;")
            layout.addWidget(label)
            box = QTextEdit()
            box.setReadOnly(True)
            box.setPlainText(error_text)
            layout.addWidget(box)

    return ErrorMode

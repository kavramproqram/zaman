"""Pencere yöneticisi: mod listesini yükler, sekmeleri yönetir, tepsi ve global zamanlayıcıyı çalıştırır."""
import os
import sys

os.environ.setdefault(
    "QT_LOGGING_RULES",
    "qt.*=false;*.debug=false;qt.x11.*=false;qt.qpa.*=false;qt.accessibility.*=false",
)

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QAction, QApplication, QComboBox, QFrame, QHBoxLayout, QLabel, QMainWindow,
    QMenu, QSizePolicy, QStackedWidget, QSystemTrayIcon, QVBoxLayout, QWidget,
)

from core.paths import ICON_PATH
from core.pomodoro_engine import PomodoroEngine
from core.storage import db
from core.theme import DARK_STYLE
from core.ui import create_scrollable_container, enable_high_dpi
import modes


class AppContext:
    """Modların ihtiyaç duyduğu ortak servisler. Modlar doğrudan pencereye bağlanmaz."""

    def __init__(self):
        self.db = db
        self.pomodoro = PomodoroEngine()
        self.pomodoro.on_alarm_callback = self._on_pomodoro_alarm
        self._tray = None
        self._notes_listeners = []

    # Notlar değiştiğinde açık olan Not sekmesini yenilemek için
    def add_notes_listener(self, callback):
        self._notes_listeners.append(callback)

    def notes_changed(self):
        for cb in self._notes_listeners:
            cb()

    def notify(self, title: str, message: str, ms: int = 5000):
        if self._tray is not None:
            self._tray.showMessage(title, message, QSystemTrayIcon.Information, ms)

    def _on_pomodoro_alarm(self, old_phase, new_phase):
        if db.data["settings"].get("pomodoro", {}).get("show_notification", True):
            self.notify("Pomodoro Zamanlayıcı", f"{old_phase} tamamlandı! Yeni evre: {new_phase}")


class MainWindow(QMainWindow):
    def __init__(self, ctx: AppContext):
        super().__init__()
        self.ctx = ctx
        self.setWindowTitle("Zaman")
        self.setMinimumSize(920, 620)
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))
        self.setStyleSheet(DARK_STYLE)

        self.mode_instances = []   # sıralı mod örnekleri
        self._build_ui()
        self._build_tray()

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.global_tick)
        self.timer.start()

    # ---- arayüz ----
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        top_bar = QFrame()
        top_layout = QHBoxLayout(top_bar)
        label = QLabel("Çalışma Modu:")
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        top_layout.addWidget(label)

        self.mode_combo = QComboBox()
        self.mode_combo.setMinimumHeight(38)
        self.mode_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        font = QFont()
        font.setBold(True)
        font.setPointSize(11)
        self.mode_combo.setFont(font)
        top_layout.addWidget(self.mode_combo, 1)
        layout.addWidget(top_bar)

        self.stack = QStackedWidget()
        for index, (module_name, mode_cls) in enumerate(modes.load_modes()):
            instance = mode_cls(self.ctx)
            self.mode_instances.append(instance)
            self.stack.addWidget(create_scrollable_container(instance))
            self.mode_combo.addItem(f"Mod {index}: {instance.TITLE}")

        self.mode_combo.currentIndexChanged.connect(self.change_mode)
        layout.addWidget(self.stack)
        self.change_mode(0)

    def _build_tray(self):
        self._tray = None
        if os.path.exists(ICON_PATH):
            self._tray = QSystemTrayIcon(QIcon(ICON_PATH), self)
            menu = QMenu()
            show_action = QAction("Göster / Gizle", self)
            show_action.triggered.connect(self.toggle_window)
            quit_action = QAction("Çıkış", self)
            quit_action.triggered.connect(QApplication.instance().quit)
            menu.addAction(show_action)
            menu.addAction(quit_action)
            self._tray.setContextMenu(menu)
            self._tray.show()
        self.ctx._tray = self._tray

    def toggle_window(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()

    # ---- mod yönetimi ----
    def change_mode(self, index):
        if index < 0:
            return
        self.stack.setCurrentIndex(index)
        instance = self.mode_instances[index]
        if hasattr(instance, "on_shown"):
            instance.on_shown()
        self.global_tick()

    def global_tick(self):
        """Her saniye: Pomodoro ve arka plan modları çalışır, görünen mod ekranı yenilenir."""
        self.ctx.pomodoro.tick()
        for mode in self.mode_instances:
            mode.tick()
        current = self.stack.currentWidget()
        if current is not None:
            child = current.widget() if hasattr(current, "widget") else current
            if hasattr(child, "update_display"):
                child.update_display()


def main(argv) -> int:
    enable_high_dpi()
    app = QApplication(argv)
    app.setStyle("Fusion")
    app.setQuitOnLastWindowClosed(False)

    ctx = AppContext()
    window = MainWindow(ctx)
    start_hidden = any(a in ("--startupHidden=true", "--startupHidden") for a in argv[1:])
    if not start_hidden:
        window.show()
    elif ctx._tray is None:
        window.show()   # tepsi yoksa pencereyi gizlemek uygulamayı erişilemez yapar
    return app.exec_()

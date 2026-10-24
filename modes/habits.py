"""Mod 9: Alışkanlık takibi (40 günlük döngü)."""
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QCursor
from PyQt5.QtWidgets import (
    QFrame, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMenu, QMessageBox,
    QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from core.storage import get_now
from core.theme import C
from core.ui import FlowLayout, ModernButton
from modes.base import ModeBase

CYCLE_DAYS = 40


def get_habit_progress(habit) -> int:
    """Alışkanlığın kaçıncı gününde olduğunu döndürür (1-40)."""
    start = datetime.strptime(habit["start_date"], "%Y-%m-%d").date()
    delta = (get_now().date() - start).days
    return min(delta + 1, CYCLE_DAYS)


class Mode(ModeBase):
    TITLE = "Alışkanlık Takibi"

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        add_frame = QFrame()
        add_layout = QHBoxLayout(add_frame)
        add_layout.setContentsMargins(8, 8, 8, 8)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Alışkanlık adı yazın...")
        self.name_input.returnPressed.connect(self.add_habit)
        add_layout.addWidget(self.name_input, 3)
        self.start_btn = ModernButton("Başla", tooltip="Yeni alışkanlık takibini başlat", role="success")
        self.start_btn.clicked.connect(self.add_habit)
        add_layout.addWidget(self.start_btn, 1)
        layout.addWidget(add_frame)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(20)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

        self.update_display()

    def add_habit(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir alışkanlık adı girin.")
            return
        self.ctx.db.add_habit(name)
        self.name_input.clear()
        self.update_display()

    def delete_habit(self, habit_id):
        self.ctx.db.delete_habit(habit_id)
        self.update_display()

    def toggle_failed(self, habit_id, day_index):
        self.ctx.db.toggle_failed(habit_id, day_index)
        self.update_display()

    def update_display(self):
        for i in reversed(range(self.container_layout.count())):
            item = self.container_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

        habits = self.ctx.db.data.get("habits", [])
        if not habits:
            empty = QLabel("Henüz hiç alışkanlık takibi başlatılmamış.\nYukarıdan yeni bir alışkanlık ekleyin.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(f"color: {C.TEXT_MUTED}; font-size: 14px; padding: 40px;")
            self.container_layout.addWidget(empty)
            return

        for habit in habits:
            self.container_layout.addWidget(self._create_habit_card(habit))

    def _create_habit_card(self, habit):
        group = QGroupBox()
        group.setTitle(habit["name"])
        group.setStyleSheet(f"QGroupBox::title {{ color: {C.HEADING}; }}")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        days = get_habit_progress(habit)
        info = QHBoxLayout()
        day_label = QLabel(f"Gün {days} / {CYCLE_DAYS}")
        day_label.setStyleSheet(f"font-weight: bold; color: {C.TEXT};")
        info.addWidget(day_label, 1)

        now = get_now()
        end_of_day = now.replace(hour=23, minute=59, second=59)
        remaining = end_of_day - now
        if remaining.total_seconds() > 0:
            rem_text = f"Kalan: {remaining.seconds // 3600:02d}:{(remaining.seconds % 3600) // 60:02d}:{remaining.seconds % 60:02d}"
        else:
            rem_text = "Gün bitti"
        rem_label = QLabel(rem_text)
        rem_label.setStyleSheet(f"color: {C.TEXT_MUTED};")
        info.addWidget(rem_label, 1)
        layout.addLayout(info)

        flow = FlowLayout(spacing=6)
        failed = habit.get("failed", [])
        for i in range(CYCLE_DAYS):
            btn = QPushButton(str(i + 1))
            btn.setFixedSize(60, 60)
            if i < days:
                if i in failed:
                    btn.setStyleSheet(
                        f"border-radius: 18px; background-color: #2A2D33; color: {C.TEXT_DISABLED};"
                        f" border: 1px solid {C.BORDER};"
                    )
                else:
                    # Günlere sabit, orta tonlu renkler: aynı gün her zaman aynı renk
                    hue = int((i * 360 / CYCLE_DAYS) % 360)
                    color = QColor.fromHsv(hue, 110, 165)
                    btn.setStyleSheet(
                        f"border-radius: 18px; background-color: {color.name()}; color: {C.TEXT}; border: none;"
                    )
            else:
                btn.setStyleSheet(
                    f"border-radius: 18px; background-color: {C.PANEL}; color: {C.TEXT_DISABLED};"
                    f" border: 1px solid {C.BORDER};"
                )
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(
                lambda pos, hid=habit["id"], idx=i: self._show_context_menu(hid, idx)
            )
            flow.addWidget(btn)
        layout.addLayout(flow)

        if days >= CYCLE_DAYS:
            fail_n = len(failed)
            success = CYCLE_DAYS - fail_n
            stats = f"Başarılı: {success}, Başarısız: {fail_n}"
            if success >= 30:
                stats += " 🎉 Tebrikler!"
            stats_label = QLabel(stats)
            stats_label.setStyleSheet(f"color: {C.TEXT}; font-weight: bold; padding: 4px;")
            stats_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(stats_label)

        del_btn = ModernButton("Alışkanlığı Sil", tooltip="Bu alışkanlık takibini sil", role="danger")
        del_btn.clicked.connect(lambda: self.delete_habit(habit["id"]))
        layout.addWidget(del_btn, alignment=Qt.AlignRight)
        return group

    def _show_context_menu(self, habit_id, day_index):
        habit = next((h for h in self.ctx.db.data.get("habits", []) if h["id"] == habit_id), None)
        if not habit:
            return
        menu = QMenu()
        label = "Normal Yap (başarılı)" if day_index in habit.get("failed", []) else "Siyah Yap (başarısız)"
        action = menu.addAction(label)
        action.triggered.connect(lambda: self.toggle_failed(habit_id, day_index))
        menu.exec_(QCursor.pos())

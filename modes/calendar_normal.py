"""Mod 3: Normal takvim ve 12 saatlik gün ilerlemesi."""
import calendar

from PyQt5.QtCore import Qt, QLocale
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QAbstractItemView, QFrame, QHBoxLayout, QHeaderView, QLabel, QMessageBox,
    QProgressBar, QTableWidget, QTableWidgetItem, QVBoxLayout,
)

from core.storage import get_now
from core.theme import C
from core.ui import ModernButton
from modes.base import ModeBase


class Mode(ModeBase):
    TITLE = "Normal Takvim"

    def build_ui(self):
        now = get_now()
        self.view_year, self.view_month = now.year, now.month
        layout = QVBoxLayout(self)

        clock_frame = QFrame()
        clock_layout = QVBoxLayout(clock_frame)
        self.digital_clock = QLabel("00:00:00")
        self.digital_clock.setAlignment(Qt.AlignCenter)
        f = QFont(); f.setPointSize(28); f.setBold(True)
        self.digital_clock.setFont(f)
        self.digital_clock.setStyleSheet(f"color: {C.TEXT}; border: none;")
        clock_layout.addWidget(self.digital_clock)

        half = QHBoxLayout()
        self.first_half_bar = QProgressBar()
        self.first_half_bar.setFormat("İlk 12 Saat %p%")
        half.addWidget(self.first_half_bar, 1)
        self.second_half_bar = QProgressBar()
        self.second_half_bar.setFormat("Son 12 Saat %p%")
        half.addWidget(self.second_half_bar, 1)
        clock_layout.addLayout(half)
        layout.addWidget(clock_frame)

        nav = QFrame()
        nav_layout = QHBoxLayout(nav)
        self.btn_prev = ModernButton("◀ Önceki Ay", tooltip="Bir Önceki Aya Git")
        self.btn_prev.clicked.connect(self.prev_month)
        nav_layout.addWidget(self.btn_prev, 1)
        self.header_label = QLabel()
        self.header_label.setAlignment(Qt.AlignCenter)
        h = QFont(); h.setPointSize(14); h.setBold(True)
        self.header_label.setFont(h)
        nav_layout.addWidget(self.header_label, 2)
        self.btn_today = ModernButton("Bugün", tooltip="Bugünün Tarihine Git")
        self.btn_today.clicked.connect(self.go_today)
        nav_layout.addWidget(self.btn_today, 1)
        self.btn_next = ModernButton("Sonraki Ay ▶", tooltip="Bir Sonraki Aya Git")
        self.btn_next.clicked.connect(self.next_month)
        nav_layout.addWidget(self.btn_next, 1)
        layout.addWidget(nav)

        self.table = QTableWidget(6, 7)
        headers = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
        for col, name in enumerate(headers):
            item = QTableWidgetItem(name)
            if col in (5, 6):
                item.setForeground(QColor(C.DANGER))
                fb = QFont(); fb.setBold(True); item.setFont(fb)
            else:
                item.setForeground(QColor(C.HEADING))
            self.table.setHorizontalHeaderItem(col, item)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.cellClicked.connect(self.cell_clicked)
        layout.addWidget(self.table)
        self.render_month()

    def prev_month(self):
        self.view_month -= 1
        if self.view_month < 1:
            self.view_month, self.view_year = 12, self.view_year - 1
        self.render_month()

    def next_month(self):
        self.view_month += 1
        if self.view_month > 12:
            self.view_month, self.view_year = 1, self.view_year + 1
        self.render_month()

    def go_today(self):
        now = get_now()
        self.view_year, self.view_month = now.year, now.month
        self.render_month()

    def render_month(self):
        m_name = QLocale(QLocale.Turkish).monthName(self.view_month)
        self.header_label.setText(f"{m_name.capitalize()} {self.view_year}")
        cal = calendar.monthcalendar(self.view_year, self.view_month)
        self.table.clearContents()
        now = get_now()
        tasks = self.ctx.db.data["tasks"]

        for r in range(6):
            week = cal[r] if r < len(cal) else [0] * 7
            for c in range(7):
                day = week[c]
                if day == 0:
                    continue
                item = QTableWidgetItem(str(day))
                item.setTextAlignment(Qt.AlignCenter)
                d_str = f"{self.view_year}-{self.view_month:02d}-{day:02d}"
                has_task = any(t["date"] == d_str for t in tasks)

                if self.view_year == now.year and self.view_month == now.month and day == now.day:
                    item.setBackground(QColor(C.ACCENT_DIM))
                    item.setForeground(QColor(C.TEXT))
                    fb = QFont(); fb.setBold(True); item.setFont(fb)
                elif has_task:
                    item.setBackground(QColor(C.SUCCESS_DIM))
                    item.setForeground(QColor(C.TEXT))
                elif c in (5, 6):
                    item.setForeground(QColor(C.DANGER))
                else:
                    item.setForeground(QColor(C.TEXT))
                self.table.setItem(r, c, item)

    def cell_clicked(self, row, col):
        item = self.table.item(row, col)
        if not (item and item.text()):
            return
        day = int(item.text())
        d_str = f"{self.view_year}-{self.view_month:02d}-{day:02d}"
        tasks = [t for t in self.ctx.db.data["tasks"] if t["date"] == d_str]
        msg = f"{day} {QLocale(QLocale.Turkish).monthName(self.view_month)} {self.view_year}\n\n"
        if tasks:
            msg += "Görevler:\n" + "\n".join(f"- [{t['priority']}] {t['title']}" for t in tasks)
        else:
            msg += "Bu tarihe ait görev yok."
        QMessageBox.information(self, "Gün Detayı", msg)

    def update_display(self):
        now = get_now()
        self.digital_clock.setText(now.strftime("%H:%M:%S"))
        hour, minute = now.hour, now.minute
        if hour < 12:
            v1, v2 = int(((hour * 60) + minute) / 720 * 100), 0
        else:
            v1, v2 = 100, int((((hour - 12) * 60) + minute) / 720 * 100)
        self.first_half_bar.setValue(v1)
        self.second_half_bar.setValue(v2)

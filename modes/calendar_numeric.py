"""Mod 4: Rakamlı takvim (ay/gün numaraları)."""
import calendar

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QAbstractItemView, QFrame, QHBoxLayout, QHeaderView, QLabel, QTableWidget,
    QTableWidgetItem, QVBoxLayout,
)

from core.storage import get_now
from core.theme import C
from core.ui import ModernButton
from modes.base import ModeBase


class Mode(ModeBase):
    TITLE = "Rakamlı Takvim"

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
        layout.addWidget(clock_frame)

        nav = QFrame()
        nav_layout = QHBoxLayout(nav)
        self.btn_prev = ModernButton("◀ Önceki Ay", tooltip="Bir Önceki Aya Git")
        self.btn_prev.clicked.connect(self.prev_month)
        nav_layout.addWidget(self.btn_prev, 1)
        self.month_year_label = QLabel()
        self.month_year_label.setAlignment(Qt.AlignCenter)
        h = QFont(); h.setPointSize(14); h.setBold(True)
        self.month_year_label.setFont(h)
        nav_layout.addWidget(self.month_year_label, 2)
        self.btn_today = ModernButton("Bugün", tooltip="Bugünün Tarihine Git")
        self.btn_today.clicked.connect(self.go_today)
        nav_layout.addWidget(self.btn_today, 1)
        self.btn_next = ModernButton("Sonraki Ay ▶", tooltip="Bir Sonraki Aya Git")
        self.btn_next.clicked.connect(self.next_month)
        nav_layout.addWidget(self.btn_next, 1)
        layout.addWidget(nav)

        self.table = QTableWidget(6, 7)
        for col, name in enumerate(["1", "2", "3", "4", "5", "6", "7"]):
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
        self.month_year_label.setText(f"Ay {self.view_month}, Yıl {self.view_year}")
        cal = calendar.monthcalendar(self.view_year, self.view_month)
        self.table.clearContents()
        now = get_now()
        for r in range(6):
            week = cal[r] if r < len(cal) else [0] * 7
            for c in range(7):
                day = week[c]
                if day == 0:
                    continue
                item = QTableWidgetItem(str(day))
                item.setTextAlignment(Qt.AlignCenter)
                if self.view_year == now.year and self.view_month == now.month and day == now.day:
                    item.setBackground(QColor(C.ACCENT_DIM))
                    item.setForeground(QColor(C.TEXT))
                    fb = QFont(); fb.setBold(True); item.setFont(fb)
                elif c in (5, 6):
                    item.setForeground(QColor(C.DANGER))
                else:
                    item.setForeground(QColor(C.TEXT))
                self.table.setItem(r, c, item)

    def update_display(self):
        self.digital_clock.setText(get_now().strftime("%H:%M:%S"))

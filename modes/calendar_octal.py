"""Mod 5: Sekizli takvim (yılı 9 ay x 40 gün olarak böler, 8 sütunlu ızgara)."""
import calendar

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QAbstractItemView, QCheckBox, QFrame, QHBoxLayout, QHeaderView, QLabel, QSpinBox,
    QTableWidget, QTableWidgetItem, QVBoxLayout,
)

from core.storage import get_now
from core.theme import C
from core.ui import ModernButton
from modes.base import ModeBase


class Mode(ModeBase):
    TITLE = "Sekizli Takvim"

    def build_ui(self):
        settings = self.ctx.db.data["settings"]
        self.show_seconds = settings.get("mod3_show_seconds", False)
        self.seg1_start = settings.get("mod3_seg1", 0)
        self.seg2_start = settings.get("mod3_seg2", 8)
        self.seg3_start = settings.get("mod3_seg3", 11)
        self.view_year = get_now().year
        self.view_month = self.get_current_octal_month()

        layout = QVBoxLayout(self)

        clock_frame = QFrame()
        clock_layout = QVBoxLayout(clock_frame)
        self.small_clock = QLabel("00:00:00")
        self.small_clock.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.small_clock.setStyleSheet(f"color: {C.TEXT_MUTED}; border: none;")
        clock_layout.addWidget(self.small_clock)

        self.segment_label = QLabel("1. Bölüm - 0:00")
        self.segment_label.setAlignment(Qt.AlignCenter)
        f = QFont(); f.setPointSize(28); f.setBold(True)
        self.segment_label.setFont(f)
        self.segment_label.setStyleSheet(f"color: {C.SUCCESS}; border: none;")
        clock_layout.addWidget(self.segment_label)

        self.sec_check = QCheckBox("Saniyeyi Göster")
        self.sec_check.setChecked(self.show_seconds)
        self.sec_check.toggled.connect(self.toggle_seconds)
        clock_layout.addWidget(self.sec_check, 0, Qt.AlignHCenter)
        layout.addWidget(clock_frame)

        seg = QFrame()
        seg_layout = QHBoxLayout(seg)
        self.spin_seg1 = self._seg_spin("1. Bölüm:", self.seg1_start, seg_layout)
        self.spin_seg2 = self._seg_spin("2. Bölüm:", self.seg2_start, seg_layout)
        self.spin_seg3 = self._seg_spin("3. Bölüm:", self.seg3_start, seg_layout)
        layout.addWidget(seg)

        nav = QFrame()
        nav_layout = QHBoxLayout(nav)
        self.btn_prev = ModernButton("◀ Önceki Ay", tooltip="Bir Önceki Sekizli Aya Git")
        self.btn_prev.clicked.connect(self.prev_month)
        nav_layout.addWidget(self.btn_prev, 1)
        self.month_info_label = QLabel()
        self.month_info_label.setAlignment(Qt.AlignCenter)
        h = QFont(); h.setPointSize(14); h.setBold(True)
        self.month_info_label.setFont(h)
        nav_layout.addWidget(self.month_info_label, 2)
        self.btn_today = ModernButton("Bugün", tooltip="Bugünün Tarihine Git")
        self.btn_today.clicked.connect(self.go_today)
        nav_layout.addWidget(self.btn_today, 1)
        self.btn_next = ModernButton("Sonraki Ay ▶", tooltip="Bir Sonraki Sekizli Aya Git")
        self.btn_next.clicked.connect(self.next_month)
        nav_layout.addWidget(self.btn_next, 1)
        layout.addWidget(nav)

        self.grid_table = QTableWidget(5, 8)
        for col in range(8):
            item = QTableWidgetItem(str(col + 1))
            if col in (5, 6, 7):
                item.setForeground(QColor(C.DANGER))
                fb = QFont(); fb.setBold(True); item.setFont(fb)
            else:
                item.setForeground(QColor(C.HEADING))
            self.grid_table.setHorizontalHeaderItem(col, item)
        self.grid_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.grid_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.grid_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.grid_table)
        self.update_calendar_grid()

    def _seg_spin(self, label, value, layout):
        layout.addWidget(QLabel(label))
        spin = QSpinBox()
        spin.setRange(0, 23)
        spin.setValue(value)
        spin.valueChanged.connect(self.save_segments)
        layout.addWidget(spin, 1)
        return spin

    def get_current_octal_month(self):
        doy = get_now().timetuple().tm_yday
        return min(((doy - 1) // 40) + 1, 9)

    def save_segments(self):
        self.seg1_start = self.spin_seg1.value()
        self.seg2_start = self.spin_seg2.value()
        self.seg3_start = self.spin_seg3.value()
        s = self.ctx.db.data["settings"]
        s["mod3_seg1"], s["mod3_seg2"], s["mod3_seg3"] = self.seg1_start, self.seg2_start, self.seg3_start
        self.ctx.db.save()

    def toggle_seconds(self, checked):
        self.show_seconds = checked
        self.ctx.db.data["settings"]["mod3_show_seconds"] = checked
        self.ctx.db.save()

    def prev_month(self):
        self.view_month -= 1
        if self.view_month < 1:
            self.view_month, self.view_year = 9, self.view_year - 1
        self.update_calendar_grid()

    def next_month(self):
        self.view_month += 1
        if self.view_month > 9:
            self.view_month, self.view_year = 1, self.view_year + 1
        self.update_calendar_grid()

    def go_today(self):
        self.view_year = get_now().year
        self.view_month = self.get_current_octal_month()
        self.update_calendar_grid()

    def update_calendar_grid(self):
        self.month_info_label.setText(f"Sekizli Ay: {self.view_month}, Yıl: {self.view_year}")
        days_in_year = 366 if calendar.isleap(self.view_year) else 365
        days_in_this_month = 40 if self.view_month < 9 else days_in_year - 320

        self.grid_table.clearContents()
        rows = (days_in_this_month + 7) // 8
        self.grid_table.setRowCount(rows)
        self.grid_table.setVerticalHeaderLabels([str(i + 1) for i in range(rows)])

        now = get_now()
        current_doy = now.timetuple().tm_yday
        current_oct_month = self.get_current_octal_month()
        current_oct_day = ((current_doy - 1) % 40) + 1 if current_oct_month < 9 else current_doy - 320

        for r in range(rows):
            for c in range(8):
                gun_no = r * 8 + c + 1
                if gun_no > days_in_this_month:
                    continue
                item = QTableWidgetItem(str(gun_no))
                item.setTextAlignment(Qt.AlignCenter)
                if self.view_year == now.year and self.view_month == current_oct_month and gun_no == current_oct_day:
                    item.setBackground(QColor(C.ACCENT_DIM))
                    item.setForeground(QColor(C.TEXT))
                    fb = QFont(); fb.setBold(True); item.setFont(fb)
                elif c in (5, 6, 7) or r >= 5:
                    item.setForeground(QColor(C.DANGER))
                else:
                    item.setForeground(QColor(C.TEXT))
                self.grid_table.setItem(r, c, item)

    def update_display(self):
        now = get_now()
        self.small_clock.setText(now.strftime("%H:%M:%S"))
        hour, minute, second = now.hour, now.minute, now.second

        times = sorted([(self.seg1_start, 1), (self.seg2_start, 2), (self.seg3_start, 3)], reverse=True)
        current_seg, seg_start_hour = times[-1][1], times[-1][0]
        for start_h, seg_idx in times:
            if hour >= start_h:
                current_seg, seg_start_hour = seg_idx, start_h
                break

        seg_hour = (hour - seg_start_hour) % 24
        text = f"{current_seg}. Bölüm  |  {seg_hour}:{minute:02d}"
        if self.show_seconds:
            text += f":{second:02d}"
        self.segment_label.setText(text)

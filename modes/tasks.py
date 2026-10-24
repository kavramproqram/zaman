"""Mod 1: Görev / Planlayıcı."""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QAbstractItemView, QCheckBox, QComboBox, QFrame, QHBoxLayout, QHeaderView,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from core.storage import get_now
from core.theme import C
from core.ui import ModernButton
from modes.base import ModeBase

PRIO_ICON = {"Yüksek": "[!]", "Orta": "[-]", "Düşük": "[o]"}


class Mode(ModeBase):
    TITLE = "Görev / Planlayıcı"

    def build_ui(self):
        layout = QVBoxLayout(self)

        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(8, 8, 8, 8)

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Yeni görev tanımı yazın...")
        self.task_input.returnPressed.connect(self.add_task)
        input_layout.addWidget(self.task_input, 3)

        self.prio_combo = QComboBox()
        self.prio_combo.addItems(["Yüksek", "Orta", "Düşük"])
        self.prio_combo.setCurrentIndex(1)
        input_layout.addWidget(self.prio_combo, 1)

        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("Tarih (YYYY-AA-GG)")
        self.date_input.setText(get_now().strftime("%Y-%m-%d"))
        self.date_input.setMinimumWidth(100)
        input_layout.addWidget(self.date_input, 1)

        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("Saat (SS:DD)")
        self.time_input.setMinimumWidth(80)
        input_layout.addWidget(self.time_input, 1)

        self.add_btn = ModernButton("+ Ekle", tooltip="Yeni Görev Ekle", role="success")
        self.add_btn.clicked.connect(self.add_task)
        input_layout.addWidget(self.add_btn, 1)
        layout.addWidget(input_frame)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Durum", "Öncelik", "Görev Başlığı", "Tarih/Saat", "Pomodoro", "İşlem"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(5, 75)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)

        self.refresh_tasks()

    def add_task(self):
        title = self.task_input.text().strip()
        if not title:
            return
        prio = ["Yüksek", "Orta", "Düşük"][self.prio_combo.currentIndex()]
        self.ctx.db.add_task(title, prio, self.date_input.text().strip(), self.time_input.text().strip())
        self.task_input.clear()
        self.refresh_tasks()

    def refresh_tasks(self):
        db = self.ctx.db
        self.table.setRowCount(0)
        for task in db.data["tasks"]:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 36)

            chk = QCheckBox()
            chk.setChecked(task["completed"])
            chk.toggled.connect(lambda _, tid=task["id"]: self.toggle_task(tid))
            chk_widget = QWidget()
            l = QHBoxLayout(chk_widget)
            l.addWidget(chk)
            l.setAlignment(Qt.AlignCenter)
            l.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 0, chk_widget)

            p_item = QTableWidgetItem(f"{PRIO_ICON.get(task['priority'], '')} {task['priority']}")
            p_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, p_item)

            t_item = QTableWidgetItem(task["title"])
            if task["completed"]:
                font = t_item.font()
                font.setStrikeOut(True)
                t_item.setFont(font)
                t_item.setForeground(QColor(C.TEXT_MUTED))
            self.table.setItem(row, 2, t_item)

            dt_str = f"{task['date']} {task['time']}".strip()
            dt_item = QTableWidgetItem(dt_str if dt_str else "-")
            dt_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, dt_item)

            pomo_item = QTableWidgetItem(f"Pomo: {task['pomodoro_sessions']}")
            pomo_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, pomo_item)

            btn_container = QWidget()
            btn_lay = QHBoxLayout(btn_container)
            btn_lay.setContentsMargins(2, 2, 2, 2)
            btn_lay.setAlignment(Qt.AlignCenter)
            del_btn = QPushButton("Sil")
            del_btn.setFixedSize(55, 26)
            del_btn.setToolTip("Görevi Sil")
            del_btn.setStyleSheet(
                f"QPushButton {{ background-color: {C.DANGER_DIM}; color: {C.TEXT};"
                f" border: 1px solid {C.DANGER}; border-radius: 4px; font-weight: bold; font-size: 11px; }}"
                f"QPushButton:hover {{ background-color: {C.DANGER}; }}"
            )
            del_btn.clicked.connect(lambda _, tid=task["id"]: self.delete_task(tid))
            btn_lay.addWidget(del_btn)
            self.table.setCellWidget(row, 5, btn_container)

    def toggle_task(self, task_id):
        self.ctx.db.toggle_task(task_id)
        self.refresh_tasks()

    def delete_task(self, task_id):
        self.ctx.db.delete_task(task_id)
        self.refresh_tasks()

    def on_shown(self):
        self.refresh_tasks()

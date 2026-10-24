"""Mod 0: Pomodoro zamanlayıcı."""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QCheckBox, QComboBox, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QProgressBar, QSizePolicy, QSlider, QSpinBox, QVBoxLayout,
)

from core.theme import C
from core.ui import ModernButton
from modes.base import ModeBase

PHASE_COLORS = {"Çalışma": C.SUCCESS, "Kısa Mola": C.ACCENT, "Uzun Mola": C.WARN}


class Mode(ModeBase):
    TITLE = "Pomodoro"

    def build_ui(self):
        engine = self.ctx.pomodoro
        engine.tick_signal.connect(self.update_display)
        db = self.ctx.db
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        display_frame = QFrame()
        display_layout = QVBoxLayout(display_frame)

        self.phase_label = QLabel(engine.phase)
        self.phase_label.setAlignment(Qt.AlignCenter)
        f = QFont(); f.setPointSize(16); f.setBold(True)
        self.phase_label.setFont(f)
        display_layout.addWidget(self.phase_label)

        self.time_label = QLabel("25:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        f = QFont(); f.setPointSize(44); f.setBold(True)
        self.time_label.setFont(f)
        display_layout.addWidget(self.time_label)

        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setMinimumHeight(10)
        display_layout.addWidget(self.progress)
        layout.addWidget(display_frame)

        task_frame = QFrame()
        task_layout = QHBoxLayout(task_frame)
        task_layout.setContentsMargins(8, 4, 8, 4)
        task_lbl = QLabel("Göreve Bağla:")
        task_lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        task_layout.addWidget(task_lbl)
        self.task_combo = QComboBox()
        self.task_combo.setMinimumHeight(38)
        self.task_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.task_combo.currentIndexChanged.connect(self.on_task_selected)
        task_layout.addWidget(self.task_combo, 1)
        layout.addWidget(task_frame)

        btn_layout = QHBoxLayout()
        self.start_btn = ModernButton("▶ Başlat / Duraklat", tooltip="Zamanlayıcıyı Başlat/Duraklat", role="primary")
        self.start_btn.clicked.connect(engine.start_or_pause)
        btn_layout.addWidget(self.start_btn, 1)
        self.reset_btn = ModernButton("↺ Sıfırla", tooltip="Süreyi Sıfırla")
        self.reset_btn.clicked.connect(engine.reset)
        btn_layout.addWidget(self.reset_btn, 1)
        layout.addLayout(btn_layout)

        sound_gb = QGroupBox("Zil ve Ses Ayarları")
        grid = QGridLayout(sound_gb)
        grid.setSpacing(8)
        cfg = db.data["settings"].get("pomodoro", {})

        self.sound_check = QCheckBox("Zil Sesi Açık")
        self.sound_check.setChecked(cfg.get("sound_enabled", True))
        self.sound_check.toggled.connect(self.save_sound_settings)
        grid.addWidget(self.sound_check, 0, 0)

        self.work_sound_check = QCheckBox("Çalışma Bitince Ses")
        self.work_sound_check.setChecked(cfg.get("sound_work_end", True))
        self.work_sound_check.toggled.connect(self.save_sound_settings)
        grid.addWidget(self.work_sound_check, 0, 1)

        self.break_sound_check = QCheckBox("Mola Bitince Ses")
        self.break_sound_check.setChecked(cfg.get("sound_break_end", True))
        self.break_sound_check.toggled.connect(self.save_sound_settings)
        grid.addWidget(self.break_sound_check, 0, 2)

        self.notif_check = QCheckBox("Masaüstü Bildirimi")
        self.notif_check.setChecked(cfg.get("show_notification", True))
        self.notif_check.toggled.connect(self.save_sound_settings)
        grid.addWidget(self.notif_check, 1, 0)

        grid.addWidget(QLabel("Ses Seviyesi:"), 1, 1)
        self.vol_slider = QSlider(Qt.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(cfg.get("volume", 85))
        self.vol_slider.valueChanged.connect(self.save_sound_settings)
        grid.addWidget(self.vol_slider, 1, 2)

        dur = QHBoxLayout()
        dur.addWidget(QLabel("Çalışma (dk):"))
        self.work_spin = self._duration_spin(1, 120, engine.work_sec // 60)
        dur.addWidget(self.work_spin, 1)
        dur.addWidget(QLabel("Kısa Mola:"))
        self.short_spin = self._duration_spin(1, 60, engine.short_break_sec // 60)
        dur.addWidget(self.short_spin, 1)
        dur.addWidget(QLabel("Uzun Mola:"))
        self.long_spin = self._duration_spin(1, 120, engine.long_break_sec // 60)
        dur.addWidget(self.long_spin, 1)
        grid.addLayout(dur, 2, 0, 1, 3)
        layout.addWidget(sound_gb)

        quick = QFrame()
        qn = QHBoxLayout(quick)
        qn.setContentsMargins(8, 6, 8, 6)
        self.qn_input = QLineEdit()
        self.qn_input.setPlaceholderText("Hızlı bir not yazın... (Notlar sekmesine kaydedilir)")
        self.qn_input.returnPressed.connect(self.add_quick_note)
        qn.addWidget(self.qn_input, 3)
        self.qn_btn = ModernButton("+ Not Ekle", tooltip="Notlar Sekmesine Hızlı Not Ekle", role="success")
        self.qn_btn.clicked.connect(self.add_quick_note)
        qn.addWidget(self.qn_btn, 1)
        layout.addWidget(quick)
        layout.addStretch()

        self.refresh_task_combo()

    def _duration_spin(self, lo, hi, value):
        spin = QSpinBox()
        spin.setRange(lo, hi)
        spin.setValue(value)
        spin.valueChanged.connect(self.on_durations_changed)
        return spin

    # ---- görevler ----
    def refresh_task_combo(self):
        db = self.ctx.db
        self.task_combo.blockSignals(True)
        self.task_combo.clear()
        self.task_combo.addItem("--- Bağımsız Pomodoro ---", None)
        active_id = db.data["settings"].get("pomodoro", {}).get("active_task_id")
        sel_idx = 0
        for task in db.data["tasks"]:
            if not task["completed"]:
                txt = f"[{task['priority']}] {task['title']} (Pomo: {task['pomodoro_sessions']})"
                self.task_combo.addItem(txt, task["id"])
                if task["id"] == active_id:
                    sel_idx = self.task_combo.count() - 1
        self.task_combo.setCurrentIndex(sel_idx)
        self.task_combo.blockSignals(False)

    def on_task_selected(self, index):
        db = self.ctx.db
        db.data["settings"]["pomodoro"]["active_task_id"] = self.task_combo.itemData(index)
        db.save()

    def on_shown(self):
        self.refresh_task_combo()

    # ---- ayarlar ----
    def add_quick_note(self):
        txt = self.qn_input.text().strip()
        if txt:
            self.ctx.db.add_keep_note("Pomodoro Notu", txt)
            self.qn_input.clear()
            self.ctx.notes_changed()

    def save_sound_settings(self):
        cfg = self.ctx.db.data["settings"]["pomodoro"]
        cfg["sound_enabled"] = self.sound_check.isChecked()
        cfg["sound_work_end"] = self.work_sound_check.isChecked()
        cfg["sound_break_end"] = self.break_sound_check.isChecked()
        cfg["show_notification"] = self.notif_check.isChecked()
        cfg["volume"] = self.vol_slider.value()
        self.ctx.db.save()

    def on_durations_changed(self):
        engine = self.ctx.pomodoro
        w, s, l = self.work_spin.value(), self.short_spin.value(), self.long_spin.value()
        engine.work_sec, engine.short_break_sec, engine.long_break_sec = w * 60, s * 60, l * 60

        cfg = self.ctx.db.data["settings"]["pomodoro"]
        cfg["work_min"], cfg["short_break_min"], cfg["long_break_min"] = w, s, l
        self.ctx.db.save()

        if not engine.running:
            engine.remaining_seconds = {
                "Çalışma": engine.work_sec,
                "Kısa Mola": engine.short_break_sec,
            }.get(engine.phase, engine.long_break_sec)
            engine.tick_signal.emit()

    # ---- görünüm ----
    def update_display(self):
        engine = self.ctx.pomodoro
        mins, secs = divmod(engine.remaining_seconds, 60)
        self.time_label.setText(f"{int(mins):02d}:{int(secs):02d}")
        self.phase_label.setText(engine.phase)

        total = {
            "Çalışma": engine.work_sec,
            "Kısa Mola": engine.short_break_sec,
        }.get(engine.phase, engine.long_break_sec)
        self.time_label.setStyleSheet(f"color: {PHASE_COLORS.get(engine.phase, C.WARN)}; border: none;")
        self.progress.setMaximum(max(1, total))
        self.progress.setValue(int(total - engine.remaining_seconds))

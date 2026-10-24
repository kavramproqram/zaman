"""Mod 6: Ömür sayacı (hedef yıla kadar kalan saniye/dakika/saat/gün)."""
from datetime import datetime, timedelta

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QSpinBox, QVBoxLayout

from core.storage import get_now
from core.theme import C
from core.ui import ModernButton, format_sayi
from modes.base import ModeBase


class Mode(ModeBase):
    TITLE = "Ömür Sayacı"

    def build_ui(self):
        self.target_ts = self._load_target()
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        display = QFrame()
        disp = QVBoxLayout(display)
        self.sec_label = self._big_label(20, C.TEXT_MUTED, disp)
        self.min_label = self._big_label(26, C.TEXT_SOFT, disp)
        self.hour_label = self._big_label(32, C.TEXT, disp)
        self.day_label = self._big_label(40, C.HEADING, disp)
        layout.addWidget(display)

        cfg = QFrame()
        cfg_layout = QHBoxLayout(cfg)
        cfg_layout.addWidget(QLabel("Ömür Hedefi (Yıl):"))
        self.year_spin = QSpinBox()
        self.year_spin.setRange(1, 1000)
        self.year_spin.setValue(40)
        cfg_layout.addWidget(self.year_spin, 1)
        self.set_btn = ModernButton("▶ Sayaç Başlat", tooltip="Belirtilen Yıla Göre Geri Sayımı Başlat", role="primary")
        self.set_btn.clicked.connect(self.start_countdown)
        cfg_layout.addWidget(self.set_btn, 1)
        layout.addWidget(cfg)
        layout.addStretch()

    def _big_label(self, size, color, parent_layout):
        lbl = QLabel("0")
        lbl.setAlignment(Qt.AlignCenter)
        f = QFont(); f.setPointSize(size); f.setBold(True)
        lbl.setFont(f)
        lbl.setStyleSheet(f"color: {color}; border: none;")
        parent_layout.addWidget(lbl)
        return lbl

    def _load_target(self):
        val = self.ctx.db.data["settings"].get("life_target_ts")
        if val:
            try:
                return datetime.fromisoformat(val)
            except ValueError:
                pass
        return None

    def start_countdown(self):
        years = self.year_spin.value()
        self.target_ts = get_now() + timedelta(days=years * 365.25)
        self.ctx.db.data["settings"]["life_target_ts"] = self.target_ts.isoformat()
        self.ctx.db.save()
        self.update_display()

    def update_display(self):
        if not self.target_ts:
            return
        delta = (self.target_ts - get_now()).total_seconds()
        if delta <= 0:
            return
        self.sec_label.setText(f"{format_sayi(delta)} Saniye")
        self.min_label.setText(f"{format_sayi(delta / 60)} Dakika")
        self.hour_label.setText(f"{format_sayi(delta / 3600)} Saat")
        self.day_label.setText(f"{format_sayi(delta / 86400)} Gün")

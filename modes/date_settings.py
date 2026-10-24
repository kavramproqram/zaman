"""Mod 7: Tarih ve saat referans ayarı (tüm modlar bu saate göre çalışır)."""
from datetime import datetime

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QMessageBox, QSizePolicy, QSpinBox,
    QVBoxLayout,
)

from core.storage import get_now
from core.theme import C
from core.ui import ModernButton
from modes.base import ModeBase


class Mode(ModeBase):
    TITLE = "Tarih Ayarı"

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        info = QFrame()
        info_layout = QVBoxLayout(info)
        title = QLabel("Tarih ve Saat Referans Ayarı")
        title.setStyleSheet(f"font-weight: bold; color: {C.HEADING}; border: none;")
        f = QFont(); f.setPointSize(14)
        title.setFont(f)
        info_layout.addWidget(title)
        desc = QLabel("Belirleyeceğiniz tarih/saat referans alınarak tüm modlar senkronize çalışır.")
        desc.setWordWrap(True)
        desc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        desc.setStyleSheet(f"color: {C.TEXT_SOFT}; border: none;")
        info_layout.addWidget(desc)
        layout.addWidget(info)

        inputs = QFrame()
        grid = QGridLayout(inputs)
        now = get_now()
        self.spin_year = self._spin(1900, 2100, now.year, grid, 0, 0, "Yıl:")
        self.spin_month = self._spin(1, 12, now.month, grid, 0, 2, "Ay:")
        self.spin_day = self._spin(1, 31, now.day, grid, 0, 4, "Gün:")
        self.spin_hour = self._spin(0, 23, now.hour, grid, 1, 0, "Saat:")
        self.spin_minute = self._spin(0, 59, now.minute, grid, 1, 2, "Dakika:")
        self.spin_second = self._spin(0, 59, now.second, grid, 1, 4, "Saniye:")
        layout.addWidget(inputs)

        btns = QHBoxLayout()
        self.btn_update = ModernButton("Referans Zamanı Güncelle", tooltip="Girilen Saati Tüm Modlar İçin Geçerli Kıl", role="success")
        self.btn_update.clicked.connect(self.apply_custom_time)
        btns.addWidget(self.btn_update, 1)
        self.btn_reset = ModernButton("Sistem Zamanına Sıfırla", tooltip="Gerçek Sistem Saatine Dön", role="danger")
        self.btn_reset.clicked.connect(self.reset_to_system_time)
        btns.addWidget(self.btn_reset, 1)
        layout.addLayout(btns)

        disp = QFrame()
        disp_lay = QVBoxLayout(disp)
        self.lbl_real_time = QLabel()
        self.lbl_app_time = QLabel()
        disp_lay.addWidget(self.lbl_real_time)
        disp_lay.addWidget(self.lbl_app_time)
        layout.addWidget(disp)
        layout.addStretch()

    def _spin(self, lo, hi, value, grid, row, col, text):
        grid.addWidget(QLabel(text), row, col)
        spin = QSpinBox()
        spin.setRange(lo, hi)
        spin.setValue(value)
        grid.addWidget(spin, row, col + 1)
        return spin

    def apply_custom_time(self):
        try:
            target = datetime(
                self.spin_year.value(), self.spin_month.value(), self.spin_day.value(),
                self.spin_hour.value(), self.spin_minute.value(), self.spin_second.value(),
            )
            db = self.ctx.db
            db.data["settings"]["time_offset_seconds"] = (target - datetime.now()).total_seconds()
            db.save()
            QMessageBox.information(self, "Başarılı", "Referans saat güncellendi!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def reset_to_system_time(self):
        self.ctx.db.data["settings"]["time_offset_seconds"] = 0
        self.ctx.db.save()

    def update_display(self):
        self.lbl_real_time.setText(f"Bilgisayar Saati: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        self.lbl_app_time.setText(f"Referans Saati: {get_now().strftime('%d.%m.%Y %H:%M:%S')}")

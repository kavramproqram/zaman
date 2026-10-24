"""Mod 8: Ekran ayarı ve mavi ışık filtresi.

Sürücü seçimi core/display tarafındadır; bu mod yalnızca kullanıcı arayüzü ve
zamanlama (saat aralığı / kademeli otomatik) mantığını içerir.

- Zamanlama modları sekme açık olmasa da çalışır (ModeBase.tick her saniye çağrılır).
- Aynı değerler tekrar uygulanmaz; her saniye donanıma komut gitmez.
- Alt + V: ekran bozulursa uygulamanın herhangi bir yerinde varsayılana döndürür.
"""
from PyQt5.QtCore import QEvent, Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QComboBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QSizePolicy,
    QSlider, QSpinBox, QVBoxLayout, QFrame,
)

from core.display import ScreenController, autostart
from core.display.wayland import TOOL as WAYLAND_TOOL
from core.storage import get_now
from core.theme import C, HINT_STYLE
from core.ui import ModernButton
from modes.base import ModeBase


class Mode(ModeBase):
    TITLE = "Ekran Ayarı"

    def build_ui(self):
        self.controller = ScreenController()
        self._block_save = True

        self._apply_timer = QTimer(self)
        self._apply_timer.setSingleShot(True)
        self._apply_timer.timeout.connect(self._apply_user_change)

        main = QVBoxLayout(self)
        main.setContentsMargins(10, 10, 10, 10)
        main.setSpacing(10)

        # Üst çubuk: referans saati, sıfırla, ekranları yenile, otomatik başlat
        clock_frame = QFrame()
        clock_box = QHBoxLayout(clock_frame)
        clock_box.setContentsMargins(12, 8, 12, 8)
        self.ref_clock_label = QLabel("Referans Saati: --:--:--")
        self.ref_clock_label.setStyleSheet(f"font-weight: bold; color: {C.HEADING}; border: none;")
        f = QFont(); f.setPointSize(11)
        self.ref_clock_label.setFont(f)
        clock_box.addWidget(self.ref_clock_label, 2)

        self.reset_button = ModernButton("↺ Sıfırla", tooltip="Ekran Ayarlarını Varsayılana Döndür")
        self.reset_button.clicked.connect(self._reset)
        clock_box.addWidget(self.reset_button, 1)

        self.refresh_btn = ModernButton("⟳ Ekranları Yenile", tooltip="Bağlı Ekran Monitörlerini Tekrar Tara")
        self.refresh_btn.clicked.connect(self._on_refresh_clicked)
        clock_box.addWidget(self.refresh_btn, 1)

        self.autostart_button = ModernButton("⚙ Otomatik Başlat", tooltip="Sistem Açılışında Otomatik Çalıştır")
        self.autostart_button.setCheckable(True)
        self.autostart_button.setChecked(autostart.is_enabled())
        self.autostart_button.toggled.connect(autostart.set_enabled)
        clock_box.addWidget(self.autostart_button, 1)
        main.addWidget(clock_frame)

        # Durum
        sg = QGroupBox("Sistem Durumu")
        sl = QVBoxLayout()
        self.status_label = QLabel("Durum: -")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        sl.addWidget(self.status_label)
        sg.setLayout(sl)
        main.addWidget(sg)

        if not self.controller.available and self.controller.session == "wayland":
            hint = QLabel(f"Wayland için '{WAYLAND_TOOL}' kurulu olmalı (ör. sudo apt install gammastep).")
            hint.setStyleSheet(HINT_STYLE)
            hint.setAlignment(Qt.AlignCenter)
            main.addWidget(hint)

        # Zamanlama
        sched = QGroupBox("Zamanlı & Kademeli Filtreleme Ayarları")
        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QLabel("Mavi Işık Modu:"), 0, 0)
        self.combo_blue_mode = QComboBox()
        self.combo_blue_mode.addItems(["Her Zaman", "Saat Aralığı", "Kademeli Otomatik"])
        self.combo_blue_mode.currentIndexChanged.connect(self._apply)
        grid.addWidget(self.combo_blue_mode, 0, 1)
        grid.addWidget(QLabel("Başlangıç Saati:"), 0, 2)
        self.spin_blue_start = self._hour_spin(20)
        grid.addWidget(self.spin_blue_start, 0, 3)
        grid.addWidget(QLabel("Bitiş Saati:"), 0, 4)
        self.spin_blue_end = self._hour_spin(7)
        grid.addWidget(self.spin_blue_end, 0, 5)

        grid.addWidget(QLabel("Gri Mod Çalışma:"), 1, 0)
        self.combo_gray_mode = QComboBox()
        self.combo_gray_mode.addItems(["Her Zaman", "Saat Aralığı"])
        self.combo_gray_mode.currentIndexChanged.connect(self._apply)
        grid.addWidget(self.combo_gray_mode, 1, 1)
        grid.addWidget(QLabel("Başlangıç Saati:"), 1, 2)
        self.spin_gray_start = self._hour_spin(22)
        grid.addWidget(self.spin_gray_start, 1, 3)
        grid.addWidget(QLabel("Bitiş Saati:"), 1, 4)
        self.spin_gray_end = self._hour_spin(6)
        grid.addWidget(self.spin_gray_end, 1, 5)
        sched.setLayout(grid)
        main.addWidget(sched)

        # Mavi ışık, renk, parlaklık
        bg = QGroupBox("Mavi Işık Filtresi (Hedef Seviye)")
        bv = QVBoxLayout()
        self.blue_filter_slider = self._make_row(bv, "Mavi Işık Filtre Şiddeti",
                                                 "0–40: Hafif filtre | 40–80: Derin gece koruması | 80–100: Ultra sıcak okuma modu",
                                                 0, 100, 0)
        bg.setLayout(bv)
        main.addWidget(bg)

        cg = QGroupBox("RGB Renk Dengesi")
        cv = QVBoxLayout()
        self.red_slider = self._make_row(cv, "Kırmızı Kanalı", "Sıcaklığı artırır", 50, 160, 100)
        self.green_slider = self._make_row(cv, "Yeşil Kanalı", "Yeşil ton ayarı", 50, 160, 100)
        cg.setLayout(cv)
        main.addWidget(cg)

        pg = QGroupBox("Parlaklık & Gama Karartma")
        pv = QVBoxLayout()
        self.brightness_slider = self._make_row(pv, "Ekran Parlaklığı", "Genel ekran ışık gücü", 20, 150, 100)
        self.darkness_slider = self._make_row(pv, "Gama Karartma", "Karanlık ortamlarda gözü korur", 0, 80, 0)
        pg.setLayout(pv)
        main.addWidget(pg)

        bottom = QHBoxLayout()
        self.reading_button = ModernButton("📖 Okuma Modu", tooltip="Hızlı Sıcak Okuma Tonu")
        self.reading_button.setCheckable(True)
        self.reading_button.toggled.connect(self._on_reading)
        self.gray_button = ModernButton("◐ Gri Mod (Grayscale)", tooltip="Ekranı Siyah Beyaz Yap")
        self.gray_button.setCheckable(True)
        self.gray_button.toggled.connect(self._apply)
        bottom.addWidget(self.reading_button, 1)
        bottom.addWidget(self.gray_button, 1)
        main.addLayout(bottom)

        shortcut = QLabel("Kısayol: Ekran bozulursa düzeltmek için Alt + V tuşlarına basın.")
        shortcut.setStyleSheet(HINT_STYLE)
        shortcut.setAlignment(Qt.AlignCenter)
        shortcut.setWordWrap(True)
        shortcut.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        main.addWidget(shortcut)
        main.addStretch()

        self._load_settings()
        self._block_save = False
        self.controller.refresh_outputs()
        self._apply_now(save=False)

        # Alt+V: uygulama genelinde kısayol
        QApplication.instance().installEventFilter(self)

    # ---- yardımcılar ----
    def _hour_spin(self, value):
        spin = QSpinBox()
        spin.setRange(0, 23)
        spin.setValue(value)
        spin.valueChanged.connect(self._apply)
        return spin

    def _make_row(self, layout, name, hint_text, min_v, max_v, def_v):
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(f"color: {C.TEXT}; font-weight: bold; border: none;")
        layout.addWidget(name_lbl)
        sld = QSlider(Qt.Horizontal)
        sld.setRange(min_v, max_v)
        sld.setValue(def_v)
        sld.valueChanged.connect(self._apply)
        layout.addWidget(sld)
        hint = QLabel(hint_text)
        hint.setStyleSheet(HINT_STYLE)
        hint.setWordWrap(True)
        hint.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(hint)
        return sld

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.modifiers() == Qt.AltModifier and event.key() == Qt.Key_V:
                self._reset()
                return True
        return False

    @staticmethod
    def _is_in_hours(start_h, end_h, current_h):
        if start_h <= end_h:
            return start_h <= current_h < end_h
        return current_h >= start_h or current_h < end_h

    def _calculate_effective_blue_level(self):
        target = self.blue_filter_slider.value()
        mode = self.combo_blue_mode.currentText()
        cur_h = get_now().hour
        start_h, end_h = self.spin_blue_start.value(), self.spin_blue_end.value()

        if mode == "Saat Aralığı":
            return target if self._is_in_hours(start_h, end_h, cur_h) else 0
        if mode == "Kademeli Otomatik":
            if not self._is_in_hours(start_h, end_h, cur_h):
                return 0
            if start_h <= end_h:
                duration = max(1, end_h - start_h)
                elapsed = cur_h - start_h
            else:
                duration = max(1, (24 - start_h) + end_h)
                elapsed = (cur_h - start_h) if cur_h >= start_h else ((24 - start_h) + cur_h)
            factor = min(1.0, max(0.2, (elapsed + 1) / duration))
            return int(target * factor)
        return target

    # ---- uygulama ----
    def _apply(self):
        if self._block_save:
            return
        self._apply_timer.start(50)

    def _apply_user_change(self):
        self._apply_now(save=True)

    def _apply_now(self, save=True):
        now = get_now()
        is_gray = self.gray_button.isChecked()
        if is_gray and self.combo_gray_mode.currentText() == "Saat Aralığı":
            if not self._is_in_hours(self.spin_gray_start.value(), self.spin_gray_end.value(), now.hour):
                is_gray = False

        status = self.controller.apply(
            red=self.red_slider.value(),
            green=self.green_slider.value(),
            blue_filter=self._calculate_effective_blue_level(),
            brightness=self.brightness_slider.value(),
            darkness=self.darkness_slider.value(),
            gray=is_gray,
        )
        self.status_label.setText(f"Durum: {status}")

        if save and not self._block_save:
            self._save_settings()

    def _on_refresh_clicked(self):
        self.controller.refresh_outputs()
        self._apply_now(save=False)

    def _on_reading(self, checked):
        if checked:
            self.red_slider.setValue(110)
            self.green_slider.setValue(90)
            self.blue_filter_slider.setValue(60)
        else:
            self.red_slider.setValue(100)
            self.green_slider.setValue(100)
            self.blue_filter_slider.setValue(0)
        self._apply()

    def _reset(self):
        self._block_save = True
        self.combo_blue_mode.setCurrentIndex(0)
        self.spin_blue_start.setValue(20)
        self.spin_blue_end.setValue(7)
        self.combo_gray_mode.setCurrentIndex(0)
        self.spin_gray_start.setValue(22)
        self.spin_gray_end.setValue(6)
        self.blue_filter_slider.setValue(0)
        self.red_slider.setValue(100)
        self.green_slider.setValue(100)
        self.brightness_slider.setValue(100)
        self.darkness_slider.setValue(0)
        self.reading_button.setChecked(False)
        self.gray_button.setChecked(False)
        self._block_save = False

        self.controller.reset()
        self._apply_now(save=True)

    # ---- kayıt ----
    def _save_settings(self):
        s = self.ctx.db.data["settings"]["screen"]
        s["blue_filter"] = self.blue_filter_slider.value()
        s["brightness"] = self.brightness_slider.value()
        s["darkness"] = self.darkness_slider.value()
        s["red"] = self.red_slider.value()
        s["green"] = self.green_slider.value()
        s["gray"] = self.gray_button.isChecked()
        s["reading"] = self.reading_button.isChecked()
        s["blue_mode"] = self.combo_blue_mode.currentText()
        s["blue_start_hour"] = self.spin_blue_start.value()
        s["blue_end_hour"] = self.spin_blue_end.value()
        s["gray_mode"] = self.combo_gray_mode.currentText()
        s["gray_start_hour"] = self.spin_gray_start.value()
        s["gray_end_hour"] = self.spin_gray_end.value()
        self.ctx.db.save()

    def _load_settings(self):
        s = self.ctx.db.data["settings"].get("screen", {})
        self.gray_button.setChecked(s.get("gray", False))
        self.reading_button.setChecked(s.get("reading", False))
        self.blue_filter_slider.setValue(s.get("blue_filter", 0))
        self.brightness_slider.setValue(s.get("brightness", 100))
        self.darkness_slider.setValue(s.get("darkness", 0))
        self.red_slider.setValue(s.get("red", 100))
        self.green_slider.setValue(s.get("green", 100))

        idx = self.combo_blue_mode.findText(s.get("blue_mode", "Her Zaman"))
        if idx >= 0:
            self.combo_blue_mode.setCurrentIndex(idx)
        self.spin_blue_start.setValue(s.get("blue_start_hour", 20))
        self.spin_blue_end.setValue(s.get("blue_end_hour", 7))

        g_idx = self.combo_gray_mode.findText(s.get("gray_mode", "Her Zaman"))
        if g_idx >= 0:
            self.combo_gray_mode.setCurrentIndex(g_idx)
        self.spin_gray_start.setValue(s.get("gray_start_hour", 22))
        self.spin_gray_end.setValue(s.get("gray_end_hour", 6))

    # ---- ModeBase kancaları ----
    def tick(self):
        # Zamanlı filtreler sekme kapalıyken de çalışır; değişmeyen değerler yeniden gönderilmez.
        self._apply_now(save=False)

    def update_display(self):
        self.ref_clock_label.setText(f"Referans Saati: {get_now().strftime('%H:%M:%S')}")

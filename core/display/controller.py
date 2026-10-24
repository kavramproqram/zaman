"""Ekran kontrol merkezi. Modların istediği değerleri oturum sürücüsüne çevirir.

Aynı değerler tekrar gönderilirse hiçbir komut çalıştırılmaz (her saniye xrandr çağrısı yapılmaz).
"""
import os

from core.display.wayland import WaylandBackend
from core.display.x11 import X11Backend


class ScreenController:
    def __init__(self):
        self.session = (os.environ.get("XDG_SESSION_TYPE") or "x11").lower()
        self.backend = WaylandBackend() if self.session == "wayland" else X11Backend()
        self._last_key = None
        self.status = ""

    @property
    def available(self) -> bool:
        return self.backend.available()

    def describe(self) -> str:
        return self.backend.describe()

    def refresh_outputs(self):
        self.backend.refresh_outputs()
        self._last_key = None

    def apply(self, red, green, blue_filter, brightness, darkness, gray):
        """Yüzde değerleri alır (100 = normal). gray: gri mod isteniyor mu."""
        key = (red, green, blue_filter, brightness, darkness, bool(gray))
        if key == self._last_key:
            return self.status
        self._last_key = key

        r = red / 100.0
        g = green / 100.0 - blue_filter * 0.003
        b = 1.0 - blue_filter * 0.008

        method = self.backend.set_grayscale(bool(gray))
        if gray and method is None:
            self.status = (f"{self.backend.name}: gri mod kurulamadı "
                           "(CTM desteklenmiyor ve picom çalışmıyor)")
        elif gray and method == "gamma":
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            r = g = b = lum

        r, g, b = (max(0.1, min(1.0, v)) for v in (r, g, b))

        effective_br = max(0.1, min(1.5, (brightness / 100.0) * (1.0 - darkness / 100.0)))
        self.backend.set_color(r, g, b, effective_br)

        if not (gray and method is None):
            self.status = f"Aktif — {self.backend.describe()}" + (f", gri: {method}" if method else "")
        return self.status

    def reset(self):
        self.backend.set_grayscale(False)
        self.backend.reset()
        self._last_key = None
        self.status = "Varsayılana döndürüldü"

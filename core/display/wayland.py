"""Wayland sürücüsü: gammastep (wlr-gamma-control destekleyen compositor'lar: sway, Hyprland, wlroots).

Not: Wayland'da genel bir gri mod protokolü yoktur; gri mod bu sürücüde desteklenmez.
GNOME/KDE gibi compositor'lar gamma protokolünü açmadığı için gammastep çalışmayabilir.
"""
from core.display.base import DisplayBackend, has_cmd, run_quiet

TOOL = "gammastep"


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


class WaylandBackend(DisplayBackend):
    name = "wayland"

    def available(self) -> bool:
        return has_cmd(TOOL)

    def set_color(self, r, g, b, brightness) -> None:
        if not self.available():
            return
        # gammastep parlaklığı 0.1-1.0 ile sınırlı; fazlasını kanal çarpanına taşıyoruz.
        gr = _clamp(r * brightness, 0.1, 10.0)
        gg = _clamp(g * brightness, 0.1, 10.0)
        gb = _clamp(b * brightness, 0.1, 10.0)
        run_quiet([TOOL, "-P", "-O", "6500", "-g", f"{gr:.2f}:{gg:.2f}:{gb:.2f}", "-b", "1.0"])

    def reset(self) -> None:
        if self.available():
            run_quiet([TOOL, "-x"])

    def set_grayscale(self, enable: bool):
        return None

    def describe(self) -> str:
        return "Wayland (gammastep)" if self.available() else "Wayland (gammastep kurulu değil)"

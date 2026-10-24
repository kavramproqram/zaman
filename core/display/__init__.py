"""Ekran ayarı katmanı. Oturum türüne göre uygun sürücüyü seçer (X11 veya Wayland)."""
from core.display.controller import ScreenController
from core.display import autostart

__all__ = ["ScreenController", "autostart"]

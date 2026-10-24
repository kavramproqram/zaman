#!/usr/bin/env python3
"""Zaman - giriş noktası.

Çekirdek core/app.py içindedir; modlar modes/ klasöründe ayrı dosyalardadır.
Kullanım: python3 zaman.py [--startupHidden=true]
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.app import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main(sys.argv))

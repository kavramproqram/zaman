# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['zaman.py'],
    pathex=[],
    binaries=[],
    datas=[('ikon', 'ikon')],
    hiddenimports=['modes.pomodoro', 'modes.tasks', 'modes.notes', 'modes.calendar_normal', 'modes.calendar_numeric', 'modes.calendar_octal', 'modes.life', 'modes.date_settings', 'modes.screen', 'modes.habits'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='zaman',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

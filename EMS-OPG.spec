# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for EMS-OPG.
#
# This must be run on Windows (PyInstaller cannot cross-compile), with the
# project's venv active, from the project root:
#
#     uv sync --extra dev
#     uv run pyinstaller EMS-OPG.spec
#
# Output lands in dist\EMS-OPG\ - the whole folder is the app, not just the
# .exe inside it. frontend/, config/, and assets/ are bundled next to the
# .exe and resolved via PathManager.root at runtime (see
# src/ems_opg/core/paths_manager.py's `sys.frozen` branch), while
# database/logs/cache/exports/backup are intentionally NOT bundled - those
# are created fresh at first run, at whatever `data_root` config.json points
# to.
#
# dist\EMS-OPG\ itself isn't meant to be handed to an operator directly -
# run scripts\install_windows.ps1 afterward to move it to a clean per-user
# location (%LOCALAPPDATA%\Programs\EMS-OPG\) and create a single Desktop
# shortcut pointing at the exe inside it, so the Desktop only ever shows
# one icon instead of the whole runtime folder:
#
#     uv run pyinstaller EMS-OPG.spec
#     powershell -ExecutionPolicy Bypass -File scripts\install_windows.ps1


from PyInstaller.utils.hooks import collect_all

block_cipher = None

# frontend/config/assets travel with the app itself, regardless of data_root.
datas = [
    ("frontend", "frontend"),
    ("config", "config"),
    ("assets", "assets"),
]

# pywebview ships non-Python resources (and its Windows/EdgeChromium backend
# pulls in pythonnet) that PyInstaller's static import analysis can miss on
# its own - collect_all pulls in its data files, binaries, and hidden
# imports together instead of guessing at --hidden-import flags one at a time.
webview_datas, webview_binaries, webview_hiddenimports = collect_all("webview")
datas += webview_datas

a = Analysis(
    ["app.py"],
    pathex=["src"],
    binaries=webview_binaries,
    datas=datas,
    hiddenimports=webview_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="EMS-OPG",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    contents_directory="."
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="EMS-OPG"
)
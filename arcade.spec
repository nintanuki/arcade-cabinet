# PyInstaller spec for the Coding Club Arcade launcher.
#
# What this bundles into the exe (via PyInstaller's archive):
#   - main.py and the launcher/ package
#
# What stays OUTSIDE the exe, as real folders next to ArcadeCabinet.exe:
#   - assets/   -- launcher fonts/graphics/previews/sounds. Kept external so
#                  the launcher resolves them via the same root_dir as
#                  games/ and runtime/, and so they can be swapped without
#                  rebuilding the exe.
#   - settings.py -- top-level configuration; same rationale.
#   - games/    -- so games run from disk in their own working directory,
#                  preserving the launcher/game boundary, and so student
#                  games can be dropped in without rebuilding.
#   - runtime/  -- the bundled embeddable Python that runs game subprocesses.
#                  Populated by scripts/setup_runtime.ps1.
#
# These are copied into dist/ArcadeCabinet/ by build.ps1 after PyInstaller
# finishes; do NOT add them to `datas` here.

# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

block_cipher = None

# Nothing extra to bundle into the archive: every data file the launcher
# loads is resolved against root_dir at runtime, and root_dir is the folder
# containing the exe in a frozen build. build.ps1 copies the real folders
# (assets/, games/, runtime/) and settings.py next to the exe.
datas = []

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ArcadeCabinet",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # No console window; this is a kiosk-style app.
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="ArcadeCabinet",
)

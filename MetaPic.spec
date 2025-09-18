# MetaPicPick.spec — CLI + GUI EXEs, plugins & assets included
# Build with:  pyinstaller MetaPicPick.spec
# Output: dist/MetaPicPick/ (folder you can zip or use scripts/pack_release.ps1)

import sys
import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# ---- Project entrypoints ----
CLI_ENTRY = 'src/metapic/cli.py'
GUI_ENTRY = 'src/metapic/gui/enhanced_app.py'  # enhanced GUI

# ---- Hidden imports (plugins, optional extras) ----
hidden = []
hidden += collect_submodules('metapic')                    # package itself
hidden += collect_submodules('metapic.plugins')             # parser plugins
hidden += collect_submodules('metapic.core')                # core modules
# Common deps that sometimes need nudging
hidden += collect_submodules('orjson')
hidden += collect_submodules('pydantic')
hidden += collect_submodules('PySide6')                     # GUI optional

# ---- Data files (plugins as “source” not pyz, any assets later) ----
datas = []
# Include plugin .py files so dynamic loading works even in noarchive mode
# (PyInstaller can import from pyz, but explicit data keeps it simple for plugins)
datas += [('src/metapic/plugins', 'metapic/plugins')]
datas += [('src/metapic/core', 'metapic/core')]

# If you add icons/assets later, append here, e.g.:
# datas += [('assets', 'assets')]

# PySide6 data (Qt plugins) are auto-hooked; collect if you add QML etc.:
datas += collect_data_files('PySide6', include_py_files=False)

# ---- Analysis (CLI) ----
a_cli = Analysis(
    [CLI_ENTRY],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,    # keep as zip; set True if you prefer loose .pyc for easier plugin swapping
)

pyz_cli = PYZ(a_cli.pure, a_cli.zipped_data, cipher=block_cipher)

exe_cli = EXE(
    pyz_cli,
    a_cli.scripts,
    [],
    exclude_binaries=True,
    name='MetaPic',         # console app (CLI)
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,           # console on
)

coll_cli = COLLECT(
    exe_cli,
    a_cli.binaries,
    a_cli.zipfiles,
    a_cli.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MetaPic'
)

# ---- Analysis (GUI) ----
a_gui = Analysis(
    [GUI_ENTRY],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz_gui = PYZ(a_gui.pure, a_gui.zipped_data, cipher=block_cipher)

exe_gui = EXE(
    pyz_gui,
    a_gui.scripts,
    [],
    exclude_binaries=True,
    name='MetaPicGUI',      # windowed app (enhanced GUI)
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # no console window
    # icon='assets/app.ico',  # uncomment if you add an icon
)

coll_gui = COLLECT(
    exe_gui,
    a_gui.binaries,
    a_gui.zipfiles,
    a_gui.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MetaPicGUI'
)

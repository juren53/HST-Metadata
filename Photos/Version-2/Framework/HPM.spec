# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Collect all data files
datas = [
    ('__init__.py', '.'),
    ('launcher/HPM_icon.png', 'launcher'),
    ('icons', 'icons'),
    ('gui/Copyright_Watermark.png', 'gui'),
]

# Hidden imports - include all our packages and third-party libraries
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.sip',
    'pandas',
    'openpyxl',
    'yaml',
    'ftfy',
    'PIL',
    'exiftool',
    '__init__',
    'gui',
    'gui.main_window',
    'gui.theme_manager',
    'gui.zoom_manager',
    'gui.dialogs',
    'gui.widgets',
    'core',
    'core.pipeline',
    'steps',
    'steps.base_step',
    'utils',
    'config',
    'config.config_manager',
    'config.settings',
]

a = Analysis(
    ['gui\\hstl_gui.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HPM',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI application (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icons\\app.ico',
)

# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gui\\hstl_gui.py'],
    pathex=['.', '../dev'],
    binaries=[],
    datas=[('gui', 'gui'), ('config', 'config'), ('utils', 'utils'), ('steps', 'steps'), ('core', 'core'), ('../dev/g2c.py', '.')],
    hiddenimports=['g2c', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'yaml', 'pandas', 'PIL', 'PIL.Image', 'google.auth', 'google.oauth2', 'google.auth.transport.requests', 'googleapiclient.discovery', 'structlog', 'pydantic', 'config.config_manager', 'config.settings', 'utils.batch_registry', 'utils.path_manager', 'utils.validator', 'utils.logger', 'utils.file_utils', 'steps.base_step', 'core.pipeline', 'hstl_framework', 'gui.main_window', 'gui.widgets.batch_list_widget', 'gui.widgets.step_widget', 'gui.widgets.config_widget', 'gui.widgets.log_widget', 'gui.dialogs.new_batch_dialog', 'gui.dialogs.batch_info_dialog', 'gui.dialogs.settings_dialog', 'gui.dialogs.step1_dialog', 'gui.dialogs.step2_dialog', 'gui.dialogs.step4_dialog', 'gui.dialogs.step5_dialog', 'gui.dialogs.step6_dialog', 'gui.dialogs.step7_dialog', 'gui.dialogs.step8_dialog'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'scipy', 'pytest', 'PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='HSTL_Photo_Framework_GUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='HSTL_Photo_Framework_GUI',
)

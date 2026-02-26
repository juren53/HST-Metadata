"""
icon_loader.py
A robust, cross-platform icon loader for PyQt6 applications.

Features:
- Unified icon loading for all parts of the app
- Automatic OS-specific icon selection (.ico, .icns, .png)
- Optional Qt Resource System support (":/icons/...")
- Multi-resolution icon handling
- Absolute path resolution for packaged apps (PyInstaller, cx_Freeze)
- Windows taskbar icon fix (AppUserModelID + WM_SETICON)
- Graceful fallback behavior
"""

from __future__ import annotations

import sys
import os
import pathlib
from typing import Optional

from PyQt6.QtGui import QIcon

# When running as a PyInstaller frozen executable with console=False,
# sys.stdout and sys.stderr are None on Windows. Redirect to devnull
# to prevent "'NoneType' object has no attribute 'write'" errors from print().
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")


class IconLoader:
    """
    A centralized icon loader that ensures consistent icon behavior across
    Windows, macOS, and Linux.
    """

    def __init__(self, base_path: Optional[pathlib.Path] = None):
        """
        base_path:
            Directory containing your icon files.
            If None, defaults to: <project_root>/resources/icons
        """
        if base_path is None:
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                base_path = pathlib.Path(sys._MEIPASS) / "resources" / "icons"
            else:
                base_path = pathlib.Path(__file__).resolve().parent / "resources" / "icons"

        self.base_path = base_path.resolve()

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------

    def app_icon(self) -> QIcon:
        """
        Returns the best icon for the application window, dock, and taskbar.
        Automatically selects .ico (Windows), .icns (macOS), or multi-resolution
        PNGs (Linux), with cross-platform fallback.
        """
        if sys.platform.startswith("win"):
            ico_path = self.base_path / "app.ico"
            if ico_path.exists():
                return QIcon(str(ico_path))
            print(f"[IconLoader] WARNING: app.ico not found, falling back to PNGs")

        elif sys.platform == "darwin":
            icns_path = self.base_path / "app.icns"
            if icns_path.exists():
                return QIcon(str(icns_path))
            print(f"[IconLoader] WARNING: app.icns not found, falling back to PNGs")

        # Linux primary path, or fallback for Windows/macOS when native format missing
        return self._load_multi_res_png()

    def load(self, filename: str) -> QIcon:
        """
        Loads an icon from disk or Qt resources.
        """
        # Qt Resource System path
        if filename.startswith(":/"):
            return QIcon(filename)

        # Absolute path resolution
        path = self.base_path / filename

        if not path.exists():
            print(f"[IconLoader] WARNING: Icon not found: {path}")
            return QIcon()  # Null icon

        return QIcon(str(path))

    def theme(self, name: str, fallback: str) -> QIcon:
        """
        Loads a theme icon (Linux) with a guaranteed fallback.
        """
        return QIcon.fromTheme(name, self.load(fallback))

    def set_taskbar_icon(self, window, app_id: str = "python.pyqt6.app") -> None:
        """
        Force the taskbar icon on Windows via COM property store + WM_SETICON.

        On non-Windows platforms this is a silent no-op.

        Parameters
        ----------
        window : QWidget
            A visible (shown) window whose taskbar icon should be set.
        app_id : str
            The AppUserModelID string for this window (default "python.pyqt6.app").
        """
        if not sys.platform.startswith("win"):
            return

        import ctypes
        from ctypes import (
            Structure, byref, c_byte, c_ulong, c_ushort, c_void_p, POINTER,
        )
        from ctypes import wintypes

        # ---- COM structures ----

        class GUID(Structure):
            _fields_ = [
                ("Data1", c_ulong), ("Data2", c_ushort), ("Data3", c_ushort),
                ("Data4", c_byte * 8),
            ]

        class PROPERTYKEY(Structure):
            _fields_ = [("fmtid", GUID), ("pid", c_ulong)]

        # Simplified PROPVARIANT -- only needs to hold VT_LPWSTR
        class PROPVARIANT(Structure):
            _fields_ = [
                ("vt", c_ushort),
                ("reserved1", c_ushort), ("reserved2", c_ushort),
                ("reserved3", c_ushort),
                ("ptr_val", c_void_p),
            ]

        IID_IPropertyStore = GUID(
            0x886D8EEB, 0x8CF2, 0x4446,
            (c_byte * 8)(0x8D, 0x02, 0xCD, 0xBA, 0x1D, 0xBD, 0xCF, 0x99),
        )
        PKEY_AppUserModel_ID = PROPERTYKEY(
            GUID(0x9F4C2855, 0x9F79, 0x4B39,
                 (c_byte * 8)(0xA8, 0xD0, 0xE1, 0xD4, 0x2D, 0xE1, 0xD5, 0xF3)),
            5,
        )

        hwnd = int(window.winId())

        # ---- 1. Set per-window AppUserModelID via IPropertyStore ----

        shell32 = ctypes.windll.shell32
        shell32.SHGetPropertyStoreForWindow.argtypes = [
            wintypes.HWND, POINTER(GUID), POINTER(c_void_p),
        ]
        shell32.SHGetPropertyStoreForWindow.restype = ctypes.HRESULT

        store = c_void_p()
        hr = shell32.SHGetPropertyStoreForWindow(
            hwnd, byref(IID_IPropertyStore), byref(store),
        )

        if hr == 0 and store:
            vtable = ctypes.cast(
                ctypes.cast(store, POINTER(c_void_p))[0],
                POINTER(c_void_p * 10),
            ).contents

            SetValue = ctypes.WINFUNCTYPE(
                ctypes.HRESULT, c_void_p,
                POINTER(PROPERTYKEY), POINTER(PROPVARIANT),
            )(vtable[6])
            Release = ctypes.WINFUNCTYPE(c_ulong, c_void_p)(vtable[2])

            c_app_id = ctypes.c_wchar_p(app_id)
            pv = PROPVARIANT()
            pv.vt = 31  # VT_LPWSTR
            pv.ptr_val = ctypes.cast(c_app_id, c_void_p).value

            SetValue(store, byref(PKEY_AppUserModel_ID), byref(pv))
            Release(store)

        # ---- 2. WM_SETICON with the .ico loaded through Win32 ----

        user32 = ctypes.windll.user32
        ico_path = str(self.base_path / "app.ico")

        IMAGE_ICON = 1
        LR_LOADFROMFILE = 0x0010
        WM_SETICON = 0x0080
        ICON_BIG = 1
        ICON_SMALL = 0

        hicon_big = user32.LoadImageW(
            0, ico_path, IMAGE_ICON, 48, 48, LR_LOADFROMFILE,
        )
        hicon_small = user32.LoadImageW(
            0, ico_path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE,
        )

        if hicon_big:
            user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon_big)
        if hicon_small:
            user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon_small)

    # ------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------

    def ensure_valid(self, icon: QIcon, context: str = "") -> QIcon:
        """
        Debug helper: warn if icon is null.
        """
        if icon.isNull():
            print(f"[IconLoader] WARNING: Null icon encountered ({context})")
        return icon

    # ------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------

    def _load_multi_res_png(self) -> QIcon:
        """
        Build a QIcon from all app_NxN.png files found in base_path,
        giving Qt every available resolution. Falls back to app.png.
        """
        icon = QIcon()
        found = False

        for png in sorted(self.base_path.glob("app_*x*.png")):
            icon.addFile(str(png))
            found = True

        if found:
            return icon

        # Final fallback: plain app.png
        app_png = self.base_path / "app.png"
        if app_png.exists():
            return QIcon(str(app_png))

        print("[IconLoader] WARNING: No app icon files found")
        return QIcon()


# ------------------------------------------------------------
# Module-level Windows init
# ------------------------------------------------------------

def _init_win32(app_id: str = "python.pyqt6.app") -> None:
    """Set a process-level AppUserModelID so Windows shows our icon."""
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

if sys.platform.startswith("win"):
    _init_win32()


# ------------------------------------------------------------
# Convenience global instance
# ------------------------------------------------------------

# Typical usage:
#   from icon_loader import icons
#   window.setWindowIcon(icons.app_icon())
icons = IconLoader()

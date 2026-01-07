# Quick Start: USB Portable WinPython

## The Problem You're Solving

WinPython installed to `D:\winpython` breaks when the USB drive becomes `E:\` or `F:\` on another computer.

## The Solution in 3 Steps

### Step 1: Use the Magic Variable `%~d0`

In batch files, `%~d0` automatically detects the drive letter where the batch file is located.

**Example:**
```batch
set USB_DRIVE=%~d0
REM If batch file is on E:\, then USB_DRIVE = E:
REM If batch file is on F:\, then USB_DRIVE = F:
```

### Step 2: Build All Paths From USB_DRIVE

```batch
set WINPYTHON_ACTIVATE=%USB_DRIVE%\WinPython\WPy64-31201b5\scripts\activate.bat
set FRAMEWORK_DIR=%USB_DRIVE%\Projects\HST-Metadata\Photos\Version-2\Framework
```

### Step 3: Use the Portable Launcher

Copy `LAUNCH_HPM_PORTABLE.bat` to your USB drive root and adjust the paths to match your directory structure.

---

## How to Set Up Your USB Drive

```
[Your USB Drive - any letter]:
│
├── LAUNCH_HPM_PORTABLE.bat  ← Copy this file here
│
├── WinPython/
│   └── WPy64-31201b5/
│       └── scripts/
│           └── activate.bat
│
└── Projects/
    └── HST-Metadata/
        └── Photos/
            └── Version-2/
                └── Framework/
                    └── gui/
                        └── hstl_gui.py
```

---

## Testing

1. **First test:** Run `LAUNCH_HPM_PORTABLE.bat` on your current computer
2. **Change drive letter test:**
   - Open Disk Management
   - Change your USB drive letter
   - Run the batch file again - should still work!
3. **Different computer test:**
   - Move USB to another computer
   - Run the batch file - works regardless of assigned letter!

---

## Key Batch File Variables Reference

| Variable | Meaning | Example |
|----------|---------|---------|
| `%0` | The batch file itself | `E:\LAUNCH_HPM_PORTABLE.bat` |
| `%~d0` | Drive letter only | `E:` |
| `%~p0` | Path only (no drive) | `\` |
| `%~dp0` | Full directory path | `E:\` |
| `%~n0` | Filename without extension | `LAUNCH_HPM_PORTABLE` |
| `%~x0` | Extension only | `.bat` |

---

## Customizing for Your Setup

Edit these lines in `LAUNCH_HPM_PORTABLE.bat` to match your USB structure:

```batch
REM Line 15-17: Adjust these paths
set WINPYTHON_ACTIVATE=%USB_DRIVE%\WinPython\WPy64-31201b5\scripts\activate.bat
set FRAMEWORK_DIR=%USB_DRIVE%\Projects\HST-Metadata\Photos\Version-2\Framework
set GUI_SCRIPT=gui\hstl_gui.py
```

**Important:**
- Always start paths with `%USB_DRIVE%\`
- Use `\` (backslash) for Windows paths
- No spaces in folder names = fewer headaches

---

## Troubleshooting

**Problem:** Batch file can't find WinPython
- **Fix:** Check the `WINPYTHON_ACTIVATE` path matches your actual folder name
- **Tip:** WinPython folders often have version numbers - make sure they match!

**Problem:** Gets wrong drive letter
- **Fix:** Make sure batch file is at the ROOT of your USB drive
- **Why:** `%~d0` detects the drive where the batch file is located

**Problem:** Works on Computer A but not Computer B
- **Likely cause:** Different WinPython versions or Python package locations
- **Fix:** Keep all Python packages in the WinPython folder, not in `%APPDATA%`

---

## Why This Works

Traditional approach (BROKEN on USB):
```batch
D:\WinPython\activate.bat  ← Hardcoded D:\ fails when USB becomes E:\
```

Portable approach (WORKS everywhere):
```batch
%~d0\WinPython\activate.bat  ← Always finds current drive letter
```

The magic is that `%~d0` **automatically updates** to whatever drive letter Windows assigns!

---

## Next Steps

1. Copy `LAUNCH_HPM_PORTABLE.bat` to your USB root
2. Edit the paths in lines 15-17 to match your structure
3. Test it on your current computer
4. Test it on a different computer
5. Create a desktop shortcut for convenience (it will need to be recreated on each new computer)

For detailed information, see `USB_PORTABLE_SETUP.md`.

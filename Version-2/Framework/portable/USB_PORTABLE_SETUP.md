# Making WinPython Portable on USB Drive

## The Problem

When WinPython is installed with absolute paths (e.g., `D:\winpython\...`), it fails when the USB drive gets assigned a different drive letter on another computer. For example:
- Computer 1: USB = `D:\` (works)
- Computer 2: USB = `E:\` or `F:\` (WinPython broken because it's looking for `D:\`)

## The Solution: Relative Path Launcher

The key is to use **relative paths** or **dynamic drive letter detection** so WinPython always finds itself regardless of the assigned drive letter.

---

## Setup Instructions

### Step 1: USB Drive Directory Structure

Organize your USB drive like this:

```
[USB Drive Letter]:
├── WinPython/
│   └── WPy64-31201b5/
│       ├── python-3.12.0.amd64/
│       ├── scripts/
│       │   └── activate.bat
│       └── ...
├── Projects/
│   └── HST-Metadata/
│       └── Photos/
│           └── Version-2/
│               └── Framework/
│                   ├── gui/
│                   │   └── hstl_gui.py
│                   └── ...
└── LAUNCH_HPM.bat  ← Main launcher (created below)
```

### Step 2: Create Portable Launcher Batch File

Create a file named `LAUNCH_HPM.bat` at the **root of your USB drive** with this content:

```batch
@echo off
REM ==============================================================
REM Portable WinPython Launcher for HSTL Photo Metadata System
REM Works regardless of USB drive letter assignment
REM ==============================================================

REM Get the drive letter of this batch file (the USB drive)
set USB_DRIVE=%~d0
echo USB Drive detected: %USB_DRIVE%

REM Define paths relative to USB drive root
set WINPYTHON_ACTIVATE=%USB_DRIVE%\WinPython\WPy64-31201b5\scripts\activate.bat
set FRAMEWORK_DIR=%USB_DRIVE%\Projects\HST-Metadata\Photos\Version-2\Framework
set GUI_SCRIPT=gui\hstl_gui.py

REM Validate that required paths exist
if not exist "%WINPYTHON_ACTIVATE%" (
    echo ERROR: WinPython activation script not found!
    echo Expected: %WINPYTHON_ACTIVATE%
    pause
    exit /b 1
)

if not exist "%FRAMEWORK_DIR%" (
    echo ERROR: Framework directory not found!
    echo Expected: %FRAMEWORK_DIR%
    pause
    exit /b 1
)

if not exist "%FRAMEWORK_DIR%\%GUI_SCRIPT%" (
    echo ERROR: GUI script not found!
    echo Expected: %FRAMEWORK_DIR%\%GUI_SCRIPT%
    pause
    exit /b 1
)

REM All paths validated - proceed with launch
echo.
echo Activating WinPython environment...
call "%WINPYTHON_ACTIVATE%"

echo.
echo Changing to Framework directory...
cd /d "%FRAMEWORK_DIR%"

echo.
echo Launching HSTL Photo Metadata System...
python %GUI_SCRIPT%

REM Check if application launched successfully
if errorlevel 1 (
    echo.
    echo ERROR: Application failed to launch
    pause
    exit /b 1
)

exit /b 0
```

### Step 3: Create Desktop Shortcut (Optional)

To create a desktop shortcut that always points to the USB launcher:

**Option A: Manual Shortcut Creation**
1. Right-click on `LAUNCH_HPM.bat` on your USB drive
2. Select "Create shortcut"
3. Move the shortcut to your Desktop
4. Rename it to "HSTL Photo Metadata (USB)"

**Option B: PowerShell Script for Dynamic Shortcut**

Create `create_usb_shortcut.ps1` on your USB drive:

```powershell
# Find the USB drive letter dynamically
$usbDrive = Split-Path -Qualifier $PSScriptRoot
$launcherPath = "$usbDrive\LAUNCH_HPM.bat"

# Create desktop shortcut
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\HSTL Photo Metadata (USB).lnk")
$Shortcut.TargetPath = $launcherPath
$Shortcut.WorkingDirectory = $usbDrive
$Shortcut.IconLocation = "shell32.dll,137"  # Computer icon
$Shortcut.Description = "Launch HSTL Photo Metadata from USB"
$Shortcut.Save()

Write-Host "Desktop shortcut created successfully!" -ForegroundColor Green
Write-Host "Target: $launcherPath" -ForegroundColor Cyan
pause
```

Run this script whenever you connect the USB to a new computer to create/update the shortcut.

---

## Alternative Solution: Python-Based Portable Launcher

For more advanced needs, you can modify the existing `launcher.py` to detect USB drive dynamically:

### Modified launcher_config.json for USB

Instead of using absolute paths, detect the script's location:

```json
{
    "base_directory": "DETECT_USB",
    "winpython_activate": "DETECT_USB",
    "gui_script": "gui\\hstl_gui.py",
    "script_timeout": 300,
    "enable_logging": true,
    "show_success_message": false
}
```

### Add USB Detection to launcher.py

Add this function after line 80 in `launcher.py`:

```python
def detect_usb_paths(config):
    """Detect USB drive paths dynamically if using DETECT_USB"""
    if config.get("base_directory") == "DETECT_USB":
        # Get the drive where this script is located
        script_location = Path(__file__).resolve()
        usb_drive = script_location.drive + "\\"

        # Set paths relative to USB drive
        config["base_directory"] = f"{usb_drive}Projects\\HST-Metadata\\Photos\\Version-2\\Framework"
        config["winpython_activate"] = f"{usb_drive}WinPython\\WPy64-31201b5\\scripts\\activate.bat"

        logging.info(f"USB drive detected: {usb_drive}")
        logging.info(f"Base directory: {config['base_directory']}")
        logging.info(f"WinPython activate: {config['winpython_activate']}")

    return config
```

Then call it in `load_config()` function before returning:

```python
def load_config():
    """Load configuration from JSON file, create default if not exists"""
    try:
        # ... existing code ...

        # Add this before return statements
        config = detect_usb_paths(config)
        return config
    except Exception as e:
        # ... existing error handling ...
```

---

## Testing Your Portable Setup

1. **Test on current computer:**
   - Double-click `LAUNCH_HPM.bat`
   - Application should launch successfully

2. **Test drive letter independence:**
   - Open Disk Management (`diskmgmt.msc`)
   - Right-click your USB drive → Change Drive Letter and Paths
   - Assign a different letter
   - Run `LAUNCH_HPM.bat` again - should still work!

3. **Test on another computer:**
   - Safely eject USB drive
   - Connect to different computer
   - Navigate to USB drive
   - Double-click `LAUNCH_HPM.bat`
   - Should work regardless of assigned drive letter

---

## Technical Explanation

### How `%~d0` Works

In batch files:
- `%0` = The batch file itself
- `%~d0` = **Drive letter only** of `%0` (e.g., `D:`, `E:`, `F:`)
- `%~p0` = Path only of `%0` (without drive letter)
- `%~dp0` = Full path to directory containing `%0`

**Example:**
If your batch file is at `E:\LAUNCH_HPM.bat`:
- `%~d0` = `E:`
- `%~p0` = `\`
- `%~dp0` = `E:\`

This allows the batch file to always detect which drive it's running from!

### Alternative: Using Current Directory

Instead of `%~d0`, you can also use:

```batch
cd /d "%~dp0"
set USB_DRIVE=%CD%
```

This changes to the batch file's directory and captures the current directory.

---

## Troubleshooting

### Issue: "WinPython activation script not found"
- **Cause:** WinPython not in expected location
- **Fix:** Update the `WINPYTHON_ACTIVATE` path in the batch file to match your actual WinPython location on the USB drive

### Issue: "Framework directory not found"
- **Cause:** Project not in expected location
- **Fix:** Update the `FRAMEWORK_DIR` path to match your actual project location

### Issue: Python packages missing
- **Cause:** WinPython environment not fully portable
- **Fix:** Make sure all Python packages are installed in the WinPython directory itself, not in user's home directory

### Issue: Settings/cache files not found
- **Cause:** Application trying to save settings to fixed locations
- **Fix:** Modify your application to use relative paths or detect USB drive for config storage

---

## Additional Tips

1. **Keep Everything on the USB:**
   - Install all Python packages to WinPython's site-packages
   - Store config files in the project directory
   - Avoid writing to `%USERPROFILE%` or `%APPDATA%`

2. **Use Fast USB 3.0/3.1 Drive:**
   - Python startup is faster on faster drives
   - Reduces load times significantly

3. **Avoid Long Paths:**
   - Keep your directory structure shallow
   - Windows has a 260-character path limit

4. **Consider Using Virtual Environments:**
   - Even more portable than WinPython's base environment
   - Can be created with `python -m venv venv` within your project

---

## Summary

The key to USB portability is **never using absolute paths** (like `D:\` or `C:\Users\...`). Instead:

1. Use `%~d0` to detect the USB drive letter dynamically
2. Build all other paths relative to the USB root
3. Validate paths before execution
4. Store everything on the USB drive itself

This ensures your WinPython environment will work on **any computer**, regardless of which drive letter gets assigned!

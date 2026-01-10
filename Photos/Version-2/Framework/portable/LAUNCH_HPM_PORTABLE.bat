@echo off
REM ==============================================================
REM Portable WinPython Launcher for HSTL Photo Metadata System
REM Works regardless of USB drive letter assignment
REM ==============================================================

title HSTL Photo Metadata System - Portable Launcher

REM Get the drive letter of this batch file (the USB drive)
set USB_DRIVE=%~d0
echo.
echo ========================================
echo Portable WinPython Launcher
echo ========================================
echo USB Drive detected: %USB_DRIVE%
echo.

REM Define paths relative to USB drive root
REM Adjust these paths to match your USB drive structure
set WINPYTHON_ACTIVATE=%USB_DRIVE%\WinPython\WPy64-31201b5\scripts\activate.bat
set FRAMEWORK_DIR=%USB_DRIVE%\Projects\HST-Metadata\Photos\Version-2\Framework
set GUI_SCRIPT=gui\hstl_gui.py

echo Checking required paths...
echo.

REM Validate that required paths exist
if not exist "%WINPYTHON_ACTIVATE%" (
    echo [ERROR] WinPython activation script not found!
    echo Expected: %WINPYTHON_ACTIVATE%
    echo.
    echo Please verify:
    echo 1. WinPython is installed on this USB drive
    echo 2. The path in this batch file is correct
    echo.
    pause
    exit /b 1
)
echo [OK] WinPython found: %WINPYTHON_ACTIVATE%

if not exist "%FRAMEWORK_DIR%" (
    echo [ERROR] Framework directory not found!
    echo Expected: %FRAMEWORK_DIR%
    echo.
    echo Please verify the project is on this USB drive
    echo.
    pause
    exit /b 1
)
echo [OK] Framework found: %FRAMEWORK_DIR%

if not exist "%FRAMEWORK_DIR%\%GUI_SCRIPT%" (
    echo [ERROR] GUI script not found!
    echo Expected: %FRAMEWORK_DIR%\%GUI_SCRIPT%
    echo.
    pause
    exit /b 1
)
echo [OK] GUI script found: %GUI_SCRIPT%

REM All paths validated - proceed with launch
echo.
echo ========================================
echo Launching Application
echo ========================================
echo.

echo [1/3] Activating WinPython environment...
call "%WINPYTHON_ACTIVATE%"
if errorlevel 1 (
    echo [ERROR] Failed to activate WinPython
    pause
    exit /b 1
)

echo [2/3] Changing to Framework directory...
cd /d "%FRAMEWORK_DIR%"
if errorlevel 1 (
    echo [ERROR] Failed to change directory
    pause
    exit /b 1
)

echo [3/3] Launching HSTL Photo Metadata System...
echo.
python %GUI_SCRIPT%

REM Check if application exited with error
if errorlevel 1 (
    echo.
    echo ========================================
    echo [ERROR] Application failed or exited with error
    echo ========================================
    pause
    exit /b 1
)

REM Success - exit quietly
exit /b 0

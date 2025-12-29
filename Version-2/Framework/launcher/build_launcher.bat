@echo off
REM Batch file to build thumbdrive_launcher.exe using PyInstaller

echo ============================================
echo Thumbdrive Launcher - Build Script
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
) else (
    echo PyInstaller already installed
)
echo.

REM Build the executable
echo Building executable...
echo.

pyinstaller --onefile --windowed --name "ThumbdriveLauncher" thumbdrive_launcher.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo Build Complete!
echo ============================================
echo.
echo The executable is located at:
echo   dist\ThumbdriveLauncher.exe
echo.
echo IMPORTANT: Copy launcher_config.json to the same directory as the .exe
echo.
echo Next steps:
echo   1. Copy dist\ThumbdriveLauncher.exe to your desired location
echo   2. Copy launcher_config.json to the same directory
echo   3. Right-click ThumbdriveLauncher.exe and create a desktop shortcut
echo   4. (Optional) Customize the shortcut icon
echo.
pause

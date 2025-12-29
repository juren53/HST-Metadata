@echo off
REM Complete setup script: Creates icon and desktop shortcut

echo ============================================
echo Thumbdrive Launcher - Desktop Icon Setup
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

echo Step 1: Installing required packages...
echo.

REM Install Pillow for icon creation
python -m pip install --user Pillow >nul 2>&1
if errorlevel 1 (
    echo Warning: Could not install Pillow, trying alternative method...
)

REM Install pywin32 for shortcut creation
python -m pip install --user pywin32 >nul 2>&1
if errorlevel 1 (
    echo Warning: Could not install pywin32, trying alternative method...
)

echo.
echo Step 2: Creating icon...
echo.

python create_icon.py
if errorlevel 1 (
    echo.
    echo Warning: Icon creation failed, will proceed without custom icon
    echo.
)

echo.
echo Step 3: Creating desktop shortcut...
echo.

python create_desktop_shortcut.py
if errorlevel 1 (
    echo.
    echo Automatic shortcut creation failed.
    echo Please create shortcut manually - see instructions above.
    echo.
)

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
pause

@echo off
REM HPM ExifTool Setup - Batch Script
REM This script installs ExifTool and adds it to the user PATH

echo ============================================
echo HPM ExifTool Setup
echo ============================================
echo.

REM Check if ExifTool already exists
where exiftool >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] ExifTool is already installed and in PATH
    exiftool -ver
    echo.
    echo No installation needed!
    pause
    exit /b 0
)

echo [INFO] ExifTool not found in PATH
echo.

REM Check if source zip exists
if not exist "%~dp0exiftool-13.27_64.zip" (
    echo [ERROR] ExifTool source file not found
    echo Expected: %~dp0exiftool-13.27_64.zip
    echo.
    pause
    exit /b 1
)

echo Installing ExifTool...
echo.

REM Create installation directory
set INSTALL_DIR=%LOCALAPPDATA%\exiftool
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    echo [OK] Created directory: %INSTALL_DIR%
)

REM Extract zip using PowerShell
echo Extracting ExifTool...
powershell -Command "Expand-Archive -Path '%~dp0exiftool-13.27_64.zip' -DestinationPath '%INSTALL_DIR%' -Force"

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to extract ExifTool
    pause
    exit /b 1
)

echo [OK] ExifTool extracted successfully
echo.

REM Add to user PATH using PowerShell
echo Adding ExifTool to PATH...
powershell -Command "[Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path', 'User') + ';%INSTALL_DIR%', 'User')"

if %ERRORLEVEL% EQU 0 (
    echo [OK] Added to PATH: %INSTALL_DIR%
) else (
    echo [WARNING] Could not automatically add to PATH
    echo Please manually add this directory to your PATH:
    echo   %INSTALL_DIR%
)

echo.
echo ============================================
echo Installation Complete!
echo ============================================
echo.
echo ExifTool has been installed to: %INSTALL_DIR%
echo.
echo IMPORTANT: Please restart your terminal/PowerShell windows
echo for PATH changes to take effect.
echo.
echo You can now run HPM without ExifTool errors!
echo.
pause

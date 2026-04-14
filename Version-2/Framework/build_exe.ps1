# HPM Build Script
# Compiles the HSTL Photo Framework into a standalone executable
#
# IMPORTANT: always builds with the project venv Python so that all
# dependencies (ftfy, pandas, etc.) are visible to PyInstaller.

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "HPM Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Resolve venv Python — abort if the venv doesn't exist
$venvPython = ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "ERROR: venv not found at $venvPython" -ForegroundColor Red
    Write-Host "Create it with: python -m venv .venv && .venv\Scripts\pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}
Write-Host "Using venv Python: $venvPython" -ForegroundColor Green

# Check if PyInstaller is installed in the venv
Write-Host "Checking for PyInstaller in venv..." -ForegroundColor Yellow
$pyinstallerCheck = & $venvPython -c "import PyInstaller; print(PyInstaller.__version__)" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "PyInstaller not found in venv. Installing..." -ForegroundColor Yellow
    & $venvPython -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install PyInstaller. Exiting." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "PyInstaller version $pyinstallerCheck found" -ForegroundColor Green
}

Write-Host ""

# Clean previous build artifacts
Write-Host "Cleaning previous build artifacts..." -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}
Write-Host "Clean complete" -ForegroundColor Green
Write-Host ""

# Generate version_info.txt from __init__.py
Write-Host "Generating version_info.txt..." -ForegroundColor Yellow
& $venvPython generate_version_info.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to generate version_info.txt. Exiting." -ForegroundColor Red
    exit 1
}
Write-Host ""

# Build the executable using the venv Python so all packages are visible
Write-Host "Building HPM executable..." -ForegroundColor Yellow
Write-Host "This may take several minutes..." -ForegroundColor Yellow
Write-Host ""

& $venvPython -m PyInstaller HPM.spec --clean

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Build Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable location: dist\HPM.exe" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You can now run HPM.exe directly without Python installed." -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Build Failed!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check the error messages above." -ForegroundColor Yellow
    exit 1
}

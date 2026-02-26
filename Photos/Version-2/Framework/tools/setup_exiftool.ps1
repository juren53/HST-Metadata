# HPM ExifTool Setup Script
# This script installs ExifTool to the user's local directory and adds it to PATH

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "HPM ExifTool Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Define paths
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$exiftoolSourceZip = Join-Path $scriptDir "exiftool-13.27_64.zip"
$installDir = Join-Path $env:LOCALAPPDATA "exiftool"
$exiftoolExe = Join-Path $installDir "exiftool.exe"

# Check if ExifTool is already in PATH
Write-Host "Checking for existing ExifTool installation..." -ForegroundColor Yellow
try {
    $existingExiftool = Get-Command exiftool -ErrorAction SilentlyContinue
    if ($existingExiftool) {
        Write-Host "[OK] ExifTool is already installed and accessible" -ForegroundColor Green
        Write-Host "Location: $($existingExiftool.Source)" -ForegroundColor Gray
        
        # Verify it works
        $version = & exiftool -ver 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Version: $version" -ForegroundColor Gray
            Write-Host ""
            Write-Host "No installation needed!" -ForegroundColor Green
            Read-Host "Press Enter to exit"
            exit 0
        }
    }
} catch {
    # ExifTool not found, continue with installation
}

Write-Host "[INFO] ExifTool not found in PATH" -ForegroundColor Yellow
Write-Host ""

# Check if source zip exists
if (-not (Test-Path $exiftoolSourceZip)) {
    Write-Host "[ERROR] ExifTool source file not found:" -ForegroundColor Red
    Write-Host "  Expected: $exiftoolSourceZip" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Please ensure exiftool-13.27_64.zip is in the framework directory." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Installing ExifTool..." -ForegroundColor Cyan
Write-Host ""

# Create installation directory if it doesn't exist
if (-not (Test-Path $installDir)) {
    try {
        New-Item -ItemType Directory -Path $installDir -Force | Out-Null
        Write-Host "[OK] Created directory: $installDir" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to create directory: $_" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Extract ExifTool
try {
    Write-Host "Extracting ExifTool..." -ForegroundColor Yellow
    Expand-Archive -Path $exiftoolSourceZip -DestinationPath $installDir -Force
    
    # The zip extracts to a subdirectory, we need to move files up
    $extractedSubdir = Get-ChildItem -Path $installDir -Directory | Select-Object -First 1
    if ($extractedSubdir) {
        Get-ChildItem -Path $extractedSubdir.FullName -Recurse | Move-Item -Destination $installDir -Force
        Remove-Item -Path $extractedSubdir.FullName -Recurse -Force
    }
    
    Write-Host "[OK] ExifTool extracted successfully" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to extract ExifTool: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Verify exiftool.exe exists
if (-not (Test-Path $exiftoolExe)) {
    Write-Host "[ERROR] exiftool.exe not found after extraction" -ForegroundColor Red
    Write-Host "Expected location: $exiftoolExe" -ForegroundColor Gray
    Read-Host "Press Enter to exit"
    exit 1
}

# Add to user PATH
try {
    Write-Host ""
    Write-Host "Adding ExifTool to PATH..." -ForegroundColor Yellow
    
    # Get current user PATH
    $currentPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
    
    # Check if already in PATH
    if ($currentPath -split ';' | Where-Object { $_ -eq $installDir }) {
        Write-Host "[OK] ExifTool directory already in PATH" -ForegroundColor Green
    } else {
        # Add to PATH
        $newPath = $currentPath + ";" + $installDir
        [Environment]::SetEnvironmentVariable("Path", $newPath, [EnvironmentVariableTarget]::User)
        Write-Host "[OK] Added to PATH: $installDir" -ForegroundColor Green
    }
    
    # Update PATH for current session
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    
} catch {
    Write-Host "[ERROR] Failed to update PATH: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "You can manually add this directory to your PATH:" -ForegroundColor Yellow
    Write-Host "  $installDir" -ForegroundColor Gray
    Read-Host "Press Enter to exit"
    exit 1
}

# Verify installation
Write-Host ""
Write-Host "Verifying installation..." -ForegroundColor Yellow

try {
    $version = & $exiftoolExe -ver 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] ExifTool is working!" -ForegroundColor Green
        Write-Host "Version: $version" -ForegroundColor Gray
        Write-Host "Location: $exiftoolExe" -ForegroundColor Gray
    } else {
        Write-Host "[WARNING] ExifTool may not be working correctly" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[WARNING] Could not verify ExifTool: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "ExifTool has been installed and added to your PATH." -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: You may need to:" -ForegroundColor Yellow
Write-Host "  1. Restart PowerShell/Command Prompt windows" -ForegroundColor White
Write-Host "  2. Or log out and log back in for PATH changes to take effect" -ForegroundColor White
Write-Host ""
Write-Host "You can now run HPM without ExifTool errors!" -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to exit"

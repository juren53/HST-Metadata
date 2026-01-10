# Thumbdrive Launcher - Installation Script
# This script copies the launcher to a user-specified location and creates a desktop shortcut

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Thumbdrive Launcher - Installation Wizard" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Get the source directory (where this script is located)
$sourceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "Source location: $sourceDir" -ForegroundColor Gray
Write-Host ""

# Suggest default installation location
$defaultInstallPath = "C:\Tools\ThumbdriveLauncher"
Write-Host "Where would you like to install the Thumbdrive Launcher?" -ForegroundColor Yellow
Write-Host "Default: $defaultInstallPath" -ForegroundColor Gray
Write-Host ""
$installPath = Read-Host "Install location (press Enter for default)"

# Use default if user just pressed Enter
if ([string]::IsNullOrWhiteSpace($installPath)) {
    $installPath = $defaultInstallPath
}

Write-Host ""

# Check if directory exists
if (Test-Path $installPath) {
    Write-Host "Directory already exists: $installPath" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to overwrite existing files? (y/n)"

    if ($overwrite -ne 'y' -and $overwrite -ne 'Y') {
        Write-Host "Installation cancelled." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    # Create directory
    try {
        New-Item -ItemType Directory -Path $installPath -Force | Out-Null
        Write-Host "[OK] Created directory: $installPath" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to create directory: $_" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "Installing files..." -ForegroundColor Cyan

# List of files to copy
$filesToCopy = @(
    "launcher.py",
    "launcher_config.json",
    "LAUNCHER_README.md",
    "build_launcher.bat",
    "create_shortcut.ps1",
    "create_icon.py",
    "create_desktop_shortcut.py",
    "setup_desktop_icon.bat",
    "thumbdrive_icon.ico"
)

# Copy files
$copiedCount = 0
foreach ($file in $filesToCopy) {
    $sourcePath = Join-Path $sourceDir $file
    $destPath = Join-Path $installPath $file

    if (Test-Path $sourcePath) {
        try {
            Copy-Item -Path $sourcePath -Destination $destPath -Force
            Write-Host "  [OK] Copied: $file" -ForegroundColor Green
            $copiedCount++
        } catch {
            Write-Host "  [ERROR] Failed to copy $file : $_" -ForegroundColor Red
        }
    } else {
        Write-Host "  [WARNING] File not found: $file" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Copied $copiedCount of $($filesToCopy.Count) files" -ForegroundColor Cyan
Write-Host ""

# Ask if user wants to create desktop shortcut
Write-Host "Would you like to create a desktop shortcut now? (y/n)" -ForegroundColor Yellow
$createShortcut = Read-Host

if ($createShortcut -eq 'y' -or $createShortcut -eq 'Y') {
    Write-Host ""
    Write-Host "Creating desktop shortcut..." -ForegroundColor Cyan

    # Run the create_shortcut.ps1 from the NEW location
    $shortcutScript = Join-Path $installPath "create_shortcut.ps1"

    if (Test-Path $shortcutScript) {
        try {
            Push-Location $installPath
            & powershell.exe -ExecutionPolicy Bypass -File $shortcutScript
            Pop-Location
        } catch {
            Write-Host "[ERROR] Failed to create shortcut: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "[ERROR] create_shortcut.ps1 not found in installation directory" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Checking Python Dependencies" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Load the config to get WinPython path
$configPath = Join-Path $installPath "launcher_config.json"
if (Test-Path $configPath) {
    try {
        $config = Get-Content $configPath | ConvertFrom-Json
        $winpythonActivate = $env:USERPROFILE + $config.winpython_activate.Replace('%USERPROFILE%', '')
        $frameworkDir = $env:USERPROFILE + $config.base_directory.Replace('%USERPROFILE%', '')
        $requirementsFile = Join-Path $frameworkDir "requirements.txt"
        
        if (Test-Path $winpythonActivate) {
            Write-Host "Checking for required Python packages..." -ForegroundColor Yellow
            
            # Create a temporary batch file to check for key dependencies
            $tempBatch = Join-Path $env:TEMP "check_deps.bat"
            @"
@echo off
call "$winpythonActivate"
python -c "import PyQt6; import yaml; import pandas" 2>nul
exit /b %ERRORLEVEL%
"@ | Out-File -FilePath $tempBatch -Encoding ASCII
            
            try {
                $null = cmd /c $tempBatch 2>&1
                Remove-Item $tempBatch -ErrorAction SilentlyContinue
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "[OK] Required dependencies are already installed" -ForegroundColor Green
                } else {
                    Write-Host "[WARNING] Some required dependencies are missing" -ForegroundColor Yellow
                    
                    if (Test-Path $requirementsFile) {
                        Write-Host ""
                        Write-Host "Would you like to install missing Python dependencies now? (y/n)" -ForegroundColor Yellow
                        Write-Host "This will install packages from: requirements.txt" -ForegroundColor Gray
                        $installDeps = Read-Host
                        
                        if ($installDeps -eq 'y' -or $installDeps -eq 'Y') {
                            Write-Host ""
                            Write-Host "Installing dependencies (this may take a few minutes)..." -ForegroundColor Cyan
                            
                            # Create a temporary batch file to install requirements
                            $installBatch = Join-Path $env:TEMP "install_deps.bat"
                            @"
@echo off
call "$winpythonActivate"
cd /d "$frameworkDir"
python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org PyYAML pandas pydantic ftfy tqdm colorama structlog Pillow PyExifTool google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client gspread pytest pytest-cov PyQt6 PyQt6-Qt6 PyQt6-sip
"@ | Out-File -FilePath $installBatch -Encoding ASCII
                            
                            try {
                                $result = cmd /c $installBatch 2>&1
                                Remove-Item $installBatch -ErrorAction SilentlyContinue
                                
                                if ($LASTEXITCODE -eq 0) {
                                    Write-Host "[OK] Dependencies installed successfully" -ForegroundColor Green
                                } else {
                                    Write-Host "[WARNING] Some dependencies may not have installed correctly" -ForegroundColor Yellow
                                    Write-Host "You can manually install them later with:" -ForegroundColor Gray
                                    Write-Host "  cmd /c `"call $winpythonActivate && cd /d $frameworkDir && pip install -r requirements.txt`"" -ForegroundColor Gray
                                }
                            } catch {
                                Write-Host "[ERROR] Failed to install dependencies: $_" -ForegroundColor Red
                            }
                        } else {
                            Write-Host "[SKIPPED] You can install dependencies later" -ForegroundColor Yellow
                        }
                    } else {
                        Write-Host "[WARNING] requirements.txt not found at: $requirementsFile" -ForegroundColor Yellow
                    }
                }
            } catch {
                Write-Host "[WARNING] Could not check dependencies: $_" -ForegroundColor Yellow
            }
        } else {
            Write-Host "[WARNING] WinPython activation script not found at: $winpythonActivate" -ForegroundColor Yellow
            Write-Host "You may need to edit launcher_config.json with the correct path" -ForegroundColor Gray
        }
    } catch {
        Write-Host "[WARNING] Could not read launcher config: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "[WARNING] launcher_config.json not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Installation location: $installPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Edit launcher_config.json to customize settings" -ForegroundColor White
Write-Host "     (drive letter, required files, timeouts, etc.)" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. (Optional) Build standalone .exe:" -ForegroundColor White
Write-Host "     Run: $installPath\build_launcher.bat" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Read the documentation:" -ForegroundColor White
Write-Host "     $installPath\LAUNCHER_README.md" -ForegroundColor Gray
Write-Host ""
Write-Host "The desktop shortcut is ready to use!" -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to exit"

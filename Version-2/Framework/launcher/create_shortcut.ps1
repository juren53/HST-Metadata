# PowerShell script to create desktop shortcut for Thumbdrive Launcher

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$desktopPath = [Environment]::GetFolderPath("Desktop")

# Determine target (exe or py script)
$exePath = Join-Path $scriptDir "dist\HPMLauncher.exe"
$pyScript = Join-Path $scriptDir "launcher.py"
$iconPath = Join-Path $scriptDir "thumbdrive_icon.ico"

# Find Python interpreter
$pythonw = $null
$pythonPaths = @(
    "C:\Users\$env:USERNAME\AppData\Local\Microsoft\WindowsApps\pythonw.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python*\pythonw.exe",
    "C:\Python*\pythonw.exe"
)

foreach ($path in $pythonPaths) {
    $found = Get-Item $path -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        $pythonw = $found.FullName
        break
    }
}

# If pythonw not found, try python.exe
if (-not $pythonw) {
    try {
        $pythonExe = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
        if ($pythonExe) {
            $pythonw = $pythonExe -replace "python\.exe$", "pythonw.exe"
            if (-not (Test-Path $pythonw)) {
                $pythonw = $pythonExe
            }
        }
    } catch {
        $pythonw = $null
    }
}

# Determine what to use
$targetPath = $null
$arguments = $null

if (Test-Path $exePath) {
    $targetPath = $exePath
    $arguments = ""
    Write-Host "Found executable: $targetPath"
} elseif ((Test-Path $pyScript) -and $pythonw) {
    $targetPath = $pythonw
    $arguments = "`"$pyScript`""
    Write-Host "Creating shortcut using Python: $pythonw"
    Write-Host "Script: $pyScript"
} elseif (Test-Path $pyScript) {
    Write-Host "[ERROR] Python not found!" -ForegroundColor Red
    Write-Host "Please install Python or build the .exe using build_launcher.bat"
    Read-Host "Press Enter to exit"
    exit 1
} else {
    Write-Host "[ERROR] Neither .exe nor .py file found!" -ForegroundColor Red
    Write-Host "  Looking for: $exePath"
    Write-Host "           or: $pyScript"
    Read-Host "Press Enter to exit"
    exit 1
}

# Create shortcut
$shortcutPath = Join-Path $desktopPath "HPM Launcher.lnk"

try {
    $WScriptShell = New-Object -ComObject WScript.Shell
    $shortcut = $WScriptShell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = $targetPath

    # Set arguments if we're using Python
    if ($arguments) {
        $shortcut.Arguments = $arguments
    }

    $shortcut.WorkingDirectory = $scriptDir
    $shortcut.Description = "Launch HSTL Photo Metadata System"

    # Set icon if it exists
    if (Test-Path $iconPath) {
        $shortcut.IconLocation = $iconPath
        Write-Host "Using icon: $iconPath"
    }

    $shortcut.Save()
    Write-Host "[OK] Desktop shortcut created: $shortcutPath" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now use the desktop shortcut to launch your thumbdrive script!"

} catch {
    Write-Host "[ERROR] Failed to create shortcut: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual alternative:"
    Write-Host "  1. Right-click on: $targetPath"
    Write-Host "  2. Select 'Create shortcut'"
    Write-Host "  3. Move shortcut to Desktop"
    if (Test-Path $iconPath) {
        Write-Host "  4. Right-click shortcut -> Properties -> Change Icon"
        Write-Host "     Browse to: $iconPath"
    }
}

Write-Host ""
Read-Host "Press Enter to close"

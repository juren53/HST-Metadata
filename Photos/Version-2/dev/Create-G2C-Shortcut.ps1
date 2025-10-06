# Create-G2C-Shortcut.ps1
# Script to create a desktop shortcut for G2C GUI with custom icon

# Get the current script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# Define paths
$pythonExe = "python.exe"
$g2cScript = Join-Path $scriptPath "g2c_gui.py"
$iconFile = Join-Path $scriptPath "ICON_g2c.ico"
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "G2C GUI.lnk"

# Create Shell Object
$WScriptShell = New-Object -ComObject WScript.Shell

# Create shortcut
$Shortcut = $WScriptShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = $pythonExe
$Shortcut.Arguments = "`"$g2cScript`""
$Shortcut.WorkingDirectory = $scriptPath
$Shortcut.IconLocation = $iconFile
$Shortcut.Description = "G2C GUI - Google Sheet to CSV Converter"
$Shortcut.Save()

Write-Host "Desktop shortcut created successfully!"
Write-Host "Location: $shortcutPath"

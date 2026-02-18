# HPM launcher — creates/activates venv and installs dependencies if needed

$ErrorActionPreference = "Stop"

# Resolve project directory (where this script lives)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$VenvDir = ".venv"
$Requirements = "requirements.txt"
$EntryPoint = "gui\hstl_gui.py"

# Create venv if it doesn't exist
if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating virtual environment..."
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCmd) {
        Write-Error "Error: python not found. Install Python from https://python.org"
        exit 1
    }
    python -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Error: Failed to create venv."
        exit 1
    }
}

# Activate venv
$ActivateScript = "$VenvDir\Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    & $ActivateScript
} else {
    Write-Error "Error: cannot find venv activate script"
    exit 1
}

# Install/update dependencies if requirements.txt is newer than the marker
$Marker = "$VenvDir\.deps_installed"
$installDeps = $false
if (-not (Test-Path $Marker)) {
    $installDeps = $true
} elseif ((Get-Item $Requirements).LastWriteTime -gt (Get-Item $Marker).LastWriteTime) {
    $installDeps = $true
}

if ($installDeps) {
    Write-Host "Installing dependencies..."
    pip install --upgrade pip -q
    pip install -r $Requirements -q
    New-Item -ItemType File -Path $Marker -Force | Out-Null
}

# Launch the application, passing through any command-line arguments
python $EntryPoint @args

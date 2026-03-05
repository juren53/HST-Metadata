# HPM - Installation Guide (Running from Source)

This guide covers how to download and run HPM from the Python source code. If you just want to run the application on Windows, download `HPM.exe` from the [GitHub Releases page](https://github.com/juren53/HST-Metadata/releases) instead — no Python required.

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Internet connection for package downloads

## Step 1: Get the Source Code

### Option A: Download a ZIP (no Git required)

1. Go to [https://github.com/juren53/HST-Metadata/releases](https://github.com/juren53/HST-Metadata/releases)
2. Under the latest release, click **Source code (zip)**
3. Extract the archive to your preferred location
4. Navigate into the Framework folder:

```powershell
cd HST-Metadata-<version>\Photos\Version-2\Framework
```

### Option B: Clone with Git

```powershell
git clone https://github.com/juren53/HST-Metadata.git
cd HST-Metadata\Photos\Version-2\Framework
```

## Step 2: Launch HPM

### Windows (PowerShell) — Recommended

```powershell
.\run.ps1
```

`run.ps1` automatically:
- Creates a `.venv` virtual environment (first run only)
- Installs all dependencies from `requirements.txt` if needed
- Launches the HPM GUI

If PowerShell blocks the script, run this once first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Linux / macOS / Git Bash

```bash
./run.sh
```

### WinPython Environments

If you use WinPython instead of a standard Python installation, use the HPM Launcher, which handles WinPython environment activation automatically:

```powershell
python launcher\launcher.py
```

Configure the launcher via `launcher\launcher_config.json`. See [`launcher/LAUNCHER_README.md`](launcher/LAUNCHER_README.md) for details.

### Manual Launch

```powershell
pip install -r requirements.txt
python gui\hstl_gui.py
```

## Step 3: Install ExifTool

ExifTool is required for Step 5 (metadata embedding) and must be installed separately. It is **not** installed by `run.ps1`.

### Automated Setup (Windows)

```powershell
.\tools\setup_exiftool.ps1    # PowerShell
tools\setup_exiftool.bat      # Command Prompt
```

### Manual Setup

1. Download from [https://exiftool.org/](https://exiftool.org/)
2. On Windows: rename `exiftool(-k).exe` to `exiftool.exe` and place it in a directory on your system PATH
3. Verify with: `exiftool -ver`

**macOS:**
```bash
brew install exiftool
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install libimage-exiftool-perl
```

See [notes/QUICKFIX_EXIFTOOL.md](notes/QUICKFIX_EXIFTOOL.md) for troubleshooting "ExifTool not found" errors.

## Python Dependencies

All dependencies are installed automatically by `run.ps1`. For reference, the key packages are:

| Package | Purpose |
|---------|---------|
| PyQt6 | GUI framework |
| pandas, openpyxl | Excel/CSV processing (Steps 1–2) |
| ftfy | Unicode/mojibake repair (Step 3) |
| Pillow | Image processing (Step 8 watermarking) |
| PyExifTool | Python wrapper for ExifTool (Step 5) |
| PyYAML | Configuration file parsing |
| pyqt-app-info | About dialog and app info |

## Troubleshooting

### ModuleNotFoundError
```powershell
pip install -r requirements.txt
```

### ExifTool not found
```powershell
where exiftool    # Windows
which exiftool    # macOS/Linux
```
If not found, follow Step 3 above or see [notes/QUICKFIX_EXIFTOOL.md](notes/QUICKFIX_EXIFTOOL.md).

### PyQt6 installation issues
- **Windows**: usually works without extra steps
- **macOS**: `brew install qt` may be needed
- **Linux (Ubuntu/Debian)**: `sudo apt-get install python3-pyqt6`

### Dependency conflicts
Use a virtual environment (which `run.ps1` creates automatically):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python gui\hstl_gui.py
```

## Updating to a Newer Version

If you cloned with Git:
```powershell
git pull
.\run.ps1
```

Or use the built-in **Help → Check for Updates** menu in the HPM application.

To download a specific older version, see [`docs/PROCEDURE_HPM-download-specific-version.md`](docs/PROCEDURE_HPM-download-specific-version.md).

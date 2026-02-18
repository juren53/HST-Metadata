#!/bin/bash
# HPM launcher — creates/activates venv and installs dependencies if needed

set -e

# Resolve project directory (where this script lives)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR=".venv"
REQUIREMENTS="requirements.txt"
ENTRY_POINT="gui/hstl_gui.py"

# Create venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    if ! python3 -m venv "$VENV_DIR"; then
        echo "Error: Failed to create venv. Install python3-venv:"
        echo "  pkexec apt install python3-venv"
        exit 1
    fi
fi

# Activate venv (works on Linux/macOS and Git Bash on Windows)
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    source "$VENV_DIR/Scripts/activate"
else
    echo "Error: cannot find venv activate script" >&2
    exit 1
fi

# Install/update dependencies if requirements.txt is newer than the marker
MARKER="$VENV_DIR/.deps_installed"
if [ ! -f "$MARKER" ] || [ "$REQUIREMENTS" -nt "$MARKER" ]; then
    echo "Installing dependencies..."
    pip install --upgrade pip -q
    pip install -r "$REQUIREMENTS" -q
    touch "$MARKER"
fi

# Launch the application, passing through any command-line arguments
python3 "$ENTRY_POINT" "$@"

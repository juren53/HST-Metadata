#!/bin/bash
# HPM launcher — creates/activates venv and installs dependencies if needed

set -e

# --- CONFIGURATION ---
APP_NAME="HPM"                    # Display name shown in status messages
ENTRY_POINT="gui/hstl_gui.py"    # Main Python script to run
VENV_DIR=".venv"                  # Virtual environment directory name
REQUIREMENTS="requirements.txt"   # Pip requirements file
# --- END CONFIGURATION ---

# Resolve project directory (where this script lives)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if an existing venv's base Python is still present.
# Reads pyvenv.cfg directly — never runs the (potentially broken) venv Python.
test_venv_valid() {
    local venv_path="$1"
    local cfg="$venv_path/pyvenv.cfg"
    [ -f "$cfg" ] || return 1

    local home_line
    home_line=$(grep -E "^home\s*=" "$cfg" 2>/dev/null) || return 1
    local python_home
    python_home=$(echo "$home_line" | sed 's/^home\s*=\s*//')

    # Check for python3 or python binary in the recorded home directory
    [ -x "$python_home/python3" ] || [ -x "$python_home/python" ]
}

# Find a working system Python, bypassing any currently activated (possibly broken) venv.
# Priority: python3 > python > common paths
find_python() {
    # 1. python3 — standard on Linux/macOS
    if command -v python3 &>/dev/null; then
        python3 --version &>/dev/null && echo "python3" && return
    fi

    # 2. python — fallback
    if command -v python &>/dev/null; then
        python --version &>/dev/null && echo "python" && return
    fi

    # 3. Common fixed paths (bypasses PATH issues from activated venv)
    for candidate in \
        /usr/bin/python3 \
        /usr/local/bin/python3 \
        "$HOME/.pyenv/shims/python3"; do
        if [ -x "$candidate" ]; then
            "$candidate" --version &>/dev/null && echo "$candidate" && return
        fi
    done

    return 1
}

# Wipe venv if it exists but points to a missing Python
if [ -d "$VENV_DIR" ] && ! test_venv_valid "$VENV_DIR"; then
    echo "[$APP_NAME] Existing venv has a broken Python reference, recreating..."
    rm -rf "$VENV_DIR"
fi

# Create venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "[$APP_NAME] Creating virtual environment..."
    PYTHON_EXE=$(find_python) || {
        echo "Error: no working Python found. Install Python 3 from https://python.org" >&2
        exit 1
    }
    echo "[$APP_NAME] Using Python: $PYTHON_EXE"
    "$PYTHON_EXE" -m venv "$VENV_DIR" || {
        echo "Error: Failed to create venv. You may need to install python3-venv:" >&2
        echo "  sudo apt install python3-venv   # Debian/Ubuntu" >&2
        exit 1
    }
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
    echo "[$APP_NAME] Installing dependencies..."
    pip install --upgrade pip -q
    pip install -r "$REQUIREMENTS" -q
    touch "$MARKER"
fi

# Launch the application, passing through any command-line arguments
python "$ENTRY_POINT" "$@"

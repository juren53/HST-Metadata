"""
Thumbdrive Launcher
A robust launcher for running PowerShell scripts from a thumbdrive with comprehensive error handling.
"""

import subprocess
import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from tkinter import messagebox
import json

# Configuration file path (looks in same directory as script)
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "launcher_config.json"

# Default configuration
DEFAULT_CONFIG = {
    "drive_letter": "D:\\",
    "startup_script": "startup.ps1",
    "required_files": [
        "startup.ps1"
    ],
    "wait_for_drive_timeout": 30,
    "script_timeout": 300,
    "enable_logging": True,
    "show_success_message": False,
    "auto_retry": True
}

# Setup logging
LOG_FILE = Path.home() / "thumbdrive_launcher.log"


def setup_logging(enabled=True):
    """Setup logging configuration"""
    if enabled:
        logging.basicConfig(
            filename=LOG_FILE,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.info("=" * 60)
        logging.info("Thumbdrive Launcher started")
    else:
        logging.disable(logging.CRITICAL)


def load_config():
    """Load configuration from JSON file, create default if not exists"""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                logging.info(f"Configuration loaded from {CONFIG_FILE}")
                return config
        else:
            # Create default config file
            with open(CONFIG_FILE, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
                logging.info(f"Created default configuration at {CONFIG_FILE}")
            return DEFAULT_CONFIG
    except Exception as e:
        logging.error(f"Error loading config: {e}, using defaults")
        return DEFAULT_CONFIG


def check_drive_exists(drive):
    """Check if the specified drive exists"""
    exists = Path(drive).exists()
    logging.info(f"Drive {drive} exists: {exists}")
    return exists


def wait_for_drive(drive, timeout=30):
    """Wait for drive to become available, with optional user notification"""
    logging.info(f"Waiting up to {timeout} seconds for drive {drive}")

    for i in range(timeout):
        if check_drive_exists(drive):
            logging.info(f"Drive {drive} detected after {i} seconds")
            return True
        time.sleep(1)

    logging.warning(f"Drive {drive} not detected after {timeout} seconds")
    return False


def check_required_files(drive, required_files):
    """Check if all required files exist on the thumbdrive"""
    missing = []
    for file in required_files:
        full_path = Path(drive) / file
        if not full_path.exists():
            missing.append(file)
            logging.warning(f"Missing required file: {file}")
        else:
            logging.info(f"Found required file: {file}")

    return missing


def run_powershell_script(script_path, timeout=300):
    """Execute the PowerShell script with error handling"""
    logging.info(f"Executing PowerShell script: {script_path}")

    try:
        result = subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0:
            logging.info("PowerShell script completed successfully")
            if result.stdout:
                logging.info(f"Script output: {result.stdout}")
            return True, None
        else:
            error_msg = result.stderr if result.stderr else "Unknown error"
            logging.error(f"PowerShell script failed with return code {result.returncode}: {error_msg}")
            return False, error_msg

    except subprocess.TimeoutExpired:
        error_msg = f"Script execution timed out after {timeout} seconds"
        logging.error(error_msg)
        return False, error_msg
    except FileNotFoundError:
        error_msg = "PowerShell not found. Is PowerShell installed?"
        logging.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logging.error(error_msg)
        return False, error_msg


def main():
    """Main launcher function"""
    # Load configuration
    config = load_config()

    # Setup logging
    setup_logging(config.get("enable_logging", True))

    drive = config.get("drive_letter", "D:\\")
    startup_script = config.get("startup_script", "startup.ps1")
    required_files = config.get("required_files", ["startup.ps1"])
    wait_timeout = config.get("wait_for_drive_timeout", 30)
    script_timeout = config.get("script_timeout", 300)
    show_success = config.get("show_success_message", False)
    auto_retry = config.get("auto_retry", True)

    script_path = Path(drive) / startup_script

    # Check if drive exists, wait if configured
    if not check_drive_exists(drive):
        if auto_retry:
            # Show waiting message
            result = messagebox.askretrycancel(
                "Waiting for Thumbdrive",
                f"Drive {drive} is not available.\n\n"
                f"Please insert the thumbdrive.\n"
                f"Waiting up to {wait_timeout} seconds...\n\n"
                "Click 'Retry' to continue waiting, or 'Cancel' to exit."
            )

            if not result:
                logging.info("User cancelled operation")
                return 1

            if not wait_for_drive(drive, wait_timeout):
                messagebox.showerror(
                    "Thumbdrive Not Found",
                    f"Drive {drive} is still not available after {wait_timeout} seconds.\n\n"
                    "Please check:\n"
                    "• Thumbdrive is properly inserted\n"
                    "• Drive letter is correct\n"
                    f"• Check configuration in: {CONFIG_FILE}"
                )
                return 1
        else:
            messagebox.showerror(
                "Thumbdrive Not Found",
                f"Drive {drive} is not available.\n\n"
                "Please insert the thumbdrive and try again."
            )
            return 1

    # Check for missing required files
    missing_files = check_required_files(drive, required_files)
    if missing_files:
        messagebox.showerror(
            "Missing Required Files",
            f"The following required files are missing from {drive}:\n\n" +
            "\n".join(f"  • {f}" for f in missing_files) +
            "\n\nPlease ensure all required files are on the thumbdrive."
        )
        return 1

    # Execute the PowerShell script
    success, error_msg = run_powershell_script(script_path, script_timeout)

    if success:
        if show_success:
            messagebox.showinfo(
                "Success",
                f"Script {startup_script} completed successfully!"
            )
        return 0
    else:
        messagebox.showerror(
            "Script Execution Failed",
            f"The PowerShell script failed:\n\n{error_msg}\n\n"
            f"Check the log file for details:\n{LOG_FILE}"
        )
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        # Catch-all for any unexpected errors
        error_msg = f"Unexpected error in launcher: {str(e)}"
        logging.error(error_msg, exc_info=True)
        messagebox.showerror("Launcher Error", error_msg)
        sys.exit(1)

"""
HSTL Photo Metadata System Launcher
Launches the HPM GUI application from the local Framework directory.
"""

import subprocess
import os
import sys
import logging
from pathlib import Path
from tkinter import messagebox
import json

# Configuration file path (looks in same directory as script)
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "launcher_config.json"

# Default configuration
DEFAULT_CONFIG = {
    "base_directory": "%USERPROFILE%\\Projects\\HST-Metadata\\Photos\\Version-2\\Framework",
    "winpython_activate": "%USERPROFILE%\\winpython\\WPy64-31201b5\\scripts\\activate.bat",
    "gui_script": "gui\\hstl_gui.py",
    "script_timeout": 300,
    "enable_logging": True,
    "show_success_message": False
}

# Setup logging
LOG_FILE = Path.home() / "hpm_launcher.log"


def setup_logging(enabled=True):
    """Setup logging configuration"""
    if enabled:
        logging.basicConfig(
            filename=LOG_FILE,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.info("=" * 60)
        logging.info("HPM Launcher started")
    else:
        logging.disable(logging.CRITICAL)


def expand_env_vars(value):
    """Expand environment variables in a string"""
    if isinstance(value, str):
        return os.path.expandvars(value)
    return value


def load_config():
    """Load configuration from JSON file, create default if not exists"""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Expand environment variables in all string values
                for key, value in config.items():
                    config[key] = expand_env_vars(value)
                logging.info(f"Configuration loaded from {CONFIG_FILE}")
                return config
        else:
            # Create default config file
            with open(CONFIG_FILE, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
                logging.info(f"Created default configuration at {CONFIG_FILE}")
            # Expand environment variables in default config
            expanded_config = {}
            for key, value in DEFAULT_CONFIG.items():
                expanded_config[key] = expand_env_vars(value)
            return expanded_config
    except Exception as e:
        logging.error(f"Error loading config: {e}, using defaults")
        # Expand environment variables in default config
        expanded_config = {}
        for key, value in DEFAULT_CONFIG.items():
            expanded_config[key] = expand_env_vars(value)
        return expanded_config


def check_paths_exist(config):
    """Check if required paths exist"""
    base_dir = Path(config.get("base_directory"))
    activate_bat = Path(config.get("winpython_activate"))
    gui_script = base_dir / config.get("gui_script")
    
    missing = []
    
    if not base_dir.exists():
        missing.append(f"Base directory: {base_dir}")
        logging.error(f"Base directory not found: {base_dir}")
    else:
        logging.info(f"Base directory found: {base_dir}")
    
    if not activate_bat.exists():
        missing.append(f"WinPython activate script: {activate_bat}")
        logging.error(f"WinPython activate script not found: {activate_bat}")
    else:
        logging.info(f"WinPython activate script found: {activate_bat}")
    
    if not gui_script.exists():
        missing.append(f"GUI script: {gui_script}")
        logging.error(f"GUI script not found: {gui_script}")
    else:
        logging.info(f"GUI script found: {gui_script}")
    
    return missing


def run_hpm_application(config, timeout=300):
    """Execute the HPM application using WinPython"""
    base_dir = Path(config.get("base_directory"))
    activate_bat = config.get("winpython_activate")
    gui_script = config.get("gui_script")
    
    logging.info(f"Launching HPM application from {base_dir}")
    
    # Create a batch script that:
    # 1. Activates WinPython environment
    # 2. Changes to Framework directory
    # 3. Runs the GUI script
    batch_commands = [
        '@echo off',
        f'call "{activate_bat}"',
        f'cd /d "{base_dir}"',
        f'python {gui_script}'
    ]
    
    try:
        # Create a temporary batch file
        temp_batch = SCRIPT_DIR / "_temp_launcher.bat"
        with open(temp_batch, 'w') as f:
            f.write('\n'.join(batch_commands))
        
        logging.info(f"Created temporary batch file: {temp_batch}")
        logging.info(f"Batch commands:\n{chr(10).join(batch_commands)}")
        
        # Execute the batch file
        result = subprocess.run(
            [str(temp_batch)],
            shell=True,
            capture_output=False,
            timeout=timeout
        )
        
        # Clean up temporary batch file
        try:
            temp_batch.unlink()
        except:
            pass
        
        if result.returncode == 0:
            logging.info("HPM application launched successfully")
            return True, None
        else:
            error_msg = f"Application exited with return code {result.returncode}"
            logging.error(error_msg)
            return False, error_msg
    
    except subprocess.TimeoutExpired:
        error_msg = f"Application timed out after {timeout} seconds"
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

    script_timeout = config.get("script_timeout", 300)
    show_success = config.get("show_success_message", False)

    # Check for missing required paths
    missing_paths = check_paths_exist(config)
    if missing_paths:
        messagebox.showerror(
            "Missing Required Paths",
            f"The following required paths are missing:\n\n" +
            "\n".join(f"  • {p}" for p in missing_paths) +
            f"\n\nPlease check the configuration in:\n{CONFIG_FILE}"
        )
        return 1

    # Execute the HPM application
    success, error_msg = run_hpm_application(config, script_timeout)

    if success:
        if show_success:
            messagebox.showinfo(
                "Success",
                "HSTL Photo Metadata System launched successfully!"
            )
        return 0
    else:
        messagebox.showerror(
            "Application Launch Failed",
            f"Failed to launch HPM application:\n\n{error_msg}\n\n"
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

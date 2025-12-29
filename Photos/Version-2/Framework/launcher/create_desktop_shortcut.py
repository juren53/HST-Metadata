"""
Create a desktop shortcut for the Thumbdrive Launcher
"""

import os
import sys
from pathlib import Path


def create_desktop_shortcut():
    """Create a desktop shortcut for the launcher"""

    script_dir = Path(__file__).parent
    desktop = Path.home() / "Desktop"

    # Determine what to link to
    exe_path = script_dir / "dist" / "ThumbdriveLauncher.exe"
    py_script = script_dir / "thumbdrive_launcher.py"
    icon_path = script_dir / "thumbdrive_icon.ico"

    # Check what exists
    if exe_path.exists():
        target = exe_path
        print(f"Found executable: {target}")
    elif py_script.exists():
        # Create shortcut to Python script
        target = py_script
        print(f"Executable not found, creating shortcut to Python script: {target}")
    else:
        print("[ERROR] Error: Neither .exe nor .py file found!")
        print(f"  Looking for: {exe_path}")
        print(f"           or: {py_script}")
        return False

    # Shortcut path
    shortcut_path = desktop / "Thumbdrive Launcher.lnk"

    try:
        # Try using win32com (Windows-specific)
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.TargetPath = str(target)
            shortcut.WorkingDirectory = str(script_dir)
            shortcut.Description = "Launch PowerShell script from thumbdrive"

            # Set icon if it exists
            if icon_path.exists():
                shortcut.IconLocation = str(icon_path)
                print(f"Using icon: {icon_path}")
            elif exe_path.exists():
                # Use the exe's icon
                shortcut.IconLocation = str(target)

            shortcut.save()
            print(f"[OK] Desktop shortcut created: {shortcut_path}")
            return True

        except ImportError:
            print("\nwin32com not found. Installing pywin32...")
            import subprocess
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "pywin32"], check=True)
                print("[OK] pywin32 installed. Please run this script again.")
                return False
            except:
                print("[ERROR] Could not install pywin32.")
                print("\nAlternative: Create shortcut manually:")
                print(f"  1. Right-click on: {target}")
                print(f"  2. Select 'Create shortcut'")
                print(f"  3. Move shortcut to Desktop")
                if icon_path.exists():
                    print(f"  4. Right-click shortcut → Properties → Change Icon")
                    print(f"     Browse to: {icon_path}")
                return False

    except Exception as e:
        print(f"[ERROR] Error creating shortcut: {e}")
        return False


def main():
    """Main function"""
    print("=" * 50)
    print("Thumbdrive Launcher - Desktop Shortcut Creator")
    print("=" * 50)
    print()

    success = create_desktop_shortcut()

    print()
    if success:
        print("[OK] Setup complete!")
        print("\nYou can now launch your thumbdrive script from the desktop shortcut.")
    else:
        print("[WARNING] Setup incomplete. See messages above.")

    print()
    input("Press Enter to close...")


if __name__ == "__main__":
    main()

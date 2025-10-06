#!/usr/bin/env python3
"""
Installation script for UTF-8 encoding libraries used by g2c.py

This script installs the optional libraries that improve encoding detection and repair:
- chardet: For automatic encoding detection
- ftfy: For automatic double-encoding repair ("fix text for you")

Usage:
    python install_encoding_libs.py
"""

import subprocess
import sys

def install_package(package_name, description):
    """Install a package using pip."""
    print(f"\n📦 Installing {package_name} ({description})...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {e}")
        return False

def main():
    """Main installation function."""
    print("🚀 Installing UTF-8 Encoding Libraries for g2c.py")
    print("=" * 50)
    
    libraries = [
        ("chardet", "automatic encoding detection"),
        ("ftfy", "automatic double-encoding repair")
    ]
    
    successful = 0
    total = len(libraries)
    
    for package, description in libraries:
        if install_package(package, description):
            successful += 1
    
    print(f"\n📊 Installation Summary:")
    print(f"✅ Successfully installed: {successful}/{total} libraries")
    
    if successful == total:
        print("\n🎉 All libraries installed successfully!")
        print("Your g2c.py script now has access to:")
        print("  - Automatic encoding detection (chardet)")
        print("  - Automatic double-encoding repair (ftfy)")
        print("  - Manual artifact table (fallback)")
        print("\nThis should eliminate most manual table maintenance!")
    else:
        print(f"\n⚠️  Some libraries failed to install. The script will still work but with reduced functionality.")
        print("Missing libraries will fall back to manual artifact cleaning.")

if __name__ == "__main__":
    main()

"""
File utilities for HSTL Photo Framework

Common file operations and utilities.
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict
import shutil
import os
import csv
import subprocess


def get_exiftool_path() -> str:
    """Get the path to the exiftool executable.
    
    In frozen PyInstaller builds, returns the bundled copy in tools/.
    Otherwise, returns 'exiftool' to use the system PATH.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundled = Path(sys._MEIPASS) / 'tools' / 'exiftool.exe'
        if bundled.exists():
            return str(bundled)
    # Check framework tools/ directory (source mode)
    framework_tools = Path(__file__).parent.parent / 'tools' / 'exiftool.exe'
    if framework_tools.exists():
        return str(framework_tools)
    # Fall back to system PATH
    return 'exiftool'


class FileUtils:
    """Utility functions for file operations."""
    
    @staticmethod
    def ensure_directory(directory: Path) -> bool:
        """Ensure directory exists, create if it doesn't."""
        try:
            directory.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False
    
    @staticmethod
    def backup_file(file_path: Path, backup_suffix: str = ".bak") -> Optional[Path]:
        """Create backup of file."""
        try:
            backup_path = file_path.with_suffix(file_path.suffix + backup_suffix)
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception:
            return None
    
    @staticmethod
    def find_files(directory: Path, pattern: str) -> List[Path]:
        """Find all files matching pattern in directory."""
        try:
            return list(directory.glob(pattern))
        except Exception:
            return []
    
    @staticmethod
    def count_csv_records(csv_path: Path) -> int:
        """
        Count the number of records in a CSV file by counting Accession Numbers/ObjectNames.
        
        Args:
            csv_path: Path to the CSV file
            
        Returns:
            Number of records, 0 if file doesn't exist or is invalid
        """
        if not csv_path.exists():
            return 0
            
        try:
            with open(csv_path, 'r', encoding='utf-8', newline='') as file:
                reader = csv.DictReader(file)
                record_count = 0
                
                for row in reader:
                    # Count rows that have either Accession Number or ObjectName (case-insensitive)
                    accession_num = row.get('Accession Number', '').strip()
                    object_name = row.get('ObjectName', '').strip()
                    accession_num_alt = row.get('AccessionNumber', '').strip()
                    
                    if accession_num or object_name or accession_num_alt:
                        record_count += 1
                        
                return record_count
        except Exception:
            return 0
    
    @staticmethod
    def get_directory_size(directory: Path) -> int:
        """
        Calculate total size of a directory in bytes.
        
        Args:
            directory: Path to the directory
            
        Returns:
            Total size in bytes, 0 if directory doesn't exist or is inaccessible
        """
        if not directory.exists():
            return 0
            
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(file_path)
                    except (OSError, PermissionError):
                        # Skip files that can't be accessed
                        continue
            return total_size
        except (OSError, PermissionError):
            return 0
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string (e.g., "1.5 MB", "500 KB", "2.3 GB")
        """
        if size_bytes == 0:
            return "0 B"
            
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and unit_index < len(units) - 1:
            size /= 1024.0
            unit_index += 1
            
        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        else:
            return f"{size:.1f} {units[unit_index]}"

    @staticmethod
    def get_exiftool_info() -> Dict[str, Optional[str]]:
        """
        Get ExifTool executable path and version information.

        Returns:
            Dictionary with:
                - 'path': Path to exiftool executable, or None if not found
                - 'version': Version string, or None if not available
                - 'status': Status message ('available', 'not_found', 'error')
        """
        result = {
            'path': None,
            'version': None,
            'status': 'not_found'
        }

        # Try to find exiftool - use bundled version first, then PATH
        exiftool_path = get_exiftool_path()
        
        # If we got the default 'exiftool' string, resolve it via PATH
        if exiftool_path == 'exiftool':
            exiftool_path = shutil.which('exiftool')

        if not exiftool_path:
            # Check common Windows installation location
            local_app_data = os.environ.get('LOCALAPPDATA', '')
            if local_app_data:
                potential_path = Path(local_app_data) / 'exiftool' / 'exiftool.exe'
                if potential_path.exists():
                    exiftool_path = str(potential_path)

        if not exiftool_path:
            return result

        result['path'] = exiftool_path

        # Get version
        try:
            version_result = subprocess.run(
                [exiftool_path, '-ver'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if version_result.returncode == 0:
                result['version'] = version_result.stdout.strip()
                result['status'] = 'available'
            else:
                result['status'] = 'error'
        except subprocess.TimeoutExpired:
            result['status'] = 'error'
        except Exception:
            result['status'] = 'error'

        return result
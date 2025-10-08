"""
File utilities for HSTL Photo Framework

Common file operations and utilities.
"""

from pathlib import Path
from typing import List, Optional
import shutil


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
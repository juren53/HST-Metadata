"""
Path Manager for HSTL Photo Framework

Centralized management of all directory paths used by the framework.
"""

from pathlib import Path
from typing import Optional, Dict, Any


class PathManager:
    """Manages all file and directory paths for the framework."""
    
    def __init__(self, framework_root: Path, data_directory: Optional[str] = None):
        """
        Initialize path manager.
        
        Args:
            framework_root: Root directory of the framework
            data_directory: Base data directory for the project
        """
        self.framework_root = Path(framework_root)
        self.data_directory = Path(data_directory) if data_directory else None
        
    def get_data_path(self, relative_path: str = "") -> Optional[Path]:
        """Get path within the data directory."""
        if not self.data_directory:
            return None
        
        if relative_path:
            return self.data_directory / relative_path
        return self.data_directory
    
    def get_input_tiff_dir(self) -> Optional[Path]:
        """Get input TIFF directory."""
        return self.get_data_path("input/tiff")
    
    def get_output_csv_dir(self) -> Optional[Path]:
        """Get output CSV directory."""
        return self.get_data_path("output/csv")
    
    def get_logs_dir(self) -> Optional[Path]:
        """Get logs directory."""
        return self.get_data_path("logs")
    
    def get_reports_dir(self) -> Optional[Path]:
        """Get reports directory."""
        return self.get_data_path("reports")
    
    def validate_paths(self) -> tuple[bool, list]:
        """Validate that required paths exist."""
        errors = []
        
        if not self.data_directory:
            errors.append("Data directory not set")
            return False, errors
        
        if not self.data_directory.exists():
            errors.append(f"Data directory does not exist: {self.data_directory}")
        
        return len(errors) == 0, errors
"""
Validation utilities for HSTL Photo Framework

Provides validation functionality for steps, files, and configurations.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


class ValidationResult:
    """Result of a validation operation."""
    
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, error: str):
        """Add an error to the result."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add a warning to the result."""
        self.warnings.append(warning)
    
    def __bool__(self):
        return self.is_valid


class Validator:
    """Validation utilities for the framework."""
    
    @staticmethod
    def validate_file_exists(file_path: Path) -> ValidationResult:
        """Validate that a file exists."""
        result = ValidationResult(True)
        
        if not file_path.exists():
            result.add_error(f"File does not exist: {file_path}")
        elif not file_path.is_file():
            result.add_error(f"Path is not a file: {file_path}")
        
        return result
    
    @staticmethod
    def validate_directory_exists(dir_path: Path) -> ValidationResult:
        """Validate that a directory exists."""
        result = ValidationResult(True)
        
        if not dir_path.exists():
            result.add_error(f"Directory does not exist: {dir_path}")
        elif not dir_path.is_dir():
            result.add_error(f"Path is not a directory: {dir_path}")
        
        return result
    
    @staticmethod
    def validate_file_count(directory: Path, pattern: str, expected_count: int) -> ValidationResult:
        """Validate file count in directory matches expected."""
        result = ValidationResult(True)
        
        if not directory.exists():
            result.add_error(f"Directory does not exist: {directory}")
            return result
        
        files = list(directory.glob(pattern))
        actual_count = len(files)
        
        if actual_count != expected_count:
            result.add_error(
                f"Expected {expected_count} files matching '{pattern}', "
                f"found {actual_count} in {directory}"
            )
        
        return result
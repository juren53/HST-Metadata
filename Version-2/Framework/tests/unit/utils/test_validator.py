"""
Unit tests for Validator.

Tests validation utilities for files, directories, and configurations.
"""

import pytest
from pathlib import Path

from utils.validator import Validator, ValidationResult


class TestValidationResult:
    """Tests for ValidationResult class."""

    @pytest.mark.unit
    def test_validation_result_init_valid(self):
        """ValidationResult can be created as valid."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []

    @pytest.mark.unit
    def test_validation_result_init_invalid(self):
        """ValidationResult can be created as invalid with errors."""
        result = ValidationResult(is_valid=False, errors=["Error 1", "Error 2"])
        assert result.is_valid is False
        assert len(result.errors) == 2

    @pytest.mark.unit
    def test_validation_result_add_error(self):
        """Adding error sets is_valid to False."""
        result = ValidationResult(is_valid=True)
        result.add_error("New error")
        assert result.is_valid is False
        assert "New error" in result.errors

    @pytest.mark.unit
    def test_validation_result_add_warning(self):
        """Adding warning doesn't change is_valid."""
        result = ValidationResult(is_valid=True)
        result.add_warning("Warning message")
        assert result.is_valid is True
        assert "Warning message" in result.warnings

    @pytest.mark.unit
    def test_validation_result_bool(self):
        """ValidationResult can be used as boolean."""
        valid_result = ValidationResult(is_valid=True)
        invalid_result = ValidationResult(is_valid=False)

        assert bool(valid_result) is True
        assert bool(invalid_result) is False

        # Can use in if statements
        if valid_result:
            passed = True
        else:
            passed = False
        assert passed is True


class TestValidatorFileExists:
    """Tests for file existence validation."""

    @pytest.mark.unit
    def test_validate_file_exists(self, temp_dir):
        """Validate existing file passes."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        result = Validator.validate_file_exists(test_file)
        assert result.is_valid is True

    @pytest.mark.unit
    def test_validate_file_not_exists(self, temp_dir):
        """Validate non-existent file fails."""
        missing_file = temp_dir / "missing.txt"

        result = Validator.validate_file_exists(missing_file)
        assert result.is_valid is False
        assert any("does not exist" in e for e in result.errors)

    @pytest.mark.unit
    def test_validate_file_is_directory(self, temp_dir):
        """Validate directory as file fails."""
        result = Validator.validate_file_exists(temp_dir)
        assert result.is_valid is False
        assert any("not a file" in e for e in result.errors)


class TestValidatorDirectoryExists:
    """Tests for directory existence validation."""

    @pytest.mark.unit
    def test_validate_directory_exists(self, temp_dir):
        """Validate existing directory passes."""
        result = Validator.validate_directory_exists(temp_dir)
        assert result.is_valid is True

    @pytest.mark.unit
    def test_validate_directory_not_exists(self, temp_dir):
        """Validate non-existent directory fails."""
        missing_dir = temp_dir / "missing"

        result = Validator.validate_directory_exists(missing_dir)
        assert result.is_valid is False
        assert any("does not exist" in e for e in result.errors)

    @pytest.mark.unit
    def test_validate_directory_is_file(self, temp_dir):
        """Validate file as directory fails."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        result = Validator.validate_directory_exists(test_file)
        assert result.is_valid is False
        assert any("not a directory" in e for e in result.errors)


class TestValidatorFileCount:
    """Tests for file count validation."""

    @pytest.mark.unit
    def test_validate_file_count_match(self, temp_dir):
        """Validate matching file count passes."""
        # Create 3 .txt files
        for i in range(3):
            (temp_dir / f"file{i}.txt").write_text("content")

        result = Validator.validate_file_count(temp_dir, "*.txt", 3)
        assert result.is_valid is True

    @pytest.mark.unit
    def test_validate_file_count_mismatch(self, temp_dir):
        """Validate mismatched file count fails."""
        # Create 2 files but expect 5
        (temp_dir / "file1.txt").write_text("content")
        (temp_dir / "file2.txt").write_text("content")

        result = Validator.validate_file_count(temp_dir, "*.txt", 5)
        assert result.is_valid is False
        assert any("Expected 5" in e for e in result.errors)

    @pytest.mark.unit
    def test_validate_file_count_directory_not_exists(self, temp_dir):
        """Validate file count in non-existent directory fails."""
        missing_dir = temp_dir / "missing"

        result = Validator.validate_file_count(missing_dir, "*.txt", 0)
        assert result.is_valid is False
        assert any("does not exist" in e for e in result.errors)

    @pytest.mark.unit
    def test_validate_file_count_pattern_filter(self, temp_dir):
        """Validate file count respects pattern."""
        # Create mixed files
        (temp_dir / "file1.txt").write_text("content")
        (temp_dir / "file2.txt").write_text("content")
        (temp_dir / "file3.csv").write_text("content")

        # Only count .txt files
        result = Validator.validate_file_count(temp_dir, "*.txt", 2)
        assert result.is_valid is True

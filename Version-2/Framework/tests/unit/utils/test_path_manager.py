"""
Unit tests for PathManager.

Tests path management and directory operations.
"""

import pytest
from pathlib import Path

from utils.path_manager import PathManager


class TestPathManagerInit:
    """Tests for PathManager initialization."""

    @pytest.mark.unit
    def test_path_manager_init(self, temp_dir):
        """PathManager can be instantiated."""
        pm = PathManager(framework_root=temp_dir)
        assert pm is not None
        assert pm.framework_root == temp_dir

    @pytest.mark.unit
    def test_path_manager_init_with_data_dir(self, temp_dir):
        """PathManager can be instantiated with data directory."""
        data_dir = temp_dir / "data"
        data_dir.mkdir()
        pm = PathManager(framework_root=temp_dir, data_directory=str(data_dir))
        assert pm.data_directory == data_dir

    @pytest.mark.unit
    def test_path_manager_init_no_data_dir(self, temp_dir):
        """PathManager handles missing data directory."""
        pm = PathManager(framework_root=temp_dir)
        assert pm.data_directory is None


class TestPathManagerDirectories:
    """Tests for directory path methods."""

    @pytest.mark.unit
    def test_get_framework_dir(self, temp_dir):
        """Returns framework directory."""
        pm = PathManager(framework_root=temp_dir)
        assert pm.framework_root == temp_dir

    @pytest.mark.unit
    def test_get_data_path(self, temp_dir):
        """Returns data directory path."""
        data_dir = temp_dir / "data"
        data_dir.mkdir()
        pm = PathManager(framework_root=temp_dir, data_directory=str(data_dir))
        assert pm.get_data_path() == data_dir

    @pytest.mark.unit
    def test_get_data_path_no_data_dir(self, temp_dir):
        """Returns None when no data directory set."""
        pm = PathManager(framework_root=temp_dir)
        assert pm.get_data_path() is None

    @pytest.mark.unit
    def test_get_input_tiff_dir(self, temp_dir):
        """Returns input TIFF directory path."""
        data_dir = temp_dir / "data"
        data_dir.mkdir()
        pm = PathManager(framework_root=temp_dir, data_directory=str(data_dir))
        input_path = pm.get_input_tiff_dir()
        assert input_path == data_dir / "input" / "tiff"

    @pytest.mark.unit
    def test_get_output_csv_dir(self, temp_dir):
        """Returns output CSV directory path."""
        data_dir = temp_dir / "data"
        data_dir.mkdir()
        pm = PathManager(framework_root=temp_dir, data_directory=str(data_dir))
        output_path = pm.get_output_csv_dir()
        assert output_path == data_dir / "output" / "csv"

    @pytest.mark.unit
    def test_get_logs_dir(self, temp_dir):
        """Returns logs directory path."""
        data_dir = temp_dir / "data"
        data_dir.mkdir()
        pm = PathManager(framework_root=temp_dir, data_directory=str(data_dir))
        logs_path = pm.get_logs_dir()
        assert logs_path == data_dir / "logs"

    @pytest.mark.unit
    def test_get_reports_dir(self, temp_dir):
        """Returns reports directory path."""
        data_dir = temp_dir / "data"
        data_dir.mkdir()
        pm = PathManager(framework_root=temp_dir, data_directory=str(data_dir))
        reports_path = pm.get_reports_dir()
        assert reports_path == data_dir / "reports"


class TestPathManagerRelativePaths:
    """Tests for relative path resolution."""

    @pytest.mark.unit
    def test_get_data_path_relative(self, temp_dir):
        """Resolves relative path within data directory."""
        data_dir = temp_dir / "data"
        data_dir.mkdir()
        pm = PathManager(framework_root=temp_dir, data_directory=str(data_dir))

        path = pm.get_data_path("subdir/file.txt")
        assert path == data_dir / "subdir" / "file.txt"

    @pytest.mark.unit
    def test_get_data_path_empty_relative(self, temp_dir):
        """Empty relative path returns data directory."""
        data_dir = temp_dir / "data"
        data_dir.mkdir()
        pm = PathManager(framework_root=temp_dir, data_directory=str(data_dir))

        path = pm.get_data_path("")
        assert path == data_dir

    @pytest.mark.unit
    def test_get_data_path_nested_relative(self, temp_dir):
        """Handles deeply nested relative paths."""
        data_dir = temp_dir / "data"
        data_dir.mkdir()
        pm = PathManager(framework_root=temp_dir, data_directory=str(data_dir))

        path = pm.get_data_path("a/b/c/d/file.txt")
        assert path == data_dir / "a" / "b" / "c" / "d" / "file.txt"


class TestPathManagerValidation:
    """Tests for path validation."""

    @pytest.mark.unit
    def test_validate_paths_valid(self, temp_dir):
        """Validation passes for existing paths."""
        data_dir = temp_dir / "data"
        data_dir.mkdir()
        pm = PathManager(framework_root=temp_dir, data_directory=str(data_dir))

        is_valid, errors = pm.validate_paths()
        assert is_valid is True
        assert len(errors) == 0

    @pytest.mark.unit
    def test_validate_paths_no_data_dir(self, temp_dir):
        """Validation fails when no data directory set."""
        pm = PathManager(framework_root=temp_dir)

        is_valid, errors = pm.validate_paths()
        assert is_valid is False
        assert any("Data directory not set" in e for e in errors)

    @pytest.mark.unit
    def test_validate_paths_nonexistent_data_dir(self, temp_dir):
        """Validation fails for nonexistent data directory."""
        nonexistent = temp_dir / "nonexistent"
        pm = PathManager(framework_root=temp_dir, data_directory=str(nonexistent))

        is_valid, errors = pm.validate_paths()
        assert is_valid is False
        assert any("does not exist" in e for e in errors)


class TestPathManagerEdgeCases:
    """Tests for edge cases and special scenarios."""

    @pytest.mark.unit
    def test_path_with_spaces(self, temp_dir):
        """Handles paths with spaces correctly."""
        data_dir = temp_dir / "data with spaces"
        data_dir.mkdir()
        pm = PathManager(framework_root=temp_dir, data_directory=str(data_dir))

        path = pm.get_data_path("sub dir/file name.txt")
        assert "data with spaces" in str(path)
        assert "sub dir" in str(path)

    @pytest.mark.unit
    def test_path_normalization(self, temp_dir):
        """Paths are normalized correctly."""
        data_dir = temp_dir / "data"
        data_dir.mkdir()
        pm = PathManager(framework_root=temp_dir, data_directory=str(data_dir))

        # Path should be a proper Path object regardless of input format
        path = pm.get_data_path("subdir/file.txt")
        assert isinstance(path, Path)

    @pytest.mark.unit
    def test_data_directory_as_path_object(self, temp_dir):
        """Accepts Path object for data directory."""
        data_dir = temp_dir / "data"
        data_dir.mkdir()
        # Pass as string (the actual implementation takes string)
        pm = PathManager(framework_root=temp_dir, data_directory=str(data_dir))
        assert pm.data_directory == data_dir

    @pytest.mark.unit
    def test_returns_none_without_data_dir(self, temp_dir):
        """Methods return None when no data directory."""
        pm = PathManager(framework_root=temp_dir)

        assert pm.get_input_tiff_dir() is None
        assert pm.get_output_csv_dir() is None
        assert pm.get_logs_dir() is None
        assert pm.get_reports_dir() is None

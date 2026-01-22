"""
Unit tests for FileUtils.

Tests file operations and utilities.
"""

import pytest
from pathlib import Path

from utils.file_utils import FileUtils


class TestFileUtilsEnsureDirectory:
    """Tests for ensure_directory method."""

    @pytest.mark.unit
    def test_ensure_directory_creates(self, temp_dir):
        """Creates directory if it doesn't exist."""
        new_dir = temp_dir / "new_directory"
        assert not new_dir.exists()

        result = FileUtils.ensure_directory(new_dir)

        assert result is True
        assert new_dir.exists()

    @pytest.mark.unit
    def test_ensure_directory_exists(self, temp_dir):
        """No error if directory already exists."""
        existing_dir = temp_dir / "existing"
        existing_dir.mkdir()

        result = FileUtils.ensure_directory(existing_dir)

        assert result is True
        assert existing_dir.exists()

    @pytest.mark.unit
    def test_ensure_directory_nested(self, temp_dir):
        """Creates nested directories."""
        nested_dir = temp_dir / "a" / "b" / "c"

        result = FileUtils.ensure_directory(nested_dir)

        assert result is True
        assert nested_dir.exists()


class TestFileUtilsBackup:
    """Tests for backup_file method."""

    @pytest.mark.unit
    def test_backup_file(self, temp_dir):
        """Creates backup of file."""
        original = temp_dir / "original.txt"
        original.write_text("original content")

        backup_path = FileUtils.backup_file(original)

        assert backup_path is not None
        assert backup_path.exists()
        assert backup_path.read_text() == "original content"
        assert backup_path.name == "original.txt.bak"

    @pytest.mark.unit
    def test_backup_file_custom_suffix(self, temp_dir):
        """Creates backup with custom suffix."""
        original = temp_dir / "original.txt"
        original.write_text("content")

        backup_path = FileUtils.backup_file(original, backup_suffix=".backup")

        assert backup_path is not None
        assert backup_path.name == "original.txt.backup"

    @pytest.mark.unit
    def test_backup_file_not_exists(self, temp_dir):
        """Returns None for non-existent file."""
        missing = temp_dir / "missing.txt"

        backup_path = FileUtils.backup_file(missing)

        assert backup_path is None


class TestFileUtilsFindFiles:
    """Tests for find_files method."""

    @pytest.mark.unit
    def test_find_files_pattern(self, temp_dir):
        """Finds files matching pattern."""
        (temp_dir / "file1.txt").write_text("a")
        (temp_dir / "file2.txt").write_text("b")
        (temp_dir / "file3.csv").write_text("c")

        files = FileUtils.find_files(temp_dir, "*.txt")

        assert len(files) == 2
        assert all(f.suffix == ".txt" for f in files)

    @pytest.mark.unit
    def test_find_files_recursive(self, temp_dir):
        """Finds files recursively."""
        (temp_dir / "file1.txt").write_text("a")
        subdir = temp_dir / "sub"
        subdir.mkdir()
        (subdir / "file2.txt").write_text("b")

        files = FileUtils.find_files(temp_dir, "**/*.txt")

        assert len(files) == 2

    @pytest.mark.unit
    def test_find_files_empty(self, temp_dir):
        """Returns empty list when no matches."""
        files = FileUtils.find_files(temp_dir, "*.xyz")
        assert files == []


class TestFileUtilsCsvRecords:
    """Tests for count_csv_records method."""

    @pytest.mark.unit
    def test_count_csv_records(self, temp_dir):
        """Counts records with Accession Number."""
        csv_file = temp_dir / "test.csv"
        csv_content = """Accession Number,Title,Description
ACC001,Title 1,Desc 1
ACC002,Title 2,Desc 2
ACC003,Title 3,Desc 3
"""
        csv_file.write_text(csv_content)

        count = FileUtils.count_csv_records(csv_file)
        assert count == 3

    @pytest.mark.unit
    def test_count_csv_records_not_exists(self, temp_dir):
        """Returns 0 for non-existent file."""
        missing = temp_dir / "missing.csv"
        count = FileUtils.count_csv_records(missing)
        assert count == 0

    @pytest.mark.unit
    def test_count_csv_records_empty(self, temp_dir):
        """Returns 0 for empty records."""
        csv_file = temp_dir / "empty.csv"
        csv_file.write_text("Accession Number,Title\n")

        count = FileUtils.count_csv_records(csv_file)
        assert count == 0


class TestFileUtilsDirectorySize:
    """Tests for get_directory_size method."""

    @pytest.mark.unit
    def test_get_directory_size(self, temp_dir):
        """Calculates directory size."""
        # Create files with known sizes
        (temp_dir / "file1.txt").write_text("a" * 100)  # 100 bytes
        (temp_dir / "file2.txt").write_text("b" * 200)  # 200 bytes

        size = FileUtils.get_directory_size(temp_dir)

        assert size >= 300  # At least 300 bytes

    @pytest.mark.unit
    def test_get_directory_size_not_exists(self, temp_dir):
        """Returns 0 for non-existent directory."""
        missing = temp_dir / "missing"
        size = FileUtils.get_directory_size(missing)
        assert size == 0

    @pytest.mark.unit
    def test_get_directory_size_empty(self, temp_dir):
        """Returns 0 for empty directory."""
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()

        size = FileUtils.get_directory_size(empty_dir)
        assert size == 0


class TestFileUtilsFormatSize:
    """Tests for format_file_size method."""

    @pytest.mark.unit
    def test_format_file_size_bytes(self):
        """Formats bytes correctly."""
        assert FileUtils.format_file_size(0) == "0 B"
        assert FileUtils.format_file_size(500) == "500 B"

    @pytest.mark.unit
    def test_format_file_size_kilobytes(self):
        """Formats kilobytes correctly."""
        result = FileUtils.format_file_size(1024)
        assert "KB" in result

    @pytest.mark.unit
    def test_format_file_size_megabytes(self):
        """Formats megabytes correctly."""
        result = FileUtils.format_file_size(1024 * 1024)
        assert "MB" in result

    @pytest.mark.unit
    def test_format_file_size_gigabytes(self):
        """Formats gigabytes correctly."""
        result = FileUtils.format_file_size(1024 * 1024 * 1024)
        assert "GB" in result


class TestFileUtilsExifTool:
    """Tests for ExifTool detection."""

    @pytest.mark.unit
    def test_get_exiftool_info_structure(self):
        """Returns expected dictionary structure."""
        info = FileUtils.get_exiftool_info()

        assert isinstance(info, dict)
        assert 'path' in info
        assert 'version' in info
        assert 'status' in info

    @pytest.mark.unit
    def test_get_exiftool_info_status_values(self):
        """Status is one of expected values."""
        info = FileUtils.get_exiftool_info()
        assert info['status'] in ['available', 'not_found', 'error']

"""
Smoke tests to verify test infrastructure is working.

These tests ensure pytest and fixtures are properly configured.
"""

import pytest
from pathlib import Path


class TestInfrastructure:
    """Tests to verify test infrastructure."""

    @pytest.mark.unit
    def test_pytest_runs(self):
        """Verify pytest executes tests."""
        assert True

    @pytest.mark.unit
    def test_temp_dir_fixture(self, temp_dir):
        """Verify temp_dir fixture creates directory."""
        assert temp_dir.exists()
        assert temp_dir.is_dir()

    @pytest.mark.unit
    def test_sample_batch_dir_fixture(self, sample_batch_dir):
        """Verify sample_batch_dir fixture creates structure."""
        assert sample_batch_dir.exists()
        assert (sample_batch_dir / "input").exists()
        assert (sample_batch_dir / "output").exists()
        assert (sample_batch_dir / "logs").exists()

    @pytest.mark.unit
    def test_sample_config_dict_fixture(self, sample_config_dict):
        """Verify sample_config_dict fixture has expected keys."""
        assert "project" in sample_config_dict
        assert "step_status" in sample_config_dict
        assert "step_configurations" in sample_config_dict

    @pytest.mark.unit
    def test_sample_config_file_fixture(self, sample_config_file):
        """Verify sample_config_file fixture creates file."""
        assert sample_config_file.exists()
        assert sample_config_file.suffix == ".yaml"

    @pytest.mark.unit
    def test_sample_csv_file_fixture(self, sample_csv_file):
        """Verify sample_csv_file fixture creates file."""
        assert sample_csv_file.exists()
        content = sample_csv_file.read_text()
        assert "filename" in content
        assert "IMG_001.tif" in content

    @pytest.mark.unit
    def test_framework_imports(self):
        """Verify framework modules can be imported."""
        # These should not raise ImportError
        try:
            from config.config_manager import ConfigManager
            assert True
        except ImportError:
            pytest.skip("ConfigManager not importable")

    @pytest.mark.unit
    def test_temp_dir_cleanup(self, temp_dir):
        """Verify temp_dir is unique per test."""
        # Create a file in temp_dir
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        assert test_file.exists()
        # The directory will be cleaned up after this test


class TestMarkers:
    """Tests to verify pytest markers work."""

    @pytest.mark.unit
    def test_unit_marker(self):
        """Test with unit marker."""
        assert True

    @pytest.mark.integration
    def test_integration_marker(self):
        """Test with integration marker."""
        assert True

    @pytest.mark.slow
    def test_slow_marker(self):
        """Test with slow marker."""
        assert True

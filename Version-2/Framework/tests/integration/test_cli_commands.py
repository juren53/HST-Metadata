"""
Integration tests for CLI Commands.

Tests command-line interface functionality.
"""

import pytest
import sys
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

# Import the framework module components
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hstl_framework import (
    HSLTFramework,
    create_parser,
    parse_steps_argument,
    FRAMEWORK_VERSION,
    SUPPORTED_STEPS,
)
from utils.batch_registry import BatchRegistry


@pytest.fixture
def framework():
    """Create a fresh framework instance."""
    return HSLTFramework()


@pytest.fixture
def registry_dir(temp_dir):
    """Create a directory for test registry."""
    reg_dir = temp_dir / "config"
    reg_dir.mkdir()
    return reg_dir


@pytest.fixture(autouse=True)
def isolate_registry(temp_dir, monkeypatch):
    """
    Automatically isolate all tests from production BatchRegistry.

    This fixture runs automatically for every test in this module,
    ensuring tests never pollute the production registry.
    """
    # Create isolated registry directory
    reg_dir = temp_dir / "isolated_config"
    reg_dir.mkdir(exist_ok=True)
    registry_path = reg_dir / "batch_registry.yaml"

    # Store original init
    original_init = BatchRegistry.__init__

    def patched_init(self, registry_path_arg=None):
        # Always use the isolated test registry
        original_init(self, registry_path=registry_path)

    monkeypatch.setattr(BatchRegistry, '__init__', patched_init)

    yield registry_path

    # Cleanup is automatic via temp_dir fixture


@pytest.fixture
def clean_registry(isolate_registry):
    """Alias for backward compatibility - returns the isolated registry path."""
    return isolate_registry


class TestCLIParser:
    """Tests for CLI argument parser."""

    @pytest.mark.integration
    def test_cli_help(self, capsys):
        """--help shows usage."""
        parser = create_parser()

        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(['--help'])

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert 'HSTL Photo Framework' in captured.out

    @pytest.mark.integration
    def test_cli_version(self, capsys):
        """--version shows version."""
        parser = create_parser()

        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(['--version'])

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert FRAMEWORK_VERSION in captured.out


class TestCLIInitCommand:
    """Tests for init command."""

    @pytest.mark.integration
    def test_cli_init(self, temp_dir, framework):
        """init command works."""
        data_dir = temp_dir / "new_project"

        result = framework.init_project(
            data_dir=str(data_dir),
            project_name="Test Project"
        )

        assert result is True
        assert data_dir.exists()
        assert (data_dir / "config" / "project_config.yaml").exists()

    @pytest.mark.integration
    def test_cli_init_creates_structure(self, temp_dir, framework):
        """init creates project structure."""
        data_dir = temp_dir / "structured_project"

        framework.init_project(
            data_dir=str(data_dir),
            project_name="Structured Project"
        )

        # Check all expected directories
        expected_dirs = [
            "input/tiff",
            "input/spreadsheet",
            "output/csv",
            "output/tiff_processed",
            "output/jpeg",
            "output/jpeg_resized",
            "output/jpeg_watermarked",
            "reports",
            "logs",
            "config",
        ]

        for dir_path in expected_dirs:
            assert (data_dir / dir_path).exists(), f"Missing: {dir_path}"

    @pytest.mark.integration
    def test_cli_init_creates_config(self, temp_dir, framework):
        """init creates default config."""
        data_dir = temp_dir / "config_project"

        framework.init_project(
            data_dir=str(data_dir),
            project_name="Config Project"
        )

        config_path = data_dir / "config" / "project_config.yaml"
        assert config_path.exists()

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert config['project']['name'] == "Config Project"
        assert 'steps_completed' in config


class TestCLIRunCommand:
    """Tests for run command."""

    @pytest.mark.integration
    def test_parse_steps_single(self):
        """Parse single step number."""
        steps = parse_steps_argument("3")
        assert steps == [3]

    @pytest.mark.integration
    def test_parse_steps_range(self):
        """Parse step range."""
        steps = parse_steps_argument("1-3")
        assert steps == [1, 2, 3]

    @pytest.mark.integration
    def test_parse_steps_list(self):
        """Parse comma-separated steps."""
        steps = parse_steps_argument("2,4,6")
        assert steps == [2, 4, 6]

    @pytest.mark.integration
    def test_parse_steps_mixed(self):
        """Parse mixed range and list."""
        steps = parse_steps_argument("1-3,5,7-8")
        assert steps == [1, 2, 3, 5, 7, 8]

    @pytest.mark.integration
    def test_parse_steps_deduplication(self):
        """Duplicate steps are removed."""
        steps = parse_steps_argument("1,1,2,2,3")
        assert steps == [1, 2, 3]


class TestCLIConfigCommand:
    """Tests for config command."""

    @pytest.mark.integration
    def test_cli_config_list(self, temp_dir, framework):
        """config --list shows config."""
        # Initialize a project first
        data_dir = temp_dir / "config_test"
        framework.init_project(str(data_dir), "Config Test")

        # Load the config
        config_path = data_dir / "config" / "project_config.yaml"
        framework.initialize(config_path)

        # list_config should return True
        result = framework.list_config()
        assert result is True

    @pytest.mark.integration
    def test_cli_config_set(self, temp_dir, framework):
        """config --set updates config."""
        # Initialize project
        data_dir = temp_dir / "config_set_test"
        framework.init_project(str(data_dir), "Set Test")

        config_path = data_dir / "config" / "project_config.yaml"
        framework.initialize(config_path)

        # Set a config value
        result = framework.set_config("project.description", "Test description")
        assert result is True

        # Verify it was set
        assert framework.config_manager.get("project.description") == "Test description"


class TestCLIValidateCommand:
    """Tests for validate command."""

    @pytest.mark.integration
    def test_cli_validate(self, temp_dir, framework):
        """validate checks project."""
        data_dir = temp_dir / "validate_test"
        framework.init_project(str(data_dir), "Validate Test")

        config_path = data_dir / "config" / "project_config.yaml"
        framework.initialize(config_path)

        result = framework.validate()
        assert result is True

    @pytest.mark.integration
    def test_cli_validate_preflight(self, temp_dir, framework):
        """validate --pre-flight runs checks."""
        data_dir = temp_dir / "preflight_test"
        framework.init_project(str(data_dir), "Preflight Test")

        config_path = data_dir / "config" / "project_config.yaml"
        framework.initialize(config_path)

        result = framework.validate(pre_flight=True)
        assert result is True


class TestCLIBatchesCommand:
    """Tests for batches command."""

    @pytest.mark.integration
    def test_cli_batches_list(self, temp_dir, framework, clean_registry):
        """batches lists all batches."""
        # Create some batches
        for i in range(3):
            data_dir = temp_dir / f"batch_{i}"
            framework.init_project(str(data_dir), f"Batch {i}")

        result = framework.list_batches()
        assert result is True


class TestCLIBatchCommand:
    """Tests for batch management commands."""

    @pytest.mark.integration
    def test_cli_batch_complete(self, temp_dir, framework, clean_registry):
        """batch complete marks complete."""
        # Create a batch
        data_dir = temp_dir / "complete_test"
        framework.init_project(str(data_dir), "Complete Test")

        result = framework.complete_batch("complete_test")
        assert result is True

        # Verify status
        registry = BatchRegistry()
        batch = registry.get_batch("complete_test")
        assert batch['status'] == 'completed'

    @pytest.mark.integration
    def test_cli_batch_archive(self, temp_dir, framework, clean_registry):
        """batch archive archives batch."""
        # Create a batch
        data_dir = temp_dir / "archive_test"
        framework.init_project(str(data_dir), "Archive Test")

        result = framework.archive_batch("archive_test")
        assert result is True

        # Verify status
        registry = BatchRegistry()
        batch = registry.get_batch("archive_test")
        assert batch['status'] == 'archived'

    @pytest.mark.integration
    def test_cli_batch_reactivate(self, temp_dir, framework, clean_registry):
        """batch reactivate reactivates batch."""
        # Create and archive a batch
        data_dir = temp_dir / "reactivate_test"
        framework.init_project(str(data_dir), "Reactivate Test")
        framework.archive_batch("reactivate_test")

        # Reactivate
        result = framework.reactivate_batch("reactivate_test")
        assert result is True

        # Verify status
        registry = BatchRegistry()
        batch = registry.get_batch("reactivate_test")
        assert batch['status'] == 'active'


class TestCLIErrorHandling:
    """Tests for CLI error handling."""

    @pytest.mark.integration
    def test_cli_invalid_batch_id(self, framework):
        """Invalid batch ID shows error."""
        result = framework.archive_batch("nonexistent_batch")
        assert result is False

    @pytest.mark.integration
    def test_cli_no_project_status(self, framework):
        """status without project shows error."""
        # Don't initialize anything
        result = framework.show_status()
        assert result is False

    @pytest.mark.integration
    def test_cli_no_project_config(self, framework):
        """config without project shows error."""
        result = framework.list_config()
        assert result is False


class TestCLIConvertConfigValue:
    """Tests for config value conversion."""

    @pytest.mark.integration
    def test_convert_bool_true(self, framework):
        """Convert 'true' to bool."""
        assert framework._convert_config_value("true") is True
        assert framework._convert_config_value("True") is True
        assert framework._convert_config_value("yes") is True
        assert framework._convert_config_value("1") is True

    @pytest.mark.integration
    def test_convert_bool_false(self, framework):
        """Convert 'false' to bool."""
        assert framework._convert_config_value("false") is False
        assert framework._convert_config_value("False") is False
        assert framework._convert_config_value("no") is False
        assert framework._convert_config_value("0") is False

    @pytest.mark.integration
    def test_convert_int(self, framework):
        """Convert to int."""
        assert framework._convert_config_value("42") == 42
        assert framework._convert_config_value("-10") == -10

    @pytest.mark.integration
    def test_convert_float(self, framework):
        """Convert to float."""
        assert framework._convert_config_value("3.14") == 3.14
        assert framework._convert_config_value("-2.5") == -2.5

    @pytest.mark.integration
    def test_convert_string(self, framework):
        """Keep as string when not convertible."""
        assert framework._convert_config_value("hello") == "hello"
        assert framework._convert_config_value("path/to/file") == "path/to/file"

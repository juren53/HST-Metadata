"""
Unit tests for ConfigManager.

Tests configuration loading, saving, and manipulation operations.
"""

import pytest
import yaml
from pathlib import Path
from datetime import datetime

from config.config_manager import ConfigManager
from config.settings import DEFAULT_SETTINGS


class TestConfigManagerInit:
    """Tests for ConfigManager initialization."""

    @pytest.mark.unit
    def test_config_manager_init(self):
        """ConfigManager can be instantiated without arguments."""
        cm = ConfigManager()
        assert cm is not None
        assert cm.config_path is None
        assert cm.config_data is not None

    @pytest.mark.unit
    def test_config_manager_init_no_file(self, temp_dir):
        """ConfigManager handles missing config file gracefully."""
        missing_path = temp_dir / "nonexistent.yaml"
        cm = ConfigManager(config_path=missing_path)
        # Should use defaults when file doesn't exist
        assert cm.config_data is not None
        assert "project" in cm.config_data

    @pytest.mark.unit
    def test_config_manager_init_with_file(self, sample_config_file):
        """ConfigManager loads config when file exists."""
        cm = ConfigManager(config_path=sample_config_file)
        assert cm.config_path == sample_config_file
        assert cm.get("project.name") == "test_project"


class TestConfigManagerLoad:
    """Tests for configuration loading."""

    @pytest.mark.unit
    def test_load_config(self, sample_config_file):
        """Load existing YAML config successfully."""
        cm = ConfigManager()
        result = cm.load_config(sample_config_file)
        assert result is True
        assert cm.config_path == sample_config_file

    @pytest.mark.unit
    def test_load_config_empty(self, empty_config_file):
        """Handle empty config file gracefully."""
        cm = ConfigManager()
        result = cm.load_config(empty_config_file)
        # Should succeed but keep defaults
        assert result is True
        assert cm.config_data is not None

    @pytest.mark.unit
    def test_load_config_invalid_yaml(self, invalid_yaml_file):
        """Handle malformed YAML gracefully."""
        cm = ConfigManager()
        result = cm.load_config(invalid_yaml_file)
        # Should fail but not crash
        assert result is False

    @pytest.mark.unit
    def test_load_config_missing_file(self, temp_dir):
        """Handle missing file gracefully."""
        cm = ConfigManager()
        missing_path = temp_dir / "missing.yaml"
        result = cm.load_config(missing_path)
        assert result is False


class TestConfigManagerSave:
    """Tests for configuration saving."""

    @pytest.mark.unit
    def test_save_config(self, temp_dir):
        """Save config to file successfully."""
        cm = ConfigManager()
        config_path = temp_dir / "saved_config.yaml"
        config_data = {"project": {"name": "test"}}

        result = cm.save_config(config_data, config_path)

        assert result is True
        assert config_path.exists()

        # Verify saved content
        with open(config_path) as f:
            loaded = yaml.safe_load(f)
        assert loaded["project"]["name"] == "test"

    @pytest.mark.unit
    def test_save_config_creates_dirs(self, temp_dir):
        """Save config creates parent directories if needed."""
        cm = ConfigManager()
        config_path = temp_dir / "nested" / "deep" / "config.yaml"
        config_data = {"project": {"name": "nested_test"}}

        result = cm.save_config(config_data, config_path)

        assert result is True
        assert config_path.exists()
        assert config_path.parent.exists()


class TestConfigManagerGet:
    """Tests for configuration value retrieval."""

    @pytest.mark.unit
    def test_get_simple_key(self, sample_config_file):
        """Get top-level key value."""
        cm = ConfigManager(config_path=sample_config_file)
        project = cm.get("project")
        assert project is not None
        assert isinstance(project, dict)

    @pytest.mark.unit
    def test_get_nested_key(self, sample_config_file):
        """Get nested key with dot notation."""
        cm = ConfigManager(config_path=sample_config_file)
        name = cm.get("project.name")
        assert name == "test_project"

    @pytest.mark.unit
    def test_get_missing_key_default(self):
        """Return default for missing key."""
        cm = ConfigManager()
        value = cm.get("nonexistent.key", default="default_value")
        assert value == "default_value"

    @pytest.mark.unit
    def test_get_missing_key_none(self):
        """Return None when no default provided for missing key."""
        cm = ConfigManager()
        value = cm.get("nonexistent.key")
        assert value is None

    @pytest.mark.unit
    def test_get_deeply_nested_key(self, sample_config_file):
        """Get deeply nested key with multiple dots."""
        cm = ConfigManager(config_path=sample_config_file)
        value = cm.get("step_configurations.step1.enabled")
        assert value is True


class TestConfigManagerSet:
    """Tests for configuration value setting."""

    @pytest.mark.unit
    def test_set_simple_key(self):
        """Set top-level key value."""
        cm = ConfigManager()
        result = cm.set("new_key", "new_value")
        assert result is True
        assert cm.get("new_key") == "new_value"

    @pytest.mark.unit
    def test_set_nested_key(self):
        """Set nested key with dot notation."""
        cm = ConfigManager()
        result = cm.set("project.custom_field", "custom_value")
        assert result is True
        assert cm.get("project.custom_field") == "custom_value"

    @pytest.mark.unit
    def test_set_creates_parents(self):
        """Set creates parent keys if they don't exist."""
        cm = ConfigManager()
        result = cm.set("new_section.subsection.value", 42)
        assert result is True
        assert cm.get("new_section.subsection.value") == 42
        assert cm.get("new_section.subsection") == {"value": 42}

    @pytest.mark.unit
    def test_set_overwrites_existing(self):
        """Set overwrites existing value."""
        cm = ConfigManager()
        cm.set("project.name", "original")
        cm.set("project.name", "updated")
        assert cm.get("project.name") == "updated"


class TestConfigManagerStepStatus:
    """Tests for step status management."""

    @pytest.mark.unit
    def test_update_step_status_completed(self):
        """Mark step as completed."""
        cm = ConfigManager()
        result = cm.update_step_status(1, True)
        assert result is True
        assert cm.get_step_status(1) is True

    @pytest.mark.unit
    def test_update_step_status_pending(self):
        """Mark step as pending (not completed)."""
        cm = ConfigManager()
        cm.update_step_status(1, True)  # First mark complete
        result = cm.update_step_status(1, False)  # Then mark pending
        assert result is True
        assert cm.get_step_status(1) is False

    @pytest.mark.unit
    def test_get_next_step_none_completed(self):
        """Returns step 1 when no steps completed."""
        cm = ConfigManager()
        # Ensure all steps are False
        for i in range(1, 9):
            cm.update_step_status(i, False)

        next_step = cm.get_next_step()
        assert next_step == 1

    @pytest.mark.unit
    def test_get_next_step_some_completed(self):
        """Returns next uncompleted step."""
        cm = ConfigManager()
        # Complete steps 1, 2, 3
        cm.update_step_status(1, True)
        cm.update_step_status(2, True)
        cm.update_step_status(3, True)

        next_step = cm.get_next_step()
        assert next_step == 4

    @pytest.mark.unit
    def test_get_next_step_all_completed(self):
        """Returns None when all steps complete."""
        cm = ConfigManager()
        # Complete all steps
        for i in range(1, 9):
            cm.update_step_status(i, True)

        next_step = cm.get_next_step()
        assert next_step is None

    @pytest.mark.unit
    def test_get_completed_steps(self):
        """Get list of completed step numbers."""
        cm = ConfigManager()
        # First ensure all steps are False
        for i in range(1, 9):
            cm.update_step_status(i, False)
        # Then set specific steps to True
        cm.update_step_status(1, True)
        cm.update_step_status(3, True)
        cm.update_step_status(5, True)

        completed = cm.get_completed_steps()
        assert completed == [1, 3, 5]


class TestConfigManagerValidation:
    """Tests for configuration validation."""

    @pytest.mark.unit
    def test_validate_config_valid(self, temp_dir, sample_config_file):
        """Valid config passes validation."""
        cm = ConfigManager(config_path=sample_config_file)
        # Set a valid data directory that exists
        cm.set("project.data_directory", str(temp_dir))

        is_valid, errors = cm.validate_config()
        assert is_valid is True
        assert len(errors) == 0

    @pytest.mark.unit
    def test_validate_config_missing_required(self):
        """Missing required fields fail validation."""
        cm = ConfigManager()
        cm.set("project.name", None)
        cm.set("project.data_directory", None)

        is_valid, errors = cm.validate_config()
        assert is_valid is False
        assert len(errors) > 0
        assert any("Missing required field" in e for e in errors)

    @pytest.mark.unit
    def test_validate_config_invalid_data_dir(self, temp_dir):
        """Non-existent data directory fails validation."""
        cm = ConfigManager()
        cm.set("project.name", "test")
        cm.set("project.data_directory", str(temp_dir / "nonexistent"))

        is_valid, errors = cm.validate_config()
        assert is_valid is False
        assert any("does not exist" in e for e in errors)

    @pytest.mark.unit
    def test_validate_config_invalid_step_type(self, temp_dir):
        """Invalid step status type fails validation."""
        cm = ConfigManager()
        cm.set("project.name", "test")
        cm.set("project.data_directory", str(temp_dir))
        # Set invalid type for step status
        cm.set("steps_completed.step1", "invalid_string")

        is_valid, errors = cm.validate_config()
        assert is_valid is False
        assert any("Invalid step status type" in e for e in errors)


class TestConfigManagerMetadata:
    """Tests for configuration metadata handling."""

    @pytest.mark.unit
    def test_config_metadata_version(self, temp_dir):
        """Saved config stores framework version."""
        cm = ConfigManager()
        config_path = temp_dir / "config.yaml"
        cm.save_config({"project": {"name": "test"}}, config_path)

        # Reload and check metadata
        with open(config_path) as f:
            saved = yaml.safe_load(f)

        assert "_metadata" in saved
        assert "framework_version" in saved["_metadata"]

    @pytest.mark.unit
    def test_config_metadata_timestamps(self, temp_dir):
        """Saved config includes timestamps."""
        cm = ConfigManager()
        config_path = temp_dir / "config.yaml"
        cm.save_config({"project": {"name": "test"}}, config_path)

        with open(config_path) as f:
            saved = yaml.safe_load(f)

        assert "_metadata" in saved
        assert "created" in saved["_metadata"]
        assert "last_modified" in saved["_metadata"]


class TestConfigManagerMerge:
    """Tests for configuration merging."""

    @pytest.mark.unit
    def test_config_merge_with_defaults(self, temp_dir):
        """Loaded config merges with defaults."""
        # Create a partial config file
        config_path = temp_dir / "partial.yaml"
        partial_config = {
            "project": {
                "name": "partial_project"
            }
        }
        with open(config_path, "w") as f:
            yaml.dump(partial_config, f)

        cm = ConfigManager(config_path=config_path)

        # Should have the custom value
        assert cm.get("project.name") == "partial_project"
        # Should also have default values for other keys
        assert cm.get("steps_completed") is not None
        assert cm.get("logging") is not None


class TestConfigManagerUtils:
    """Tests for utility methods."""

    @pytest.mark.unit
    def test_to_dict(self, sample_config_file):
        """to_dict returns configuration as dictionary."""
        cm = ConfigManager(config_path=sample_config_file)
        config_dict = cm.to_dict()

        assert isinstance(config_dict, dict)
        assert "project" in config_dict

    @pytest.mark.unit
    def test_str_representation(self, sample_config_file):
        """String representation is readable."""
        cm = ConfigManager(config_path=sample_config_file)
        str_repr = str(cm)

        assert "ConfigManager" in str_repr
        assert "config_path" in str_repr

    @pytest.mark.unit
    def test_repr_representation(self, sample_config_file):
        """Repr representation includes details."""
        cm = ConfigManager(config_path=sample_config_file)
        repr_str = repr(cm)

        assert "ConfigManager" in repr_str
        assert "keys" in repr_str

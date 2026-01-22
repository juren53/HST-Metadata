"""
Unit tests for BatchRegistry.

Tests batch registration, tracking, and status management.
"""

import pytest
import yaml
from pathlib import Path
from datetime import datetime

from utils.batch_registry import BatchRegistry


class TestBatchRegistryInit:
    """Tests for BatchRegistry initialization."""

    @pytest.mark.unit
    def test_registry_init(self, temp_dir):
        """BatchRegistry can be instantiated with path."""
        registry_path = temp_dir / "registry.yaml"
        br = BatchRegistry(registry_path=registry_path)
        assert br is not None
        assert br.registry_path == registry_path

    @pytest.mark.unit
    def test_registry_init_no_file(self, temp_dir):
        """Creates new empty registry if file doesn't exist."""
        registry_path = temp_dir / "new_registry.yaml"
        br = BatchRegistry(registry_path=registry_path)
        assert br.batches == {'batches': {}}

    @pytest.mark.unit
    def test_registry_init_loads_existing(self, sample_registry_file):
        """Loads existing registry from file."""
        br = BatchRegistry(registry_path=sample_registry_file)
        assert "batch_001" in br.batches['batches']
        assert "batch_002" in br.batches['batches']


class TestBatchRegistration:
    """Tests for batch registration operations."""

    @pytest.mark.unit
    def test_register_batch(self, temp_dir):
        """Register new batch successfully."""
        registry_path = temp_dir / "registry.yaml"
        br = BatchRegistry(registry_path=registry_path)

        # Create test directories
        data_dir = temp_dir / "data"
        data_dir.mkdir()
        config_path = temp_dir / "config.yaml"
        config_path.write_text("project:\n  name: test")

        result = br.register_batch(
            project_name="Test Project",
            data_directory=str(data_dir),
            config_path=str(config_path)
        )

        assert result is True
        assert "test_project" in br.batches['batches']

    @pytest.mark.unit
    def test_register_batch_duplicate(self, temp_dir):
        """Handle duplicate batch names by appending number."""
        registry_path = temp_dir / "registry.yaml"
        br = BatchRegistry(registry_path=registry_path)

        data_dir = temp_dir / "data"
        data_dir.mkdir()
        config1 = temp_dir / "config1.yaml"
        config1.write_text("project:\n  name: test1")
        config2 = temp_dir / "config2.yaml"
        config2.write_text("project:\n  name: test2")

        # Register first batch
        br.register_batch("Test Project", str(data_dir), str(config1))
        # Register second batch with same name
        br.register_batch("Test Project", str(data_dir), str(config2))

        assert "test_project" in br.batches['batches']
        assert "test_project_1" in br.batches['batches']

    @pytest.mark.unit
    def test_register_batch_saves_metadata(self, temp_dir):
        """Registered batch includes proper metadata."""
        registry_path = temp_dir / "registry.yaml"
        br = BatchRegistry(registry_path=registry_path)

        data_dir = temp_dir / "data"
        data_dir.mkdir()
        config_path = temp_dir / "config.yaml"
        config_path.write_text("project:\n  name: test")

        br.register_batch("Test Project", str(data_dir), str(config_path))

        batch = br.get_batch("test_project")
        assert batch['name'] == "Test Project"
        assert batch['status'] == 'active'
        assert 'created' in batch
        assert 'last_accessed' in batch


class TestBatchRetrieval:
    """Tests for batch retrieval operations."""

    @pytest.mark.unit
    def test_get_batch(self, sample_registry_file):
        """Get batch by ID."""
        br = BatchRegistry(registry_path=sample_registry_file)
        batch = br.get_batch("batch_001")
        assert batch is not None
        assert batch['name'] == "Test Batch 1"

    @pytest.mark.unit
    def test_get_batch_not_found(self, sample_registry_file):
        """Return None for missing batch."""
        br = BatchRegistry(registry_path=sample_registry_file)
        batch = br.get_batch("nonexistent")
        assert batch is None

    @pytest.mark.unit
    def test_get_all_batches(self, sample_registry_file):
        """Get all registered batches."""
        br = BatchRegistry(registry_path=sample_registry_file)
        all_batches = br.get_all_batches()
        assert len(all_batches) == 3
        assert "batch_001" in all_batches
        assert "batch_002" in all_batches
        assert "batch_003" in all_batches

    @pytest.mark.unit
    def test_get_active_batches(self, sample_registry_file):
        """Get only active batches."""
        br = BatchRegistry(registry_path=sample_registry_file)
        active = br.get_active_batches()
        assert len(active) == 1
        assert "batch_001" in active

    @pytest.mark.unit
    def test_find_batch_by_name(self, sample_registry_file):
        """Find batch by project name."""
        br = BatchRegistry(registry_path=sample_registry_file)
        result = br.find_batch_by_name("Test Batch 1")
        assert result is not None
        batch_id, batch_info = result
        assert batch_id == "batch_001"

    @pytest.mark.unit
    def test_find_batch_by_name_not_found(self, sample_registry_file):
        """Return None when batch name not found."""
        br = BatchRegistry(registry_path=sample_registry_file)
        result = br.find_batch_by_name("Nonexistent Batch")
        assert result is None


class TestBatchStatusManagement:
    """Tests for batch status management."""

    @pytest.mark.unit
    def test_update_batch_status(self, temp_dir):
        """Update batch status successfully."""
        registry_path = temp_dir / "registry.yaml"
        br = BatchRegistry(registry_path=registry_path)

        # Register a batch first
        data_dir = temp_dir / "data"
        data_dir.mkdir()
        config_path = temp_dir / "config.yaml"
        config_path.write_text("project:\n  name: test")
        br.register_batch("Test", str(data_dir), str(config_path))

        # Update status
        result = br.update_batch_status("test", "completed")
        assert result is True
        assert br.get_batch("test")['status'] == "completed"

    @pytest.mark.unit
    def test_update_batch_status_not_found(self, temp_dir):
        """Return False when batch not found."""
        registry_path = temp_dir / "registry.yaml"
        br = BatchRegistry(registry_path=registry_path)
        result = br.update_batch_status("nonexistent", "completed")
        assert result is False

    @pytest.mark.unit
    def test_update_last_accessed(self, temp_dir):
        """Update last accessed timestamp."""
        registry_path = temp_dir / "registry.yaml"
        br = BatchRegistry(registry_path=registry_path)

        data_dir = temp_dir / "data"
        data_dir.mkdir()
        config_path = temp_dir / "config.yaml"
        config_path.write_text("project:\n  name: test")
        br.register_batch("Test", str(data_dir), str(config_path))

        original_time = br.get_batch("test")['last_accessed']
        import time
        time.sleep(0.01)  # Small delay to ensure different timestamp

        result = br.update_last_accessed("test")
        assert result is True
        new_time = br.get_batch("test")['last_accessed']
        assert new_time >= original_time


class TestBatchSummary:
    """Tests for batch summary functionality."""

    @pytest.mark.unit
    def test_get_batch_summary(self, temp_dir):
        """Get batch summary with completion info."""
        registry_path = temp_dir / "registry.yaml"
        br = BatchRegistry(registry_path=registry_path)

        # Create config with step status
        data_dir = temp_dir / "data"
        data_dir.mkdir()
        config_path = temp_dir / "config.yaml"
        config_content = {
            "project": {"name": "test"},
            "steps_completed": {
                "step1": True,
                "step2": True,
                "step3": False,
                "step4": False,
                "step5": False,
                "step6": False,
                "step7": False,
                "step8": False,
            }
        }
        with open(config_path, 'w') as f:
            yaml.dump(config_content, f)

        br.register_batch("Test", str(data_dir), str(config_path))

        summary = br.get_batch_summary("test")
        assert summary is not None
        assert summary['completed_steps'] == 2
        assert summary['total_steps'] == 8
        assert summary['completion_percentage'] == 25.0

    @pytest.mark.unit
    def test_get_batch_summary_not_found(self, temp_dir):
        """Return None for nonexistent batch summary."""
        registry_path = temp_dir / "registry.yaml"
        br = BatchRegistry(registry_path=registry_path)
        summary = br.get_batch_summary("nonexistent")
        assert summary is None

    @pytest.mark.unit
    def test_list_batches_summary(self, sample_registry_file):
        """List all batch summaries sorted by last accessed."""
        br = BatchRegistry(registry_path=sample_registry_file)
        summaries = br.list_batches_summary()
        assert isinstance(summaries, list)
        assert len(summaries) == 3


class TestBatchRemoval:
    """Tests for batch removal operations."""

    @pytest.mark.unit
    def test_unregister_batch(self, temp_dir):
        """Remove batch from registry."""
        registry_path = temp_dir / "registry.yaml"
        br = BatchRegistry(registry_path=registry_path)

        data_dir = temp_dir / "data"
        data_dir.mkdir()
        config_path = temp_dir / "config.yaml"
        config_path.write_text("project:\n  name: test")
        br.register_batch("Test", str(data_dir), str(config_path))

        result = br.unregister_batch("test")
        assert result is True
        assert br.get_batch("test") is None

    @pytest.mark.unit
    def test_unregister_batch_not_found(self, temp_dir):
        """Return False when trying to remove nonexistent batch."""
        registry_path = temp_dir / "registry.yaml"
        br = BatchRegistry(registry_path=registry_path)
        result = br.unregister_batch("nonexistent")
        assert result is False

    @pytest.mark.unit
    def test_unregister_preserves_files(self, temp_dir):
        """Removing batch from registry preserves actual files."""
        registry_path = temp_dir / "registry.yaml"
        br = BatchRegistry(registry_path=registry_path)

        data_dir = temp_dir / "data"
        data_dir.mkdir()
        test_file = data_dir / "test.txt"
        test_file.write_text("test content")
        config_path = temp_dir / "config.yaml"
        config_path.write_text("project:\n  name: test")

        br.register_batch("Test", str(data_dir), str(config_path))
        br.unregister_batch("test")

        # Files should still exist
        assert data_dir.exists()
        assert test_file.exists()
        assert config_path.exists()


class TestRegistryPersistence:
    """Tests for registry persistence."""

    @pytest.mark.unit
    def test_registry_persistence(self, temp_dir):
        """Changes persist to file."""
        registry_path = temp_dir / "registry.yaml"

        # Create and register in first instance
        br1 = BatchRegistry(registry_path=registry_path)
        data_dir = temp_dir / "data"
        data_dir.mkdir()
        config_path = temp_dir / "config.yaml"
        config_path.write_text("project:\n  name: test")
        br1.register_batch("Test", str(data_dir), str(config_path))

        # Load in second instance
        br2 = BatchRegistry(registry_path=registry_path)
        assert br2.get_batch("test") is not None
        assert br2.get_batch("test")['name'] == "Test"

    @pytest.mark.unit
    def test_registry_saves_on_update(self, temp_dir):
        """Status updates are persisted."""
        registry_path = temp_dir / "registry.yaml"
        br1 = BatchRegistry(registry_path=registry_path)

        data_dir = temp_dir / "data"
        data_dir.mkdir()
        config_path = temp_dir / "config.yaml"
        config_path.write_text("project:\n  name: test")
        br1.register_batch("Test", str(data_dir), str(config_path))
        br1.update_batch_status("test", "completed")

        br2 = BatchRegistry(registry_path=registry_path)
        assert br2.get_batch("test")['status'] == "completed"


class TestBatchIdGeneration:
    """Tests for batch ID generation."""

    @pytest.mark.unit
    def test_generate_id_simple(self, temp_dir):
        """Generate simple ID from project name."""
        registry_path = temp_dir / "registry.yaml"
        br = BatchRegistry(registry_path=registry_path)

        data_dir = temp_dir / "data"
        data_dir.mkdir()
        config_path = temp_dir / "config.yaml"
        config_path.write_text("project:\n  name: test")

        br.register_batch("My Project", str(data_dir), str(config_path))
        assert "my_project" in br.batches['batches']

    @pytest.mark.unit
    def test_generate_id_with_special_chars(self, temp_dir):
        """Generate ID handles special characters."""
        registry_path = temp_dir / "registry.yaml"
        br = BatchRegistry(registry_path=registry_path)

        data_dir = temp_dir / "data"
        data_dir.mkdir()
        config_path = temp_dir / "config.yaml"
        config_path.write_text("project:\n  name: test")

        br.register_batch("My-Project Name", str(data_dir), str(config_path))
        assert "my_project_name" in br.batches['batches']


class TestBatchRegistryUtils:
    """Tests for utility methods."""

    @pytest.mark.unit
    def test_str_representation(self, sample_registry_file):
        """String representation is readable."""
        br = BatchRegistry(registry_path=sample_registry_file)
        str_repr = str(br)
        assert "BatchRegistry" in str_repr
        assert "batches=3" in str_repr

    @pytest.mark.unit
    def test_repr_representation(self, sample_registry_file):
        """Repr representation includes batch IDs."""
        br = BatchRegistry(registry_path=sample_registry_file)
        repr_str = repr(br)
        assert "BatchRegistry" in repr_str
        assert "batch_001" in repr_str

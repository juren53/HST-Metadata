"""
Integration tests for Batch Lifecycle.

Tests batch creation, status transitions, and lifecycle management.
"""

import pytest
import yaml
from pathlib import Path

from utils.batch_registry import BatchRegistry
from config.config_manager import ConfigManager


@pytest.fixture
def registry_dir(temp_dir):
    """Create a directory for the batch registry."""
    reg_dir = temp_dir / "registry"
    reg_dir.mkdir()
    return reg_dir


@pytest.fixture
def batch_registry(registry_dir):
    """Create a fresh batch registry for testing."""
    registry_path = registry_dir / "batch_registry.yaml"
    return BatchRegistry(registry_path=registry_path)


@pytest.fixture
def sample_batch(temp_dir, batch_registry):
    """Create a sample batch with project structure."""
    batch_name = "Test Batch"
    data_dir = temp_dir / "test_batch_data"
    data_dir.mkdir()

    # Create directory structure
    dirs = ["input/tiff", "input/spreadsheet", "output/csv", "config", "logs"]
    for d in dirs:
        (data_dir / d).mkdir(parents=True, exist_ok=True)

    # Create config file
    config_path = data_dir / "config" / "project_config.yaml"
    config = {
        "project": {"name": batch_name, "data_directory": str(data_dir)},
        "steps_completed": {f"step{i}": False for i in range(1, 9)}
    }
    with open(config_path, 'w') as f:
        yaml.dump(config, f)

    # Register the batch
    batch_registry.register_batch(batch_name, str(data_dir), str(config_path))

    return {
        "name": batch_name,
        "data_dir": data_dir,
        "config_path": config_path,
        "batch_id": "test_batch"
    }


class TestBatchCreation:
    """Tests for batch creation."""

    @pytest.mark.integration
    def test_create_new_batch(self, temp_dir, batch_registry):
        """Create new batch project."""
        data_dir = temp_dir / "new_batch"
        data_dir.mkdir()
        config_path = data_dir / "config.yaml"
        config_path.write_text("project:\n  name: New Batch")

        result = batch_registry.register_batch(
            "New Batch",
            str(data_dir),
            str(config_path)
        )

        assert result is True
        assert "new_batch" in batch_registry.batches['batches']

    @pytest.mark.integration
    def test_batch_directory_structure(self, sample_batch):
        """Batch has correct structure."""
        data_dir = sample_batch['data_dir']

        # Check expected directories exist
        assert (data_dir / "input" / "tiff").exists()
        assert (data_dir / "input" / "spreadsheet").exists()
        assert (data_dir / "output" / "csv").exists()
        assert (data_dir / "config").exists()
        assert (data_dir / "logs").exists()

        # Check config file exists
        assert sample_batch['config_path'].exists()


class TestBatchStatusTransitions:
    """Tests for batch status transitions."""

    @pytest.mark.integration
    def test_batch_status_active_to_complete(self, batch_registry, sample_batch):
        """Status transitions: active -> completed."""
        batch_id = sample_batch['batch_id']

        # Initial status should be active
        batch = batch_registry.get_batch(batch_id)
        assert batch['status'] == 'active'

        # Transition to completed
        result = batch_registry.update_batch_status(batch_id, 'completed')
        assert result is True

        batch = batch_registry.get_batch(batch_id)
        assert batch['status'] == 'completed'

    @pytest.mark.integration
    def test_batch_status_complete_to_archived(self, batch_registry, sample_batch):
        """Status transitions: completed -> archived."""
        batch_id = sample_batch['batch_id']

        # Set to completed first
        batch_registry.update_batch_status(batch_id, 'completed')

        # Then archive
        result = batch_registry.update_batch_status(batch_id, 'archived')
        assert result is True

        batch = batch_registry.get_batch(batch_id)
        assert batch['status'] == 'archived'

    @pytest.mark.integration
    def test_batch_full_status_lifecycle(self, batch_registry, sample_batch):
        """Full lifecycle: active -> completed -> archived -> reactivated."""
        batch_id = sample_batch['batch_id']

        # Active (initial)
        assert batch_registry.get_batch(batch_id)['status'] == 'active'

        # -> Completed
        batch_registry.update_batch_status(batch_id, 'completed')
        assert batch_registry.get_batch(batch_id)['status'] == 'completed'

        # -> Archived
        batch_registry.update_batch_status(batch_id, 'archived')
        assert batch_registry.get_batch(batch_id)['status'] == 'archived'

        # -> Reactivated (back to active)
        batch_registry.update_batch_status(batch_id, 'active')
        assert batch_registry.get_batch(batch_id)['status'] == 'active'


class TestBatchStepTracking:
    """Tests for batch step tracking."""

    @pytest.mark.integration
    def test_batch_step_tracking(self, sample_batch):
        """Track completed steps per batch."""
        config_path = sample_batch['config_path']

        # Load config and update steps
        cm = ConfigManager(config_path=config_path)
        cm.update_step_status(1, True)
        cm.update_step_status(2, True)
        cm.save_config(cm.to_dict(), config_path)

        # Reload and verify
        cm2 = ConfigManager(config_path=config_path)
        assert cm2.get_step_status(1) is True
        assert cm2.get_step_status(2) is True
        assert cm2.get_step_status(3) is False

    @pytest.mark.integration
    def test_batch_completion_percentage(self, batch_registry, sample_batch):
        """Calculate completion percentage."""
        config_path = sample_batch['config_path']
        batch_id = sample_batch['batch_id']

        # Mark some steps complete
        cm = ConfigManager(config_path=config_path)
        cm.update_step_status(1, True)
        cm.update_step_status(2, True)
        cm.update_step_status(3, True)
        cm.update_step_status(4, True)
        cm.save_config(cm.to_dict(), config_path)

        # Get summary
        summary = batch_registry.get_batch_summary(batch_id)

        assert summary['completed_steps'] == 4
        assert summary['total_steps'] == 8
        assert summary['completion_percentage'] == 50.0


class TestBatchArchive:
    """Tests for batch archiving."""

    @pytest.mark.integration
    def test_batch_archive_workflow(self, batch_registry, sample_batch):
        """Archive completed batch."""
        batch_id = sample_batch['batch_id']

        # Complete and archive
        batch_registry.update_batch_status(batch_id, 'completed')
        batch_registry.update_batch_status(batch_id, 'archived')

        batch = batch_registry.get_batch(batch_id)
        assert batch['status'] == 'archived'

        # Archived batches shouldn't show in active list
        active = batch_registry.get_active_batches()
        assert batch_id not in active

    @pytest.mark.integration
    def test_batch_reactivate_workflow(self, batch_registry, sample_batch):
        """Reactivate archived batch."""
        batch_id = sample_batch['batch_id']

        # Archive then reactivate
        batch_registry.update_batch_status(batch_id, 'archived')
        batch_registry.update_batch_status(batch_id, 'active')

        batch = batch_registry.get_batch(batch_id)
        assert batch['status'] == 'active'

        # Should now be in active list
        active = batch_registry.get_active_batches()
        assert batch_id in active


class TestBatchRemoval:
    """Tests for batch removal."""

    @pytest.mark.integration
    def test_batch_remove_preserves_data(self, batch_registry, sample_batch):
        """Remove from registry, keep files."""
        batch_id = sample_batch['batch_id']
        data_dir = sample_batch['data_dir']
        config_path = sample_batch['config_path']

        # Create some test files
        test_file = data_dir / "test_data.txt"
        test_file.write_text("important data")

        # Remove from registry
        result = batch_registry.unregister_batch(batch_id)
        assert result is True

        # Batch should be gone from registry
        assert batch_registry.get_batch(batch_id) is None

        # But files should still exist
        assert data_dir.exists()
        assert test_file.exists()
        assert config_path.exists()


class TestBatchInfo:
    """Tests for batch info display."""

    @pytest.mark.integration
    def test_batch_info_display(self, batch_registry, sample_batch):
        """Batch info shows correct data."""
        batch_id = sample_batch['batch_id']

        summary = batch_registry.get_batch_summary(batch_id)

        assert summary['name'] == sample_batch['name']
        assert summary['data_directory'] == str(sample_batch['data_dir'])
        assert summary['config_path'] == str(sample_batch['config_path'])
        assert 'created' in summary
        assert 'status' in summary


class TestBatchListFiltering:
    """Tests for batch list filtering."""

    @pytest.mark.integration
    def test_batch_list_filtering(self, temp_dir, batch_registry):
        """Filter batches by status."""
        # Create multiple batches with different statuses
        for i, status in enumerate(['active', 'active', 'completed', 'archived']):
            data_dir = temp_dir / f"batch_{i}"
            data_dir.mkdir()
            config_path = data_dir / "config.yaml"
            config_path.write_text(f"project:\n  name: Batch {i}")

            batch_registry.register_batch(f"Batch {i}", str(data_dir), str(config_path))
            batch_id = f"batch_{i}"
            if status != 'active':
                batch_registry.update_batch_status(batch_id, status)

        # Check filtering
        all_batches = batch_registry.get_all_batches()
        active_batches = batch_registry.get_active_batches()

        assert len(all_batches) == 4
        assert len(active_batches) == 2

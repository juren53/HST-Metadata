"""
Unit tests for BatchRegistry class.
"""

import pytest
import os
import tempfile
import yaml
from datetime import datetime
from pathlib import Path

from utils.batch_registry import BatchRegistry


class TestBatchRegistry:
    """Test cases for BatchRegistry class."""

    def test_load_valid_registry(self, batch_registry, batch_registry_file):
        """Test loading a valid batch registry file."""
        assert batch_registry.registry is not None
        assert 'batches' in batch_registry.registry
        assert 'metadata' in batch_registry.registry
        
        # Check sample batches
        assert 'TEST-001' in batch_registry.get_all_batches()
        assert 'TEST-002' in batch_registry.get_all_batches()

    def test_load_nonexistent_registry(self, temp_dir):
        """Test loading a registry file that doesn't exist."""
        nonexistent_path = os.path.join(temp_dir, 'nonexistent.yaml')
        registry = BatchRegistry(nonexistent_path)
        
        # Should create empty registry
        assert registry.registry == {'batches': {}, 'metadata': {'version': '1.0'}}

    def test_register_new_batch(self, batch_registry):
        """Test registering a new batch."""
        batch_info = {
            'name': 'New Test Project',
            'description': 'A new test project',
            'config_file': 'new_config.yaml'
        }
        
        batch_id = batch_registry.register_batch(batch_info)
        
        assert batch_id is not None
        assert batch_registry.batch_exists(batch_id)
        assert batch_registry.get_batch_info(batch_id)['name'] == 'New Test Project'
        assert batch_registry.get_batch_info(batch_id)['status'] == 'active'

    def test_register_batch_with_custom_id(self, batch_registry):
        """Test registering a batch with custom ID."""
        batch_info = {
            'name': 'Custom ID Project',
            'config_file': 'custom_config.yaml'
        }
        
        custom_id = 'CUSTOM-001'
        returned_id = batch_registry.register_batch(batch_info, batch_id=custom_id)
        
        assert returned_id == custom_id
        assert batch_registry.batch_exists(custom_id)

    def test_register_duplicate_batch(self, batch_registry):
        """Test registering a batch with duplicate ID."""
        batch_info = {
            'name': 'Duplicate Project',
            'config_file': 'duplicate_config.yaml'
        }
        
        # Register first batch
        batch_id1 = batch_registry.register_batch(batch_info)
        
        # Try to register with same ID
        batch_info['name'] = 'Another Project'
        batch_id2 = batch_registry.register_batch(batch_info, batch_id=batch_id1)
        
        assert batch_id2 != batch_id1
        assert batch_registry.get_batch_info(batch_id1)['name'] == 'Duplicate Project'

    def test_update_batch_status(self, batch_registry):
        """Test updating batch status."""
        batch_id = 'TEST-001'
        
        # Update to completed
        batch_registry.update_batch_status(batch_id, 'completed')
        assert batch_registry.get_batch_status(batch_id) == 'completed'
        
        # Update to archived
        batch_registry.update_batch_status(batch_id, 'archived')
        assert batch_registry.get_batch_status(batch_id) == 'archived'

    def test_update_batch_info(self, batch_registry):
        """Test updating batch information."""
        batch_id = 'TEST-001'
        
        updated_info = {
            'name': 'Updated Project Name',
            'description': 'Updated description',
            'new_field': 'new value'
        }
        
        batch_registry.update_batch_info(batch_id, updated_info)
        
        batch_info = batch_registry.get_batch_info(batch_id)
        assert batch_info['name'] == 'Updated Project Name'
        assert batch_info['description'] == 'Updated description'
        assert batch_info['new_field'] == 'new value'
        
        # Ensure original fields are preserved
        assert 'status' in batch_info
        assert 'created_at' in batch_info

    def test_get_batch_info(self, batch_registry):
        """Test getting batch information."""
        batch_id = 'TEST-001'
        batch_info = batch_registry.get_batch_info(batch_id)
        
        assert batch_info is not None
        assert batch_info['name'] == 'Test Project'
        assert batch_info['status'] == 'active'
        assert 'created_at' in batch_info
        assert 'config_file' in batch_info
        
        # Test nonexistent batch
        assert batch_registry.get_batch_info('NONEXISTENT') is None

    def test_get_batch_status(self, batch_registry):
        """Test getting batch status."""
        assert batch_registry.get_batch_status('TEST-001') == 'active'
        assert batch_registry.get_batch_status('TEST-002') == 'completed'
        assert batch_registry.get_batch_status('NONEXISTENT') is None

    def test_get_all_batches(self, batch_registry):
        """Test getting all batch IDs."""
        all_batches = batch_registry.get_all_batches()
        
        assert isinstance(all_batches, list)
        assert 'TEST-001' in all_batches
        assert 'TEST-002' in all_batches
        assert len(all_batches) >= 2

    def test_get_batches_by_status(self, batch_registry):
        """Test getting batches filtered by status."""
        active_batches = batch_registry.get_batches_by_status('active')
        completed_batches = batch_registry.get_batches_by_status('completed')
        archived_batches = batch_registry.get_batches_by_status('archived')
        
        assert 'TEST-001' in active_batches
        assert 'TEST-002' in completed_batches
        assert len(archived_batches) == 0  # No archived batches in sample data

    def test_delete_batch(self, batch_registry):
        """Test deleting a batch."""
        # Register a new batch first
        batch_info = {'name': 'To Delete', 'config_file': 'delete_config.yaml'}
        batch_id = batch_registry.register_batch(batch_info)
        
        assert batch_registry.batch_exists(batch_id)
        
        # Delete the batch
        batch_registry.delete_batch(batch_id)
        assert not batch_registry.batch_exists(batch_id)
        assert batch_registry.get_batch_info(batch_id) is None

    def test_batch_exists(self, batch_registry):
        """Test checking if batch exists."""
        assert batch_registry.batch_exists('TEST-001') is True
        assert batch_registry.batch_exists('TEST-002') is True
        assert batch_registry.batch_exists('NONEXISTENT') is False

    def test_get_active_batches(self, batch_registry):
        """Test getting only active batches."""
        active_batches = batch_registry.get_active_batches()
        
        assert 'TEST-001' in active_batches
        assert 'TEST-002' not in active_batches  # This one is completed

    def test_get_completed_batches(self, batch_registry):
        """Test getting only completed batches."""
        completed_batches = batch_registry.get_completed_batches()
        
        assert 'TEST-002' in completed_batches
        assert 'TEST-001' not in completed_batches  # This one is active

    def test_save_registry(self, batch_registry, temp_dir):
        """Test saving registry to file."""
        # Modify registry
        batch_info = {'name': 'Save Test', 'config_file': 'save_config.yaml'}
        batch_id = batch_registry.register_batch(batch_info)
        
        # Save to new file
        saved_path = os.path.join(temp_dir, 'saved_registry.yaml')
        batch_registry.save(saved_path)
        
        # Load and verify
        with open(saved_path, 'r') as f:
            saved_data = yaml.safe_load(f)
        
        assert batch_id in saved_data['batches']
        assert saved_data['batches'][batch_id]['name'] == 'Save Test'

    def test_auto_save_on_modification(self, batch_registry, batch_registry_file):
        """Test that registry auto-saves on modification."""
        # Get original modification time
        original_mtime = os.path.getmtime(batch_registry_file)
        
        # Wait a bit to ensure different timestamp
        import time
        time.sleep(0.1)
        
        # Modify registry
        batch_info = {'name': 'Auto Save Test', 'config_file': 'auto_config.yaml'}
        batch_registry.register_batch(batch_info)
        
        # Check if file was modified
        new_mtime = os.path.getmtime(batch_registry_file)
        assert new_mtime > original_mtime

    def test_generate_batch_id(self, batch_registry):
        """Test batch ID generation."""
        batch_id1 = batch_registry._generate_batch_id()
        batch_id2 = batch_registry._generate_batch_id()
        
        assert batch_id1 != batch_id2
        assert len(batch_id1) > 0
        assert '-' in batch_id1  # Should contain separator

    def test_validate_batch_info(self, batch_registry):
        """Test batch info validation."""
        # Valid batch info
        valid_info = {
            'name': 'Valid Project',
            'config_file': 'valid_config.yaml'
        }
        assert batch_registry._validate_batch_info(valid_info) is True
        
        # Missing required fields
        invalid_info1 = {'name': 'Missing Config'}
        assert batch_registry._validate_batch_info(invalid_info1) is False
        
        invalid_info2 = {'config_file': 'missing_name.yaml'}
        assert batch_registry._validate_batch_info(invalid_info2) is False
        
        # Empty batch info
        assert batch_registry._validate_batch_info({}) is False
        assert batch_registry._validate_batch_info(None) is False

    def test_get_batch_count(self, batch_registry):
        """Test getting batch count."""
        total_count = batch_registry.get_batch_count()
        active_count = batch_registry.get_batch_count('active')
        completed_count = batch_registry.get_batch_count('completed')
        
        assert total_count >= 2
        assert active_count >= 1
        assert completed_count >= 1

    def test_get_registry_metadata(self, batch_registry):
        """Test getting registry metadata."""
        metadata = batch_registry.get_registry_metadata()
        
        assert 'version' in metadata
        assert 'last_updated' in metadata
        assert metadata['version'] == '1.0'

    def test_update_metadata(self, batch_registry):
        """Test updating registry metadata."""
        new_metadata = {
            'version': '2.0',
            'author': 'Test Author',
            'custom_field': 'custom_value'
        }
        
        batch_registry.update_metadata(new_metadata)
        
        metadata = batch_registry.get_registry_metadata()
        assert metadata['version'] == '2.0'
        assert metadata['author'] == 'Test Author'
        assert metadata['custom_field'] == 'custom_value'
        assert 'last_updated' in metadata  # Should preserve auto-updated field

    def test_cleanup_old_batches(self, batch_registry):
        """Test cleaning up old archived batches."""
        # Register some batches and mark as archived
        old_batch_ids = []
        for i in range(3):
            batch_info = {'name': f'Old Batch {i}', 'config_file': f'old_{i}.yaml'}
            batch_id = batch_registry.register_batch(batch_info)
            batch_registry.update_batch_status(batch_id, 'archived')
            old_batch_ids.append(batch_id)
        
        # Get count before cleanup
        total_before = batch_registry.get_batch_count()
        
        # Cleanup old batches (mock old date)
        batch_registry.cleanup_old_batches(days_old=0)  # Should cleanup all archived
        
        # Verify cleanup
        total_after = batch_registry.get_batch_count()
        assert total_after < total_before
        
        # Check that archived batches are removed but active ones remain
        for batch_id in old_batch_ids:
            assert not batch_registry.batch_exists(batch_id)
        
        assert batch_registry.batch_exists('TEST-001')  # Should still exist

    def test_concurrent_batch_registration(self, batch_registry):
        """Test handling of concurrent batch registrations."""
        batch_infos = [
            {'name': 'Concurrent 1', 'config_file': 'concurrent1.yaml'},
            {'name': 'Concurrent 2', 'config_file': 'concurrent2.yaml'},
            {'name': 'Concurrent 3', 'config_file': 'concurrent3.yaml'}
        ]
        
        batch_ids = []
        for info in batch_infos:
            batch_id = batch_registry.register_batch(info)
            batch_ids.append(batch_id)
        
        # Verify all batches were registered with unique IDs
        assert len(set(batch_ids)) == len(batch_ids)
        for batch_id in batch_ids:
            assert batch_registry.batch_exists(batch_id)

    def test_search_batches(self, batch_registry):
        """Test searching batches by name or description."""
        # Register test batches
        search_info1 = {'name': 'Search Test Alpha', 'description': 'First search test', 'config_file': 'search1.yaml'}
        search_info2 = {'name': 'Search Test Beta', 'description': 'Second search test', 'config_file': 'search2.yaml'}
        search_info3 = {'name': 'Different Name', 'description': 'Contains search term', 'config_file': 'search3.yaml'}
        
        batch_id1 = batch_registry.register_batch(search_info1)
        batch_id2 = batch_registry.register_batch(search_info2)
        batch_id3 = batch_registry.register_batch(search_info3)
        
        # Search by name
        results = batch_registry.search_batches('Search Test')
        assert batch_id1 in results
        assert batch_id2 in results
        assert batch_id3 not in results
        
        # Search by description
        results = batch_registry.search_batches('search test')
        assert batch_id1 in results
        assert batch_id2 in results
        
        # Search with partial match
        results = batch_registry.search_batches('Alpha')
        assert batch_id1 in results
        assert batch_id2 not in results
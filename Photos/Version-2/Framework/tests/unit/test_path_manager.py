"""
Unit tests for PathManager utility class.
"""

import pytest
import os
import tempfile
from pathlib import Path

from utils.path_manager import PathManager


class TestPathManager:
    """Test cases for PathManager class."""

    def test_path_manager_initialization(self, temp_dir):
        """Test PathManager initialization."""
        manager = PathManager(temp_dir)
        
        assert manager.base_path == temp_dir
        assert manager.base_path == Path(temp_dir)

    def test_create_directory_structure(self, path_manager):
        """Test creating directory structure."""
        dirs_to_create = ['input', 'output', 'temp', 'logs']
        
        path_manager.create_directory_structure(dirs_to_create)
        
        for dir_name in dirs_to_create:
            dir_path = os.path.join(path_manager.base_path, dir_name)
            assert os.path.exists(dir_path)
            assert os.path.isdir(dir_path)

    def test_get_path(self, path_manager):
        """Test getting paths relative to base."""
        # Test string path
        path = path_manager.get_path('input')
        expected = os.path.join(path_manager.base_path, 'input')
        assert path == expected
        
        # Test nested path
        nested_path = path_manager.get_path('output', 'processed')
        expected_nested = os.path.join(path_manager.base_path, 'output', 'processed')
        assert nested_path == expected_nested
        
        # Test Path object
        path_obj = path_manager.get_path(Path('temp'))
        assert str(path_obj) == os.path.join(path_manager.base_path, 'temp')

    def test_ensure_directory_exists(self, path_manager):
        """Test ensuring directory exists."""
        new_dir = path_manager.get_path('new_directory')
        
        # Directory doesn't exist initially
        assert not os.path.exists(new_dir)
        
        # Ensure it exists
        path_manager.ensure_directory_exists(new_dir)
        assert os.path.exists(new_dir)
        assert os.path.isdir(new_dir)
        
        # Should not raise error if directory already exists
        path_manager.ensure_directory_exists(new_dir)

    def test_ensure_directory_exists_relative(self, path_manager):
        """Test ensuring directory exists with relative path."""
        path_manager.ensure_directory_exists('relative', 'path')
        
        expected_path = path_manager.get_path('relative', 'path')
        assert os.path.exists(expected_path)
        assert os.path.isdir(expected_path)

    def test_get_input_path(self, path_manager):
        """Test getting input directory path."""
        # Create input directory first
        path_manager.ensure_directory_exists('input')
        
        input_path = path_manager.get_input_path()
        expected = path_manager.get_path('input')
        assert input_path == expected

    def test_get_output_path(self, path_manager):
        """Test getting output directory path."""
        # Create output directory first
        path_manager.ensure_directory_exists('output')
        
        output_path = path_manager.get_output_path()
        expected = path_manager.get_path('output')
        assert output_path == expected

    def test_get_temp_path(self, path_manager):
        """Test getting temp directory path."""
        # Create temp directory first
        path_manager.ensure_directory_exists('temp')
        
        temp_path = path_manager.get_temp_path()
        expected = path_manager.get_path('temp')
        assert temp_path == expected

    def test_get_logs_path(self, path_manager):
        """Test getting logs directory path."""
        # Create logs directory first
        path_manager.ensure_directory_exists('logs')
        
        logs_path = path_manager.get_logs_path()
        expected = path_manager.get_path('logs')
        assert logs_path == expected

    def test_get_step_path(self, path_manager):
        """Test getting step-specific directory path."""
        # Create step directory
        path_manager.ensure_directory_exists('steps', 'step1')
        
        step_path = path_manager.get_step_path('step1')
        expected = path_manager.get_path('steps', 'step1')
        assert step_path == expected

    def test_get_batch_path(self, path_manager):
        """Test getting batch-specific directory path."""
        batch_id = 'TEST-001'
        
        # Create batch directory
        path_manager.ensure_directory_exists('batches', batch_id)
        
        batch_path = path_manager.get_batch_path(batch_id)
        expected = path_manager.get_path('batches', batch_id)
        assert batch_path == expected

    def test_create_batch_directories(self, path_manager):
        """Test creating complete batch directory structure."""
        batch_id = 'TEST-002'
        
        path_manager.create_batch_directories(batch_id)
        
        # Check all expected directories exist
        expected_dirs = [
            path_manager.get_batch_path(batch_id),
            path_manager.get_path('batches', batch_id, 'input'),
            path_manager.get_path('batches', batch_id, 'output'),
            path_manager.get_path('batches', batch_id, 'temp'),
            path_manager.get_path('batches', batch_id, 'logs')
        ]
        
        for dir_path in expected_dirs:
            assert os.path.exists(dir_path)
            assert os.path.isdir(dir_path)

    def test_get_project_file_path(self, path_manager):
        """Test getting project file paths."""
        # Test config file
        config_path = path_manager.get_project_file_path('config.yaml')
        expected = path_manager.get_path('config.yaml')
        assert config_path == expected
        
        # Test nested file
        nested_path = path_manager.get_project_file_path('data', 'metadata.csv')
        expected_nested = path_manager.get_path('data', 'metadata.csv')
        assert nested_path == expected_nested

    def test_list_files(self, path_manager, generate_test_files):
        """Test listing files in directory."""
        # Generate test files
        test_files = generate_test_files(path_manager.base_path, count=3)
        
        # List all files
        all_files = path_manager.list_files()
        assert len(all_files) >= 3
        
        # List files with pattern
        tif_files = path_manager.list_files(pattern='*.tif')
        assert len(tif_files) >= 3
        
        # Verify all listed files are TIFF files
        for file_path in tif_files:
            assert file_path.endswith('.tif')

    def test_list_directories(self, path_manager):
        """Test listing directories."""
        # Create some directories
        dirs_to_create = ['dir1', 'dir2', 'dir3']
        for dir_name in dirs_to_create:
            path_manager.ensure_directory_exists(dir_name)
        
        # List directories
        directories = path_manager.list_directories()
        
        for dir_name in dirs_to_create:
            dir_path = path_manager.get_path(dir_name)
            assert dir_path in directories

    def test_find_files(self, path_manager, temp_dir):
        """Test finding files by pattern."""
        # Create test files
        test_files = [
            ('test1.tif', b'\x49\x49\x2A\x00'),
            ('test2.jpg', b'test jpg content'),
            ('subdir/test3.tif', b'\x49\x49\x2A\x00'),
            ('other.txt', b'test text content')
        ]
        
        for file_path, content in test_files:
            full_path = path_manager.get_path(file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'wb') as f:
                f.write(content)
        
        # Find TIFF files
        tif_files = path_manager.find_files('*.tif')
        assert len(tif_files) >= 2
        
        # Find files recursively
        all_tif_files = path_manager.find_files('*.tif', recursive=True)
        assert len(all_tif_files) >= 3
        
        # Verify all found files are TIFF files
        for file_path in all_tif_files:
            assert file_path.endswith('.tif')

    def test_clean_temp_directory(self, path_manager):
        """Test cleaning temporary directory."""
        # Create temp directory and some files
        temp_dir = path_manager.get_temp_path()
        path_manager.ensure_directory_exists('temp')
        
        temp_files = ['temp1.txt', 'temp2.txt']
        for file_name in temp_files:
            file_path = os.path.join(temp_dir, file_name)
            with open(file_path, 'w') as f:
                f.write('temp content')
        
        # Verify files exist
        for file_name in temp_files:
            file_path = os.path.join(temp_dir, file_name)
            assert os.path.exists(file_path)
        
        # Clean temp directory
        path_manager.clean_temp_directory()
        
        # Verify files are gone but directory remains
        assert os.path.exists(temp_dir)
        assert os.path.isdir(temp_dir)
        for file_name in temp_files:
            file_path = os.path.join(temp_dir, file_name)
            assert not os.path.exists(file_path)

    def test_get_relative_path(self, path_manager):
        """Test getting relative paths."""
        # Create a file
        file_path = path_manager.get_path('input', 'test.txt')
        path_manager.ensure_directory_exists('input')
        with open(file_path, 'w') as f:
            f.write('test')
        
        # Get relative path
        relative_path = path_manager.get_relative_path(file_path)
        expected = os.path.join('input', 'test.txt')
        assert relative_path == expected

    def test_validate_path_exists(self, path_manager):
        """Test validating path exists."""
        # Test existing path
        existing_path = path_manager.base_path
        assert path_manager.validate_path_exists(existing_path) is True
        
        # Test non-existing path
        non_existing_path = path_manager.get_path('nonexistent')
        assert path_manager.validate_path_exists(non_existing_path) is False

    def test_copy_file(self, path_manager, temp_dir):
        """Test copying files."""
        # Create source file
        source_path = path_manager.get_path('source.txt')
        with open(source_path, 'w') as f:
            f.write('source content')
        
        # Copy file
        dest_path = path_manager.get_path('destination.txt')
        path_manager.copy_file(source_path, dest_path)
        
        # Verify copy
        assert os.path.exists(dest_path)
        with open(dest_path, 'r') as f:
            content = f.read()
        assert content == 'source content'

    def test_move_file(self, path_manager):
        """Test moving files."""
        # Create source file
        source_path = path_manager.get_path('move_source.txt')
        with open(source_path, 'w') as f:
            f.write('move content')
        
        # Move file
        dest_path = path_manager.get_path('move_dest.txt')
        path_manager.move_file(source_path, dest_path)
        
        # Verify move
        assert not os.path.exists(source_path)
        assert os.path.exists(dest_path)
        with open(dest_path, 'r') as f:
            content = f.read()
        assert content == 'move content'

    def test_delete_file(self, path_manager):
        """Test deleting files."""
        # Create file
        file_path = path_manager.get_path('delete_test.txt')
        with open(file_path, 'w') as f:
            f.write('delete content')
        
        assert os.path.exists(file_path)
        
        # Delete file
        path_manager.delete_file(file_path)
        assert not os.path.exists(file_path)

    def test_get_file_info(self, path_manager):
        """Test getting file information."""
        # Create test file
        file_path = path_manager.get_path('info_test.txt')
        test_content = 'test content for file info'
        with open(file_path, 'w') as f:
            f.write(test_content)
        
        # Get file info
        file_info = path_manager.get_file_info(file_path)
        
        assert file_info['exists'] is True
        assert file_info['size'] == len(test_content)
        assert 'modified_time' in file_info
        assert 'is_file' in file_info
        assert file_info['is_file'] is True

    def test_get_directory_info(self, path_manager):
        """Test getting directory information."""
        # Create some files in directory
        path_manager.ensure_directory_exists('test_dir')
        test_dir = path_manager.get_path('test_dir')
        
        test_files = ['file1.txt', 'file2.txt']
        for file_name in test_files:
            file_path = os.path.join(test_dir, file_name)
            with open(file_path, 'w') as f:
                f.write('test content')
        
        # Get directory info
        dir_info = path_manager.get_directory_info(test_dir)
        
        assert dir_info['exists'] is True
        assert dir_info['is_directory'] is True
        assert dir_info['file_count'] >= len(test_files)
        assert 'total_size' in dir_info

    def test_create_backup(self, path_manager):
        """Test creating file backups."""
        # Create original file
        original_path = path_manager.get_path('original.txt')
        with open(original_path, 'w') as f:
            f.write('original content')
        
        # Create backup
        backup_path = path_manager.create_backup(original_path)
        
        # Verify backup exists
        assert os.path.exists(backup_path)
        assert os.path.exists(original_path)
        
        # Verify backup content
        with open(backup_path, 'r') as f:
            backup_content = f.read()
        with open(original_path, 'r') as f:
            original_content = f.read()
        
        assert backup_content == original_content

    def test_get_available_space(self, path_manager):
        """Test getting available disk space."""
        space_info = path_manager.get_available_space()
        
        assert 'free' in space_info
        assert 'total' in space_info
        assert isinstance(space_info['free'], int)
        assert isinstance(space_info['total'], int)
        assert space_info['free'] > 0
        assert space_info['total'] > 0

    def test_is_path_safe(self, path_manager):
        """Test path safety validation."""
        # Safe paths
        assert path_manager.is_path_safe('input') is True
        assert path_manager.is_path_safe('output/file.txt') is True
        
        # Unsafe paths (directory traversal)
        assert path_manager.is_path_safe('../outside') is False
        assert path_manager.is_path_safe('input/../../../etc/passwd') is False
        assert path_manager.is_path_safe('..') is False

    def test_resolve_path(self, path_manager):
        """Test path resolution."""
        # Test relative path
        relative_path = 'input/test.txt'
        resolved = path_manager.resolve_path(relative_path)
        expected = path_manager.get_path('input', 'test.txt')
        assert resolved == expected
        
        # Test absolute path (should return as-is if within base)
        absolute_path = path_manager.get_path('absolute', 'test.txt')
        resolved_absolute = path_manager.resolve_path(absolute_path)
        assert resolved_absolute == absolute_path
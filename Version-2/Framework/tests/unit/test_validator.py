"""
Unit tests for Validator utility class.
"""

import pytest
import os
import tempfile
from pathlib import Path

from utils.validator import Validator


class TestValidator:
    """Test cases for Validator class."""

    def test_validate_directory_exists(self, validator, temp_dir):
        """Test validating an existing directory."""
        assert validator.validate_directory_exists(temp_dir) is True
        
        # Test with Path object
        assert validator.validate_directory_exists(Path(temp_dir)) is True

    def test_validate_directory_not_exists(self, validator):
        """Test validating a non-existent directory."""
        assert validator.validate_directory_exists('/nonexistent/directory') is False

    def test_validate_file_exists(self, validator, temp_dir):
        """Test validating an existing file."""
        # Create a test file
        test_file = os.path.join(temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')
        
        assert validator.validate_file_exists(test_file) is True
        
        # Test with Path object
        assert validator.validate_file_exists(Path(test_file)) is True

    def test_validate_file_not_exists(self, validator):
        """Test validating a non-existent file."""
        assert validator.validate_file_exists('/nonexistent/file.txt') is False

    def test_validate_file_extension(self, validator):
        """Test validating file extensions."""
        # Valid extensions
        assert validator.validate_file_extension('test.tif', ['tif', 'tiff']) is True
        assert validator.validate_file_extension('test.jpg', ['jpg', 'jpeg']) is True
        assert validator.validate_file_extension('test.csv', ['csv']) is True
        
        # Invalid extensions
        assert validator.validate_file_extension('test.txt', ['tif', 'jpg']) is False
        assert validator.validate_file_extension('test.tif', ['jpg', 'png']) is False
        
        # Case insensitive
        assert validator.validate_file_extension('test.TIF', ['tif']) is True
        assert validator.validate_file_extension('test.JPG', ['jpg']) is True

    def test_validate_file_size(self, validator, temp_dir):
        """Test validating file sizes."""
        # Create test files with different sizes
        small_file = os.path.join(temp_dir, 'small.txt')
        large_file = os.path.join(temp_dir, 'large.txt')
        
        with open(small_file, 'w') as f:
            f.write('small content')
        
        with open(large_file, 'w') as f:
            f.write('x' * 10000)  # 10KB
        
        # Test size validation
        assert validator.validate_file_size(small_file, min_size=1) is True
        assert validator.validate_file_size(large_file, max_size=5000) is False
        assert validator.validate_file_size(small_file, min_size=1, max_size=1000) is True

    def test_validate_directory_structure(self, validator, sample_project_structure):
        """Test validating required directory structure."""
        required_dirs = ['input', 'output', 'temp', 'logs']
        
        assert validator.validate_directory_structure(sample_project_structure, required_dirs) is True
        
        # Test with missing directory
        required_dirs_with_missing = ['input', 'output', 'missing_dir']
        assert validator.validate_directory_structure(sample_project_structure, required_dirs_with_missing) is False

    def test_validate_required_files(self, validator, sample_project_structure):
        """Test validating required files exist."""
        required_files = ['input/metadata.csv', 'logs/test.log']
        
        assert validator.validate_required_files(sample_project_structure, required_files) is True
        
        # Test with missing file
        required_files_with_missing = ['input/metadata.csv', 'missing_file.txt']
        assert validator.validate_required_files(sample_project_structure, required_files_with_missing) is False

    def test_validate_file_count(self, validator, temp_dir, generate_test_files):
        """Test validating file count in directory."""
        # Generate test files
        test_files = generate_test_files(temp_dir, count=5)
        
        # Test exact count
        assert validator.validate_file_count(temp_dir, expected_count=5, pattern='*.tif') is True
        assert validator.validate_file_count(temp_dir, expected_count=10, pattern='*.tif') is False
        
        # Test range
        assert validator.validate_file_count(temp_dir, min_count=3, max_count=7, pattern='*.tif') is True
        assert validator.validate_file_count(temp_dir, min_count=6, max_count=10, pattern='*.tif') is False

    def test_validate_csv_structure(self, validator, temp_dir):
        """Test validating CSV file structure."""
        # Create valid CSV
        valid_csv = os.path.join(temp_dir, 'valid.csv')
        with open(valid_csv, 'w') as f:
            f.write('title,description,keywords\n')
            f.write('Test1,Description1,keyword1\n')
        
        required_columns = ['title', 'description', 'keywords']
        assert validator.validate_csv_structure(valid_csv, required_columns) is True
        
        # Create invalid CSV (missing columns)
        invalid_csv = os.path.join(temp_dir, 'invalid.csv')
        with open(invalid_csv, 'w') as f:
            f.write('title,description\n')  # Missing keywords column
            f.write('Test1,Description1\n')
        
        assert validator.validate_csv_structure(invalid_csv, required_columns) is False

    def test_validate_image_format(self, validator, sample_tiff_file):
        """Test validating image file formats."""
        # Test TIFF format
        assert validator.validate_image_format(sample_tiff_file, ['tif', 'tiff']) is True
        assert validator.validate_image_format(sample_tiff_file, ['jpg', 'jpeg']) is False

    def test_validate_path_format(self, validator):
        """Test validating path formats."""
        # Valid paths
        assert validator.validate_path_format('/valid/path') is True
        assert validator.validate_path_format('C:\\valid\\path') is True
        assert validator.validate_path_format('relative/path') is True
        
        # Invalid paths (containing invalid characters)
        assert validator.validate_path_format('path/with<invalid') is False
        assert validator.validate_path_format('path/with>invalid') is False
        assert validator.validate_path_format('path/with|invalid') is False

    def test_validate_batch_id_format(self, validator):
        """Test validating batch ID format."""
        # Valid batch IDs
        assert validator.validate_batch_id_format('TEST-001') is True
        assert validator.validate_batch_id_format('PROJECT-2024-001') is True
        assert validator.validate_batch_id_format('BATCH-ABC123') is True
        
        # Invalid batch IDs
        assert validator.validate_batch_id_format('invalid') is False
        assert validator.validate_batch_id_format('TEST_001') is False
        assert validator.validate_batch_id_format('TEST-') is False
        assert validator.validate_batch_id_format('-001') is False

    def test_validate_spreadsheet_id(self, validator):
        """Test validating Google Spreadsheet ID format."""
        # Valid spreadsheet IDs (typical format)
        assert validator.validate_spreadsheet_id('1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms') is True
        assert validator.validate_spreadsheet_id('abcdefghijklmnopqrstuvwxyz1234567890') is True
        
        # Invalid spreadsheet IDs
        assert validator.validate_spreadsheet_id('short') is False
        assert validator.validate_spreadsheet_id('invalid_chars_here!@#') is False
        assert validator.validate_spreadsheet_id('') is False

    def test_validate_encoding(self, validator, temp_dir):
        """Test validating file encoding."""
        # Create UTF-8 file
        utf8_file = os.path.join(temp_dir, 'utf8.txt')
        with open(utf8_file, 'w', encoding='utf-8') as f:
            f.write('UTF-8 content: 测试')
        
        # Create ASCII file
        ascii_file = os.path.join(temp_dir, 'ascii.txt')
        with open(ascii_file, 'w', encoding='ascii') as f:
            f.write('ASCII content only')
        
        # Test encoding validation
        assert validator.validate_encoding(utf8_file, 'utf-8') is True
        assert validator.validate_encoding(ascii_file, 'ascii') is True
        assert validator.validate_encoding(utf8_file, 'ascii') is False

    def test_validate_permissions(self, validator, temp_dir):
        """Test validating file/directory permissions."""
        test_file = os.path.join(temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        
        # Test read permission
        assert validator.validate_permissions(test_file, 'r') is True
        
        # Test write permission
        assert validator.validate_permissions(test_file, 'w') is True
        
        # Test execute permission (file)
        assert validator.validate_permissions(test_file, 'x') is False
        
        # Test directory permissions
        assert validator.validate_permissions(temp_dir, 'r') is True
        assert validator.validate_permissions(temp_dir, 'w') is True
        assert validator.validate_permissions(temp_dir, 'x') is True

    def test_validate_json_structure(self, validator, temp_dir):
        """Test validating JSON file structure."""
        # Create valid JSON
        valid_json = os.path.join(temp_dir, 'valid.json')
        with open(valid_json, 'w') as f:
            f.write('{"name": "test", "value": 123}')
        
        # Create invalid JSON
        invalid_json = os.path.join(temp_dir, 'invalid.json')
        with open(invalid_json, 'w') as f:
            f.write('{"name": "test", "value": 123')  # Missing closing brace
        
        required_fields = ['name', 'value']
        assert validator.validate_json_structure(valid_json, required_fields) is True
        assert validator.validate_json_structure(invalid_json, required_fields) is False

    def test_validate_yaml_structure(self, validator, temp_dir):
        """Test validating YAML file structure."""
        # Create valid YAML
        valid_yaml = os.path.join(temp_dir, 'valid.yaml')
        with open(valid_yaml, 'w') as f:
            f.write('name: test\nvalue: 123\n')
        
        # Create invalid YAML
        invalid_yaml = os.path.join(temp_dir, 'invalid.yaml')
        with open(invalid_yaml, 'w') as f:
            f.write('name: test\nvalue: 123\n  invalid: [')
        
        required_fields = ['name', 'value']
        assert validator.validate_yaml_structure(valid_yaml, required_fields) is True
        assert validator.validate_yaml_structure(invalid_yaml, required_fields) is False

    def test_validate_date_format(self, validator):
        """Test validating date format."""
        # Valid dates
        assert validator.validate_date_format('2024-01-01', '%Y-%m-%d') is True
        assert validator.validate_date_format('01/01/2024', '%m/%d/%Y') is True
        assert validator.validate_date_format('2024-01-01T12:00:00', '%Y-%m-%dT%H:%M:%S') is True
        
        # Invalid dates
        assert validator.validate_date_format('2024-13-01', '%Y-%m-%d') is False  # Invalid month
        assert validator.validate_date_format('2024-01-32', '%Y-%m-%d') is False  # Invalid day
        assert validator.validate_date_format('not-a-date', '%Y-%m-%d') is False

    def test_validate_email_format(self, validator):
        """Test validating email format."""
        # Valid emails
        assert validator.validate_email_format('test@example.com') is True
        assert validator.validate_email_format('user.name@domain.co.uk') is True
        assert validator.validate_email_format('user+tag@example.org') is True
        
        # Invalid emails
        assert validator.validate_email_format('invalid-email') is False
        assert validator.validate_email_format('@domain.com') is False
        assert validator.validate_email_format('user@') is False
        assert validator.validate_email_format('user@domain') is False

    def test_validate_url_format(self, validator):
        """Test validating URL format."""
        # Valid URLs
        assert validator.validate_url_format('https://example.com') is True
        assert validator.validate_url_format('http://example.com/path') is True
        assert validator.validate_url_format('https://example.com/path?param=value') is True
        
        # Invalid URLs
        assert validator.validate_url_format('not-a-url') is False
        assert validator.validate_url_format('ftp://example.com') is False  # Protocol not allowed
        assert validator.validate_url_format('https://') is False

    def test_validate_numeric_range(self, validator):
        """Test validating numeric ranges."""
        # Test integers
        assert validator.validate_numeric_range(5, min_val=1, max_val=10) is True
        assert validator.validate_numeric_range(0, min_val=1, max_val=10) is False
        assert validator.validate_numeric_range(15, min_val=1, max_val=10) is False
        
        # Test floats
        assert validator.validate_numeric_range(5.5, min_val=1.0, max_val=10.0) is True
        assert validator.validate_numeric_range(0.5, min_val=1.0, max_val=10.0) is False

    def test_validate_string_length(self, validator):
        """Test validating string length."""
        # Test within range
        assert validator.validate_string_length('hello', min_length=3, max_length=10) is True
        assert validator.validate_string_length('hi', min_length=3, max_length=10) is False
        assert validator.validate_string_length('this is too long', min_length=3, max_length=10) is False
        
        # Test exact length
        assert validator.validate_string_length('hello', exact_length=5) is True
        assert validator.validate_string_length('hello', exact_length=3) is False

    def test_validate_regex_pattern(self, validator):
        """Test validating regex patterns."""
        # Test pattern matching
        assert validator.validate_regex_pattern('TEST-001', r'^[A-Z]+-\d{3}$') is True
        assert validator.validate_regex_pattern('test-001', r'^[A-Z]+-\d{3}$') is False
        assert validator.validate_regex_pattern('TEST-1', r'^[A-Z]+-\d{3}$') is False
        
        # Test email pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        assert validator.validate_regex_pattern('test@example.com', email_pattern) is True
        assert validator.validate_regex_pattern('invalid-email', email_pattern) is False

    def test_validate_list_content(self, validator):
        """Test validating list content."""
        # Test valid list
        valid_list = ['item1', 'item2', 'item3']
        allowed_items = ['item1', 'item2', 'item3', 'item4']
        assert validator.validate_list_content(valid_list, allowed_items) is True
        
        # Test list with invalid items
        invalid_list = ['item1', 'item2', 'invalid_item']
        assert validator.validate_list_content(invalid_list, allowed_items) is False
        
        # Test empty list
        assert validator.validate_list_content([], allowed_items) is True

    def test_validate_dict_structure(self, validator):
        """Test validating dictionary structure."""
        # Test valid dict
        valid_dict = {'name': 'test', 'value': 123, 'active': True}
        required_keys = ['name', 'value']
        assert validator.validate_dict_structure(valid_dict, required_keys) is True
        
        # Test dict missing keys
        invalid_dict = {'name': 'test'}  # Missing 'value'
        assert validator.validate_dict_structure(invalid_dict, required_keys) is False
        
        # Test with optional keys
        optional_keys = ['active']
        assert validator.validate_dict_structure(valid_dict, required_keys, optional_keys) is True

    def test_validate_coordinates(self, validator):
        """Test validating geographic coordinates."""
        # Valid coordinates
        assert validator.validate_coordinates(40.7128, -74.0060) is True  # NYC
        assert validator.validate_coordinates(51.5074, -0.1278) is True   # London
        assert validator.validate_coordinates(0, 0) is True              # Null Island
        
        # Invalid coordinates
        assert validator.validate_coordinates(91, 0) is False   # Latitude too high
        assert validator.validate_coordinates(-91, 0) is False  # Latitude too low
        assert validator.validate_coordinates(0, 181) is False   # Longitude too high
        assert validator.validate_coordinates(0, -181) is False  # Longitude too low
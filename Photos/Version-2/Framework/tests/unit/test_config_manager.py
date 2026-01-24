"""
Unit tests for ConfigManager class.
"""

import pytest
import os
import tempfile
import yaml
from pathlib import Path

from config.config_manager import ConfigManager


class TestConfigManager:
    """Test cases for ConfigManager class."""

    def test_load_valid_config(self, config_file, sample_config):
        """Test loading a valid configuration file."""
        manager = ConfigManager(config_file)
        
        assert manager.config is not None
        assert manager.get('project.name') == sample_config['project']['name']
        assert manager.get('project.batch_id') == sample_config['project']['batch_id']

    def test_load_nonexistent_file(self):
        """Test loading a configuration file that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            ConfigManager('nonexistent_config.yaml')

    def test_load_invalid_yaml(self, temp_dir):
        """Test loading an invalid YAML file."""
        invalid_yaml_path = os.path.join(temp_dir, 'invalid.yaml')
        with open(invalid_yaml_path, 'w') as f:
            f.write('invalid: yaml: content: [')
        
        with pytest.raises(yaml.YAMLError):
            ConfigManager(invalid_yaml_path)

    def test_get_dot_notation(self, config_manager, sample_config):
        """Test getting configuration values using dot notation."""
        # Test nested access
        assert config_manager.get('project.name') == sample_config['project']['name']
        assert config_manager.get('steps.step1.enabled') is True
        assert config_manager.get('paths.input_dir') == 'input'
        
        # Test default value
        assert config_manager.get('nonexistent.key', 'default') == 'default'
        assert config_manager.get('project.nonexistent', None) is None

    def test_set_dot_notation(self, config_manager):
        """Test setting configuration values using dot notation."""
        # Set new value
        config_manager.set('project.new_field', 'new_value')
        assert config_manager.get('project.new_field') == 'new_value'
        
        # Override existing value
        config_manager.set('project.name', 'Updated Name')
        assert config_manager.get('project.name') == 'Updated Name'
        
        # Set nested value
        config_manager.set('new.nested.key', 'nested_value')
        assert config_manager.get('new.nested.key') == 'nested_value'

    def test_has_key(self, config_manager):
        """Test checking if configuration keys exist."""
        assert config_manager.has('project.name') is True
        assert config_manager.has('steps.step1.enabled') is True
        assert config_manager.has('nonexistent.key') is False
        assert config_manager.has('project.nonexistent') is False

    def test_get_section(self, config_manager, sample_config):
        """Test getting entire configuration sections."""
        project_section = config_manager.get_section('project')
        assert project_section == sample_config['project']
        
        steps_section = config_manager.get_section('steps')
        assert 'step1' in steps_section
        assert 'step2' in steps_section
        
        # Test nonexistent section
        assert config_manager.get_section('nonexistent') is None

    def test_save_config(self, config_manager, temp_dir):
        """Test saving configuration to file."""
        # Modify configuration
        config_manager.set('project.name', 'Saved Project')
        config_manager.set('new.field', 'new_value')
        
        # Save to new file
        saved_path = os.path.join(temp_dir, 'saved_config.yaml')
        config_manager.save(saved_path)
        
        # Load and verify
        with open(saved_path, 'r') as f:
            saved_data = yaml.safe_load(f)
        
        assert saved_data['project']['name'] == 'Saved Project'
        assert saved_data['new']['field'] == 'new_value'

    def test_validate_config_valid(self, config_manager):
        """Test validation of a valid configuration."""
        assert config_manager.validate() is True

    def test_validate_config_missing_required(self, temp_dir, incomplete_config):
        """Test validation of configuration missing required fields."""
        config_path = os.path.join(temp_dir, 'incomplete_config.yaml')
        with open(config_path, 'w') as f:
            yaml.dump(incomplete_config, f)
        
        manager = ConfigManager(config_path)
        assert manager.validate() is False

    def test_get_step_config(self, config_manager):
        """Test getting step-specific configuration."""
        step1_config = config_manager.get_step_config('step1')
        assert step1_config['enabled'] is True
        assert 'spreadsheet_id' in step1_config
        
        step2_config = config_manager.get_step_config('step2')
        assert step2_config['enabled'] is True
        assert step2_config['input_format'] == 'csv'
        
        # Test nonexistent step
        assert config_manager.get_step_config('nonexistent_step') is None

    def test_is_step_enabled(self, config_manager):
        """Test checking if steps are enabled."""
        assert config_manager.is_step_enabled('step1') is True
        assert config_manager.is_step_enabled('step2') is True
        
        # Test disabled step
        config_manager.set('steps.step1.enabled', False)
        assert config_manager.is_step_enabled('step1') is False
        
        # Test nonexistent step
        assert config_manager.is_step_enabled('nonexistent') is False

    def test_get_enabled_steps(self, config_manager):
        """Test getting list of enabled steps."""
        enabled_steps = config_manager.get_enabled_steps()
        assert 'step1' in enabled_steps
        assert 'step2' in enabled_steps
        assert 'step3' in enabled_steps
        
        # Disable a step and test again
        config_manager.set('steps.step2.enabled', False)
        enabled_steps = config_manager.get_enabled_steps()
        assert 'step2' not in enabled_steps
        assert 'step1' in enabled_steps

    def test_get_batch_info(self, config_manager, sample_config):
        """Test getting batch information."""
        batch_info = config_manager.get_batch_info()
        assert batch_info['name'] == sample_config['project']['name']
        assert batch_info['batch_id'] == sample_config['project']['batch_id']
        assert batch_info['description'] == sample_config['project']['description']

    def test_get_paths_config(self, config_manager):
        """Test getting paths configuration."""
        paths = config_manager.get_paths_config()
        assert 'input_dir' in paths
        assert 'output_dir' in paths
        assert 'temp_dir' in paths
        assert paths['input_dir'] == 'input'

    def test_get_validation_config(self, config_manager):
        """Test getting validation configuration."""
        validation = config_manager.get_validation_config()
        assert validation['strict_mode'] is True
        assert 'required_files' in validation

    def test_config_immutable_original(self, config_file):
        """Test that original config data remains immutable."""
        manager1 = ConfigManager(config_file)
        manager2 = ConfigManager(config_file)
        
        # Modify config in first manager
        manager1.set('project.name', 'Modified')
        
        # Verify second manager is unaffected
        assert manager2.get('project.name') != 'Modified'

    def test_reload_config(self, config_manager, temp_dir):
        """Test reloading configuration from file."""
        original_name = config_manager.get('project.name')
        
        # Modify file directly
        config_manager.config['project']['name'] = 'Directly Modified'
        modified_path = os.path.join(temp_dir, 'modified_config.yaml')
        config_manager.save(modified_path)
        
        # Create new manager and reload
        new_manager = ConfigManager(modified_path)
        assert new_manager.get('project.name') == 'Directly Modified'

    def test_deep_copy_config(self, config_manager):
        """Test that config operations use deep copies."""
        original_config = config_manager.config
        
        # Get section and modify it
        project_section = config_manager.get_section('project')
        project_section['name'] = 'Modified Section'
        
        # Verify original config is unchanged
        assert config_manager.get('project.name') != 'Modified Section'
        assert config_manager.config is not original_config

    def test_config_with_special_characters(self, temp_dir):
        """Test handling of configuration with special characters."""
        special_config = {
            'project': {
                'name': 'Test "Project" with \'special\' chars & symbols',
                'description': 'Line 1\nLine 2\tTabbed',
                'unicode_field': '测试项目'
            },
            'special': {
                'path': 'C:\\Users\\Test\\Path\\With\\Backslashes',
                'url': 'https://example.com/path?param=value&other=123'
            }
        }
        
        config_path = os.path.join(temp_dir, 'special_config.yaml')
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(special_config, f, allow_unicode=True)
        
        manager = ConfigManager(config_path)
        assert manager.get('project.name') == special_config['project']['name']
        assert manager.get('project.unicode_field') == special_config['project']['unicode_field']
        assert manager.get('special.path') == special_config['special']['path']

    def test_config_type_safety(self, config_manager):
        """Test type safety in configuration operations."""
        # Test setting different types
        config_manager.set('test.string', 'string_value')
        config_manager.set('test.integer', 42)
        config_manager.set('test.boolean', True)
        config_manager.set('test.list', [1, 2, 3])
        config_manager.set('test.dict', {'key': 'value'})
        
        assert config_manager.get('test.string') == 'string_value'
        assert config_manager.get('test.integer') == 42
        assert config_manager.get('test.boolean') is True
        assert config_manager.get('test.list') == [1, 2, 3]
        assert config_manager.get('test.dict') == {'key': 'value'}
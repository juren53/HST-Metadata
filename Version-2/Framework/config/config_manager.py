"""
Configuration Manager for HSTL Photo Framework

Handles loading, saving, and managing configuration data for projects.
Supports YAML configuration files with hierarchical key access.
"""

import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Union
from datetime import datetime

from config.settings import DEFAULT_SETTINGS


class ConfigManager:
    """Manages configuration for HSTL Photo Framework projects."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file. If None, uses default settings.
        """
        self.config_path = config_path
        self.config_data = DEFAULT_SETTINGS.copy()
        
        if config_path and config_path.exists():
            self.load_config(config_path)
    
    def load_config(self, config_path: Path) -> bool:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
            
            if loaded_config:
                # Merge loaded config with defaults
                self._merge_config(self.config_data, loaded_config)
            
            self.config_path = config_path
            return True
            
        except Exception as e:
            print(f"Error loading configuration from {config_path}: {e}")
            return False
    
    def save_config(self, config_data: Dict, config_path: Path) -> bool:
        """
        Save configuration to YAML file.
        
        Args:
            config_data: Configuration data to save
            config_path: Path to save configuration file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Add metadata
            config_with_meta = config_data.copy()
            config_with_meta['_metadata'] = {
                'framework_version': '1.0.0',
                'created': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat()
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_with_meta, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False)
            
            self.config_data = config_with_meta
            self.config_path = config_path
            return True
            
        except Exception as e:
            print(f"Error saving configuration to {config_path}: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'project.name' or 'steps_completed.step1')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        try:
            current = self.config_data
            for key_part in key.split('.'):
                if isinstance(current, dict) and key_part in current:
                    current = current[key_part]
                else:
                    return default
            return current
        except:
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'project.name')
            value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            keys = key.split('.')
            current = self.config_data
            
            # Navigate to parent of target key
            for key_part in keys[:-1]:
                if key_part not in current:
                    current[key_part] = {}
                current = current[key_part]
            
            # Set the value
            current[keys[-1]] = value
            
            # Update last_modified if metadata exists
            if '_metadata' in self.config_data:
                self.config_data['_metadata']['last_modified'] = datetime.now().isoformat()
            
            return True
            
        except Exception as e:
            print(f"Error setting configuration key '{key}': {e}")
            return False
    
    def update_step_status(self, step_num: int, completed: bool) -> bool:
        """
        Update completion status for a specific step.
        
        Args:
            step_num: Step number (1-8)
            completed: Whether step is completed
            
        Returns:
            True if successful, False otherwise
        """
        key = f'steps_completed.step{step_num}'
        return self.set(key, completed)
    
    def get_step_status(self, step_num: int) -> bool:
        """
        Get completion status for a specific step.
        
        Args:
            step_num: Step number (1-8)
            
        Returns:
            True if completed, False otherwise
        """
        key = f'steps_completed.step{step_num}'
        return self.get(key, False)
    
    def get_next_step(self) -> Optional[int]:
        """
        Get the next step that needs to be completed.
        
        Returns:
            Next step number, or None if all steps completed
        """
        for step_num in range(1, 9):
            if not self.get_step_status(step_num):
                return step_num
        return None
    
    def get_completed_steps(self) -> list:
        """
        Get list of completed step numbers.
        
        Returns:
            List of completed step numbers
        """
        completed = []
        for step_num in range(1, 9):
            if self.get_step_status(step_num):
                completed.append(step_num)
        return completed
    
    def _merge_config(self, base: Dict, overlay: Dict) -> None:
        """
        Recursively merge configuration dictionaries.
        
        Args:
            base: Base configuration dictionary (modified in place)
            overlay: Configuration to overlay on base
        """
        for key, value in overlay.items():
            if (key in base and isinstance(base[key], dict) and 
                isinstance(value, dict)):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def validate_config(self) -> tuple[bool, list]:
        """
        Validate current configuration.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        required_fields = [
            'project.name',
            'project.data_directory'
        ]
        
        for field in required_fields:
            if not self.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Check data directory exists
        data_dir = self.get('project.data_directory')
        if data_dir and not Path(data_dir).exists():
            errors.append(f"Data directory does not exist: {data_dir}")
        
        # Check steps_completed structure
        for step_num in range(1, 9):
            step_key = f'steps_completed.step{step_num}'
            status = self.get(step_key)
            if status is None:
                errors.append(f"Missing step status: {step_key}")
            elif not isinstance(status, bool):
                errors.append(f"Invalid step status type for {step_key}: expected bool")
        
        return len(errors) == 0, errors
    
    def to_dict(self) -> Dict:
        """
        Get current configuration as dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self.config_data.copy()
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return f"ConfigManager(config_path={self.config_path})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"ConfigManager(config_path={self.config_path}, keys={list(self.config_data.keys())})"
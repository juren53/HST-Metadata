"""
Batch Registry Manager for HSTL Photo Framework

Manages multiple batch projects, tracking their status and locations.
Allows users to see all batches in progress and quickly switch between them.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class BatchRegistry:
    """Manages registry of all batch projects."""
    
    def __init__(self, registry_path: Optional[Path] = None):
        """
        Initialize batch registry.
        
        Args:
            registry_path: Path to registry file. If None, uses default location
                          in user's home directory.
        """
        if registry_path is None:
            # Store registry in framework directory
            framework_dir = Path(__file__).parent.parent
            registry_path = framework_dir / 'config' / 'batch_registry.yaml'
        
        self.registry_path = Path(registry_path)
        self.batches = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """Load batch registry from file."""
        if not self.registry_path.exists():
            return {'batches': {}}
        
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data if data else {'batches': {}}
        except Exception as e:
            print(f"Warning: Could not load batch registry: {e}")
            return {'batches': {}}
    
    def _save_registry(self) -> bool:
        """Save batch registry to file."""
        try:
            # Ensure directory exists
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.registry_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.batches, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False)
            return True
        except Exception as e:
            print(f"Error saving batch registry: {e}")
            return False
    
    def register_batch(self, project_name: str, data_directory: str, 
                       config_path: str) -> bool:
        """
        Register a new batch project.
        
        Args:
            project_name: Name of the project
            data_directory: Path to data directory
            config_path: Path to project configuration file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            batch_id = self._generate_batch_id(project_name)
            
            self.batches['batches'][batch_id] = {
                'name': project_name,
                'data_directory': str(Path(data_directory).absolute()),
                'config_path': str(Path(config_path).absolute()),
                'created': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'status': 'active',
            }
            
            return self._save_registry()
        except Exception as e:
            print(f"Error registering batch: {e}")
            return False
    
    def unregister_batch(self, batch_id: str) -> bool:
        """
        Remove a batch from the registry.
        
        Args:
            batch_id: ID of the batch to remove
            
        Returns:
            True if successful, False otherwise
        """
        if batch_id in self.batches['batches']:
            del self.batches['batches'][batch_id]
            return self._save_registry()
        return False
    
    def update_last_accessed(self, batch_id: str) -> bool:
        """Update the last accessed timestamp for a batch."""
        if batch_id in self.batches['batches']:
            self.batches['batches'][batch_id]['last_accessed'] = datetime.now().isoformat()
            return self._save_registry()
        return False
    
    def update_batch_status(self, batch_id: str, status: str) -> bool:
        """
        Update the status of a batch.
        
        Args:
            batch_id: ID of the batch
            status: New status (e.g., 'active', 'completed', 'archived')
            
        Returns:
            True if successful, False otherwise
        """
        if batch_id in self.batches['batches']:
            self.batches['batches'][batch_id]['status'] = status
            return self._save_registry()
        return False
    
    def get_batch(self, batch_id: str) -> Optional[Dict]:
        """Get information about a specific batch."""
        return self.batches['batches'].get(batch_id)
    
    def get_all_batches(self) -> Dict[str, Dict]:
        """Get all registered batches."""
        return self.batches['batches']
    
    def get_active_batches(self) -> Dict[str, Dict]:
        """Get all batches with 'active' status."""
        return {
            batch_id: batch_info 
            for batch_id, batch_info in self.batches['batches'].items()
            if batch_info.get('status') == 'active'
        }
    
    def find_batch_by_name(self, project_name: str) -> Optional[Tuple[str, Dict]]:
        """
        Find a batch by project name.
        
        Returns:
            Tuple of (batch_id, batch_info) or None if not found
        """
        for batch_id, batch_info in self.batches['batches'].items():
            if batch_info['name'] == project_name:
                return batch_id, batch_info
        return None
    
    def find_batch_by_config(self, config_path: str) -> Optional[Tuple[str, Dict]]:
        """
        Find a batch by its config file path.
        
        Returns:
            Tuple of (batch_id, batch_info) or None if not found
        """
        config_path_abs = str(Path(config_path).absolute())
        for batch_id, batch_info in self.batches['batches'].items():
            if batch_info['config_path'] == config_path_abs:
                return batch_id, batch_info
        return None
    
    def _generate_batch_id(self, project_name: str) -> str:
        """Generate a unique batch ID."""
        # Create base ID from project name
        base_id = project_name.lower().replace(' ', '_').replace('-', '_')
        
        # Check if ID already exists
        if base_id not in self.batches['batches']:
            return base_id
        
        # If exists, append a number
        counter = 1
        while f"{base_id}_{counter}" in self.batches['batches']:
            counter += 1
        
        return f"{base_id}_{counter}"
    
    def get_batch_summary(self, batch_id: str) -> Optional[Dict]:
        """
        Get a summary of a batch including step completion status.
        
        Args:
            batch_id: ID of the batch
            
        Returns:
            Dictionary with batch summary including step status
        """
        batch = self.get_batch(batch_id)
        if not batch:
            return None
        
        summary = batch.copy()
        
        # Try to load step completion status from config
        try:
            config_path = Path(batch['config_path'])
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    summary['steps_completed'] = config.get('steps_completed', {})
                    
                    # Calculate completion percentage
                    completed_count = sum(1 for v in summary['steps_completed'].values() if v)
                    summary['completion_percentage'] = (completed_count / 8) * 100
                    summary['completed_steps'] = completed_count
                    summary['total_steps'] = 8
        except Exception as e:
            print(f"Warning: Could not load step status for {batch_id}: {e}")
            summary['steps_completed'] = {}
            summary['completion_percentage'] = 0
            summary['completed_steps'] = 0
            summary['total_steps'] = 8
        
        return summary
    
    def list_batches_summary(self) -> List[Dict]:
        """
        Get a summary of all batches sorted by last accessed.
        
        Returns:
            List of batch summaries
        """
        summaries = []
        for batch_id in self.batches['batches']:
            summary = self.get_batch_summary(batch_id)
            if summary:
                summary['batch_id'] = batch_id
                summaries.append(summary)
        
        # Sort by last accessed (most recent first)
        summaries.sort(key=lambda x: x.get('last_accessed', ''), reverse=True)
        
        return summaries
    
    def __str__(self) -> str:
        """String representation of batch registry."""
        count = len(self.batches['batches'])
        return f"BatchRegistry(batches={count}, registry_path={self.registry_path})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"BatchRegistry(batches={list(self.batches['batches'].keys())}, registry_path={self.registry_path})"

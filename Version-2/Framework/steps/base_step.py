"""
Base Step Processor for HSTL Photo Framework

Defines the abstract base class and common structures for all processing steps.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import logging

from utils.validator import ValidationResult
from utils.path_manager import PathManager
from config.config_manager import ConfigManager


@dataclass
class StepResult:
    """Result of a step execution."""
    success: bool
    message: str
    data: Dict[str, Any] = None
    files_processed: List[Path] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.files_processed is None:
            self.files_processed = []


class ProcessingContext:
    """Shared context passed through the pipeline."""

    def __init__(self,
                 paths: PathManager,
                 config: ConfigManager,
                 logger: logging.Logger,
                 current_step: int = 0,
                 batch_id: Optional[str] = None):
        self.paths = paths
        self.config = config
        self.logger = logger
        self.current_step = current_step
        self.batch_id = batch_id  # Batch identifier for logging
        self.shared_data = {}  # For passing data between steps

    def set_data(self, key: str, value: Any):
        """Set shared data."""
        self.shared_data[key] = value

    def get_data(self, key: str, default: Any = None) -> Any:
        """Get shared data."""
        return self.shared_data.get(key, default)


class StepProcessor(ABC):
    """Abstract base class for all step processors."""
    
    def __init__(self, step_number: int, step_name: str):
        self.step_number = step_number
        self.step_name = step_name
        self.logger = None
    
    def setup(self, context: ProcessingContext) -> bool:
        """Setup the step processor with context."""
        self.logger = context.logger
        return True
    
    @abstractmethod
    def validate_inputs(self, context: ProcessingContext) -> ValidationResult:
        """Validate inputs before step execution."""
        pass
    
    @abstractmethod
    def execute(self, context: ProcessingContext) -> StepResult:
        """Execute the step processing."""
        pass
    
    @abstractmethod
    def validate_outputs(self, context: ProcessingContext) -> ValidationResult:
        """Validate outputs after step execution."""
        pass
    
    def run(self, context: ProcessingContext) -> StepResult:
        """
        Run the complete step: validate inputs, execute, validate outputs.
        
        Args:
            context: Processing context
            
        Returns:
            StepResult indicating success or failure
        """
        context.current_step = self.step_number
        
        if not self.setup(context):
            return StepResult(False, f"Failed to setup Step {self.step_number}")
        
        self.logger.info(f"🔄 Starting Step {self.step_number}: {self.step_name}")
        
        try:
            # Validate inputs
            input_validation = self.validate_inputs(context)
            if not input_validation.is_valid:
                error_msg = f"Input validation failed: {'; '.join(input_validation.errors)}"
                self.logger.error(error_msg)
                return StepResult(False, error_msg)
            
            # Log any warnings
            for warning in input_validation.warnings:
                self.logger.warning(f"Input validation warning: {warning}")
            
            # Execute step
            result = self.execute(context)
            
            if not result.success:
                self.logger.error(f"Step execution failed: {result.message}")
                return result
            
            # Validate outputs
            output_validation = self.validate_outputs(context)
            if not output_validation.is_valid:
                error_msg = f"Output validation failed: {'; '.join(output_validation.errors)}"
                self.logger.error(error_msg)
                return StepResult(False, error_msg)
            
            # Log any output warnings
            for warning in output_validation.warnings:
                self.logger.warning(f"Output validation warning: {warning}")
            
            # Update configuration to mark step as completed
            context.config.update_step_status(self.step_number, True)
            
            self.logger.success(f"Step {self.step_number} completed successfully")
            return result
            
        except Exception as e:
            error_msg = f"Step {self.step_number} failed with exception: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return StepResult(False, error_msg)
    
    def get_config_key(self, key: str) -> str:
        """Get configuration key for this step."""
        return f"step_configurations.step{self.step_number}.{key}"
    
    def get_step_config(self, context: ProcessingContext, key: str, default: Any = None) -> Any:
        """Get configuration value for this step."""
        config_key = self.get_config_key(key)
        return context.config.get(config_key, default)
    
    def __str__(self) -> str:
        return f"Step {self.step_number}: {self.step_name}"
    
    def __repr__(self) -> str:
        return f"StepProcessor(step_number={self.step_number}, step_name='{self.step_name}')"
"""
Unit tests for base StepProcessor class.
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from steps.base_step import StepProcessor


class MockStepProcessor(StepProcessor):
    """Mock implementation of StepProcessor for testing."""
    
    def __init__(self, config, step_name='mock_step'):
        super().__init__(config, step_name)
    
    def validate_inputs(self, context):
        """Mock validation."""
        return True
    
    def execute(self, context):
        """Mock execution."""
        context.add_result(self.step_name, 'success', 'Mock step completed')
        return True
    
    def validate_outputs(self, context):
        """Mock output validation."""
        return True


class TestStepProcessor:
    """Test cases for StepProcessor base class."""

    def test_step_processor_initialization(self, config_manager):
        """Test StepProcessor initialization."""
        step = MockStepProcessor(config_manager.config, 'test_step')
        
        assert step.step_name == 'test_step'
        assert step.config == config_manager.config
        assert step.logger is not None

    def test_step_processor_with_step_config(self, config_manager):
        """Test StepProcessor with step-specific configuration."""
        # Add step config to manager
        config_manager.set('steps.test_step.enabled', True)
        config_manager.set('steps.test_step.param1', 'value1')
        config_manager.set('steps.test_step.param2', 42)
        
        step = MockStepProcessor(config_manager.config, 'test_step')
        
        assert step.get_config_value('enabled') is True
        assert step.get_config_value('param1') == 'value1'
        assert step.get_config_value('param2') == 42
        assert step.get_config_value('nonexistent', 'default') == 'default'

    def test_is_enabled(self, config_manager):
        """Test checking if step is enabled."""
        # Test enabled step
        config_manager.set('steps.enabled_step.enabled', True)
        enabled_step = MockStepProcessor(config_manager.config, 'enabled_step')
        assert enabled_step.is_enabled() is True
        
        # Test disabled step
        config_manager.set('steps.disabled_step.enabled', False)
        disabled_step = MockStepProcessor(config_manager.config, 'disabled_step')
        assert disabled_step.is_enabled() is False
        
        # Test step without config (should default to enabled)
        no_config_step = MockStepProcessor(config_manager.config, 'no_config_step')
        assert no_config_step.is_enabled() is True

    def test_get_step_config(self, config_manager):
        """Test getting step configuration."""
        config_manager.set('steps.test_step.param1', 'value1')
        config_manager.set('steps.test_step.param2', 123)
        
        step = MockStepProcessor(config_manager.config, 'test_step')
        step_config = step.get_step_config()
        
        assert step_config['param1'] == 'value1'
        assert step_config['param2'] == 123

    def test_process_step_success(self, config_manager):
        """Test successful step processing."""
        step = MockStepProcessor(config_manager.config, 'success_step')
        
        # Create mock context
        mock_context = Mock()
        mock_context.add_result = Mock()
        
        # Process step
        result = step.process_step(mock_context)
        
        assert result is True
        mock_context.add_result.assert_called_once()

    def test_process_step_validation_failure(self, config_manager):
        """Test step processing with validation failure."""
        
        class ValidationFailStep(MockStepProcessor):
            def validate_inputs(self, context):
                return False
        
        step = ValidationFailStep(config_manager.config, 'validation_fail_step')
        mock_context = Mock()
        
        result = step.process_step(mock_context)
        
        assert result is False

    def test_process_step_execution_failure(self, config_manager):
        """Test step processing with execution failure."""
        
        class ExecutionFailStep(MockStepProcessor):
            def execute(self, context):
                return False
        
        step = ExecutionFailStep(config_manager.config, 'execution_fail_step')
        mock_context = Mock()
        
        result = step.process_step(mock_context)
        
        assert result is False

    def test_process_step_output_validation_failure(self, config_manager):
        """Test step processing with output validation failure."""
        
        class OutputValidationFailStep(MockStepProcessor):
            def validate_outputs(self, context):
                return False
        
        step = OutputValidationFailStep(config_manager.config, 'output_validation_fail_step')
        mock_context = Mock()
        
        result = step.process_step(mock_context)
        
        assert result is False

    def test_log_step_start(self, config_manager):
        """Test logging step start."""
        step = MockStepProcessor(config_manager.config, 'log_test_step')
        
        with patch.object(step.logger, 'info') as mock_log:
            step.log_step_start()
            mock_log.assert_called_once()
            log_message = mock_log.call_args[0][0]
            assert 'Starting' in log_message
            assert 'log_test_step' in log_message

    def test_log_step_complete(self, config_manager):
        """Test logging step completion."""
        step = MockStepProcessor(config_manager.config, 'log_test_step')
        
        with patch.object(step.logger, 'info') as mock_log:
            step.log_step_complete()
            mock_log.assert_called_once()
            log_message = mock_log.call_args[0][0]
            assert 'Completed' in log_message
            assert 'log_test_step' in log_message

    def test_log_step_error(self, config_manager):
        """Test logging step errors."""
        step = MockStepProcessor(config_manager.config, 'log_test_step')
        test_error = Exception('Test error message')
        
        with patch.object(step.logger, 'error') as mock_log:
            step.log_step_error(test_error)
            mock_log.assert_called_once()
            log_message = mock_log.call_args[0][0]
            assert 'Error' in log_message
            assert 'log_test_step' in log_message
            assert 'Test error message' in log_message

    def test_get_required_input_files(self, config_manager):
        """Test getting required input files."""
        step = MockStepProcessor(config_manager.config, 'file_test_step')
        
        # Default implementation should return empty list
        required_files = step.get_required_input_files()
        assert required_files == []

    def test_get_output_files(self, config_manager):
        """Test getting output files."""
        step = MockStepProcessor(config_manager.config, 'file_test_step')
        
        # Default implementation should return empty list
        output_files = step.get_output_files()
        assert output_files == []

    def test_cleanup_temp_files(self, config_manager, temp_dir):
        """Test cleaning up temporary files."""
        step = MockStepProcessor(config_manager.config, 'cleanup_test_step')
        
        # Create some temp files
        temp_files = []
        for i in range(3):
            temp_file = os.path.join(temp_dir, f'temp_{i}.tmp')
            with open(temp_file, 'w') as f:
                f.write(f'temp content {i}')
            temp_files.append(temp_file)
        
        # Verify files exist
        for temp_file in temp_files:
            assert os.path.exists(temp_file)
        
        # Cleanup temp files
        step.cleanup_temp_files(temp_dir)
        
        # Verify files are gone
        for temp_file in temp_files:
            assert not os.path.exists(temp_file)

    def test_validate_file_exists(self, config_manager, temp_dir):
        """Test validating file exists."""
        step = MockStepProcessor(config_manager.config, 'validate_test_step')
        
        # Create test file
        test_file = os.path.join(temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')
        
        # Test existing file
        assert step.validate_file_exists(test_file) is True
        
        # Test non-existing file
        non_existing_file = os.path.join(temp_dir, 'nonexistent.txt')
        assert step.validate_file_exists(non_existing_file) is False

    def test_validate_directory_exists(self, config_manager, temp_dir):
        """Test validating directory exists."""
        step = MockStepProcessor(config_manager.config, 'validate_test_step')
        
        # Test existing directory
        assert step.validate_directory_exists(temp_dir) is True
        
        # Test non-existing directory
        non_existing_dir = os.path.join(temp_dir, 'nonexistent')
        assert step.validate_directory_exists(non_existing_dir) is False

    def test_get_step_description(self, config_manager):
        """Test getting step description."""
        step = MockStepProcessor(config_manager.config, 'description_test_step')
        
        # Default implementation should return step name
        description = step.get_step_description()
        assert description == 'description_test_step'

    def test_get_step_version(self, config_manager):
        """Test getting step version."""
        step = MockStepProcessor(config_manager.config, 'version_test_step')
        
        # Default implementation should return '1.0.0'
        version = step.get_step_version()
        assert version == '1.0.0'

    def test_check_dependencies(self, config_manager):
        """Test checking step dependencies."""
        step = MockStepProcessor(config_manager.config, 'dependency_test_step')
        
        # Default implementation should return True
        dependencies_ok = step.check_dependencies()
        assert dependencies_ok is True

    def test_get_progress_info(self, config_manager):
        """Test getting progress information."""
        step = MockStepProcessor(config_manager.config, 'progress_test_step')
        
        # Default implementation should return empty dict
        progress_info = step.get_progress_info()
        assert progress_info == {}

    def test_cancel_step(self, config_manager):
        """Test canceling step execution."""
        step = MockStepProcessor(config_manager.config, 'cancel_test_step')
        
        # Default implementation should not raise exception
        step.cancel_step()

    def test_pause_step(self, config_manager):
        """Test pausing step execution."""
        step = MockStepProcessor(config_manager.config, 'pause_test_step')
        
        # Default implementation should not raise exception
        step.pause_step()

    def test_resume_step(self, config_manager):
        """Test resuming step execution."""
        step = MockStepProcessor(config_manager.config, 'resume_test_step')
        
        # Default implementation should not raise exception
        step.resume_step()

    def test_get_step_metrics(self, config_manager):
        """Test getting step metrics."""
        step = MockStepProcessor(config_manager.config, 'metrics_test_step')
        
        # Default implementation should return empty dict
        metrics = step.get_step_metrics()
        assert metrics == {}

    def test_reset_step_state(self, config_manager):
        """Test resetting step state."""
        step = MockStepProcessor(config_manager.config, 'reset_test_step')
        
        # Default implementation should not raise exception
        step.reset_step_state()

    def test_step_with_complex_configuration(self, config_manager):
        """Test step with complex nested configuration."""
        # Set up complex config
        config_manager.set('steps.complex_step.enabled', True)
        config_manager.set('steps.complex_step.input.file_type', 'tif')
        config_manager.set('steps.complex_step.input.bit_depth', 16)
        config_manager.set('steps.complex_step.output.format', 'jpg')
        config_manager.set('steps.complex_step.output.quality', 85)
        config_manager.set('steps.complex_step.processing.resize', True)
        config_manager.set('steps.complex_step.processing.max_dimension', 800)
        
        step = MockStepProcessor(config_manager.config, 'complex_step')
        
        # Test nested config access
        assert step.get_config_value('input.file_type') == 'tif'
        assert step.get_config_value('input.bit_depth') == 16
        assert step.get_config_value('output.format') == 'jpg'
        assert step.get_config_value('output.quality') == 85
        assert step.get_config_value('processing.resize') is True
        assert step.get_config_value('processing.max_dimension') == 800

    def test_step_error_handling(self, config_manager):
        """Test step error handling and logging."""
        
        class ErrorStep(MockStepProcessor):
            def execute(self, context):
                raise ValueError('Test execution error')
        
        step = ErrorStep(config_manager.config, 'error_test_step')
        mock_context = Mock()
        
        with patch.object(step.logger, 'error') as mock_log:
            result = step.process_step(mock_context)
            
            assert result is False
            mock_log.assert_called_once()

    def test_step_with_missing_config(self, config_manager):
        """Test step behavior with missing configuration."""
        step = MockStepProcessor(config_manager.config, 'missing_config_step')
        
        # Should handle missing config gracefully
        assert step.get_config_value('nonexistent') is None
        assert step.get_config_value('nonexistent', 'default') == 'default'
        assert step.is_enabled() is True  # Should default to enabled

    def test_step_context_interaction(self, config_manager):
        """Test step interaction with processing context."""
        
        class ContextInteractionStep(MockStepProcessor):
            def execute(self, context):
                # Test context methods
                context.set_data('test_key', 'test_value')
                value = context.get_data('test_key')
                context.add_result(self.step_name, 'success', f'Value: {value}')
                return True
        
        step = ContextInteractionStep(config_manager.config, 'context_test_step')
        
        # Create mock context with proper methods
        mock_context = Mock()
        mock_context.set_data = Mock()
        mock_context.get_data = Mock(return_value='test_value')
        mock_context.add_result = Mock()
        
        result = step.process_step(mock_context)
        
        assert result is True
        mock_context.set_data.assert_called_once_with('test_key', 'test_value')
        mock_context.get_data.assert_called_once_with('test_key')
        mock_context.add_result.assert_called_once()
"""
Unit tests for StepProcessor base class.

Tests the abstract base class and step execution lifecycle.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock
from abc import ABC

from steps.base_step import StepProcessor, ProcessingContext, StepResult
from utils.validator import ValidationResult
from utils.path_manager import PathManager
from config.config_manager import ConfigManager


class ConcreteStepProcessor(StepProcessor):
    """Concrete implementation for testing."""

    def __init__(self, step_number: int, step_name: str = "Test Step",
                 input_valid: bool = True, output_valid: bool = True,
                 execute_success: bool = True, raise_exception: bool = False):
        super().__init__(step_number, step_name)
        self.input_valid = input_valid
        self.output_valid = output_valid
        self.execute_success = execute_success
        self.raise_exception = raise_exception
        self.setup_called = False
        self.validate_inputs_called = False
        self.execute_called = False
        self.validate_outputs_called = False

    def setup(self, context: ProcessingContext) -> bool:
        self.setup_called = True
        return super().setup(context)

    def validate_inputs(self, context: ProcessingContext) -> ValidationResult:
        self.validate_inputs_called = True
        if self.input_valid:
            return ValidationResult(is_valid=True)
        return ValidationResult(is_valid=False, errors=["Input validation failed"])

    def execute(self, context: ProcessingContext) -> StepResult:
        self.execute_called = True
        if self.raise_exception:
            raise RuntimeError("Test exception")
        return StepResult(
            success=self.execute_success,
            message="Success" if self.execute_success else "Execution failed"
        )

    def validate_outputs(self, context: ProcessingContext) -> ValidationResult:
        self.validate_outputs_called = True
        if self.output_valid:
            return ValidationResult(is_valid=True)
        return ValidationResult(is_valid=False, errors=["Output validation failed"])


@pytest.fixture
def mock_logger():
    """Create a mock logger with all required methods."""
    logger = MagicMock()
    logger.debug = MagicMock()
    logger.info = MagicMock()
    logger.warning = MagicMock()
    logger.error = MagicMock()
    logger.success = MagicMock()
    return logger


@pytest.fixture
def mock_context(temp_dir, mock_logger):
    """Create a mock processing context."""
    paths = PathManager(framework_root=temp_dir, data_directory=str(temp_dir))
    config = ConfigManager()
    return ProcessingContext(
        paths=paths,
        config=config,
        logger=mock_logger
    )


class TestStepProcessorAbstract:
    """Tests for StepProcessor abstract base class."""

    @pytest.mark.unit
    def test_step_processor_is_abstract(self):
        """Cannot instantiate base class directly."""
        with pytest.raises(TypeError):
            StepProcessor(1, "Test")

    @pytest.mark.unit
    def test_step_processor_subclass(self):
        """Can subclass with implementations."""
        step = ConcreteStepProcessor(1, "Test Step")
        assert step is not None
        assert step.step_number == 1
        assert step.step_name == "Test Step"


class TestStepProcessorLifecycle:
    """Tests for step execution lifecycle."""

    @pytest.mark.unit
    def test_step_lifecycle_order(self, mock_context):
        """Lifecycle methods called in correct order."""
        step = ConcreteStepProcessor(1)
        step.run(mock_context)

        assert step.setup_called
        assert step.validate_inputs_called
        assert step.execute_called
        assert step.validate_outputs_called

    @pytest.mark.unit
    def test_step_setup(self, mock_context):
        """Setup called before validate."""
        step = ConcreteStepProcessor(1)
        result = step.run(mock_context)

        assert step.setup_called
        assert step.logger is not None

    @pytest.mark.unit
    def test_step_validate_inputs(self, mock_context):
        """Input validation called before execute."""
        step = ConcreteStepProcessor(1)
        step.run(mock_context)

        assert step.validate_inputs_called

    @pytest.mark.unit
    def test_step_execute(self, mock_context):
        """Execute called after input validation."""
        step = ConcreteStepProcessor(1)
        step.run(mock_context)

        assert step.execute_called

    @pytest.mark.unit
    def test_step_validate_outputs(self, mock_context):
        """Output validation called after execute."""
        step = ConcreteStepProcessor(1)
        step.run(mock_context)

        assert step.validate_outputs_called


class TestStepProcessorResults:
    """Tests for step result handling."""

    @pytest.mark.unit
    def test_step_result_success(self, mock_context):
        """Returns StepResult on success."""
        step = ConcreteStepProcessor(1)
        result = step.run(mock_context)

        assert isinstance(result, StepResult)
        assert result.success
        assert result.message == "Success"

    @pytest.mark.unit
    def test_step_result_failure(self, mock_context):
        """Returns StepResult on failure."""
        step = ConcreteStepProcessor(1, execute_success=False)
        result = step.run(mock_context)

        assert isinstance(result, StepResult)
        assert not result.success

    @pytest.mark.unit
    def test_step_skip_on_input_fail(self, mock_context):
        """Skips execute if input invalid."""
        step = ConcreteStepProcessor(1, input_valid=False)
        result = step.run(mock_context)

        assert step.validate_inputs_called
        assert not step.execute_called
        assert not result.success

    @pytest.mark.unit
    def test_step_skip_on_output_fail(self, mock_context):
        """Returns failure if output validation fails."""
        step = ConcreteStepProcessor(1, output_valid=False)
        result = step.run(mock_context)

        assert step.validate_outputs_called
        assert not result.success


class TestStepProcessorContext:
    """Tests for context access."""

    @pytest.mark.unit
    def test_step_context_access(self, mock_context):
        """Step can access context."""
        step = ConcreteStepProcessor(1)
        step.run(mock_context)

        # Current step should be updated
        assert mock_context.current_step == 1

    @pytest.mark.unit
    def test_step_config_access(self, mock_context):
        """Step can access config through context."""
        # Set a step-specific config value
        mock_context.config.set("step_configurations.step1.test_key", "test_value")

        step = ConcreteStepProcessor(1)
        step.setup(mock_context)

        value = step.get_step_config(mock_context, "test_key")
        assert value == "test_value"

    @pytest.mark.unit
    def test_step_config_default(self, mock_context):
        """Step returns default for missing config."""
        step = ConcreteStepProcessor(1)
        step.setup(mock_context)

        value = step.get_step_config(mock_context, "nonexistent", default="default_value")
        assert value == "default_value"


class TestStepProcessorErrorHandling:
    """Tests for error handling."""

    @pytest.mark.unit
    def test_step_error_handling(self, mock_context):
        """Handles exceptions gracefully."""
        step = ConcreteStepProcessor(1, raise_exception=True)
        result = step.run(mock_context)

        assert not result.success
        assert "exception" in result.message.lower()

    @pytest.mark.unit
    def test_step_logs_error(self, mock_context, mock_logger):
        """Step logs errors appropriately."""
        step = ConcreteStepProcessor(1, raise_exception=True)
        step.run(mock_context)

        # Error should be logged
        assert mock_logger.error.called


class TestStepResult:
    """Tests for StepResult dataclass."""

    @pytest.mark.unit
    def test_step_result_init(self):
        """StepResult can be created."""
        result = StepResult(success=True, message="Test")
        assert result.success
        assert result.message == "Test"

    @pytest.mark.unit
    def test_step_result_defaults(self):
        """StepResult has correct defaults."""
        result = StepResult(success=True, message="Test")
        assert result.data == {}
        assert result.files_processed == []

    @pytest.mark.unit
    def test_step_result_with_data(self):
        """StepResult can include data."""
        result = StepResult(
            success=True,
            message="Test",
            data={"count": 10},
            files_processed=[Path("file1.txt"), Path("file2.txt")]
        )
        assert result.data["count"] == 10
        assert len(result.files_processed) == 2


class TestStepProcessorRepresentation:
    """Tests for string representation."""

    @pytest.mark.unit
    def test_step_str(self):
        """String representation is readable."""
        step = ConcreteStepProcessor(3, "Test Processing")
        str_repr = str(step)

        assert "Step 3" in str_repr
        assert "Test Processing" in str_repr

    @pytest.mark.unit
    def test_step_repr(self):
        """Repr representation includes details."""
        step = ConcreteStepProcessor(3, "Test Processing")
        repr_str = repr(step)

        assert "StepProcessor" in repr_str
        assert "3" in repr_str

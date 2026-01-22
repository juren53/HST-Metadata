"""
Unit tests for Pipeline.

Tests pipeline orchestration and step execution.
"""

import pytest
import logging
from pathlib import Path
from unittest.mock import MagicMock, Mock

from core.pipeline import Pipeline, PipelineResult
from steps.base_step import StepProcessor, ProcessingContext, StepResult
from utils.validator import ValidationResult
from utils.path_manager import PathManager
from config.config_manager import ConfigManager


class MockStepProcessor(StepProcessor):
    """Mock step processor for testing."""

    def __init__(self, step_number: int, step_name: str = "Mock Step",
                 should_succeed: bool = True, raise_exception: bool = False):
        super().__init__(step_number, step_name)
        self.should_succeed = should_succeed
        self.raise_exception = raise_exception
        self.was_executed = False

    def validate_inputs(self, context: ProcessingContext) -> ValidationResult:
        return ValidationResult(is_valid=True)

    def execute(self, context: ProcessingContext) -> StepResult:
        self.was_executed = True
        if self.raise_exception:
            raise RuntimeError("Test exception")
        return StepResult(
            success=self.should_succeed,
            message="Success" if self.should_succeed else "Failed"
        )

    def validate_outputs(self, context: ProcessingContext) -> ValidationResult:
        return ValidationResult(is_valid=True)


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


class TestPipelineInit:
    """Tests for Pipeline initialization."""

    @pytest.mark.unit
    def test_pipeline_init(self, mock_context):
        """Pipeline can be instantiated."""
        pipeline = Pipeline(context=mock_context)
        assert pipeline is not None
        assert pipeline.context == mock_context

    @pytest.mark.unit
    def test_pipeline_init_empty_steps(self, mock_context):
        """Pipeline starts with no registered steps."""
        pipeline = Pipeline(context=mock_context)
        assert len(pipeline.steps) == 0


class TestPipelineRegistration:
    """Tests for step registration."""

    @pytest.mark.unit
    def test_register_step(self, mock_context):
        """Register step processor."""
        pipeline = Pipeline(context=mock_context)
        step = MockStepProcessor(1, "Test Step")

        pipeline.register_step(step)

        assert 1 in pipeline.steps
        assert pipeline.steps[1] == step

    @pytest.mark.unit
    def test_register_multiple_steps(self, mock_context):
        """Register multiple step processors."""
        pipeline = Pipeline(context=mock_context)

        for i in range(1, 4):
            step = MockStepProcessor(i, f"Step {i}")
            pipeline.register_step(step)

        assert len(pipeline.steps) == 3
        assert 1 in pipeline.steps
        assert 2 in pipeline.steps
        assert 3 in pipeline.steps

    @pytest.mark.unit
    def test_register_step_maintains_order(self, mock_context):
        """Steps maintain registration order by number."""
        pipeline = Pipeline(context=mock_context)

        # Register out of order
        pipeline.register_step(MockStepProcessor(3, "Step 3"))
        pipeline.register_step(MockStepProcessor(1, "Step 1"))
        pipeline.register_step(MockStepProcessor(2, "Step 2"))

        # Steps should be accessible by their number
        assert pipeline.steps[1].step_number == 1
        assert pipeline.steps[2].step_number == 2
        assert pipeline.steps[3].step_number == 3

    @pytest.mark.unit
    def test_register_step_duplicate(self, mock_context):
        """Duplicate step number overwrites previous."""
        pipeline = Pipeline(context=mock_context)

        step1 = MockStepProcessor(1, "First Step")
        step2 = MockStepProcessor(1, "Second Step")

        pipeline.register_step(step1)
        pipeline.register_step(step2)

        assert pipeline.steps[1].step_name == "Second Step"


class TestPipelineExecution:
    """Tests for pipeline execution."""

    @pytest.mark.unit
    def test_run_single_step(self, mock_context):
        """Execute single step."""
        pipeline = Pipeline(context=mock_context)
        step = MockStepProcessor(1, "Step 1")
        pipeline.register_step(step)

        result = pipeline.run(start_step=1, end_step=1)

        assert step.was_executed
        assert result.success

    @pytest.mark.unit
    def test_run_step_range(self, mock_context):
        """Execute range of steps."""
        pipeline = Pipeline(context=mock_context)

        steps = []
        for i in range(1, 4):
            step = MockStepProcessor(i, f"Step {i}")
            pipeline.register_step(step)
            steps.append(step)

        result = pipeline.run(start_step=1, end_step=3)

        for step in steps:
            assert step.was_executed
        assert result.success

    @pytest.mark.unit
    def test_run_all_steps(self, mock_context):
        """Execute all steps in order."""
        pipeline = Pipeline(context=mock_context)

        for i in range(1, 9):
            pipeline.register_step(MockStepProcessor(i, f"Step {i}"))

        result = pipeline.run(start_step=1, end_step=8)

        assert result.success
        assert len(result.steps_completed) == 8

    @pytest.mark.unit
    def test_run_dry_run(self, mock_context):
        """Dry run validates without executing."""
        pipeline = Pipeline(context=mock_context)
        step = MockStepProcessor(1, "Step 1")
        pipeline.register_step(step)

        result = pipeline.run(start_step=1, end_step=1, dry_run=True)

        assert not step.was_executed
        # Dry run doesn't add to results
        assert len(result.step_results) == 0


class TestPipelineFailureHandling:
    """Tests for pipeline failure handling."""

    @pytest.mark.unit
    def test_run_step_failure(self, mock_context):
        """Handle step failure."""
        pipeline = Pipeline(context=mock_context)
        step = MockStepProcessor(1, "Failing Step", should_succeed=False)
        pipeline.register_step(step)

        result = pipeline.run(start_step=1, end_step=1)

        assert not result.success
        assert result.error_message is not None

    @pytest.mark.unit
    def test_run_step_failure_stops_pipeline(self, mock_context):
        """Pipeline stops on failure."""
        pipeline = Pipeline(context=mock_context)

        step1 = MockStepProcessor(1, "Step 1", should_succeed=True)
        step2 = MockStepProcessor(2, "Failing Step", should_succeed=False)
        step3 = MockStepProcessor(3, "Step 3", should_succeed=True)

        pipeline.register_step(step1)
        pipeline.register_step(step2)
        pipeline.register_step(step3)

        result = pipeline.run(start_step=1, end_step=3)

        assert step1.was_executed
        assert step2.was_executed
        assert not step3.was_executed
        assert not result.success

    @pytest.mark.unit
    def test_run_step_exception(self, mock_context):
        """Handle step exception."""
        pipeline = Pipeline(context=mock_context)
        step = MockStepProcessor(1, "Exception Step", raise_exception=True)
        pipeline.register_step(step)

        result = pipeline.run(start_step=1, end_step=1)

        assert not result.success
        assert "exception" in result.error_message.lower() or "failed" in result.error_message.lower()


class TestPipelineResult:
    """Tests for PipelineResult class."""

    @pytest.mark.unit
    def test_pipeline_result_success(self):
        """Returns success result."""
        result = PipelineResult()
        step_result = StepResult(success=True, message="Success")
        result.add_step_result(1, step_result)

        assert result.success
        assert 1 in result.steps_completed

    @pytest.mark.unit
    def test_pipeline_result_failure(self):
        """Returns failure with errors."""
        result = PipelineResult()
        step_result = StepResult(success=False, message="Failed")
        result.add_step_result(1, step_result)

        assert not result.success
        assert result.error_message is not None

    @pytest.mark.unit
    def test_pipeline_result_multiple_steps(self):
        """Tracks multiple step results."""
        result = PipelineResult()
        result.add_step_result(1, StepResult(success=True, message="OK"))
        result.add_step_result(2, StepResult(success=True, message="OK"))
        result.add_step_result(3, StepResult(success=True, message="OK"))

        assert result.success
        assert result.steps_completed == [1, 2, 3]
        assert len(result.step_results) == 3


class TestPipelineSkipping:
    """Tests for step skipping behavior."""

    @pytest.mark.unit
    def test_skip_unregistered_step(self, mock_context):
        """Skip steps that aren't registered."""
        pipeline = Pipeline(context=mock_context)
        pipeline.register_step(MockStepProcessor(1, "Step 1"))
        # Step 2 not registered
        pipeline.register_step(MockStepProcessor(3, "Step 3"))

        result = pipeline.run(start_step=1, end_step=3)

        # Should still succeed, just skip step 2
        assert result.success


class TestPipelineLogging:
    """Tests for pipeline logging."""

    @pytest.mark.unit
    def test_pipeline_logs_start(self, mock_context, mock_logger):
        """Pipeline logs execution start."""
        pipeline = Pipeline(context=mock_context)
        pipeline.register_step(MockStepProcessor(1, "Step 1"))

        pipeline.run(start_step=1, end_step=1)

        # Check that info was called at least once
        assert mock_logger.info.called

    @pytest.mark.unit
    def test_pipeline_logs_completion(self, mock_context, mock_logger):
        """Pipeline logs successful completion."""
        pipeline = Pipeline(context=mock_context)
        pipeline.register_step(MockStepProcessor(1, "Step 1"))

        pipeline.run(start_step=1, end_step=1)

        # Check that success was called
        assert mock_logger.success.called

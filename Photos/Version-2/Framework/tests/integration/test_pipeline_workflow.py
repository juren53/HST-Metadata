"""
Integration tests for Pipeline Workflow.

Tests end-to-end pipeline execution and step sequencing.
"""

import pytest
import yaml
from pathlib import Path
from unittest.mock import MagicMock

from core.pipeline import Pipeline, PipelineResult
from steps.base_step import StepProcessor, ProcessingContext, StepResult
from utils.validator import ValidationResult
from utils.path_manager import PathManager
from config.config_manager import ConfigManager


class MockStepProcessor(StepProcessor):
    """Mock step processor that tracks execution."""

    def __init__(self, step_number: int, step_name: str = "Test Step",
                 should_succeed: bool = True, create_output: bool = True):
        super().__init__(step_number, step_name)
        self.should_succeed = should_succeed
        self.create_output = create_output
        self.was_executed = False
        self.execution_order = None

    def validate_inputs(self, context: ProcessingContext) -> ValidationResult:
        return ValidationResult(is_valid=True)

    def execute(self, context: ProcessingContext) -> StepResult:
        self.was_executed = True
        # Track execution order via shared data
        order = context.get_data('execution_order', [])
        order.append(self.step_number)
        context.set_data('execution_order', order)

        if self.create_output:
            # Create a marker file to prove execution
            output_dir = context.paths.get_data_path(f"output/step{self.step_number}")
            if output_dir:
                output_dir.mkdir(parents=True, exist_ok=True)
                marker = output_dir / "completed.marker"
                marker.write_text(f"Step {self.step_number} completed")

        return StepResult(
            success=self.should_succeed,
            message="Success" if self.should_succeed else "Failed"
        )

    def validate_outputs(self, context: ProcessingContext) -> ValidationResult:
        return ValidationResult(is_valid=True)


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    logger = MagicMock()
    logger.debug = MagicMock()
    logger.info = MagicMock()
    logger.warning = MagicMock()
    logger.error = MagicMock()
    logger.success = MagicMock()
    return logger


@pytest.fixture
def project_dir(temp_dir):
    """Create a project directory structure."""
    project = temp_dir / "test_project"
    project.mkdir()

    # Create standard directories
    dirs = ["input", "output", "logs", "config", "reports"]
    for d in dirs:
        (project / d).mkdir()

    return project


@pytest.fixture
def project_config(project_dir):
    """Create a project configuration."""
    config_path = project_dir / "config" / "project_config.yaml"
    config = {
        "project": {
            "name": "Test Project",
            "data_directory": str(project_dir)
        },
        "steps_completed": {f"step{i}": False for i in range(1, 9)},
        "step_configurations": {f"step{i}": {"enabled": True} for i in range(1, 9)}
    }
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
    return config_path


@pytest.fixture
def processing_context(project_dir, mock_logger):
    """Create a processing context for testing."""
    paths = PathManager(
        framework_root=Path(__file__).parent.parent.parent,
        data_directory=str(project_dir)
    )
    config = ConfigManager()
    config.set("project.name", "Test Project")
    config.set("project.data_directory", str(project_dir))
    for i in range(1, 9):
        config.update_step_status(i, False)

    return ProcessingContext(
        paths=paths,
        config=config,
        logger=mock_logger
    )


class TestPipelineStepSequence:
    """Tests for pipeline step sequencing."""

    @pytest.mark.integration
    def test_pipeline_step_sequence(self, processing_context):
        """Steps execute in correct order."""
        pipeline = Pipeline(context=processing_context)

        # Register steps out of order
        pipeline.register_step(MockStepProcessor(3, "Step 3"))
        pipeline.register_step(MockStepProcessor(1, "Step 1"))
        pipeline.register_step(MockStepProcessor(2, "Step 2"))

        result = pipeline.run(start_step=1, end_step=3)

        # Check execution order
        order = processing_context.get_data('execution_order')
        assert order == [1, 2, 3]
        assert result.success

    @pytest.mark.integration
    def test_pipeline_resume_after_failure(self, processing_context):
        """Can resume pipeline after step failure."""
        pipeline = Pipeline(context=processing_context)

        # First run with step 2 failing
        pipeline.register_step(MockStepProcessor(1, "Step 1"))
        pipeline.register_step(MockStepProcessor(2, "Step 2", should_succeed=False))
        pipeline.register_step(MockStepProcessor(3, "Step 3"))

        result1 = pipeline.run(start_step=1, end_step=3)
        assert not result1.success
        assert 1 in result1.steps_completed
        assert 2 not in result1.steps_completed

        # Resume from step 2 with fixed step
        processing_context.shared_data['execution_order'] = []
        pipeline2 = Pipeline(context=processing_context)
        pipeline2.register_step(MockStepProcessor(2, "Step 2 Fixed"))
        pipeline2.register_step(MockStepProcessor(3, "Step 3"))

        result2 = pipeline2.run(start_step=2, end_step=3)
        assert result2.success

    @pytest.mark.integration
    def test_pipeline_skip_completed(self, processing_context):
        """Skips already completed steps when starting from higher step."""
        pipeline = Pipeline(context=processing_context)

        # Only register steps 3 and 4
        step3 = MockStepProcessor(3, "Step 3")
        step4 = MockStepProcessor(4, "Step 4")
        pipeline.register_step(step3)
        pipeline.register_step(step4)

        result = pipeline.run(start_step=3, end_step=4)

        assert result.success
        assert step3.was_executed
        assert step4.was_executed


class TestPipelineExecution:
    """Tests for pipeline execution modes."""

    @pytest.mark.integration
    def test_pipeline_dry_run_no_changes(self, processing_context, project_dir):
        """Dry run makes no file changes."""
        pipeline = Pipeline(context=processing_context)
        step = MockStepProcessor(1, "Step 1", create_output=True)
        pipeline.register_step(step)

        result = pipeline.run(start_step=1, end_step=1, dry_run=True)

        # Step should not be executed
        assert not step.was_executed
        # No output directory should be created
        output_dir = project_dir / "output" / "step1"
        assert not (output_dir / "completed.marker").exists()

    @pytest.mark.integration
    def test_pipeline_creates_output(self, processing_context, project_dir):
        """Pipeline execution creates expected outputs."""
        pipeline = Pipeline(context=processing_context)
        pipeline.register_step(MockStepProcessor(1, "Step 1"))

        result = pipeline.run(start_step=1, end_step=1)

        assert result.success
        output_dir = project_dir / "output" / "step1"
        assert output_dir.exists()
        assert (output_dir / "completed.marker").exists()

    @pytest.mark.integration
    def test_pipeline_step_range(self, processing_context):
        """Run specific step range (e.g., 3-5)."""
        pipeline = Pipeline(context=processing_context)

        for i in range(1, 9):
            pipeline.register_step(MockStepProcessor(i, f"Step {i}"))

        result = pipeline.run(start_step=3, end_step=5)

        order = processing_context.get_data('execution_order')
        assert order == [3, 4, 5]

    @pytest.mark.integration
    def test_pipeline_single_step(self, processing_context):
        """Run single step by number."""
        pipeline = Pipeline(context=processing_context)

        for i in range(1, 9):
            pipeline.register_step(MockStepProcessor(i, f"Step {i}"))

        result = pipeline.run(start_step=5, end_step=5)

        order = processing_context.get_data('execution_order')
        assert order == [5]


class TestPipelineValidation:
    """Tests for pipeline validation."""

    @pytest.mark.integration
    def test_pipeline_output_validation(self, processing_context):
        """Each step validates outputs."""

        class ValidatingStep(MockStepProcessor):
            def validate_outputs(self, context):
                # Check that marker was created
                output_dir = context.paths.get_data_path(f"output/step{self.step_number}")
                if output_dir and (output_dir / "completed.marker").exists():
                    return ValidationResult(is_valid=True)
                return ValidationResult(is_valid=False, errors=["Output missing"])

        pipeline = Pipeline(context=processing_context)
        pipeline.register_step(ValidatingStep(1, "Validating Step"))

        result = pipeline.run(start_step=1, end_step=1)
        assert result.success


class TestPipelineProgress:
    """Tests for pipeline progress tracking."""

    @pytest.mark.integration
    def test_pipeline_config_updates(self, processing_context):
        """Config updated after each step completion."""
        pipeline = Pipeline(context=processing_context)
        pipeline.register_step(MockStepProcessor(1, "Step 1"))
        pipeline.register_step(MockStepProcessor(2, "Step 2"))

        result = pipeline.run(start_step=1, end_step=2)

        # Config should show steps as completed
        assert processing_context.config.get_step_status(1) is True
        assert processing_context.config.get_step_status(2) is True

    @pytest.mark.integration
    def test_pipeline_progress_tracking(self, processing_context):
        """Progress updates during run."""
        pipeline = Pipeline(context=processing_context)

        for i in range(1, 4):
            pipeline.register_step(MockStepProcessor(i, f"Step {i}"))

        result = pipeline.run(start_step=1, end_step=3)

        assert len(result.steps_completed) == 3
        assert result.steps_completed == [1, 2, 3]


class TestPipelineFullWorkflow:
    """Tests for complete workflow scenarios."""

    @pytest.mark.integration
    def test_pipeline_full_workflow(self, processing_context, project_dir):
        """Complete workflow end-to-end."""
        pipeline = Pipeline(context=processing_context)

        # Register all 8 steps
        for i in range(1, 9):
            pipeline.register_step(MockStepProcessor(i, f"Step {i}"))

        result = pipeline.run(start_step=1, end_step=8)

        assert result.success
        assert len(result.steps_completed) == 8

        # All step outputs should exist
        for i in range(1, 9):
            output_dir = project_dir / "output" / f"step{i}"
            assert output_dir.exists()
            assert (output_dir / "completed.marker").exists()

    @pytest.mark.integration
    def test_pipeline_context_passing(self, processing_context):
        """Context passed between steps."""

        class DataSharingStep(MockStepProcessor):
            def execute(self, context):
                # Step 1 sets data, step 2 reads it
                if self.step_number == 1:
                    context.set_data('shared_value', 'from_step_1')
                elif self.step_number == 2:
                    value = context.get_data('shared_value')
                    if value != 'from_step_1':
                        return StepResult(False, "Data not shared")

                return super().execute(context)

        pipeline = Pipeline(context=processing_context)
        pipeline.register_step(DataSharingStep(1, "Step 1"))
        pipeline.register_step(DataSharingStep(2, "Step 2"))

        result = pipeline.run(start_step=1, end_step=2)
        assert result.success

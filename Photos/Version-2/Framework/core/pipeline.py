"""
Pipeline orchestrator for HSTL Photo Framework

Manages the execution of processing steps in sequence.
"""

from typing import List, Dict, Any
import logging

from steps.base_step import StepProcessor, ProcessingContext, StepResult


class PipelineResult:
    """Result of pipeline execution."""
    
    def __init__(self):
        self.success = True
        self.steps_completed = []
        self.step_results = {}
        self.error_message = None
    
    def add_step_result(self, step_num: int, result: StepResult):
        """Add a step result to the pipeline result."""
        self.step_results[step_num] = result
        if result.success:
            self.steps_completed.append(step_num)
        else:
            self.success = False
            if not self.error_message:
                self.error_message = f"Step {step_num} failed: {result.message}"


class Pipeline:
    """Pipeline orchestrator for processing steps."""
    
    def __init__(self, context: ProcessingContext):
        self.context = context
        self.steps: Dict[int, StepProcessor] = {}
        self.logger = context.logger
    
    def register_step(self, step: StepProcessor):
        """Register a step processor."""
        self.steps[step.step_number] = step
        self.logger.debug(f"Registered {step}")
    
    def run(self, start_step: int = 1, end_step: int = 8, dry_run: bool = False) -> PipelineResult:
        """
        Run the pipeline from start_step to end_step.
        
        Args:
            start_step: First step to execute
            end_step: Last step to execute
            dry_run: If True, only validate without executing
            
        Returns:
            PipelineResult with execution results
        """
        result = PipelineResult()
        
        self.logger.info(f"🚀 {'Dry run' if dry_run else 'Starting'} pipeline: steps {start_step}-{end_step}")
        
        for step_num in range(start_step, end_step + 1):
            if step_num not in self.steps:
                self.logger.warning(f"Step {step_num} not registered, skipping")
                continue
            
            step = self.steps[step_num]
            
            if dry_run:
                self.logger.info(f"✅ Would run {step}")
                continue
            
            try:
                step_result = step.run(self.context)
                result.add_step_result(step_num, step_result)
                
                if not step_result.success:
                    self.logger.error(f"Pipeline stopped at step {step_num}")
                    break
                    
            except Exception as e:
                error_msg = f"Pipeline failed at step {step_num}: {str(e)}"
                self.logger.error(error_msg, exc_info=True)
                result.success = False
                result.error_message = error_msg
                break
        
        if result.success:
            self.logger.success("Pipeline completed successfully")
        else:
            self.logger.error(f"Pipeline failed: {result.error_message}")
        
        return result
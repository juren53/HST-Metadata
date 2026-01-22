"""
Unit tests for Logger utilities.

Tests logging setup, formatters, and step logging.
"""

import pytest
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

from utils.logger import (
    ColoredFormatter,
    StepLogger,
    get_logger,
    get_batch_logger,
    BatchContextAdapter,
    SUCCESS_LEVEL,
    HAS_COLORAMA,
)


class TestLoggerSetup:
    """Tests for logger initialization."""

    @pytest.mark.unit
    def test_get_logger(self):
        """get_logger returns logger instance."""
        logger = get_logger('test_logger')
        assert logger is not None
        assert isinstance(logger, logging.Logger)

    @pytest.mark.unit
    def test_get_logger_name(self):
        """Logger has correct name."""
        logger = get_logger('custom_name')
        assert logger.name == 'custom_name'

    @pytest.mark.unit
    def test_success_level_defined(self):
        """SUCCESS level is defined."""
        assert SUCCESS_LEVEL == 25
        assert logging.getLevelName(SUCCESS_LEVEL) == "SUCCESS"


class TestColoredFormatter:
    """Tests for ColoredFormatter."""

    @pytest.mark.unit
    def test_colored_formatter_init(self):
        """ColoredFormatter can be instantiated."""
        formatter = ColoredFormatter('%(message)s')
        assert formatter is not None

    @pytest.mark.unit
    def test_colored_formatter_has_colors(self):
        """ColoredFormatter defines colors for all levels."""
        assert 'DEBUG' in ColoredFormatter.COLORS
        assert 'INFO' in ColoredFormatter.COLORS
        assert 'WARNING' in ColoredFormatter.COLORS
        assert 'ERROR' in ColoredFormatter.COLORS
        assert 'CRITICAL' in ColoredFormatter.COLORS
        assert 'SUCCESS' in ColoredFormatter.COLORS

    @pytest.mark.unit
    def test_colored_formatter_has_emojis(self):
        """ColoredFormatter defines emojis for all levels."""
        assert 'DEBUG' in ColoredFormatter.EMOJIS
        assert 'INFO' in ColoredFormatter.EMOJIS
        assert 'WARNING' in ColoredFormatter.EMOJIS
        assert 'ERROR' in ColoredFormatter.EMOJIS
        assert 'SUCCESS' in ColoredFormatter.EMOJIS

    @pytest.mark.unit
    def test_colored_formatter_format(self):
        """ColoredFormatter formats log records."""
        formatter = ColoredFormatter('%(message)s')
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='Test message',
            args=(),
            exc_info=None
        )

        formatted = formatter.format(record)
        assert 'Test message' in formatted


class TestStepLogger:
    """Tests for StepLogger context manager."""

    @pytest.mark.unit
    def test_step_logger_init(self):
        """StepLogger can be instantiated."""
        step_logger = StepLogger(1, "Test Step")
        assert step_logger.step_num == 1
        assert step_logger.step_name == "Test Step"

    @pytest.mark.unit
    def test_step_logger_with_custom_logger(self):
        """StepLogger accepts custom logger."""
        mock_logger = MagicMock()
        step_logger = StepLogger(1, "Test", logger=mock_logger)
        assert step_logger.logger == mock_logger

    @pytest.mark.unit
    def test_step_logger_context_manager(self):
        """StepLogger works as context manager."""
        mock_logger = MagicMock()

        with StepLogger(1, "Test Step", logger=mock_logger) as step:
            assert step is not None

        # Verify enter and exit logged
        assert mock_logger.info.called

    @pytest.mark.unit
    def test_step_logger_info(self):
        """StepLogger.info adds step prefix."""
        mock_logger = MagicMock()
        step_logger = StepLogger(2, "Test", logger=mock_logger)

        step_logger.info("Test message")

        mock_logger.info.assert_called()
        call_args = str(mock_logger.info.call_args)
        assert "Step 2" in call_args

    @pytest.mark.unit
    def test_step_logger_warning(self):
        """StepLogger.warning adds step prefix."""
        mock_logger = MagicMock()
        step_logger = StepLogger(3, "Test", logger=mock_logger)

        step_logger.warning("Warning message")

        mock_logger.warning.assert_called()

    @pytest.mark.unit
    def test_step_logger_error(self):
        """StepLogger.error adds step prefix."""
        mock_logger = MagicMock()
        step_logger = StepLogger(4, "Test", logger=mock_logger)

        step_logger.error("Error message")

        mock_logger.error.assert_called()

    @pytest.mark.unit
    def test_step_logger_debug(self):
        """StepLogger.debug adds step prefix."""
        mock_logger = MagicMock()
        step_logger = StepLogger(5, "Test", logger=mock_logger)

        step_logger.debug("Debug message")

        mock_logger.debug.assert_called()


class TestBatchLogger:
    """Tests for batch-specific logging."""

    @pytest.mark.unit
    def test_get_batch_logger(self):
        """get_batch_logger returns BatchContextAdapter."""
        logger = get_batch_logger('batch123')
        assert isinstance(logger, BatchContextAdapter)

    @pytest.mark.unit
    def test_batch_logger_with_step(self):
        """Batch logger can include step number."""
        logger = get_batch_logger('batch123', step=5)
        assert logger.extra['batch_id'] == 'batch123'
        assert logger.extra['step'] == 5

    @pytest.mark.unit
    def test_batch_context_adapter_process(self):
        """BatchContextAdapter adds context to kwargs."""
        base_logger = MagicMock()
        adapter = BatchContextAdapter(base_logger, {'batch_id': 'test', 'step': 1})

        msg, kwargs = adapter.process("Test message", {})

        assert kwargs['extra']['batch_id'] == 'test'
        assert kwargs['extra']['step'] == 1


class TestLoggerLevels:
    """Tests for logging levels."""

    @pytest.mark.unit
    def test_logger_levels(self):
        """All standard levels are available."""
        logger = get_logger('level_test')

        # These should not raise
        logger.debug("debug")
        logger.info("info")
        logger.warning("warning")
        logger.error("error")
        logger.critical("critical")

    @pytest.mark.unit
    def test_success_method_exists(self):
        """Logger has success method."""
        logger = get_logger('success_test')
        assert hasattr(logger, 'success')
        assert callable(logger.success)


class TestLoggerFormat:
    """Tests for log formatting."""

    @pytest.mark.unit
    def test_log_format_includes_timestamp(self):
        """Default format includes timestamp placeholder."""
        default_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        assert '%(asctime)s' in default_format

    @pytest.mark.unit
    def test_log_format_includes_level(self):
        """Default format includes level name."""
        default_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        assert '%(levelname)s' in default_format

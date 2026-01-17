"""
Centralized Logging Manager for HSTL Photo Framework

Provides:
- Session-level and per-batch logging
- Configurable verbosity levels
- Thread-safe GUI integration via Qt signals
- Log filtering and routing
"""

import logging
import threading
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler

from PyQt6.QtCore import QObject, pyqtSignal

from utils.console_capture import ConsoleCaptureHandler, ConsoleCaptureContext


# Verbosity level mappings
VERBOSITY_LEVELS = {
    'minimal': logging.WARNING,   # Errors and warnings only
    'normal': logging.INFO,       # Key actions (default)
    'detailed': logging.DEBUG,    # All operations including debug
}


@dataclass
class LogRecord:
    """Enhanced log record with additional metadata for filtering."""
    timestamp: datetime
    level: str
    level_no: int
    source: str
    message: str
    batch_id: Optional[str] = None
    step: Optional[int] = None

    def matches_filter(self, level_filter: str = 'ALL',
                       batch_filter: Optional[str] = None,
                       step_filter: Optional[int] = None,
                       search_text: str = '') -> bool:
        """Check if this record matches the given filters."""
        # Level filter
        if level_filter != 'ALL':
            level_priority = {'DEBUG': 10, 'INFO': 20, 'WARNING': 30, 'ERROR': 40, 'CRITICAL': 50}
            if level_priority.get(self.level, 0) < level_priority.get(level_filter, 0):
                return False

        # Batch filter
        if batch_filter and self.batch_id != batch_filter:
            return False

        # Step filter
        if step_filter is not None and self.step != step_filter:
            return False

        # Text search
        if search_text and search_text.lower() not in self.message.lower():
            return False

        return True

    def format_display(self) -> str:
        """Format record for display in log viewer."""
        timestamp_str = self.timestamp.strftime('%H:%M:%S')
        parts = [f"[{timestamp_str}]", f"[{self.level}]"]

        if self.batch_id:
            parts.append(f"[{self.batch_id[:8]}]")
        if self.step is not None:
            parts.append(f"[Step {self.step}]")

        parts.append(self.message)
        return ' '.join(parts)


class GUILogHandler(logging.Handler, QObject):
    """
    Thread-safe logging handler that emits Qt signals for GUI updates.

    This handler receives log records from Python's logging system and
    converts them to LogRecord objects, then emits a Qt signal that can
    be safely connected to GUI widgets across threads.
    """
    log_emitted = pyqtSignal(object)  # Emits LogRecord

    def __init__(self):
        logging.Handler.__init__(self)
        QObject.__init__(self)
        self.setFormatter(logging.Formatter('%(message)s'))

    def emit(self, record: logging.LogRecord):
        """Convert logging.LogRecord to our LogRecord and emit signal."""
        # Set flag to prevent console capture from re-logging this message
        ConsoleCaptureContext.set_logging_active(True)
        try:
            log_record = LogRecord(
                timestamp=datetime.fromtimestamp(record.created),
                level=record.levelname,
                level_no=record.levelno,
                source=record.name,
                message=self.format(record),
                batch_id=getattr(record, 'batch_id', None),
                step=getattr(record, 'step', None)
            )
            self.log_emitted.emit(log_record)
        except Exception:
            self.handleError(record)
        finally:
            ConsoleCaptureContext.set_logging_active(False)


class BatchFileHandler(RotatingFileHandler):
    """
    Rotating file handler for per-batch logging.

    Creates a log file in the batch's logs directory and automatically
    rotates when the file gets too large.
    """
    def __init__(self, batch_dir: Path, batch_id: str,
                 max_bytes: int = 10*1024*1024, backup_count: int = 3):
        # Create logs directory in batch folder
        log_dir = batch_dir / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f'batch_{batch_id}.log'
        super().__init__(
            str(log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        self.batch_id = batch_id

        # Set formatter
        self.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))


class BatchFilter(logging.Filter):
    """Filter that only allows records matching a specific batch_id."""
    def __init__(self, batch_id: str):
        super().__init__()
        self.batch_id = batch_id

    def filter(self, record: logging.LogRecord) -> bool:
        record_batch = getattr(record, 'batch_id', None)
        return record_batch == self.batch_id


class LogManager:
    """
    Singleton log manager for centralized logging control.

    Manages:
    - Session-level logging to a rotating file
    - Per-batch log files
    - GUI log handler for real-time display
    - Verbosity level control

    Usage:
        log_manager = LogManager.instance()
        log_manager.setup_session_logging(log_path)
        log_manager.info("Application started")
    """

    _instance: Optional['LogManager'] = None
    _lock = threading.Lock()

    @classmethod
    def instance(cls) -> 'LogManager':
        """Get or create the singleton instance."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    @classmethod
    def reset(cls):
        """Reset the singleton (mainly for testing)."""
        with cls._lock:
            if cls._instance is not None:
                cls._instance.shutdown()
            cls._instance = None

    def __init__(self):
        """Initialize the log manager."""
        self._logger = logging.getLogger('hstl_framework')
        self._batch_handlers: Dict[str, BatchFileHandler] = {}
        self._gui_handler: Optional[GUILogHandler] = None
        self._session_handler: Optional[RotatingFileHandler] = None
        self._verbosity = 'normal'
        self._session_log_path: Optional[Path] = None
        self._per_batch_logging = True
        self._enabled = True  # Master switch for logging
        self._console_capture_enabled = False
        self._original_stdout = None
        self._original_stderr = None
        self._initialized = False

    def setup_session_logging(self, log_dir: Path, verbosity: str = 'normal'):
        """
        Initialize session-level logging.

        Args:
            log_dir: Directory for session log files
            verbosity: 'minimal', 'normal', or 'detailed'
        """
        log_dir.mkdir(parents=True, exist_ok=True)

        # Create session log file with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self._session_log_path = log_dir / f'session_{timestamp}.log'

        # Set up rotating file handler for session
        self._session_handler = RotatingFileHandler(
            str(self._session_log_path),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        self._session_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        # Mark as owned by LogManager so setup_logger() preserves it
        self._session_handler._log_manager_owned = True

        # Set verbosity
        self.set_verbosity(verbosity)

        # Add handler to logger
        self._logger.addHandler(self._session_handler)
        self._initialized = True

        self.info(f"Session logging initialized: {self._session_log_path}")

    def get_gui_handler(self) -> GUILogHandler:
        """
        Get or create the GUI log handler.

        Returns:
            GUILogHandler instance for connecting to GUI widgets
        """
        if self._gui_handler is None:
            self._gui_handler = GUILogHandler()
            self._gui_handler.setLevel(VERBOSITY_LEVELS.get(self._verbosity, logging.INFO))
            self._logger.addHandler(self._gui_handler)
        return self._gui_handler

    def setup_batch_logging(self, batch_id: str, batch_dir: Path):
        """
        Create per-batch log file handler.

        Args:
            batch_id: Unique batch identifier
            batch_dir: Batch data directory
        """
        if not self._per_batch_logging:
            return

        if batch_id in self._batch_handlers:
            return  # Already set up

        handler = BatchFileHandler(batch_dir, batch_id)
        handler.setLevel(logging.DEBUG)  # Capture all for batch files
        handler.addFilter(BatchFilter(batch_id))

        self._batch_handlers[batch_id] = handler
        self._logger.addHandler(handler)

        self.info(f"Batch logging initialized for: {batch_id}", batch_id=batch_id)

    def remove_batch_logging(self, batch_id: str):
        """Remove per-batch log handler."""
        if batch_id in self._batch_handlers:
            handler = self._batch_handlers.pop(batch_id)
            self._logger.removeHandler(handler)
            handler.close()

    def set_verbosity(self, level: str):
        """
        Set the verbosity level for all handlers.

        Args:
            level: 'minimal', 'normal', or 'detailed'
        """
        self._verbosity = level
        log_level = VERBOSITY_LEVELS.get(level, logging.INFO)

        # Only set logger level if logging is enabled
        # (otherwise keep it at CRITICAL+1 to suppress messages)
        if self._enabled:
            self._logger.setLevel(log_level)

        if self._session_handler:
            self._session_handler.setLevel(log_level)

        if self._gui_handler:
            self._gui_handler.setLevel(log_level)

    def set_per_batch_logging(self, enabled: bool):
        """Enable or disable per-batch logging."""
        self._per_batch_logging = enabled

    def set_enabled(self, enabled: bool):
        """
        Enable or disable all logging.

        When disabled, log messages are still processed but the logger
        level is set to CRITICAL+1, effectively suppressing all output.
        This provides a master on/off switch for logging.

        Args:
            enabled: True to enable logging, False to disable
        """
        self._enabled = enabled
        if enabled:
            # Restore normal logging level based on verbosity
            self.set_verbosity(self._verbosity)
        else:
            # Set level above CRITICAL to suppress all messages
            self._logger.setLevel(logging.CRITICAL + 1)

    @property
    def enabled(self) -> bool:
        """Get whether logging is enabled."""
        return self._enabled

    def enable_console_capture(self) -> None:
        """
        Enable stdout/stderr capture to logging system.

        All print() statements and direct stdout/stderr writes will be
        captured and routed to the logging system while still appearing
        on the console.
        """
        if self._console_capture_enabled:
            return

        import sys

        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr

        sys.stdout = ConsoleCaptureHandler(
            self._original_stdout,
            self._log_captured_output,
            'stdout'
        )
        sys.stderr = ConsoleCaptureHandler(
            self._original_stderr,
            self._log_captured_output,
            'stderr'
        )

        self._console_capture_enabled = True
        self.info("Console capture enabled - print() statements will appear in logs")

    def disable_console_capture(self) -> None:
        """Restore original stdout/stderr."""
        if not self._console_capture_enabled:
            return

        import sys

        # Flush before restoring
        if hasattr(sys.stdout, 'flush'):
            sys.stdout.flush()
        if hasattr(sys.stderr, 'flush'):
            sys.stderr.flush()

        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr

        self._console_capture_enabled = False
        self.debug("Console capture disabled")

    def _log_captured_output(self, message: str, source: str) -> None:
        """
        Log captured console output.

        Args:
            message: The captured text
            source: 'stdout' or 'stderr'
        """
        # Determine log level based on source
        level = logging.WARNING if source == 'stderr' else logging.INFO

        # Set flag to prevent infinite loop (logging writes to console, which would re-capture)
        ConsoleCaptureContext.set_logging_active(True)
        try:
            # Add a marker to identify captured console output
            extra = {'batch_id': None, 'step': None, 'console_capture': True}
            self._logger.log(level, f"[console] {message}", extra=extra)
        finally:
            ConsoleCaptureContext.set_logging_active(False)

    @property
    def console_capture_enabled(self) -> bool:
        """Get whether console capture is enabled."""
        return self._console_capture_enabled

    @property
    def verbosity(self) -> str:
        """Get current verbosity level."""
        return self._verbosity

    @property
    def session_log_path(self) -> Optional[Path]:
        """Get path to current session log file."""
        return self._session_log_path

    # Convenience logging methods
    def log(self, level: int, message: str,
            batch_id: Optional[str] = None,
            step: Optional[int] = None,
            exc_info: bool = False):
        """
        Log a message with optional batch and step context.

        Args:
            level: Logging level (logging.INFO, etc.)
            message: Log message
            batch_id: Optional batch identifier
            step: Optional step number (1-8)
            exc_info: Include exception info
        """
        # Set flag to prevent console capture from re-logging
        ConsoleCaptureContext.set_logging_active(True)
        try:
            extra = {'batch_id': batch_id, 'step': step}
            self._logger.log(level, message, extra=extra, exc_info=exc_info)
        finally:
            ConsoleCaptureContext.set_logging_active(False)

    def debug(self, message: str, batch_id: Optional[str] = None, step: Optional[int] = None):
        """Log debug message."""
        self.log(logging.DEBUG, message, batch_id, step)

    def info(self, message: str, batch_id: Optional[str] = None, step: Optional[int] = None):
        """Log info message."""
        self.log(logging.INFO, message, batch_id, step)

    def warning(self, message: str, batch_id: Optional[str] = None, step: Optional[int] = None):
        """Log warning message."""
        self.log(logging.WARNING, message, batch_id, step)

    def error(self, message: str, batch_id: Optional[str] = None, step: Optional[int] = None, exc_info: bool = False):
        """Log error message."""
        self.log(logging.ERROR, message, batch_id, step, exc_info=exc_info)

    def critical(self, message: str, batch_id: Optional[str] = None, step: Optional[int] = None, exc_info: bool = False):
        """Log critical message."""
        self.log(logging.CRITICAL, message, batch_id, step, exc_info=exc_info)

    def step_start(self, step: int, step_name: str, batch_id: Optional[str] = None):
        """Log step start."""
        self.info(f"Starting Step {step}: {step_name}", batch_id, step)

    def step_complete(self, step: int, step_name: str, batch_id: Optional[str] = None):
        """Log step completion."""
        self.info(f"Completed Step {step}: {step_name}", batch_id, step)

    def step_error(self, step: int, error: str, batch_id: Optional[str] = None, exc_info: bool = False):
        """Log step error."""
        self.error(f"Step {step} failed: {error}", batch_id, step, exc_info=exc_info)

    def shutdown(self):
        """Close all handlers and clean up."""
        # Disable console capture first
        self.disable_console_capture()

        for handler in list(self._batch_handlers.values()):
            self._logger.removeHandler(handler)
            handler.close()
        self._batch_handlers.clear()

        if self._session_handler:
            self._logger.removeHandler(self._session_handler)
            self._session_handler.close()
            self._session_handler = None

        if self._gui_handler:
            self._logger.removeHandler(self._gui_handler)
            self._gui_handler = None

        self._initialized = False


def get_log_manager() -> LogManager:
    """Convenience function to get the LogManager singleton."""
    return LogManager.instance()

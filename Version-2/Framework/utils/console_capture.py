"""
Console Capture Handler for HSTL Photo Framework

Redirects stdout/stderr to the logging system while preserving original output.
Uses a thread-local flag to prevent duplicate logging when LogManager emits
messages that go to console.
"""

import re
import sys
import threading
from typing import TextIO, Callable, Optional

# Pattern to detect log-formatted messages (timestamp at start)
# Matches: "2024-01-17 11:20:01,243 - " or similar
_LOG_FORMAT_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - ')


class ConsoleCaptureHandler:
    """
    Redirects stdout/stderr to logging system while preserving original output.

    Duplicate Prevention Strategy:
    - Uses thread-local flag (_logging_in_progress) set by LogManager
    - When flag is True, captured output is NOT re-logged
    - When flag is False, captured output IS logged (came from print())
    """

    _logging_in_progress = threading.local()
    _debug = False  # Set to True to trace capture issues

    def __init__(self,
                 original_stream: TextIO,
                 log_callback: Callable[[str, str], None],
                 stream_name: str = 'stdout'):
        """
        Initialize the capture handler.

        Args:
            original_stream: The original sys.stdout or sys.stderr
            log_callback: Function to call with (message, source) for logging
            stream_name: Name of the stream ('stdout' or 'stderr')
        """
        self.original_stream = original_stream
        self.log_callback = log_callback
        self.stream_name = stream_name
        self._buffer = ''
        self._lock = threading.RLock()  # Reentrant lock to prevent deadlock

    def write(self, text: str) -> int:
        """Write to both original stream and logging system."""
        if not text:
            return 0

        # Always write to original stream
        result = self.original_stream.write(text)
        self.original_stream.flush()

        # Only log if not already coming from logging system
        flag_active = getattr(self._logging_in_progress, 'active', False)
        if self._debug:
            self.original_stream.write(f"[CAPTURE DEBUG] flag={flag_active}, text={text[:50]!r}...\n")
            self.original_stream.flush()

        # Skip if flag is set or if text looks like log-formatted output
        if not flag_active and not _LOG_FORMAT_PATTERN.match(text):
            self._capture_to_log(text)

        return result

    def _capture_to_log(self, text: str) -> None:
        """Buffer and log complete lines."""
        with self._lock:
            self._buffer += text
            while '\n' in self._buffer:
                line, self._buffer = self._buffer.split('\n', 1)
                if not line.strip():  # Skip empty lines
                    continue
                # Skip lines that look like they're already from the logging system
                # (prevents infinite loop when StreamHandler writes to captured stdout)
                if _LOG_FORMAT_PATTERN.match(line):
                    if self._debug:
                        self.original_stream.write(f"[CAPTURE DEBUG] skipping log-formatted line\n")
                        self.original_stream.flush()
                    continue
                if self._debug:
                    self.original_stream.write(f"[CAPTURE DEBUG] logging line: {line[:50]!r}\n")
                    self.original_stream.flush()
                try:
                    self.log_callback(line, self.stream_name)
                except Exception as e:
                    self.original_stream.write(f"[CAPTURE ERROR] {e}\n")
                    self.original_stream.flush()

    def flush(self) -> None:
        """Flush both original stream and any buffered content."""
        self.original_stream.flush()
        # Flush any remaining buffer content
        with self._lock:
            if self._buffer.strip():
                # Skip if it looks like log-formatted output
                if not _LOG_FORMAT_PATTERN.match(self._buffer):
                    try:
                        self.log_callback(self._buffer.strip(), self.stream_name)
                    except Exception:
                        pass
                self._buffer = ''

    # Delegate other methods to original stream for compatibility
    def fileno(self):
        return self.original_stream.fileno()

    def isatty(self):
        return self.original_stream.isatty()

    @property
    def encoding(self):
        return self.original_stream.encoding

    @property
    def errors(self):
        return self.original_stream.errors

    @property
    def mode(self):
        return getattr(self.original_stream, 'mode', 'w')

    @property
    def name(self):
        return getattr(self.original_stream, 'name', f'<{self.stream_name}>')

    def readable(self):
        return False

    def writable(self):
        return True

    def seekable(self):
        return False


class ConsoleCaptureContext:
    """Context manager and utilities for console capture."""

    @staticmethod
    def set_logging_active(active: bool) -> None:
        """
        Set the logging-in-progress flag for the current thread.

        Called by LogManager before/after emitting log records to prevent
        captured console output from being re-logged.
        """
        ConsoleCaptureHandler._logging_in_progress.active = active

    @staticmethod
    def is_logging_active() -> bool:
        """Check if logging is currently in progress on this thread."""
        return getattr(ConsoleCaptureHandler._logging_in_progress, 'active', False)

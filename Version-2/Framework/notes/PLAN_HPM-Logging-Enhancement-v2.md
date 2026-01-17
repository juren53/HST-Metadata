# HPM Logging Enhancement Plan v2

## Executive Summary

The HPM (High Performance Metadata) system has a sophisticated logging infrastructure but significant gaps in console output capture and log persistence. This plan outlines focused enhancements to ensure all system output is properly captured and preserved, with emphasis on proven solutions and minimal complexity.

## Current State Analysis

### Strengths
- **Real-time GUI display** with advanced filtering capabilities
- **Session and per-batch file logging** with automatic rotation
- **Colorized console output** for better visibility
- **Thread-safe Qt signal integration** for multi-threaded operations
- **Configurable verbosity levels** (minimal, normal, detailed)
- **Structured LogRecord format** with batch and step context

### Identified Gaps
1. **Console Output Not Fully Captured** - Many `print()` statements bypass the logging system
2. **No Graceful Shutdown** - Logs may be lost on crashes or forced termination
3. **Missing Signal Handlers** - No cleanup on SIGTERM/SIGINT signals
4. **CLI Lacks Shutdown Handling** - Command-line interface doesn't properly close logs
5. **Background Thread Cleanup** - No explicit termination of worker threads
6. **No atexit Handlers** - No guaranteed cleanup mechanism

---

## Phase 0: Technical Spike (Prerequisite)

**Priority: CRITICAL**

Before committing to full implementation, validate core assumptions with a proof-of-concept.

### 0.1 Console Capture PoC

Create a minimal test to validate:
- `sys.stdout`/`sys.stderr` redirection works alongside Qt's event loop
- Performance impact of stream interception (target: <5% overhead on I/O-heavy operations)
- Multi-threaded write safety when multiple threads output simultaneously
- Encoding handling for non-ASCII characters (important for file paths)

**Test Script Location:** `tests/poc_console_capture.py`

```python
# PoC must validate:
# 1. Basic capture works
# 2. Qt signals still function
# 3. No deadlocks under load
# 4. Captured output matches original
```

### 0.2 Signal Handling PoC

Validate Windows-specific signal behavior:
- SIGINT (Ctrl+C) behavior in console vs GUI mode
- SIGBREAK availability and reliability
- Signal handler execution during Qt event processing
- Interaction with Python's default handlers

**Test Script Location:** `tests/poc_signal_handling.py`

### 0.3 Success Criteria for PoC

| Test | Pass Criteria |
|------|---------------|
| Console capture | 100% of test output captured, no corruption |
| Performance | <5% slowdown on 10,000 print statements |
| Thread safety | No deadlocks after 1000 concurrent writes |
| Signal handling | Clean shutdown on Ctrl+C within 2 seconds |
| Qt integration | No interference with GUI responsiveness |

**Decision Gate:** Proceed only if all PoC tests pass. If failures occur, document limitations and adjust plan scope.

---

## Phase 1: Console Output Capture

**Priority: HIGH**

### 1.1 Console Capture Handler

**File:** `utils/console_capture.py`

Create `ConsoleCaptureHandler` using a thread-local flag approach to avoid duplicate logging:

```python
import sys
import threading
from typing import TextIO, Optional

class ConsoleCaptureHandler:
    """
    Redirects stdout/stderr to logging system while preserving original output.

    Duplicate Prevention Strategy:
    - Uses thread-local flag (_logging_in_progress) set by LogManager
    - When flag is True, captured output is NOT re-logged
    - When flag is False, captured output IS logged (came from print())
    """

    _logging_in_progress = threading.local()

    def __init__(self,
                 original_stream: TextIO,
                 log_callback: callable,
                 stream_name: str = 'stdout'):
        self.original_stream = original_stream
        self.log_callback = log_callback
        self.stream_name = stream_name
        self._buffer = ''
        self._lock = threading.Lock()

    def write(self, text: str) -> int:
        """Write to both original stream and logging system."""
        # Always write to original stream
        result = self.original_stream.write(text)
        self.original_stream.flush()

        # Only log if not already coming from logging system
        if not getattr(self._logging_in_progress, 'active', False):
            self._capture_to_log(text)

        return result

    def _capture_to_log(self, text: str) -> None:
        """Buffer and log complete lines."""
        with self._lock:
            self._buffer += text
            while '\n' in self._buffer:
                line, self._buffer = self._buffer.split('\n', 1)
                if line.strip():  # Skip empty lines
                    self.log_callback(line, source=self.stream_name)

    def flush(self) -> None:
        self.original_stream.flush()
        # Flush any remaining buffer content
        with self._lock:
            if self._buffer.strip():
                self.log_callback(self._buffer, source=self.stream_name)
                self._buffer = ''

    # Delegate other methods to original stream
    def fileno(self): return self.original_stream.fileno()
    def isatty(self): return self.original_stream.isatty()
    @property
    def encoding(self): return self.original_stream.encoding
    @property
    def errors(self): return self.original_stream.errors


class ConsoleCaptureContext:
    """Context manager for enabling/disabling console capture."""

    @staticmethod
    def set_logging_active(active: bool) -> None:
        """Called by LogManager before/after emitting log records."""
        ConsoleCaptureHandler._logging_in_progress.active = active
```

**Key Design Decisions:**
- Thread-local flag prevents infinite loops and duplicates
- Line buffering handles partial writes correctly
- Lock protects buffer from concurrent access
- Original stream always receives output (debugging compatibility)

### 1.2 LogManager Integration

**File:** `utils/log_manager.py` (modifications)

```python
# Add to LogManager class:

def _emit_with_flag(self, record):
    """Emit log record with capture prevention flag set."""
    ConsoleCaptureContext.set_logging_active(True)
    try:
        # existing emit logic
        pass
    finally:
        ConsoleCaptureContext.set_logging_active(False)

def enable_console_capture(self) -> None:
    """Enable stdout/stderr capture to logging system."""
    if self._console_capture_enabled:
        return

    self._original_stdout = sys.stdout
    self._original_stderr = sys.stderr

    sys.stdout = ConsoleCaptureHandler(
        self._original_stdout,
        lambda msg, source: self.log(msg, level='INFO', source=source),
        'stdout'
    )
    sys.stderr = ConsoleCaptureHandler(
        self._original_stderr,
        lambda msg, source: self.log(msg, level='WARNING', source=source),
        'stderr'
    )

    self._console_capture_enabled = True

def disable_console_capture(self) -> None:
    """Restore original stdout/stderr."""
    if not self._console_capture_enabled:
        return

    # Flush before restoring
    sys.stdout.flush()
    sys.stderr.flush()

    sys.stdout = self._original_stdout
    sys.stderr = self._original_stderr

    self._console_capture_enabled = False
```

### 1.3 Print Statement Audit and Replacement

**Primary Target:** `hstl_framework.py`

Before replacing print statements, complete an audit:

**Audit Checklist:**
- [ ] Count total print statements by category (status, error, debug, user-facing)
- [ ] Identify which prints are user-facing (must remain visible)
- [ ] Identify which prints are debug/status (can be log-only)
- [ ] Check for prints in exception handlers (ensure they log before potential crash)

**Replacement Strategy:**

| Print Type | Replacement | Log Level |
|------------|-------------|-----------|
| User-facing status | `logger.info()` with console handler | INFO |
| Error messages | `logger.error()` | ERROR |
| Debug output | `logger.debug()` | DEBUG |
| Progress updates | `logger.info()` | INFO |
| Validation results | `logger.info()` or `logger.warning()` | INFO/WARNING |

**Example Replacements:**

```python
# Before:
print(f"Processing {filename}...")
print(f"Error: {e}", file=sys.stderr)
print("Done!")

# After:
logger.info(f"Processing {filename}...")
logger.error(f"Error: {e}")
logger.info("Done!")
```

**Files Requiring Audit:**
1. `hstl_framework.py` - CLI interface (primary target)
2. `gui/hstl_gui.py` - GUI entry point
3. `utils/` - Utility modules
4. Any module using `print()` for status output

---

## Phase 2: Graceful Shutdown Implementation

**Priority: HIGH**

### 2.1 Shutdown Manager

**File:** `utils/shutdown_manager.py`

```python
import atexit
import signal
import sys
import threading
from typing import Callable, List, Optional

class ShutdownManager:
    """
    Coordinates graceful shutdown across application components.

    Handles:
    - Signal-based termination (SIGINT, SIGTERM, SIGBREAK)
    - atexit registration for normal termination
    - Thread cleanup coordination
    - Log flushing before exit

    Limitations (documented):
    - atexit handlers don't run on os._exit() or SIGKILL
    - Signal handlers may not execute during blocking I/O
    - Crash scenarios require periodic auto-flush (see Phase 2.3)
    """

    _instance: Optional['ShutdownManager'] = None
    _lock = threading.Lock()

    def __new__(cls) -> 'ShutdownManager':
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._shutdown_callbacks: List[Callable] = []
        self._shutdown_in_progress = False
        self._original_handlers = {}
        self._initialized = True

    def register_callback(self, callback: Callable, priority: int = 50) -> None:
        """
        Register a shutdown callback.

        Args:
            callback: Function to call during shutdown (no arguments)
            priority: Lower numbers execute first (0-100)
        """
        self._shutdown_callbacks.append((priority, callback))
        self._shutdown_callbacks.sort(key=lambda x: x[0])

    def install_handlers(self) -> None:
        """Install signal handlers and atexit registration."""
        # Register atexit handler
        atexit.register(self._execute_shutdown)

        # Install signal handlers
        self._install_signal_handler(signal.SIGINT)
        self._install_signal_handler(signal.SIGTERM)

        # Windows-specific
        if hasattr(signal, 'SIGBREAK'):
            self._install_signal_handler(signal.SIGBREAK)

    def _install_signal_handler(self, sig: signal.Signals) -> None:
        """Install handler for a specific signal, preserving original."""
        try:
            original = signal.signal(sig, self._signal_handler)
            self._original_handlers[sig] = original
        except (OSError, ValueError):
            # Signal not available on this platform or not main thread
            pass

    def _signal_handler(self, signum: int, frame) -> None:
        """Handle termination signals."""
        if self._shutdown_in_progress:
            # Force exit if shutdown is stuck
            sys.exit(1)

        self._execute_shutdown()
        sys.exit(0)

    def _execute_shutdown(self) -> None:
        """Execute all registered shutdown callbacks."""
        if self._shutdown_in_progress:
            return

        self._shutdown_in_progress = True

        for priority, callback in self._shutdown_callbacks:
            try:
                callback()
            except Exception as e:
                # Log to stderr since logging may be compromised
                sys.stderr.write(f"Shutdown callback error: {e}\n")

        self._shutdown_in_progress = False

    def uninstall_handlers(self) -> None:
        """Restore original signal handlers."""
        for sig, handler in self._original_handlers.items():
            try:
                signal.signal(sig, handler)
            except (OSError, ValueError):
                pass
        self._original_handlers.clear()
```

### 2.2 Application Integration

**GUI Application (`gui/hstl_gui.py`):**

```python
# At application startup:
from utils.shutdown_manager import ShutdownManager

def main():
    shutdown_manager = ShutdownManager()

    # Register LogManager shutdown (priority 90 - run late)
    shutdown_manager.register_callback(
        LogManager.instance().shutdown,
        priority=90
    )

    # Register thread cleanup (priority 50 - run mid)
    shutdown_manager.register_callback(
        cleanup_background_threads,
        priority=50
    )

    # Install handlers
    shutdown_manager.install_handlers()

    # ... rest of application startup
```

**GUI Main Window (`gui/main_window.py`):**

```python
def closeEvent(self, event: QCloseEvent) -> None:
    """Enhanced close event with comprehensive cleanup."""

    # 1. Stop accepting new work
    self._accepting_work = False

    # 2. Terminate background threads with timeout
    threads_to_stop = [
        self.update_check_thread,
        self.git_update_thread,
        # ... other threads
    ]

    timeout_ms = 5000  # 5 second timeout
    deadline = QDeadlineTimer(timeout_ms)

    for thread in threads_to_stop:
        if thread and thread.isRunning():
            thread.requestInterruption()

    for thread in threads_to_stop:
        if thread and thread.isRunning():
            remaining = deadline.remainingTime()
            if remaining > 0:
                thread.wait(remaining)
            else:
                # Log timeout but don't block forever
                logger.warning(f"Thread {thread.objectName()} did not stop in time")

    # 3. Save application state
    self._save_window_state()

    # 4. Accept the close event
    event.accept()
```

**CLI Application (`hstl_framework.py`):**

```python
def main():
    shutdown_manager = ShutdownManager()
    shutdown_manager.register_callback(LogManager.instance().shutdown, priority=90)
    shutdown_manager.install_handlers()

    try:
        # ... CLI logic
        pass
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")
    finally:
        # Explicit shutdown (atexit is backup)
        shutdown_manager._execute_shutdown()
```

### 2.3 Auto-Flush for Crash Resilience

**File:** `utils/log_manager.py` (additions)

```python
import threading

class LogManager:
    def __init__(self):
        # ... existing init
        self._auto_flush_timer: Optional[threading.Timer] = None
        self._auto_flush_interval = 60  # seconds

    def enable_auto_flush(self, interval_seconds: int = 60) -> None:
        """Enable periodic log flushing for crash resilience."""
        self._auto_flush_interval = interval_seconds
        self._schedule_auto_flush()

    def _schedule_auto_flush(self) -> None:
        """Schedule the next auto-flush."""
        if self._auto_flush_timer:
            self._auto_flush_timer.cancel()

        self._auto_flush_timer = threading.Timer(
            self._auto_flush_interval,
            self._auto_flush
        )
        self._auto_flush_timer.daemon = True  # Don't prevent shutdown
        self._auto_flush_timer.start()

    def _auto_flush(self) -> None:
        """Flush all log handlers."""
        try:
            for handler in self._handlers:
                handler.flush()
        except Exception:
            pass  # Don't let flush errors crash the timer
        finally:
            self._schedule_auto_flush()

    def disable_auto_flush(self) -> None:
        """Disable periodic log flushing."""
        if self._auto_flush_timer:
            self._auto_flush_timer.cancel()
            self._auto_flush_timer = None
```

---

## Phase 3: Configuration and Settings (Deferred)

**Priority: MEDIUM - Implement after Phase 1 and 2 are stable**

### 3.1 Minimal Configuration Additions

**File:** `config/settings.py`

Add only essential configuration options:

```json
{
  "logging": {
    "console_capture_enabled": true,
    "auto_flush_interval_seconds": 60,
    "log_retention_days": 30
  }
}
```

### 3.2 Simple Log Cleanup

**File:** `utils/log_manager.py`

```python
def cleanup_old_logs(self, retention_days: int = 30) -> int:
    """
    Delete log files older than retention_days.

    Returns:
        Number of files deleted
    """
    import os
    from datetime import datetime, timedelta

    cutoff = datetime.now() - timedelta(days=retention_days)
    deleted_count = 0

    log_dir = self._get_log_directory()

    for filename in os.listdir(log_dir):
        if not filename.endswith('.log'):
            continue

        filepath = os.path.join(log_dir, filename)
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            if mtime < cutoff:
                os.remove(filepath)
                deleted_count += 1
        except OSError:
            pass  # Skip files we can't access

    return deleted_count
```

**Deliberately Excluded Features:**
- Log compression (adds complexity, minimal disk savings for text logs)
- Searchable index (overkill for a metadata tool)
- Integrity checking (standard file operations are sufficient)
- Storage monitoring (users can monitor their own disk space)

---

## Phase 4: Testing Strategy

**Priority: HIGH - Execute alongside implementation**

### 4.1 Unit Tests

**File:** `tests/test_console_capture.py`

```python
def test_stdout_capture():
    """Verify stdout is captured to log."""

def test_stderr_capture():
    """Verify stderr is captured to log."""

def test_no_duplicate_logging():
    """Verify logger output isn't re-captured."""

def test_multithread_capture():
    """Verify thread-safe capture from multiple threads."""

def test_encoding_handling():
    """Verify non-ASCII characters are handled correctly."""

def test_buffer_flush():
    """Verify partial lines are flushed on close."""
```

**File:** `tests/test_shutdown_manager.py`

```python
def test_callback_registration():
    """Verify callbacks are registered and sorted by priority."""

def test_callback_execution_order():
    """Verify callbacks execute in priority order."""

def test_shutdown_idempotent():
    """Verify multiple shutdown calls don't re-execute callbacks."""

def test_callback_error_isolation():
    """Verify one failing callback doesn't prevent others."""
```

### 4.2 Integration Tests

**File:** `tests/test_logging_integration.py`

```python
def test_cli_logging_complete():
    """Run CLI command and verify all output appears in log file."""

def test_gui_shutdown_logs_preserved():
    """Start GUI, perform action, close, verify logs saved."""

def test_ctrl_c_graceful_shutdown():
    """Send SIGINT and verify clean shutdown with logs preserved."""
```

### 4.3 Manual Testing Checklist

| Scenario | Steps | Expected Result |
|----------|-------|-----------------|
| Normal GUI close | Start GUI, close window | Logs flushed, no errors |
| Ctrl+C in CLI | Run CLI command, press Ctrl+C | "Cancelled" message logged, clean exit |
| Task Manager kill | Kill process via Task Manager | Logs up to last auto-flush preserved |
| Long-running operation | Start batch, close mid-way | Partial progress logged |
| Rapid output | Generate 10,000 prints quickly | All captured, no deadlock |

---

## Implementation Checklist

### Phase 0: Technical Spike
- [ ] Create `tests/poc_console_capture.py`
- [ ] Create `tests/poc_signal_handling.py`
- [ ] Run PoC tests and document results
- [ ] **Decision gate:** Proceed or adjust scope

### Phase 1: Console Output Capture
- [ ] Create `utils/console_capture.py`
- [ ] Modify `utils/log_manager.py` with capture integration
- [ ] Audit print statements in `hstl_framework.py`
- [ ] Replace print statements (batch by category)
- [ ] Write unit tests for console capture
- [ ] Test Qt integration (no GUI freezing)

### Phase 2: Graceful Shutdown
- [ ] Create `utils/shutdown_manager.py`
- [ ] Integrate shutdown manager in `gui/hstl_gui.py`
- [ ] Integrate shutdown manager in `hstl_framework.py`
- [ ] Enhance `main_window.py` closeEvent
- [ ] Implement auto-flush in LogManager
- [ ] Write unit tests for shutdown manager
- [ ] Manual testing of all termination scenarios

### Phase 3: Configuration (Deferred)
- [ ] Add logging configuration to settings
- [ ] Implement log cleanup
- [ ] Update settings dialog (if needed)

### Phase 4: Testing
- [ ] Complete unit test suite
- [ ] Complete integration test suite
- [ ] Execute manual testing checklist
- [ ] Document any known limitations

---

## Rollback Plan

If issues arise after deployment:

### Feature Flags

```python
# In config/settings.py or as environment variables:
CONSOLE_CAPTURE_ENABLED = True  # Set False to disable capture
SHUTDOWN_MANAGER_ENABLED = True  # Set False to use original behavior
```

### Quick Disable

```python
# In utils/console_capture.py:
class ConsoleCaptureHandler:
    DISABLED = False  # Set True to bypass all capture

    def write(self, text):
        if self.DISABLED:
            return self.original_stream.write(text)
        # ... normal logic
```

### Full Rollback

If critical issues are found:
1. Revert `utils/console_capture.py` changes
2. Revert `utils/shutdown_manager.py` changes
3. Revert LogManager modifications
4. Keep print statement replacements (they're an improvement regardless)

---

## Dependencies

**No new external dependencies required.**

All functionality uses Python standard library:
- `sys` - stream redirection
- `threading` - thread safety, timers
- `signal` - signal handling
- `atexit` - exit registration

---

## Risk Assessment

### Low Risk
- Print statement replacement (straightforward, reversible)
- Atexit registration (standard Python pattern)
- Log cleanup (simple file operations)

### Medium Risk
- Console capture (tested via PoC first)
  - *Mitigation:* Feature flag to disable
- Signal handling on Windows (platform-specific behavior)
  - *Mitigation:* PoC validates behavior, fallback to atexit only

### Mitigated by Design
- Infinite loop in capture → Thread-local flag prevents
- Deadlock in multi-threaded capture → Lock with buffering prevents
- Lost logs on crash → Auto-flush every 60s limits loss

---

## Success Criteria

### Must Have (Phase 1 & 2)
- All `print()` output appears in log files
- Graceful shutdown on normal close and Ctrl+C
- No deadlocks or performance regression >5%
- Logs survive normal termination scenarios

### Should Have (Phase 3)
- Configurable capture behavior
- Automatic old log cleanup

### Won't Have (Out of Scope)
- Log compression
- Searchable log index
- Disk space monitoring
- Log integrity verification

---

## Conclusion

This revised plan focuses on solving the core problems—console capture and graceful shutdown—with proven, simple solutions. The technical spike in Phase 0 validates assumptions before significant development investment. Feature flags and rollback procedures ensure issues can be quickly addressed.

By deferring advanced features (compression, indexing, monitoring) and avoiding over-engineering, this plan delivers reliable logging improvements with minimal risk and maintenance burden.

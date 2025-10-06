"""
Logging utilities for HSTL Photo Framework

Provides structured logging with colorized console output and file logging.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler

try:
    import colorama
    from colorama import Fore, Style
    colorama.init()
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels."""
    
    COLORS = {
        'DEBUG': Fore.CYAN if HAS_COLORAMA else '',
        'INFO': Fore.GREEN if HAS_COLORAMA else '',
        'WARNING': Fore.YELLOW if HAS_COLORAMA else '',
        'ERROR': Fore.RED if HAS_COLORAMA else '',
        'CRITICAL': Fore.RED + Style.BRIGHT if HAS_COLORAMA else '',
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        reset = Style.RESET_ALL if HAS_COLORAMA else ''
        
        # Apply color to the level name
        record.levelname = f"{log_color}{record.levelname}{reset}"
        
        return super().format(record)


def setup_logger(name: str = 'hstl_framework', 
                 level: str = 'INFO',
                 log_file: Optional[Path] = None,
                 format_str: Optional[str] = None) -> logging.Logger:
    """
    Set up a logger with console and optional file output.
    
    Args:
        name: Logger name
        level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_file: Path to log file (optional)
        format_str: Custom format string (optional)
        
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Default format
    if not format_str:
        format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    if HAS_COLORAMA:
        console_formatter = ColoredFormatter(format_str)
    else:
        console_formatter = logging.Formatter(format_str)
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        try:
            # Ensure log directory exists
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Rotating file handler (10MB max, 5 backups)
            file_handler = RotatingFileHandler(
                log_file, 
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)  # File gets all messages
            
            file_formatter = logging.Formatter(format_str)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            logger.warning(f"Could not set up file logging: {e}")
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str = 'hstl_framework') -> logging.Logger:
    """
    Get an existing logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class StepLogger:
    """Context manager for step-specific logging."""
    
    def __init__(self, step_num: int, step_name: str, logger: Optional[logging.Logger] = None):
        self.step_num = step_num
        self.step_name = step_name
        self.logger = logger or get_logger()
    
    def __enter__(self):
        self.logger.info(f"🔄 Starting Step {self.step_num}: {self.step_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.logger.error(f"❌ Step {self.step_num} failed: {exc_val}")
        else:
            self.logger.info(f"✅ Step {self.step_num} completed successfully")
    
    def info(self, message: str):
        """Log info message with step prefix."""
        self.logger.info(f"[Step {self.step_num}] {message}")
    
    def warning(self, message: str):
        """Log warning message with step prefix."""
        self.logger.warning(f"[Step {self.step_num}] {message}")
    
    def error(self, message: str):
        """Log error message with step prefix."""
        self.logger.error(f"[Step {self.step_num}] {message}")
    
    def debug(self, message: str):
        """Log debug message with step prefix."""
        self.logger.debug(f"[Step {self.step_num}] {message}")


# Example usage and testing
if __name__ == '__main__':
    # Test the logger
    test_log_file = Path('test_framework.log')
    logger = setup_logger('test', 'DEBUG', test_log_file)
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test step logger
    with StepLogger(2, "CSV Conversion", logger) as step_logger:
        step_logger.info("Processing spreadsheet data...")
        step_logger.warning("Found some non-standard characters")
        step_logger.info("Conversion completed successfully")
    
    print(f"Log file created: {test_log_file}")
    
    # Clean up test file
    if test_log_file.exists():
        test_log_file.unlink()
"""
Centralized logging system for MetaPicPick
Provides consistent logging across all modules with configurable levels and outputs.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from .common_imports import ConfigurationError

class MetaPicPickLogger:
    """Centralized logger for the MetaPicPick application"""
    
    _instance: Optional['MetaPicPickLogger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls) -> 'MetaPicPickLogger':
        """Singleton pattern to ensure one logger instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the logging system if not already done"""
        if self._logger is None:
            self.setup_logger()
    
    def setup_logger(self, 
                    log_level: str = "INFO",
                    log_to_file: bool = True,
                    log_to_console: bool = True,
                    log_file_path: Optional[str] = None,
                    max_log_size: int = 10 * 1024 * 1024,  # 10MB
                    backup_count: int = 5):
        """
        Set up the logging configuration
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Whether to log to file
            log_to_console: Whether to log to console
            log_file_path: Custom log file path (optional)
            max_log_size: Maximum log file size in bytes before rotation
            backup_count: Number of backup log files to keep
        """
        
        # Create logger
        self._logger = logging.getLogger('MetaPicPick')
        
        # Set log level
        level = getattr(logging, log_level.upper(), logging.INFO)
        self._logger.setLevel(level)
        
        # Clear any existing handlers to avoid duplicates
        self._logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        if log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)
        
        # File handler with rotation
        if log_to_file:
            if log_file_path is None:
                # Create logs directory
                logs_dir = Path(__file__).parent.parent / "logs"
                logs_dir.mkdir(exist_ok=True)
                log_file_path = logs_dir / "metapicpick.log"
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file_path,
                maxBytes=max_log_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
        
        # Log the initialization
        self._logger.info("MetaPicPick logging system initialized")
        self._logger.info(f"Log level set to: {log_level}")
        if log_to_file:
            self._logger.info(f"Logging to file: {log_file_path}")
    
    @property
    def logger(self) -> logging.Logger:
        """Get the logger instance"""
        if self._logger is None:
            self.setup_logger()
        return self._logger
    
    def debug(self, message: str, *args, **kwargs):
        """Log debug message"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log info message"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning message"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, exception: Optional[Exception] = None, *args, **kwargs):
        """Log error message with optional exception details"""
        if exception:
            self.logger.error(f"{message}: {exception}", exc_info=True, *args, **kwargs)
        else:
            self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, exception: Optional[Exception] = None, *args, **kwargs):
        """Log critical message with optional exception details"""
        if exception:
            self.logger.critical(f"{message}: {exception}", exc_info=True, *args, **kwargs)
        else:
            self.logger.critical(message, *args, **kwargs)
    
    def log_function_entry(self, func_name: str, **kwargs):
        """Log function entry with parameters"""
        params = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        self.debug(f"Entering {func_name}({params})")
    
    def log_function_exit(self, func_name: str, result=None):
        """Log function exit with optional result"""
        if result is not None:
            self.debug(f"Exiting {func_name} with result: {result}")
        else:
            self.debug(f"Exiting {func_name}")
    
    def log_performance(self, operation: str, duration: float, details: Optional[str] = None):
        """Log performance metrics"""
        message = f"Performance: {operation} took {duration:.3f}s"
        if details:
            message += f" - {details}"
        self.info(message)
    
    def log_statistics_update(self, operation: str, before_count: int, after_count: int):
        """Log statistics update operations"""
        change = after_count - before_count
        self.info(f"Statistics: {operation} - Before: {before_count}, After: {after_count}, Change: {change:+d}")
    
    def log_file_operation(self, operation: str, file_path: str, success: bool, details: Optional[str] = None):
        """Log file operations"""
        status = "SUCCESS" if success else "FAILED"
        message = f"File {operation}: {file_path} - {status}"
        if details:
            message += f" - {details}"
        
        if success:
            self.info(message)
        else:
            self.error(message)
    
    def log_user_action(self, action: str, details: Optional[str] = None):
        """Log user actions for audit trail"""
        message = f"User Action: {action}"
        if details:
            message += f" - {details}"
        self.info(message)
    
    def configure_for_testing(self):
        """Configure logger for testing environments"""
        self.setup_logger(
            log_level="DEBUG",
            log_to_file=False,
            log_to_console=True
        )

# Global logger instance
logger = MetaPicPickLogger()

# Convenience functions for easy access
def debug(message: str, *args, **kwargs):
    """Log debug message"""
    logger.debug(message, *args, **kwargs)

def info(message: str, *args, **kwargs):
    """Log info message"""
    logger.info(message, *args, **kwargs)

def warning(message: str, *args, **kwargs):
    """Log warning message"""
    logger.warning(message, *args, **kwargs)

def error(message: str, exception: Optional[Exception] = None, *args, **kwargs):
    """Log error message"""
    logger.error(message, exception, *args, **kwargs)

def critical(message: str, exception: Optional[Exception] = None, *args, **kwargs):
    """Log critical message"""
    logger.critical(message, exception, *args, **kwargs)

def log_function_call(func_name: str):
    """Decorator to log function calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.log_function_entry(func_name, **kwargs)
            try:
                result = func(*args, **kwargs)
                logger.log_function_exit(func_name, result)
                return result
            except Exception as e:
                logger.error(f"Exception in {func_name}", e)
                raise
        return wrapper
    return decorator

# Context manager for performance logging
class PerformanceTimer:
    """Context manager to measure and log operation performance"""
    
    def __init__(self, operation_name: str, details: Optional[str] = None):
        self.operation_name = operation_name
        self.details = details
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        logger.debug(f"Starting {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            logger.log_performance(self.operation_name, duration, self.details)
        
        if exc_type is not None:
            logger.error(f"Exception during {self.operation_name}", exc_val)

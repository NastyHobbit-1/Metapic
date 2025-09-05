"""
Comprehensive Error Handling System for MetaPicPick
Provides standardized error handling, recovery strategies, and user feedback.
"""

from utils.common_imports import *
from utils.logger import logger
from config.settings import get_config
import traceback
import functools
from contextlib import contextmanager
from enum import Enum
from typing import Callable, Type, Tuple


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better handling"""
    FILE_IO = "file_io"
    METADATA = "metadata"
    PARSING = "parsing"
    STATISTICS = "statistics"
    GUI = "gui"
    CONFIGURATION = "configuration"
    NETWORK = "network"
    VALIDATION = "validation"
    PERFORMANCE = "performance"


class ErrorContext:
    """Context information for error handling"""
    
    def __init__(self, 
                 operation: str,
                 category: ErrorCategory,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 user_message: str = None,
                 recovery_suggestions: List[str] = None,
                 additional_data: Dict = None):
        self.operation = operation
        self.category = category
        self.severity = severity
        self.user_message = user_message
        self.recovery_suggestions = recovery_suggestions or []
        self.additional_data = additional_data or {}
        self.timestamp = datetime.now()


class ErrorRecoveryStrategy:
    """Strategy for error recovery"""
    
    def __init__(self, 
                 name: str,
                 action: Callable,
                 description: str,
                 auto_apply: bool = False):
        self.name = name
        self.action = action
        self.description = description
        self.auto_apply = auto_apply


class ErrorHandler:
    """Comprehensive error handling system"""
    
    def __init__(self):
        """Initialize error handler"""
        self.error_history = []
        self.recovery_strategies = {}
        self.error_counts = defaultdict(int)
        self.suppressed_errors = set()
        self.max_history_size = get_config('max_error_history', 1000)
        
        # Register default recovery strategies
        self._register_default_strategies()
        
        logger.info("Error handler initialized")
    
    def _register_default_strategies(self):
        """Register default recovery strategies"""
        
        # File I/O recovery strategies
        self.register_recovery_strategy(
            ErrorCategory.FILE_IO,
            "retry_operation",
            lambda: None,  # Placeholder
            "Retry the file operation",
            auto_apply=True
        )
        
        self.register_recovery_strategy(
            ErrorCategory.FILE_IO,
            "create_backup",
            self._create_backup_file,
            "Create a backup of the file before operation"
        )
        
        # Configuration recovery strategies
        self.register_recovery_strategy(
            ErrorCategory.CONFIGURATION,
            "reset_to_defaults",
            self._reset_config_to_defaults,
            "Reset configuration to default values"
        )
        
        # Statistics recovery strategies
        self.register_recovery_strategy(
            ErrorCategory.STATISTICS,
            "rebuild_cache",
            self._rebuild_statistics_cache,
            "Rebuild statistics cache"
        )
        
        # GUI recovery strategies
        self.register_recovery_strategy(
            ErrorCategory.GUI,
            "reset_layout",
            self._reset_gui_layout,
            "Reset GUI layout to defaults"
        )
    
    def register_recovery_strategy(self,
                                 category: ErrorCategory,
                                 name: str,
                                 action: Callable,
                                 description: str,
                                 auto_apply: bool = False):
        """Register a recovery strategy for a specific error category"""
        if category not in self.recovery_strategies:
            self.recovery_strategies[category] = []
        
        strategy = ErrorRecoveryStrategy(name, action, description, auto_apply)
        self.recovery_strategies[category].append(strategy)
        
        logger.debug(f"Registered recovery strategy: {category.value}/{name}")
    
    def handle_error(self,
                    error: Exception,
                    context: ErrorContext,
                    raise_on_critical: bool = True,
                    show_user_message: bool = True) -> bool:
        """
        Handle an error with appropriate recovery strategies
        
        Args:
            error: The exception that occurred
            context: Error context information
            raise_on_critical: Whether to re-raise critical errors
            show_user_message: Whether to show message to user
            
        Returns:
            True if error was handled successfully, False otherwise
        """
        
        # Log the error
        self._log_error(error, context)
        
        # Add to history
        self._add_to_history(error, context)
        
        # Update error counts
        error_key = f"{context.category.value}:{type(error).__name__}"
        self.error_counts[error_key] += 1
        
        # Check if error should be suppressed
        if error_key in self.suppressed_errors:
            logger.debug(f"Error suppressed: {error_key}")
            return True
        
        # Handle based on severity
        if context.severity == ErrorSeverity.CRITICAL and raise_on_critical:
            self._handle_critical_error(error, context)
            raise error
        
        # Try recovery strategies
        recovery_successful = self._try_recovery_strategies(error, context)
        
        # Show user message if requested
        if show_user_message:
            self._show_user_error_message(error, context, recovery_successful)
        
        return recovery_successful
    
    def _log_error(self, error: Exception, context: ErrorContext):
        """Log error with appropriate level"""
        error_msg = f"Error in {context.operation}: {error}"
        
        if context.additional_data:
            error_msg += f" | Data: {context.additional_data}"
        
        if context.severity == ErrorSeverity.CRITICAL:
            logger.critical(error_msg, error)
        elif context.severity == ErrorSeverity.HIGH:
            logger.error(error_msg, error)
        elif context.severity == ErrorSeverity.MEDIUM:
            logger.warning(error_msg, error)
        else:
            logger.info(error_msg)
    
    def _add_to_history(self, error: Exception, context: ErrorContext):
        """Add error to history with size limit"""
        error_record = {
            'timestamp': context.timestamp,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'operation': context.operation,
            'category': context.category.value,
            'severity': context.severity.value,
            'traceback': traceback.format_exc()
        }
        
        self.error_history.append(error_record)
        
        # Trim history if too large
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size:]
    
    def _try_recovery_strategies(self, error: Exception, context: ErrorContext) -> bool:
        """Try recovery strategies for the error category"""
        strategies = self.recovery_strategies.get(context.category, [])
        
        for strategy in strategies:
            if strategy.auto_apply:
                try:
                    strategy.action()
                    logger.info(f"Auto-recovery successful: {strategy.name}")
                    return True
                except Exception as recovery_error:
                    logger.warning(f"Auto-recovery failed ({strategy.name}): {recovery_error}")
        
        return False
    
    def _handle_critical_error(self, error: Exception, context: ErrorContext):
        """Handle critical errors that might crash the application"""
        
        # Log critical error details
        logger.critical(f"CRITICAL ERROR in {context.operation}")
        logger.critical(f"Error type: {type(error).__name__}")
        logger.critical(f"Error message: {error}")
        logger.critical(f"Traceback: {traceback.format_exc()}")
        
        # Try to save application state
        try:
            self._emergency_save_state()
            logger.info("Emergency state save completed")
        except Exception as save_error:
            logger.error("Failed to save emergency state", save_error)
        
        # Show critical error dialog to user
        self._show_critical_error_dialog(error, context)
    
    def _show_user_error_message(self, 
                                error: Exception, 
                                context: ErrorContext, 
                                recovery_attempted: bool):
        """Show appropriate error message to user"""
        
        # Skip if GUI not available
        try:
            from PyQt5.QtWidgets import QApplication
            if not QApplication.instance():
                return
        except ImportError:
            return
        
        # Determine message based on severity
        if context.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]:
            self._show_error_dialog(error, context, recovery_attempted)
        elif context.severity == ErrorSeverity.MEDIUM:
            self._show_warning_message(error, context)
        # Low severity errors are just logged
    
    def _show_error_dialog(self, 
                          error: Exception, 
                          context: ErrorContext, 
                          recovery_attempted: bool):
        """Show detailed error dialog"""
        try:
            title = f"Error in {context.operation}"
            
            # Use context user message if available
            message = context.user_message if context.user_message else str(error)
            
            details = f"Error Type: {type(error).__name__}\n"
            details += f"Category: {context.category.value}\n"
            details += f"Severity: {context.severity.value}\n"
            
            if recovery_attempted:
                details += "\nRecovery was attempted automatically."
            
            if context.recovery_suggestions:
                details += "\n\nSuggested actions:\n"
                for i, suggestion in enumerate(context.recovery_suggestions, 1):
                    details += f"{i}. {suggestion}\n"
            
            # Show dialog
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical if context.severity == ErrorSeverity.CRITICAL else QMessageBox.Warning)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setDetailedText(details)
            msg_box.exec_()
            
        except Exception as dialog_error:
            logger.error("Failed to show error dialog", dialog_error)
    
    def _show_warning_message(self, error: Exception, context: ErrorContext):
        """Show warning message for medium severity errors"""
        try:
            # Try to show in status bar or as tooltip
            # This would need to be connected to the main window
            logger.info(f"User warning: {context.user_message or str(error)}")
        except Exception as warning_error:
            logger.error("Failed to show warning message", warning_error)
    
    def _show_critical_error_dialog(self, error: Exception, context: ErrorContext):
        """Show critical error dialog with emergency options"""
        try:
            title = "Critical Error - Application Recovery"
            message = f"A critical error occurred in {context.operation}:\n\n{error}\n\n"
            message += "The application will attempt to recover, but you may need to restart."
            
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setDetailedText(traceback.format_exc())
            
            # Add custom buttons
            restart_btn = msg_box.addButton("Restart Application", QMessageBox.ActionRole)
            continue_btn = msg_box.addButton("Continue", QMessageBox.AcceptRole)
            
            msg_box.exec_()
            
            if msg_box.clickedButton() == restart_btn:
                self._restart_application()
            
        except Exception as dialog_error:
            logger.error("Failed to show critical error dialog", dialog_error)
    
    def _emergency_save_state(self):
        """Save application state in case of critical error"""
        # Save statistics
        try:
            from core.statistics_tracker import stats_tracker
            stats_tracker.save_statistics()
        except Exception as e:
            logger.error("Failed to save statistics in emergency", e)
        
        # Save configuration
        try:
            from config.settings import save_config
            save_config()
        except Exception as e:
            logger.error("Failed to save config in emergency", e)
    
    def _restart_application(self):
        """Restart the application"""
        try:
            import sys
            QApplication.quit()
            os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
            logger.error("Failed to restart application", e)
    
    def _create_backup_file(self, file_path: str = None):
        """Create backup file recovery strategy"""
        if file_path and os.path.exists(file_path):
            backup_path = file_path + '.backup'
            shutil.copy2(file_path, backup_path)
            logger.info(f"Backup created: {backup_path}")
    
    def _reset_config_to_defaults(self):
        """Reset configuration to defaults"""
        try:
            from config.settings import config_manager
            config_manager.reset_to_defaults()
            logger.info("Configuration reset to defaults")
        except Exception as e:
            logger.error("Failed to reset configuration", e)
    
    def _rebuild_statistics_cache(self):
        """Rebuild statistics cache"""
        try:
            from core.optimized_statistics_tracker import optimized_stats_tracker
            optimized_stats_tracker._clear_cache()
            logger.info("Statistics cache rebuilt")
        except Exception as e:
            logger.error("Failed to rebuild statistics cache", e)
    
    def _reset_gui_layout(self):
        """Reset GUI layout to defaults"""
        try:
            settings = QSettings('MetaPicPick', 'Layout')
            settings.clear()
            logger.info("GUI layout reset to defaults")
        except Exception as e:
            logger.error("Failed to reset GUI layout", e)
    
    def suppress_error_type(self, category: ErrorCategory, error_type: str):
        """Suppress specific error types"""
        error_key = f"{category.value}:{error_type}"
        self.suppressed_errors.add(error_key)
        logger.info(f"Error type suppressed: {error_key}")
    
    def unsuppress_error_type(self, category: ErrorCategory, error_type: str):
        """Remove error type suppression"""
        error_key = f"{category.value}:{error_type}"
        self.suppressed_errors.discard(error_key)
        logger.info(f"Error type unsuppressed: {error_key}")
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        return {
            'total_errors': len(self.error_history),
            'error_counts': dict(self.error_counts),
            'suppressed_errors': list(self.suppressed_errors),
            'recent_errors': self.error_history[-10:] if self.error_history else []
        }
    
    def clear_error_history(self):
        """Clear error history"""
        self.error_history.clear()
        self.error_counts.clear()
        logger.info("Error history cleared")


# Global error handler instance
error_handler = ErrorHandler()


# Decorators for easy error handling
def handle_errors(category: ErrorCategory,
                 operation: str = None,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 user_message: str = None,
                 recovery_suggestions: List[str] = None,
                 raise_on_critical: bool = True,
                 show_user_message: bool = True):
    """
    Decorator for automatic error handling
    
    Usage:
        @handle_errors(ErrorCategory.FILE_IO, "Loading configuration")
        def load_config():
            # function code
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_operation = operation or f"{func.__name__}"
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = ErrorContext(
                    operation=func_operation,
                    category=category,
                    severity=severity,
                    user_message=user_message,
                    recovery_suggestions=recovery_suggestions,
                    additional_data={'function': func.__name__, 'args': str(args)[:100]}
                )
                
                error_handler.handle_error(
                    e, context, raise_on_critical, show_user_message
                )
                
                # Return None for non-critical errors
                if severity != ErrorSeverity.CRITICAL:
                    return None
                raise
        
        return wrapper
    return decorator


@contextmanager
def error_context(category: ErrorCategory,
                 operation: str,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 user_message: str = None,
                 recovery_suggestions: List[str] = None):
    """
    Context manager for error handling
    
    Usage:
        with error_context(ErrorCategory.FILE_IO, "Saving file"):
            # operations that might fail
    """
    try:
        yield
    except Exception as e:
        context = ErrorContext(
            operation=operation,
            category=category,
            severity=severity,
            user_message=user_message,
            recovery_suggestions=recovery_suggestions
        )
        
        error_handler.handle_error(e, context)
        raise


# Convenience functions
def handle_file_error(error: Exception, file_path: str, operation: str):
    """Handle file-related errors"""
    context = ErrorContext(
        operation=f"{operation} ({file_path})",
        category=ErrorCategory.FILE_IO,
        severity=ErrorSeverity.MEDIUM,
        user_message=f"Failed to {operation.lower()} file: {os.path.basename(file_path)}",
        recovery_suggestions=[
            "Check if the file exists and is accessible",
            "Ensure you have proper permissions",
            "Try closing any programs that might be using the file"
        ],
        additional_data={'file_path': file_path}
    )
    
    return error_handler.handle_error(error, context, raise_on_critical=False)


def handle_parsing_error(error: Exception, parser_name: str, content: str = None):
    """Handle parsing-related errors"""
    context = ErrorContext(
        operation=f"Parsing with {parser_name}",
        category=ErrorCategory.PARSING,
        severity=ErrorSeverity.LOW,
        user_message=f"Failed to parse metadata with {parser_name}",
        recovery_suggestions=[
            "Try with a different parser",
            "Check if the file contains valid metadata",
            "Update the parser if available"
        ],
        additional_data={
            'parser': parser_name,
            'content_length': len(content) if content else 0
        }
    )
    
    return error_handler.handle_error(error, context, raise_on_critical=False)


def handle_gui_error(error: Exception, widget_name: str, action: str):
    """Handle GUI-related errors"""
    context = ErrorContext(
        operation=f"{action} in {widget_name}",
        category=ErrorCategory.GUI,
        severity=ErrorSeverity.MEDIUM,
        user_message=f"Interface error in {widget_name}",
        recovery_suggestions=[
            "Try refreshing the interface",
            "Restart the application if the problem persists",
            "Reset the layout to defaults"
        ],
        additional_data={'widget': widget_name, 'action': action}
    )
    
    return error_handler.handle_error(error, context, raise_on_critical=False)


# Function to get error handler instance
def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance"""
    return error_handler

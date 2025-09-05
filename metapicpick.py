#!/usr/bin/env python3
"""
MetaPicPick - Enhanced Main launcher script
Now with comprehensive logging, configuration, and error handling
"""

import sys
import os

# Add the current directory to the Python path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Launch the MetaPicPick GUI application with enhanced error handling"""
    try:
        # Initialize logging and configuration first
        from utils.logger import logger
        from config.settings import config_manager, get_config
        from utils.error_handler import ErrorHandler, ErrorCategory, ErrorSeverity
        
        # Configure logging with settings
        log_settings = config_manager.config.get_logging_settings()
        logger.setup_logger(
            log_level=log_settings['log_level'],
            log_to_file=log_settings['log_to_file'],
            log_to_console=log_settings['log_to_console'],
            max_log_size=log_settings['max_log_size_mb'] * 1024 * 1024,
            backup_count=log_settings['log_backup_count']
        )
        
        logger.info("=" * 50)
        logger.info("MetaPicPick Application Starting")
        logger.info("=" * 50)
        
        # Import GUI after logging is configured
        from PyQt5.QtWidgets import QApplication
        from gui_main import MetaPicPickTabbed
        
        # Create application with configuration
        app = QApplication(sys.argv)
        app.setApplicationName("MetaPicPick Enhanced")
        app.setOrganizationName("MetaPicPick")
        app.setApplicationVersion("2.0")
        
        logger.info("Creating main window...")
        window = MetaPicPickTabbed()
        window.show()
        
        logger.info("Application window displayed successfully")
        logger.info("Entering main event loop...")
        
        # Run the application
        result = app.exec_()
        
        logger.info("Application shutting down gracefully")
        sys.exit(result)
        
    except ImportError as e:
        error_msg = f"Missing required dependencies: {e}"
        print(error_msg)
        print("\nPlease install required packages:")
        print("  pip install PyQt5 Pillow")
        
        # Try to log the error if logging is available
        try:
            from utils.logger import logger
            logger.critical(error_msg, e)
        except:
            pass  # Logging not available
            
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"Critical error launching MetaPicPick: {e}"
        print(error_msg)
        
        # Try to use our error handler if available
        try:
            from utils.logger import logger
            from utils.error_handler import error_handler, ErrorContext, ErrorCategory, ErrorSeverity
            
            logger.critical(error_msg, e)
            
            # Create error context for critical startup error
            context = ErrorContext(
                operation="Application Startup",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.CRITICAL,
                user_message="Failed to start MetaPicPick application",
                recovery_suggestions=[
                    "Check that all required files are present",
                    "Verify Python and PyQt5 installation",
                    "Try running as administrator",
                    "Check the log file for detailed error information"
                ]
            )
            
            error_handler.handle_error(e, context, raise_on_critical=False)
            
        except:
            # Fallback to basic error reporting
            import traceback
            traceback.print_exc()
            
        sys.exit(1)

if __name__ == "__main__":
    main()

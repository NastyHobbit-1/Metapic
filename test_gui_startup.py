#!/usr/bin/env python3
"""
Test script to verify GUI starts without freezing
"""

import sys
import os
import time

# Add the current directory to the Python path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_gui_startup():
    """Test that the GUI starts without freezing"""
    try:
        # Initialize logging and configuration first
        from utils.logger import logger
        from config.settings import config_manager, get_config
        
        # Configure logging with settings
        log_settings = config_manager.config.get_logging_settings()
        logger.setup_logger(
            log_level=log_settings['log_level'],
            log_to_file=log_settings['log_to_file'],
            log_to_console=log_settings['log_to_console'],
            max_log_size=log_settings['max_log_size_mb'] * 1024 * 1024,
            backup_count=log_settings['log_backup_count']
        )
        
        logger.info("=== GUI Startup Test ===")
        
        # Import GUI components
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QTimer
        from gui_main import MetaPicPickTabbed
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("MetaPicPick Test")
        
        logger.info("Creating main window...")
        start_time = time.time()
        
        window = MetaPicPickTabbed()
        
        initialization_time = time.time() - start_time
        logger.info(f"Window created in {initialization_time:.2f} seconds")
        
        window.show()
        logger.info("Window displayed successfully")
        
        # Set up a timer to close the application after 2 seconds
        close_timer = QTimer()
        close_timer.timeout.connect(app.quit)
        close_timer.setSingleShot(True)
        close_timer.start(2000)  # 2 seconds
        
        logger.info("Starting event loop (will close automatically in 2 seconds)")
        result = app.exec_()
        
        logger.info("GUI startup test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"GUI startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gui_startup()
    sys.exit(0 if success else 1)

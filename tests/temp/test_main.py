#!/usr/bin/env python3
"""
Test the main MetaPicPick application with detailed debugging
"""

import sys
import os

# Add the current directory to the Python path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_main_application():
    """Test the main application with detailed error reporting"""
    try:
        print("Step 1: Testing core imports...")
        
        # Test logger first
        print("  - Testing logger...")
        from utils.logger import logger
        logger.info("Logger test successful")
        
        # Test configuration
        print("  - Testing configuration...")
        from config.settings import config_manager, get_config
        print(f"    Config loaded: auto_refresh_interval = {get_config('auto_refresh_interval')}")
        
        # Test error handler
        print("  - Testing error handler...")
        from utils.error_handler import ErrorHandler, ErrorCategory, ErrorSeverity
        
        print("Step 2: Testing PyQt5 imports...")
        from PyQt5.QtWidgets import QApplication
        
        print("Step 3: Testing GUI main import...")
        from gui_main import MetaPicPickTabbed
        
        print("Step 4: Creating application...")
        app = QApplication(sys.argv)
        app.setApplicationName("MetaPicPick Enhanced Test")
        app.setOrganizationName("MetaPicPick")
        app.setApplicationVersion("2.0")
        
        print("Step 5: Creating main window...")
        window = MetaPicPickTabbed()
        
        print("Step 6: Showing window...")
        window.show()
        
        logger.info("Main application test started successfully")
        print("SUCCESS: Main application window should be visible!")
        print("Close the window to exit.")
        
        return app.exec_()
        
    except ImportError as e:
        print(f"IMPORT ERROR: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print("="*60)
    print("MetaPicPick Enhanced v2.0 - Integration Test")
    print("="*60)
    sys.exit(test_main_application())

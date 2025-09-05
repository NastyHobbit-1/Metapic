#!/usr/bin/env python3
"""
Minimal test to verify PyQt5 integration
"""

import sys
import os

# Add the current directory to the Python path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_minimal():
    """Test minimal PyQt5 setup"""
    try:
        print("Testing PyQt5 import...")
        from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
        from PyQt5.QtCore import Qt
        
        print("PyQt5 import successful!")
        
        print("Testing our utilities import...")
        from utils.logger import logger
        from config.settings import get_config
        
        print("Utilities import successful!")
        
        print("Creating minimal application...")
        app = QApplication(sys.argv)
        
        window = QMainWindow()
        window.setWindowTitle("MetaPicPick Test")
        window.setGeometry(100, 100, 400, 200)
        
        label = QLabel("MetaPicPick Enhanced v2.0\nIntegration Test Successful!")
        label.setAlignment(Qt.AlignCenter)
        window.setCentralWidget(label)
        
        print("Showing window...")
        window.show()
        
        logger.info("Minimal test application started successfully")
        print("Test successful! GUI should be visible.")
        print("Close the window to exit.")
        
        return app.exec_()
        
    except ImportError as e:
        print(f"Import error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_minimal())

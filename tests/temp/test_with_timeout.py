#!/usr/bin/env python3
"""
Test MetaPicPick with timeout to prevent hanging
"""

import sys
import os
import signal
import threading
import time

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Test timed out after 30 seconds")

def test_with_timeout():
    """Test the application with a 30-second timeout"""
    
    def run_app():
        """Run the application in a separate function"""
        try:
            print("Step 1: Testing imports...")
            from utils.logger import logger
            from config.settings import get_config
            from PyQt5.QtWidgets import QApplication
            from gui_main import MetaPicPickTabbed
            
            print("Step 2: Creating application...")
            app = QApplication([])  # Use empty argv for testing
            app.setApplicationName("MetaPicPick Enhanced Test")
            
            print("Step 3: Creating main window...")
            window = MetaPicPickTabbed()
            
            print("Step 4: Showing window...")
            window.show()
            
            print("SUCCESS: Application started! Window should be visible.")
            logger.info("Test application started successfully")
            
            # Instead of running exec_(), just show for a moment and exit
            print("Auto-closing in 3 seconds...")
            
            # Use QTimer to auto-close
            from PyQt5.QtCore import QTimer
            timer = QTimer()
            timer.timeout.connect(app.quit)
            timer.setSingleShot(True)
            timer.start(3000)  # 3 seconds
            
            result = app.exec_()
            print(f"Application closed with result: {result}")
            return result
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    if os.name == 'nt':  # Windows
        # On Windows, use threading with timeout
        result = [None]
        exception = [None]
        
        def target():
            try:
                result[0] = run_app()
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout=30)
        
        if thread.is_alive():
            print("TIMEOUT: Test took longer than 30 seconds")
            return 1
        elif exception[0]:
            print(f"EXCEPTION: {exception[0]}")
            return 1
        else:
            return result[0] or 0
    else:
        # On Unix systems, use signal
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)
        
        try:
            return run_app()
        except TimeoutError:
            print("TIMEOUT: Test took longer than 30 seconds")
            return 1
        finally:
            signal.alarm(0)

if __name__ == "__main__":
    print("=" * 60)
    print("MetaPicPick Enhanced v2.0 - Integration Test with Timeout")
    print("=" * 60)
    
    start_time = time.time()
    result = test_with_timeout()
    end_time = time.time()
    
    print(f"\nTest completed in {end_time - start_time:.2f} seconds")
    print(f"Exit code: {result}")
    
    sys.exit(result)

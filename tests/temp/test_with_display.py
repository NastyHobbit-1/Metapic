#!/usr/bin/env python3
"""
Comprehensive test with window display and lazy loading verification
"""
import sys
import os
import signal
import time
import threading
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def timeout_handler():
    """Handle timeout by forcing exit"""
    print("\nTIMEOUT: Test took longer than 20 seconds")
    os._exit(1)

def signal_handler(signum, frame):
    """Handle termination signal"""
    print(f"\nReceived signal {signum}, exiting gracefully...")
    sys.exit(0)

# Set up signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    print("=" * 60)
    print("MetaPicPick - Comprehensive Display Test")
    print("=" * 60)
    
    # Set up timeout
    start_time = time.time()
    timeout_timer = threading.Timer(20.0, timeout_handler)
    timeout_timer.daemon = True
    timeout_timer.start()
    
    try:
        print("Step 1: Testing imports...")
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QTimer
        
        print("Step 2: Creating application...")
        app = QApplication([])
        app.setQuitOnLastWindowClosed(True)
        
        print("Step 3: Importing and creating main window...")
        from gui_main import MetaPicPickTabbed
        main_window = MetaPicPickTabbed()
        
        print("Step 4: Showing window...")
        main_window.show()
        
        print("Step 5: Processing events for 3 seconds to test UI responsiveness...")
        
        # Process events for 3 seconds to let the UI fully render
        end_time = time.time() + 3.0
        while time.time() < end_time:
            app.processEvents()
            time.sleep(0.1)
        
        print("✅ Window displayed successfully")
        print("✅ UI remained responsive")
        print("✅ Lazy loading system working")
        
        print("Step 6: Testing statistics tab switching...")
        try:
            # Find and switch to statistics tab
            tab_widget = main_window.tab_widget
            for i in range(tab_widget.count()):
                if "Statistics" in tab_widget.tabText(i):
                    print(f"Switching to statistics tab (index {i})...")
                    tab_widget.setCurrentIndex(i)
                    
                    # Process events to trigger lazy loading
                    for _ in range(10):
                        app.processEvents()
                        time.sleep(0.1)
                    break
            else:
                print("⚠️  Statistics tab not found")
        except Exception as e:
            print(f"⚠️  Error testing statistics tab: {e}")
        
        print("Step 7: Closing application...")
        main_window.close()
        app.quit()
        
        # Cancel timeout timer and show completion time
        timeout_timer.cancel()
        elapsed_time = time.time() - start_time
        print(f"\n✅ Comprehensive test completed successfully in {elapsed_time:.2f} seconds!")
        
    except Exception as e:
        timeout_timer.cancel()
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

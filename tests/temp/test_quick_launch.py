#!/usr/bin/env python3
"""
Quick launch test to verify layout fixes work correctly
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
    print("\nTIMEOUT: Test took longer than 15 seconds")
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
    print("MetaPicPick - Quick Launch Test")
    print("=" * 60)
    
    # Set up timeout
    start_time = time.time()
    timeout_timer = threading.Timer(15.0, timeout_handler)
    timeout_timer.daemon = True
    timeout_timer.start()
    
    try:
        print("Step 1: Testing imports...")
        from PyQt5.QtWidgets import QApplication
        from gui_main import MetaPicPickTabbed
        
        print("Step 2: Creating application...")
        app = QApplication([])
        app.setQuitOnLastWindowClosed(True)
        
        print("Step 3: Creating main window...")
        main_window = MetaPicPickTabbed()
        
        print("Step 4: Showing window...")
        main_window.show()
        
        print("Step 5: Window created successfully!")
        print("✅ Layout fixes appear to be working")
        print("✅ Application launches without errors")
        
        # Close immediately after showing
        print("Step 6: Closing application...")
        main_window.close()
        app.quit()
        
        # Cancel timeout timer and show completion time
        timeout_timer.cancel()
        elapsed_time = time.time() - start_time
        print(f"\n✅ Test completed successfully in {elapsed_time:.2f} seconds!")
        
    except Exception as e:
        timeout_timer.cancel()
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

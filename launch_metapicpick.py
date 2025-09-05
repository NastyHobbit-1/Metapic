#!/usr/bin/env python3
"""
MetaPicPick Enhanced - Normal Application Launcher
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    print("=" * 60)
    print("MetaPicPick Enhanced v2.0")
    print("Launching with integrated improvements...")
    print("=" * 60)
    
    try:
        from PyQt5.QtWidgets import QApplication
        from gui_main import MetaPicPickTabbed
        
        # Create application
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(True)
        
        # Create and show main window
        main_window = MetaPicPickTabbed()
        main_window.show()
        
        print("✅ Application launched successfully!")
        print("📊 Statistics will load when you click the Statistics tab")
        print("🔧 All integrated utilities are now active")
        
        # Run the application
        return app.exec_()
        
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Quick dependency check for MetaPicPick build process."""

import sys

def check_dependencies():
    """Check if all required dependencies are available."""
    missing = []
    
    # Check core dependencies
    try:
        import PyQt5
        print("✓ PyQt5 available")
    except ImportError:
        missing.append("PyQt5")
        print("✗ PyQt5 missing")
    
    try:
        import PIL
        print("✓ PIL/Pillow available")
    except ImportError:
        missing.append("PIL/Pillow")
        print("✗ PIL/Pillow missing")
    
    try:
        import piexif
        print("✓ piexif available")
    except ImportError:
        missing.append("piexif")
        print("✗ piexif missing")
    
    # Check MetaPicPick modules
    try:
        from utils.logger import logger
        print("✓ Logger module available")
    except ImportError as e:
        missing.append("logger")
        print(f"✗ Logger module missing: {e}")
    
    try:
        from config.settings import get_config
        print("✓ Config module available")
    except ImportError as e:
        missing.append("config")
        print(f"✗ Config module missing: {e}")
    
    try:
        from utils.plugin_manager import PluginManager
        print("✓ Plugin manager available")
    except ImportError as e:
        missing.append("plugin_manager")
        print(f"✗ Plugin manager missing: {e}")
    
    if missing:
        print(f"\n✗ Missing dependencies: {', '.join(missing)}")
        print("Please install missing dependencies before building.")
        return False
    else:
        print("\n✓ All dependencies available!")
        return True

if __name__ == "__main__":
    if not check_dependencies():
        sys.exit(1)
    sys.exit(0)

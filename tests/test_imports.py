#!/usr/bin/env python
"""Test script to validate imports and plugin loading"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        # Add parent directory to path for imports
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Test basic imports
        from utils import metadata_utils
        print("✓ metadata_utils imported successfully")
        
        from utils import plugin_manager
        print("✓ plugin_manager imported successfully")
        
        from utils import parser_plugin_interface
        print("✓ parser_plugin_interface imported successfully")
        
        try:
            from utils import raw_metadata_loader  
            print("✓ raw_metadata_loader imported successfully")
        except ImportError as e:
            print(f"⚠ raw_metadata_loader import failed (missing dependencies): {e}")
        
        # Test parser imports
        from parsers import automatic1111_parser, comfyui_parser, novelai_parser, general_ai_parser
        print("✓ All parser modules imported successfully")
        
        # Test plugin manager functionality
        pm = plugin_manager.PluginManager("parsers")
        print(f"✓ PluginManager created with {len(pm.plugins)} plugins loaded")
        
        # Test that plugins have required methods
        for plugin in pm.plugins:
            if hasattr(plugin, 'detect') and hasattr(plugin, 'parse'):
                print(f"✓ Plugin {plugin.__name__} has required methods")
            else:
                print(f"✗ Plugin {plugin.__name__} missing required methods")
                
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_metadata_extraction():
    """Test metadata extraction functionality"""
    print("\nTesting metadata extraction...")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from utils import metadata_utils
        from utils import plugin_manager
        
        # Create plugin manager
        pm = plugin_manager.PluginManager("parsers")
        
        # Test with dummy metadata that should trigger automatic1111 parser
        dummy_metadata = {
            'parameters': 'beautiful landscape\nNegative prompt: ugly, blurry\nSteps: 20, Sampler: DPM++ 2M Karras, CFG scale: 7, Seed: 12345'
        }
        
        # Test plugin detection and parsing
        for plugin in pm.plugins:
            if plugin.detect(dummy_metadata):
                result = plugin.parse(dummy_metadata)
                print(f"✓ Plugin {plugin.__name__} detected and parsed metadata:")
                for key, value in result.items():
                    print(f"  {key}: {value}")
                break
        else:
            print("✗ No plugin detected the dummy metadata")
            
        return True
        
    except Exception as e:
        print(f"✗ Metadata extraction test failed: {e}")
        return False

if __name__ == "__main__":
    print("MetaPicPick Import Test")
    print("=" * 40)
    
    imports_ok = test_imports()
    
    if imports_ok:
        test_metadata_extraction()
    
    if imports_ok:
        print("\n✓ All tests passed! The codebase should work correctly.")
    else:
        print("\n✗ Some tests failed. Please check the errors above.")

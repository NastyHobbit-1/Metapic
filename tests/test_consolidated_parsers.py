#!/usr/bin/env python
"""Test script to verify consolidated parsers functionality"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_parsers():
    """Test that all parsers can be imported and have required methods"""
    print("Testing Consolidated Parsers")
    print("=" * 50)
    
    try:
        print("\n1. Testing imports...")
        from parsers.automatic1111_parser import Automatic1111Parser
        from parsers.comfyui_parser import ComfyUIParser
        from parsers.novelai_parser import NovelAIParser
        from parsers.general_ai_parser import GeneralAIParser
        
        parsers = [
            ("Automatic1111Parser", Automatic1111Parser),
            ("ComfyUIParser", ComfyUIParser),
            ("NovelAIParser", NovelAIParser),
            ("GeneralAIParser", GeneralAIParser),
        ]
        
        print("✓ All parsers imported successfully")
        
        print("\n2. Testing parser methods...")
        for parser_name, parser_class in parsers:
            # Check required methods exist
            if not hasattr(parser_class, 'detect'):
                print(f"✗ {parser_name} missing detect method")
            elif not hasattr(parser_class, 'parse'):
                print(f"✗ {parser_name} missing parse method")
            else:
                print(f"✓ {parser_name} has required methods")
        
        print("\n3. Testing parser detection...")
        # Test metadata samples for each parser
        test_cases = [
            {
                "name": "Automatic1111 format",
                "parser": Automatic1111Parser,
                "metadata": {
                    "parameters": "beautiful landscape\nNegative prompt: ugly, blurry\nSteps: 20, Sampler: DPM++ 2M Karras, CFG scale: 7, Seed: 12345, Size: 512x512, Model: sd_xl_base_1.0"
                }
            },
            {
                "name": "ComfyUI format",
                "parser": ComfyUIParser,
                "metadata": {
                    "workflow": '{"nodes": {"1": {"class_type": "KSampler", "inputs": {"seed": 123, "steps": 20}}}}'
                }
            },
            {
                "name": "NovelAI format",
                "parser": NovelAIParser,
                "metadata": {
                    "Software": "NovelAI",
                    "Comment": "eyJzdGVwcyI6IDIwLCAic2NhbGUiOiA3LjUsICJzZWVkIjogMTIzNDV9"  # base64 encoded JSON
                }
            },
            {
                "name": "General AI format",
                "parser": GeneralAIParser,
                "metadata": {
                    "parameters": "Model: some_model, Steps: 20, CFG: 7.5, Seed: 12345"
                }
            }
        ]
        
        for test_case in test_cases:
            parser = test_case["parser"]
            metadata = test_case["metadata"]
            name = test_case["name"]
            
            if parser.detect(metadata):
                print(f"✓ {name} detected correctly")
                
                # Test parsing
                parsed = parser.parse(metadata)
                if parsed and isinstance(parsed, dict):
                    print(f"  → Parsed {len(parsed)} fields")
                    # Show some parsed fields
                    for key in ['steps', 'seed', 'model_name', 'source']:
                        if key in parsed:
                            print(f"    • {key}: {parsed[key]}")
                else:
                    print(f"  ✗ Parsing failed or returned invalid data")
            else:
                print(f"✗ {name} detection failed")
        
        print("\n✓ All tests completed!")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_parsers()
    sys.exit(0 if success else 1)

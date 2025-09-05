#!/usr/bin/env python3
"""
Test script to compare original vs enhanced parser metadata extraction
This helps identify what additional fields the enhanced parsers extract
"""

import os
import sys
from typing import Dict, Any
from raw_metadata_loader import extract_metadata as raw_extract

# Import original parsers
try:
    from parsers.automatic1111_parser import Automatic1111Parser
    from parsers.comfyui_parser import ComfyUIParser  
    from parsers.novelai_parser import NovelAIParser
except ImportError as e:
    print(f"Could not import original parsers: {e}")
    Automatic1111Parser = None
    ComfyUIParser = None
    NovelAIParser = None

# Import enhanced parsers
try:
    from parsers.enhanced_automatic1111_parser import EnhancedAutomatic1111Parser
    from parsers.enhanced_comfyui_parser import EnhancedComfyUIParser
    from parsers.enhanced_novelai_parser import EnhancedNovelAIParser
    from parsers.enhanced_general_ai_parser import EnhancedGeneralAIParser
except ImportError as e:
    print(f"Could not import enhanced parsers: {e}")
    EnhancedAutomatic1111Parser = None
    EnhancedComfyUIParser = None
    EnhancedNovelAIParser = None
    EnhancedGeneralAIParser = None

def test_parser_comparison(image_path: str):
    """Compare original vs enhanced parser results"""
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        return
    
    print(f"Analyzing: {image_path}")
    print("=" * 80)
    
    # Extract raw metadata
    print("1. RAW METADATA:")
    print("-" * 40)
    try:
        raw_metadata = raw_extract(image_path)
        print(f"Raw metadata keys: {list(raw_metadata.keys())}")
        
        # Show relevant raw fields that contain parameters
        param_fields = ['parameters', 'Parameters', 'comment', 'Comment', 'description', 'Description']
        for field in param_fields:
            if field in raw_metadata:
                value = str(raw_metadata[field])
                if len(value) > 100:
                    print(f"{field}: {value[:100]}... [truncated, total length: {len(value)}]")
                else:
                    print(f"{field}: {value}")
        print()
    except Exception as e:
        print(f"Error extracting raw metadata: {e}")
        return
    
    # Test parsers
    parser_pairs = [
        ("Automatic1111", Automatic1111Parser, EnhancedAutomatic1111Parser),
        ("ComfyUI", ComfyUIParser, EnhancedComfyUIParser), 
        ("NovelAI", NovelAIParser, EnhancedNovelAIParser),
        ("General AI", None, EnhancedGeneralAIParser),
    ]
    
    for name, original_parser, enhanced_parser in parser_pairs:
        print(f"2. {name.upper()} PARSER COMPARISON:")
        print("-" * 40)
        
        # Test original parser
        original_result = None
        if original_parser:
            try:
                if original_parser.detect(raw_metadata):
                    original_result = original_parser.parse(raw_metadata)
                    print(f"Original {name} - Detected: YES")
                    print(f"Original {name} - Fields: {len(original_result)} - {list(original_result.keys())}")
                else:
                    print(f"Original {name} - Detected: NO")
            except Exception as e:
                print(f"Original {name} - Error: {e}")
        else:
            print(f"Original {name} - Not available")
        
        # Test enhanced parser
        enhanced_result = None
        if enhanced_parser:
            try:
                if enhanced_parser.detect(raw_metadata):
                    enhanced_result = enhanced_parser.parse(raw_metadata)
                    print(f"Enhanced {name} - Detected: YES")
                    print(f"Enhanced {name} - Fields: {len(enhanced_result)} - {list(enhanced_result.keys())}")
                else:
                    print(f"Enhanced {name} - Detected: NO")
            except Exception as e:
                print(f"Enhanced {name} - Error: {e}")
        else:
            print(f"Enhanced {name} - Not available")
        
        # Show field differences
        if original_result and enhanced_result:
            original_fields = set(original_result.keys())
            enhanced_fields = set(enhanced_result.keys())
            
            new_fields = enhanced_fields - original_fields
            if new_fields:
                print(f"NEW FIELDS in Enhanced {name}: {list(new_fields)}")
                for field in sorted(new_fields):
                    value = enhanced_result[field]
                    if isinstance(value, str) and len(value) > 50:
                        print(f"  {field}: {value[:50]}... [truncated]")
                    else:
                        print(f"  {field}: {value}")
            
            changed_fields = []
            for field in original_fields & enhanced_fields:
                if original_result[field] != enhanced_result[field]:
                    changed_fields.append(field)
            
            if changed_fields:
                print(f"CHANGED FIELDS in Enhanced {name}: {changed_fields}")
                for field in changed_fields:
                    print(f"  {field}:")
                    print(f"    Original: {original_result[field]}")
                    print(f"    Enhanced: {enhanced_result[field]}")
        
        elif enhanced_result and not original_result:
            print(f"Enhanced {name} extracts {len(enhanced_result)} fields where original detected nothing:")
            for field, value in sorted(enhanced_result.items()):
                if isinstance(value, str) and len(value) > 50:
                    print(f"  {field}: {value[:50]}... [truncated]")
                else:
                    print(f"  {field}: {value}")
        
        print()

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_enhanced_parsers.py <image_path>")
        print()
        print("This script compares the original vs enhanced metadata parsers")
        print("to show what additional fields the enhanced versions extract.")
        print()
        print("Example:")
        print("  python test_enhanced_parsers.py sample_image.png")
        return
    
    image_path = sys.argv[1]
    test_parser_comparison(image_path)
    
    print()
    print("SUMMARY:")
    print("The enhanced parsers should extract more metadata fields compared")
    print("to the original parsers. This includes:")
    print("- More technical parameters (hires upscale, ControlNet, LoRA, etc.)")
    print("- Better prompt extraction and parsing")
    print("- Additional AI tool detection (Midjourney, DALL-E, etc.)")
    print("- More robust regex patterns for parameter extraction")

if __name__ == "__main__":
    main()

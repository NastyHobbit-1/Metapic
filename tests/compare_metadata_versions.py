#!/usr/bin/env python
"""
Compare metadata extraction between your current version and the indexed version
to understand why one shows more metadata than the other.
"""

import os
import sys
import json
from metadata_utils import extract_metadata
from plugin_manager import PluginManager

def analyze_metadata_extraction(image_path):
    """Analyze what metadata is being extracted and how"""
    
    print(f"Analyzing metadata extraction for: {os.path.basename(image_path)}")
    print("=" * 60)
    
    # Initialize current version's plugin manager
    pm = PluginManager("parsers")
    print(f"Loaded {len(pm.plugins)} plugins:")
    for plugin in pm.plugins:
        print(f"  - {plugin.__name__}")
    print()
    
    # Extract raw metadata first
    from raw_metadata_loader import extract_metadata as raw_extract
    raw_metadata = raw_extract(image_path)
    
    print("RAW METADATA FOUND:")
    print("-" * 30)
    for key, value in raw_metadata.items():
        if isinstance(value, (str, bytes)) and len(str(value)) > 100:
            print(f"  {key}: {str(value)[:100]}... (truncated)")
        else:
            print(f"  {key}: {value}")
    print()
    
    # Test each plugin individually
    print("PLUGIN DETECTION RESULTS:")
    print("-" * 30)
    detected_by = []
    
    for plugin in pm.plugins:
        try:
            can_detect = plugin.detect(raw_metadata)
            print(f"  {plugin.__name__}: {'✓ DETECTS' if can_detect else '✗ no match'}")
            if can_detect:
                detected_by.append(plugin)
        except Exception as e:
            print(f"  {plugin.__name__}: ERROR - {e}")
    print()
    
    # Parse with detected plugins
    if detected_by:
        print("PARSED METADATA:")
        print("-" * 30)
        for plugin in detected_by:
            try:
                parsed = plugin.parse(raw_metadata)
                print(f"  Using {plugin.__name__}:")
                for key, value in parsed.items():
                    if isinstance(value, str) and len(value) > 100:
                        print(f"    {key}: {value[:100]}... (truncated)")
                    else:
                        print(f"    {key}: {value}")
                print()
            except Exception as e:
                print(f"  {plugin.__name__} parsing ERROR: {e}")
                print()
    else:
        print("No plugins could detect this metadata format!")
        print()
    
    # Final extraction using metadata_utils
    print("FINAL EXTRACTED METADATA:")
    print("-" * 30)
    final_metadata = extract_metadata(image_path, pm.plugins)
    
    if final_metadata:
        for key, value in final_metadata.items():
            if isinstance(value, str) and len(value) > 100:
                print(f"  {key}: {value[:100]}... (truncated)")
            else:
                print(f"  {key}: {value}")
    else:
        print("  No metadata extracted!")
    
    print()
    print("SUMMARY:")
    print("-" * 30)
    print(f"  Raw metadata keys: {len(raw_metadata)}")
    print(f"  Plugins detected: {len(detected_by)}")
    print(f"  Final metadata keys: {len(final_metadata)}")
    
    return {
        'raw_count': len(raw_metadata),
        'plugins_detected': len(detected_by),
        'final_count': len(final_metadata),
        'raw_metadata': raw_metadata,
        'final_metadata': final_metadata
    }

def compare_with_portable_version():
    """Instructions for comparing with the portable version"""
    
    print("\n" + "=" * 80)
    print("COMPARING WITH PORTABLE VERSION")
    print("=" * 80)
    print()
    print("To understand why your portable version shows more metadata:")
    print()
    print("1. **Different Raw Metadata Extraction:**")
    print("   - The portable version might have different piexif/PIL versions")
    print("   - Different webpmux.exe version or configuration")
    print("   - Enhanced EXIF tag extraction")
    print()
    print("2. **More Parser Plugins:**")
    print("   - Additional parsers for other AI platforms")
    print("   - Better regex patterns in existing parsers")
    print("   - Enhanced field mapping")
    print()
    print("3. **Different Field Mapping:**")
    print("   - More comprehensive field extraction")
    print("   - Better handling of nested metadata")
    print("   - Additional computed fields")
    print()
    print("4. **To identify the exact differences:**")
    print(f"   - Run this same script on the portable version")
    print(f"   - Compare the 'RAW METADATA' sections")
    print(f"   - Look at which plugins detect the metadata")
    print(f"   - Check the parsed field counts")

def main():
    if len(sys.argv) < 2:
        print("Usage: python compare_metadata_versions.py <image_file>")
        print("Example: python compare_metadata_versions.py sample_image.png")
        return
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found")
        return
    
    if not image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        print("Warning: File may not be a supported image format")
    
    try:
        result = analyze_metadata_extraction(image_path)
        compare_with_portable_version()
        
        # Save results to JSON for comparison
        output_file = f"metadata_analysis_{os.path.basename(image_path)}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            # Convert any non-serializable values
            serializable_result = {}
            for key, value in result.items():
                if key in ['raw_metadata', 'final_metadata']:
                    # Convert bytes to string for JSON serialization
                    serializable_dict = {}
                    for k, v in value.items():
                        if isinstance(v, bytes):
                            serializable_dict[k] = f"<bytes: {len(v)} bytes>"
                        else:
                            serializable_dict[k] = v
                    serializable_result[key] = serializable_dict
                else:
                    serializable_result[key] = value
            
            json.dump(serializable_result, f, indent=2, ensure_ascii=False)
        
        print(f"\nDetailed results saved to: {output_file}")
        
    except Exception as e:
        print(f"Error analyzing metadata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

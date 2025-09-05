#!/usr/bin/env python3
"""
Example script demonstrating how to use the enhanced parsers
This shows the improved metadata extraction capabilities
"""

import os
from metadata_utils import extract_metadata

def demo_enhanced_extraction(image_path: str):
    """Demonstrate enhanced metadata extraction"""
    
    if not os.path.exists(image_path):
        print(f"Error: File not found: {image_path}")
        return
    
    print(f"Extracting metadata from: {image_path}")
    print("=" * 60)
    
    # Extract metadata using enhanced parsers
    metadata = extract_metadata(image_path)
    
    print(f"Detected AI Source: {metadata.get('source', 'Unknown')}")
    print(f"Total extracted fields: {len(metadata)}")
    print()
    
    # Group and display fields
    field_groups = {
        'Basic Information': [
            'source', 'model_name', 'model_hash', 'version', 'software'
        ],
        'Image Properties': [
            'width', 'height', 'size'
        ],
        'Generation Parameters': [
            'seed', 'steps', 'cfg_scale', 'sampler', 'scheduler',
            'denoising_strength', 'clip_skip', 'eta', 'subseed'
        ],
        'Prompts': [
            'positive_prompt', 'negative_prompt'
        ],
        'Advanced Features': [
            'controlnet', 'lora', 'loras', 'vae', 'hypernetwork',
            'face_restoration', 'upscaler', 'qualifiers'
        ],
        'Hi-res Fix': [
            'hires_upscale', 'hires_steps', 'hires_upscaler',
            'hires_resize_width', 'hires_resize_height'
        ],
        'Technical Details': [
            'batch_size', 'karras', 'rng', 'token_merging_ratio',
            'ti_hashes', 'lora_hashes', 'ensd', 'codeformer_weight'
        ]
    }
    
    for group_name, fields in field_groups.items():
        group_data = {}
        for field in fields:
            if field in metadata:
                group_data[field] = metadata[field]
        
        if group_data:
            print(f"{group_name}:")
            print("-" * len(group_name))
            for field, value in group_data.items():
                # Format the display
                display_name = field.replace('_', ' ').title()
                if isinstance(value, str) and len(value) > 80:
                    print(f"  {display_name}: {value[:77]}...")
                else:
                    print(f"  {display_name}: {value}")
            print()
    
    # Show any additional fields not in the predefined groups
    known_fields = set()
    for fields in field_groups.values():
        known_fields.update(fields)
    
    other_fields = {}
    for field, value in metadata.items():
        if field not in known_fields and not field.startswith('_'):
            other_fields[field] = value
    
    if other_fields:
        print("Additional Fields:")
        print("-" * 17)
        for field, value in sorted(other_fields.items()):
            display_name = field.replace('_', ' ').title()
            if isinstance(value, str) and len(value) > 80:
                print(f"  {display_name}: {value[:77]}...")
            else:
                print(f"  {display_name}: {value}")
        print()
    
    # Show comparison with raw metadata
    raw_data = metadata.get('_raw_metadata', {})
    if raw_data:
        print("Raw Metadata Summary:")
        print("-" * 21)
        print(f"  Raw fields available: {len(raw_data)}")
        print(f"  Extracted/parsed fields: {len(metadata) - 1}")  # -1 for _raw_metadata
        print(f"  Enhancement ratio: {(len(metadata) - 1) / len(raw_data):.2f}x")
        print()
        print("  Raw field names:", list(raw_data.keys()))
        print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python example_enhanced_usage.py <image_path>")
        print()
        print("This script demonstrates the enhanced metadata extraction")
        print("capabilities of the improved parsers.")
        print()
        print("Example:")
        print("  python example_enhanced_usage.py sample_ai_image.png")
        sys.exit(1)
    
    image_path = sys.argv[1]
    demo_enhanced_extraction(image_path)
    
    print("Enhanced Parsers Features:")
    print("- More comprehensive parameter extraction")
    print("- Better AI tool detection (Stable Diffusion, ComfyUI, NovelAI, etc.)")
    print("- Robust regex patterns for various metadata formats")
    print("- Support for advanced features like ControlNet, LoRA, Hi-res fix")
    print("- Graceful handling of different metadata structures")
    print("- General AI parser for tools not specifically supported")

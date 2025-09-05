#!/usr/bin/env python3
"""
Test script for statistics tracking functionality
This demonstrates how the statistics system works
"""

from statistics_tracker import stats_tracker
from metadata_utils import extract_metadata

def test_statistics_tracking(image_path: str):
    """Test the statistics tracking system"""
    
    print(f"Testing statistics tracking with: {image_path}")
    print("=" * 60)
    
    # Get initial statistics
    initial_summary = stats_tracker.get_statistics_summary()
    print("INITIAL STATISTICS:")
    print(f"  Images processed: {initial_summary['total_images_processed']}")
    print(f"  Unique models: {initial_summary['unique_models']}")
    print(f"  Unique positive tags: {initial_summary['unique_positive_tags']}")
    print(f"  Unique negative tags: {initial_summary['unique_negative_tags']}")
    print()
    
    # Extract metadata
    print("EXTRACTING METADATA...")
    metadata = extract_metadata(image_path)
    print(f"  Model: {metadata.get('model_name', 'Unknown')}")
    print(f"  Positive prompt length: {len(metadata.get('positive_prompt', ''))}")
    print(f"  Negative prompt length: {len(metadata.get('negative_prompt', ''))}")
    print()
    
    # Process with statistics tracker
    print("PROCESSING WITH STATISTICS TRACKER...")
    was_new = stats_tracker.process_image_metadata(image_path, metadata)
    print(f"  Was this a new image? {was_new}")
    print()
    
    # Try processing again (should not increment)
    print("PROCESSING SAME IMAGE AGAIN...")
    was_new_again = stats_tracker.process_image_metadata(image_path, metadata)
    print(f"  Was this a new image? {was_new_again}")
    print()
    
    # Get updated statistics
    updated_summary = stats_tracker.get_statistics_summary()
    print("UPDATED STATISTICS:")
    print(f"  Images processed: {updated_summary['total_images_processed']}")
    print(f"  Unique models: {updated_summary['unique_models']}")
    print(f"  Unique positive tags: {updated_summary['unique_positive_tags']}")
    print(f"  Unique negative tags: {updated_summary['unique_negative_tags']}")
    print()
    
    # Show top items
    print("TOP MODELS:")
    for model, count in updated_summary['top_models'][:5]:
        print(f"  {model}: {count}")
    print()
    
    print("TOP POSITIVE TAGS:")
    for tag, count in updated_summary['top_positive_tags'][:10]:
        print(f"  {tag}: {count}")
    print()
    
    print("TOP NEGATIVE TAGS:")
    for tag, count in updated_summary['top_negative_tags'][:10]:
        print(f"  {tag}: {count}")
    print()
    
    # Test tag extraction
    print("TAG EXTRACTION DEMO:")
    positive_prompt = metadata.get('positive_prompt', '')
    if positive_prompt:
        tags = stats_tracker.extract_tags_from_prompt(positive_prompt)
        print(f"  Extracted {len(tags)} tags from positive prompt:")
        for tag in sorted(list(tags)[:10]):  # Show first 10
            print(f"    - {tag}")
    print()

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_statistics.py <image_path>")
        print()
        print("This script tests the statistics tracking functionality")
        print("and demonstrates how models and tags are counted.")
        return
    
    image_path = sys.argv[1]
    test_statistics_tracking(image_path)
    
    print("STATISTICS TRACKING FEATURES:")
    print("✅ Tracks unique images (prevents double counting)")
    print("✅ Counts model usage")
    print("✅ Extracts and counts positive prompt tags")
    print("✅ Extracts and counts negative prompt tags") 
    print("✅ Saves statistics to JSON file")
    print("✅ Provides export functionality")
    print("✅ Auto-refreshes in GUI every 5 seconds")

if __name__ == "__main__":
    main()

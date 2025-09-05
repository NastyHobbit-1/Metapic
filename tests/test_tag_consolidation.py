#!/usr/bin/env python3
"""
Test script for tag consolidation functionality
"""

from statistics_tracker import stats_tracker

def test_tag_consolidation():
    """Test the tag consolidation functionality"""
    
    print("Testing Tag Consolidation")
    print("=" * 50)
    
    # Test some example tags that should be consolidated
    test_tags = [
        "1 girl", "1girl", "1 girls", 
        "blue eyes", "blue_eyes",
        "large breast", "large breasts", "big breasts",
        "long hair", "long_hair",
        "looking at viewer", "looking_at_viewer",
        "best quality", "best_quality",
        "worst quality", "worst_quality"
    ]
    
    print("Testing tag normalization:")
    for tag in test_tags:
        normalized = stats_tracker.normalize_tag(tag)
        if normalized != tag:
            print(f"  '{tag}' → '{normalized}'")
        else:
            print(f"  '{tag}' → (unchanged)")
    
    print()
    
    # Get current statistics before consolidation
    before_summary = stats_tracker.get_statistics_summary()
    print("Statistics before consolidation:")
    print(f"  Positive tags: {before_summary['unique_positive_tags']}")
    print(f"  Negative tags: {before_summary['unique_negative_tags']}")
    
    # Show some example duplicate tags from current stats
    positive_tags = stats_tracker.get_top_positive_tags(0)  # Get all
    
    # Find potential duplicates
    potential_duplicates = {}
    for tag, count in positive_tags:
        normalized = stats_tracker.normalize_tag(tag)
        if normalized != tag:
            if normalized in potential_duplicates:
                potential_duplicates[normalized].append((tag, count))
            else:
                potential_duplicates[normalized] = [(tag, count)]
    
    if potential_duplicates:
        print()
        print("Examples of tags that will be consolidated:")
        for normalized_tag, variants in list(potential_duplicates.items())[:10]:  # Show first 10
            if len(variants) > 1:
                total_count = sum(count for _, count in variants)
                variant_list = [f"'{tag}' ({count})" for tag, count in variants]
                print(f"  {' + '.join(variant_list)} → '{normalized_tag}' ({total_count})")
    
    print()
    print("To consolidate tags in the GUI:")
    print("1. Open the Statistics tab")
    print("2. Click 'Consolidate Tags' button")
    print("3. Confirm the consolidation")
    print("4. Similar tags will be merged together")

if __name__ == "__main__":
    test_tag_consolidation()

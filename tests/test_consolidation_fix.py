#!/usr/bin/env python3
"""
Test script to verify the consolidation functionality fix
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_statistics_tracker_access():
    """Test that StatisticsTracker attributes are accessible"""
    print("Testing StatisticsTracker attribute access...")
    
    from core.statistics_tracker import stats_tracker
    
    # Test that stats dictionary is properly structured
    assert 'positive_tags' in stats_tracker.stats
    assert 'negative_tags' in stats_tracker.stats
    assert 'models' in stats_tracker.stats
    assert 'processed_images' in stats_tracker.stats
    
    print("✓ StatisticsTracker attributes accessible")
    return True

def test_consolidation_method():
    """Test the apply_custom_consolidation method"""
    print("\nTesting consolidation method...")
    
    from core.statistics_tracker import stats_tracker
    
    # Add some test data
    stats_tracker.stats['positive_tags']['test_tag1'] = 5
    stats_tracker.stats['positive_tags']['test_tag2'] = 3
    stats_tracker.stats['negative_tags']['bad_tag1'] = 2
    stats_tracker.stats['negative_tags']['bad_tag2'] = 1
    
    # Test consolidation rules
    consolidation_rules = {
        'positive': {
            'consolidated_tag': ['test_tag1', 'test_tag2']
        },
        'negative': {
            'bad_consolidated': ['bad_tag1', 'bad_tag2']
        }
    }
    
    # Test blacklists
    blacklists = {
        'positive': [],
        'negative': []
    }
    
    # Apply consolidation
    result = stats_tracker.apply_custom_consolidation(consolidation_rules, blacklists)
    
    # Verify results
    assert result['success'] == True
    assert result['consolidated_count'] == 4  # 2 positive + 2 negative
    assert result['blacklisted_count'] == 0
    
    # Verify consolidation worked
    assert 'consolidated_tag' in stats_tracker.stats['positive_tags']
    assert stats_tracker.stats['positive_tags']['consolidated_tag'] == 8  # 5 + 3
    assert 'test_tag1' not in stats_tracker.stats['positive_tags']
    assert 'test_tag2' not in stats_tracker.stats['positive_tags']
    
    assert 'bad_consolidated' in stats_tracker.stats['negative_tags']
    assert stats_tracker.stats['negative_tags']['bad_consolidated'] == 3  # 2 + 1
    
    print("✓ Consolidation method works correctly")
    return True

def test_blacklist_functionality():
    """Test blacklist functionality"""
    print("\nTesting blacklist functionality...")
    
    from core.statistics_tracker import stats_tracker
    
    # Add test tags
    stats_tracker.stats['positive_tags']['remove_me'] = 10
    stats_tracker.stats['negative_tags']['delete_this'] = 5
    
    # Test blacklists
    blacklists = {
        'positive': ['remove_me'],
        'negative': ['delete_this']
    }
    
    # Apply blacklists
    result = stats_tracker.apply_custom_consolidation({}, blacklists)
    
    # Verify results
    assert result['success'] == True
    assert result['blacklisted_count'] == 2
    assert 'remove_me' not in stats_tracker.stats['positive_tags']
    assert 'delete_this' not in stats_tracker.stats['negative_tags']
    
    print("✓ Blacklist functionality works correctly")
    return True

def test_advanced_dialog_import():
    """Test that the advanced consolidation dialog can be imported"""
    print("\nTesting AdvancedTagConsolidationDialog import...")
    
    try:
        from core.advanced_tag_consolidation import AdvancedTagConsolidationDialog
        print("✓ AdvancedTagConsolidationDialog imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import AdvancedTagConsolidationDialog: {e}")
        return False

def test_pattern_matching():
    """Test pattern matching methods"""
    print("\nTesting pattern matching methods...")
    
    from core.statistics_tracker import stats_tracker
    
    # Add test tags
    stats_tracker.stats['positive_tags']['girl'] = 10
    stats_tracker.stats['positive_tags']['girls'] = 5
    stats_tracker.stats['positive_tags']['blue_hair'] = 8
    stats_tracker.stats['positive_tags']['blonde_hair'] = 12
    
    # Test pattern matching
    hair_tags = stats_tracker.get_tags_by_pattern('hair', 'positive')
    girl_tags = stats_tracker.get_tags_by_pattern('girl', 'positive')
    
    assert len(hair_tags) == 2  # blue_hair and blonde_hair
    assert len(girl_tags) == 2  # girl and girls
    
    print("✓ Pattern matching methods work correctly")
    return True

if __name__ == "__main__":
    print("MetaPicPick Consolidation Fix Verification")
    print("=" * 50)
    
    tests = [
        test_statistics_tracker_access,
        test_consolidation_method,
        test_blacklist_functionality,
        test_advanced_dialog_import,
        test_pattern_matching
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed: {test.__name__} - {e}")
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Consolidation functionality is working correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")

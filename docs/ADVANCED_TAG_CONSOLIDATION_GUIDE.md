# Advanced Tag Consolidation Guide

## Overview

The Advanced Tag Consolidation system provides comprehensive control over tag management in MetaPicPick. You can now:

1. **Select specific tags** and define custom consolidation rules
2. **Blacklist unwanted tags** to remove them completely
3. **Preview changes** before applying them
4. **Import/Export rules** for sharing and backup
5. **View consolidation history** and statistics

## How to Access

1. Open MetaPicPick
2. Navigate to the **Statistics** tab
3. You'll see three consolidation options:
   - **Simple Consolidation**: Automatic normalization (existing feature)
   - **Advanced Consolidation**: Full control interface (NEW)
   - **Auto Suggestions**: AI-powered consolidation suggestions (NEW)

## Advanced Consolidation Interface

### Tab 1: Tag Consolidation

**Left Panel - Available Tags:**
- **Category Selector**: Choose between "Positive Tags" or "Negative Tags"
- **Search Box**: Filter tags by typing partial names
- **Tags List**: Shows all tags with their usage counts
- **Multi-Selection**: Hold Ctrl to select multiple tags

**Right Panel - Consolidation Rules:**
- **Target Tag Input**: Enter the name you want to consolidate tags to
- **Rule Tags List**: Shows tags currently selected for consolidation
- **Create Rule Button**: Saves the consolidation rule
- **Existing Rules Table**: Shows all current consolidation rules

**Middle Panel - Actions:**
- **→ Add to Rule →**: Moves selected tags to the current consolidation rule
- **→ Add to Blacklist →**: Adds selected tags to the blacklist (removes them completely)
- **← Remove from Rule ←**: Removes tags from the current rule

### Tab 2: Blacklists

Manage tags that you want to remove completely:

**Positive Tags Blacklist:**
- Lists all blacklisted positive tags
- Remove individual tags or clear all

**Negative Tags Blacklist:**
- Lists all blacklisted negative tags
- Remove individual tags or clear all

### Tab 3: Rules & History

**Import/Export Rules:**
- **Export Rules**: Save your consolidation rules and blacklists to a JSON file
- **Import Rules**: Load rules from a previously exported file
- **Reset All Rules**: Clear all rules and blacklists

**Consolidation History:**
- Shows when consolidations were applied
- Records how many tags were affected

**Current Statistics:**
- Real-time counts of tags and rules
- Overview of your consolidation setup

## Step-by-Step Usage

### Creating a Consolidation Rule

1. **Select Category**: Choose "Positive Tags" or "Negative Tags"
2. **Search for Tags**: Use the search box to find similar tags (e.g., search for "girl")
3. **Select Tags**: Click on tags while holding Ctrl to select multiple variations:
   - "1girl"
   - "1 girl" 
   - "1girls"
4. **Add to Rule**: Click "→ Add to Rule →"
5. **Set Target**: Enter the target tag name (e.g., "1girl")
6. **Create Rule**: Click "Create Consolidation Rule"

### Blacklisting Tags

1. **Select Unwanted Tags**: Choose tags you want to remove entirely
2. **Add to Blacklist**: Click "→ Add to Blacklist →"
3. **Verify**: Check the Blacklists tab to see the tags will be removed

### Previewing Changes

1. **Preview Button**: Click "Preview Changes" to see what will happen
2. **Review**: The preview shows:
   - Which tags will be consolidated and their combined counts
   - Which tags will be blacklisted and removed
3. **Modify if Needed**: Go back and adjust rules before applying

### Applying Consolidation

1. **Apply Button**: Click "Apply Consolidation"
2. **Confirm**: Confirm the operation (cannot be undone)
3. **Progress**: Watch the progress bar as changes are applied
4. **Results**: See summary of consolidation results

## Practical Examples

### Example 1: Character Count Tags
**Problem**: Tags like "1girl", "1 girl", "1girls" are all separate
**Solution**:
1. Search for "girl" in positive tags
2. Select "1 girl", "1girls", "one girl"
3. Add to rule with target "1girl"
4. Apply consolidation

### Example 2: Quality Tags
**Problem**: "best quality", "best_quality", "high quality" should be one tag
**Solution**:
1. Select these quality variants
2. Consolidate to "best quality"

### Example 3: Removing Unwanted Tags
**Problem**: Tags like "text", "watermark", "signature" are not useful
**Solution**:
1. Select these unwanted tags
2. Add to blacklist
3. They'll be completely removed

## Auto Suggestions Feature

### How It Works
1. Click "Auto Suggestions" in the Statistics tab
2. The system analyzes your tags using similarity matching
3. Suggests consolidations based on:
   - String similarity (fuzzy matching)
   - Common patterns
   - Tag frequency

### Using Suggestions
1. **Review Suggestions**: See automatically detected similar tags
2. **Export Suggestions**: Save suggestions to a text file for review
3. **Apply Selectively**: Use Advanced Consolidation to apply specific suggestions

## Best Practices

### Before Starting
1. **Backup**: Export your current rules before making major changes
2. **Start Small**: Test with a few tags first
3. **Preview Always**: Always preview before applying

### Consolidation Strategy
1. **High-Frequency First**: Consolidate popular tags first for maximum impact
2. **Consistent Naming**: Choose consistent target tag formats
3. **Category Separation**: Handle positive and negative tags separately

### Maintenance
1. **Regular Review**: Periodically review and update rules
2. **Export Rules**: Keep backups of your consolidation rules
3. **Monitor History**: Check consolidation history for unexpected results

## File Formats

### Consolidation Rules (JSON)
```json
{
  "positive": {
    "1girl": ["1 girl", "1girls", "one girl"],
    "blue eyes": ["blue_eyes", "blue-eyes"]
  },
  "negative": {
    "worst quality": ["worst_quality", "bad quality"]
  }
}
```

### Blacklists (JSON)
```json
{
  "positive": ["text", "watermark", "signature"],
  "negative": ["bad anatomy", "deformed"]
}
```

## Troubleshooting

### Common Issues

**"No tags to preview"**
- Make sure you've created consolidation rules or added tags to blacklists
- Check that you've selected the correct category

**"Import failed"**
- Verify the JSON file format is correct
- Check that the file isn't corrupted

**"Consolidation had no effect"**
- Verify the source tags actually exist in your statistics
- Check that target tags aren't the same as source tags

### Recovery
1. **Undo**: There's no undo, but you can restore from exported backups
2. **Reset**: Use "Reset All Rules" to start over
3. **Selective Removal**: Remove specific rules from the rules table

## Performance Notes

- Consolidation processes run in background threads
- Large tag collections may take a few seconds to process
- Statistics refresh automatically after consolidation
- Rules and blacklists are saved to persistent files

## Integration with Existing Features

- **Simple Consolidation**: Still available for quick automatic normalization
- **Statistics Display**: All statistics reflect consolidated tags
- **Export Functions**: Exported statistics use consolidated tag names
- **Search/Filter**: Works with consolidated tag names

This advanced system gives you complete control over your tag organization while maintaining all existing functionality.

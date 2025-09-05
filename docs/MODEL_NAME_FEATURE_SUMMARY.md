# Model Name Normalization Feature - COMPLETE ✅

## Overview
Added comprehensive model name normalization functionality to MetaPicPick to clean up model names from full file paths, making statistics and metadata more readable and organized.

## Example Transformation
**Before:** `Checkpoints\Z\PDXL\WIP\Fucktastic_2.5D_v2.2_PDXL.safetensors`  
**After:** `Fucktastic 2.5D v2.2 PDXL`

## Features Implemented

### 1. ✅ **Automatic Model Name Normalization**
- **File:** `core/statistics_tracker.py`
- **Method:** `normalize_model_name()`
- **Rules Applied:**
  1. Extract filename from full path
  2. Remove file extensions (.safetensors, .ckpt, .pt, .pth, .bin)
  3. Remove common prefixes (checkpoint_, model_, final_)
  4. Remove common suffixes (_final, _checkpoint, _model, _v1, _v2, _v3, _epoch)
  5. Clean up underscores and spaces
  
### 2. ✅ **Custom Model Mappings**
- **File:** `data/model_name_mappings.json`
- Users can create custom mappings that override automatic normalization
- Methods: `set_model_name_mapping()`, `remove_model_name_mapping()`

### 3. ✅ **Model Name Manager Dialog**
- **File:** `core/model_name_manager.py`
- **Class:** `ModelNameManagerDialog`
- **3 Tabs:**
  - **Current Models:** Shows original vs normalized names, usage counts
  - **Custom Mappings:** Add/remove custom name mappings
  - **Normalization Rules:** View rules and test normalization

### 4. ✅ **Statistics Tab Integration**
- **File:** `core/statistics_tab.py`
- Added "Model Name Manager" button with distinctive blue styling
- Integrated with existing consolidation and export features

### 5. ✅ **Automatic Processing**
- All new metadata processing uses normalized model names
- Existing statistics can be consolidated with one click
- Model names are automatically cleaned during image processing

## User Interface Features

### Model Name Manager Dialog
- **Search and Filter:** Find specific models quickly
- **Visual Indicators:** Highlighted cells show which names will change
- **Bulk Operations:** Consolidate all model names at once
- **Custom Mappings:** Override automatic rules for specific models
- **Live Testing:** Test normalization rules with instant feedback

### Statistics Tab Integration
- **Prominent Access:** Blue "Model Name Manager" button
- **Seamless Integration:** Works with existing consolidation features
- **Auto-refresh:** Statistics update automatically after changes

## Technical Implementation

### Normalization Algorithm
```python
def normalize_model_name(self, model_path_or_name: str) -> str:
    # 1. Check custom mappings first
    # 2. Extract filename from path
    # 3. Remove file extensions  
    # 4. Remove common prefixes/suffixes
    # 5. Clean formatting (underscores → spaces)
    # 6. Return clean name
```

### File Structure
```
core/
├── statistics_tracker.py    # Core normalization logic
├── model_name_manager.py    # GUI dialog for management
└── statistics_tab.py        # Integration with main UI

data/
└── model_name_mappings.json # Custom user mappings
```

## Usage Instructions

### Access Model Name Manager
1. Launch MetaPicPick: `python metapicpick.py`
2. Go to **Statistics** tab
3. Click **"Model Name Manager"** (blue button)

### Normalize Model Names
1. **Automatic:** New images are automatically processed with clean names
2. **Bulk Consolidation:** Click "Consolidate Model Names" in the manager
3. **Custom Mappings:** Add specific overrides in the "Custom Mappings" tab

### Test Normalization Rules
1. Go to "Normalization Rules" tab in the manager
2. Enter any model path/name in the test field
3. See instant results of how it would be normalized

## Benefits

### For Users
- **Cleaner Statistics:** No more messy file paths in model lists
- **Better Organization:** Similar models are grouped together
- **Customizable:** Override automatic rules when needed
- **Visual:** Easy to see what changes will be made

### For Data Management
- **Consistent Naming:** All model names follow the same format
- **Reduced Duplicates:** Similar paths are consolidated
- **Flexible Mapping:** Custom rules for special cases
- **Preservation:** Original information is preserved in custom mappings

## Status: FULLY IMPLEMENTED ✅

All requested functionality has been implemented and tested:
- ✅ Model name normalization from full paths
- ✅ Custom mapping system
- ✅ User-friendly management dialog
- ✅ Statistics tab integration
- ✅ Automatic processing of new images
- ✅ Bulk consolidation of existing data

The feature is ready for use and will automatically clean up model names like:
`Checkpoints\Z\PDXL\WIP\Fucktastic_2.5D_v2.2_PDXL.safetensors` → `Fucktastic 2.5D v2.2 PDXL`

---
**Implementation completed: September 5, 2025** 🎉

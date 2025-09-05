# MetaPicPick Folder Structure

## Overview

The MetaPicPick codebase has been organized into a clean folder structure that separates different types of files and improves maintainability.

## Directory Structure

```
MetaPicPick_V_1/
│
├── metapicpick.py          # Main launcher script
├── gui_main.py             # Main GUI application file
├── requirements.txt        # Python dependencies
├── README.md               # Project readme (copy in root for visibility)
│
├── core/                   # Core application modules
│   ├── __init__.py
│   ├── statistics_tracker.py      # Statistics tracking functionality
│   ├── statistics_tab.py         # Statistics tab UI
│   └── advanced_tag_consolidation.py  # Advanced tag consolidation dialog
│
├── utils/                  # Utility modules and helpers
│   ├── __init__.py
│   ├── metadata_utils.py         # Metadata extraction utilities
│   ├── plugin_manager.py         # Plugin management system
│   ├── parser_plugin_interface.py # Parser plugin interface
│   ├── raw_metadata_loader.py    # Raw metadata loading
│   └── enhanced_metadata_writer.py # Enhanced metadata writing
│
├── parsers/                # Metadata parser plugins
│   ├── __init__.py
│   ├── automatic1111_parser.py
│   ├── comfyui_parser.py
│   ├── novelai_parser.py
│   ├── enhanced_automatic1111_parser.py
│   ├── enhanced_comfyui_parser.py
│   ├── enhanced_novelai_parser.py
│   └── enhanced_general_ai_parser.py
│
├── tests/                  # Test scripts and examples
│   ├── __init__.py
│   ├── test_imports.py
│   ├── test_metadata_editing.py
│   ├── test_statistics.py
│   ├── test_tag_consolidation.py
│   ├── test_enhanced_parsers.py
│   ├── validate_structure.py
│   ├── compare_metadata_versions.py
│   └── example_enhanced_usage.py
│
├── docs/                   # Documentation
│   ├── README.md
│   ├── FEATURES_SUMMARY.md
│   ├── ENHANCED_PARSERS_README.md
│   ├── TABBED_INTERFACE_GUIDE.md
│   ├── ADVANCED_TAG_CONSOLIDATION_GUIDE.md
│   └── FOLDER_STRUCTURE.md (this file)
│
├── scripts/                # Build and run scripts
│   ├── run.bat
│   ├── run_tabbed.bat
│   ├── run_metapicpick.bat
│   ├── setup.bat
│   ├── build.bat
│   ├── package.bat
│   ├── MetaPicPick.spec
│   └── MetaPicPick_Tabbed.spec
│
├── tools/                  # External tools and binaries
│   └── webpmux.exe
│
├── data/                   # Application data files
│   └── metapicpick_statistics.json
│
├── metapicpick_env/        # Virtual environment (not tracked in git)
├── build/                  # Build artifacts (not tracked in git)
├── dist/                   # Distribution files (not tracked in git)
└── __pycache__/            # Python cache (not tracked in git)
```

## Import Structure

### From Main Application (gui_main.py)
```python
from utils.metadata_utils import extract_metadata, save_metadata
from utils.plugin_manager import PluginManager
from core.statistics_tracker import stats_tracker
from core.statistics_tab import StatisticsTab
```

### From Core Modules
```python
# In statistics_tab.py
from .statistics_tracker import stats_tracker
from .advanced_tag_consolidation import AdvancedTagConsolidationDialog

# In statistics_tracker.py
import os
self.stats_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'metapicpick_statistics.json')
```

### From Utils Modules
```python
# In metadata_utils.py
from .raw_metadata_loader import extract_metadata as raw_extract
from .enhanced_metadata_writer import save_metadata
```

### From Tests
```python
# Add parent directory to path for imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import metadata_utils
from utils import plugin_manager
from core import statistics_tracker
```

## Running the Application

### Method 1: Using the launcher script
```bash
python metapicpick.py
```

### Method 2: Using batch files
```bash
run_metapicpick_organized.bat
```

### Method 3: Direct execution
```bash
python gui_main.py
```

## Development Guidelines

### Adding New Core Features
1. Add new core modules to the `core/` directory
2. Update `core/__init__.py` if needed
3. Import using relative imports within core modules
4. Import from main app using `from core.module_name import ...`

### Adding New Utilities
1. Add utility modules to the `utils/` directory
2. Update imports in dependent modules
3. Use relative imports within utils modules

### Adding New Tests
1. Create test files in the `tests/` directory
2. Add path setup at the beginning of test files
3. Name test files with `test_` prefix

### Adding New Parsers
1. Add parser files to the `parsers/` directory
2. Follow the naming convention: `*_parser.py`
3. Implement required `detect()` and `parse()` methods
4. The plugin manager will automatically detect and load them

## Benefits of This Structure

1. **Clear Organization**: Easy to find specific types of files
2. **Modular Design**: Core, utils, and parsers are clearly separated
3. **Easy Testing**: All tests in one place with proper imports
4. **Documentation**: All docs in one central location
5. **Build Separation**: Scripts and build files separated from source code
6. **Data Isolation**: Application data kept in dedicated folder
7. **Tool Management**: External tools in their own directory

## Migration Notes

The application maintains backward compatibility. Existing functionality remains unchanged, only the file organization has been improved. The main changes are:

1. Import paths updated to reflect new structure
2. Data file paths updated to use the `data/` directory
3. Tool paths updated to reference the `tools/` directory
4. Test files updated with proper path setup

All functionality remains the same, just better organized!

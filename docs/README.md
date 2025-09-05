# MetaPicPick - AI Image Metadata Extractor

MetaPicPick is a unified GUI application for extracting, viewing, and managing metadata from AI-generated images. It supports multiple AI image generation platforms including Automatic1111, ComfyUI, and NovelAI.

## ✅ Fixed Issues (Version 1.1)

This version fixes several critical issues that were present in the previous version:

### **Major Fixes Applied:**

1. **Missing Critical Files** - Added missing core files:
   - `plugin_manager.py` - Plugin system manager
   - `parser_plugin_interface.py` - Base interface for parsers
   - `requirements.txt` - Dependency specifications

2. **Function Signature Mismatches** - Fixed inconsistent function calls:
   - `extract_metadata()` now properly accepts plugins parameter
   - Corrected plugin manager constructor to match usage in GUI

3. **Parser Logic Errors** - Fixed metadata extraction bugs:
   - Automatic1111 parser now correctly extracts parameters from metadata string
   - Improved regex patterns for seed, steps, and CFG scale extraction
   - Better handling of negative prompts vs parameters

4. **Build Configuration** - Updated PyInstaller spec:
   - Added proper hidden imports for all modules
   - Included parsers directory in build data
   - Added webpmux.exe binary inclusion

5. **Import Dependencies** - Resolved circular and missing imports:
   - Fixed parser plugin imports
   - Corrected metadata utility function signatures
   - Added proper error handling for missing dependencies

## 🚀 Features

### **Core Features**
- **Multi-Platform Support**: Automatically detects and parses metadata from:
  - Automatic1111 (Stable Diffusion WebUI)
  - ComfyUI 
  - NovelAI
  - Generic metadata extraction

- **File Format Support**:
  - PNG (text chunks)
  - JPEG (EXIF data)
  - WebP (XMP metadata via webpmux)
  - TIFF (tag metadata)

### **Interface Options**

**📁 Original Interface** (`gui_main.py`):
- Single-window layout with all controls visible
- Compact design for simple workflows

**📑 Tabbed Interface** (`gui_main_tabbed.py`) - **Recommended**:
- **Library Tab**: Browse folders, filter images, quick preview
  - Resizable left panel with filters and actions
  - Center image list with search functionality
  - Bottom preview with image and quick metadata
- **Metadata Tab**: Detailed metadata editing
  - Form-based field editor with validation
  - Live preview and raw metadata viewer
  - Resizable panels for comfortable editing
- **Batch Tab**: Bulk processing operations (planned)
- **Settings Tab**: Application preferences (planned)

### **Usability Features**
- **Resizable Sections**: All panels can be resized and layouts persist
- **Persistent Layouts**: Window size and panel positions saved between sessions
- **Real-time Search**: Instant filtering as you type
- **Model-based Filtering**: Filter by detected AI model
- **Visual Preview**: Thumbnail previews with metadata overlay
- **Bulk Operations**: Rename, move, organize multiple files
- **Export Options**: Save filtered metadata to JSON or CSV

## 📋 Requirements

### Python Dependencies
```
PyQt5>=5.15.0
Pillow>=8.0.0
piexif>=1.1.3
```

### External Tools
- `webpmux.exe` (included) - For WebP metadata extraction

## 🛠️ Installation

1. **Clone or download** this repository
2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Verify installation**:
   ```bash
   python validate_structure.py
   ```

## 🎯 Usage

### Running the Application

**Original Single-Window Interface:**
```bash
python gui_main.py
# or
run.bat
```

**New Tabbed Interface (Recommended):**
```bash
python gui_main_tabbed.py
# or
run_tabbed.bat
```

### Basic Workflow
1. **Load Folder** - Click "Load Folder" and select directory with AI images
2. **Browse Images** - Click on images in the list to view metadata
3. **Search/Filter** - Use search bar or model filter to find specific images
4. **Export Data** - Use "Export Filtered Metadata" to save metadata to JSON/CSV
5. **Organize** - Use bulk operations to rename or move images

### Supported Metadata Fields
- **Basic**: model_name, base_model, width, height, size, format
- **Generation**: positive_prompt, negative_prompt, steps, cfg_scale, seed
- **Technical**: scheduler, sampler, method
- **Extra**: Additional platform-specific metadata

## 🏗️ Building Executable

### Create Standalone EXE
```bash
# Build using PyInstaller
python build.bat

# Or manually:
python -m PyInstaller MetaPicPick.spec
```

### Package for Distribution
```bash
# Create portable ZIP
python package.bat
```

The executable will be created in the `dist/` directory.

## 🔧 Architecture

### Plugin System
The application uses a modular plugin system for parsing different metadata formats:

```
MetaPicPick/
├── gui_main.py              # Main application GUI
├── plugin_manager.py        # Plugin loading and management
├── parser_plugin_interface.py # Base parser interface
├── metadata_utils.py        # Metadata extraction utilities
├── raw_metadata_loader.py   # Low-level metadata reading
└── parsers/                 # Parser plugins
    ├── __init__.py
    ├── automatic1111_parser.py
    ├── comfyui_parser.py
    └── novelai_parser.py
```

### Adding New Parsers
To add support for a new AI platform:

1. Create a new parser in `parsers/` directory
2. Inherit from `ParserPluginInterface`
3. Implement `detect()` and `parse()` methods
4. The plugin will be automatically loaded

Example:
```python
from parser_plugin_interface import ParserPluginInterface

class MyAIParser(ParserPluginInterface):
    @staticmethod
    def detect(metadata):
        # Return True if this parser can handle the metadata
        return 'my_ai_signature' in metadata
    
    @staticmethod  
    def parse(metadata):
        # Extract structured data from metadata
        return {
            'positive_prompt': extracted_prompt,
            'seed': extracted_seed,
            # ... other fields
        }
```

## 🐛 Troubleshooting

### Common Issues

**ImportError: No module named 'PyQt5'**
```bash
pip install PyQt5
```

**ImportError: No module named 'piexif'**
```bash
pip install piexif
```

**WebP metadata not extracted**
- Ensure `webpmux.exe` is in the same directory as the application
- Check that the WebP file actually contains metadata

**Parser not detecting images**
- Check if the image contains the expected metadata format
- Enable debug output to see what metadata is being extracted

### Debug Mode
Set environment variable for verbose output:
```bash
set DEBUG=1
python gui_main.py
```

## 📄 License

This project is open source. See the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Test thoroughly using `validate_structure.py`
5. Submit a pull request

## 📚 Changelog

### Version 1.2 (Current - Tabbed Interface)
- ✨ **NEW**: Complete tabbed interface redesign (`gui_main_tabbed.py`)
  - 📁 **Library Tab**: Organized browsing with resizable panels
  - 📝 **Metadata Tab**: Dedicated metadata editing interface
  - ⚡ **Batch Tab**: Placeholder for future batch operations
  - ⚙️ **Settings Tab**: Application preferences (planned)
- ✨ **NEW**: Resizable splitter panels with persistent layouts
- ✨ **NEW**: Enhanced QSettings integration for layout persistence
- ✨ **NEW**: Menu bar with file operations and layout reset
- ✨ **NEW**: Status bar with operation feedback
- ✨ **NEW**: Both interface options available (original + tabbed)
- ✅ Improved organization and user experience
- ✅ Professional interface design with proper spacing

### Version 1.1 (Stable - Fixed Core Issues)
- ✅ Fixed all missing critical files
- ✅ Resolved function signature mismatches  
- ✅ Corrected parser logic errors
- ✅ Updated build configuration
- ✅ Fixed import dependencies
- ✅ Added comprehensive validation tools
- ✅ Created proper documentation

### Version 1.0 (Previous - Had Issues)
- ❌ Missing core files (plugin_manager.py, parser_plugin_interface.py)
- ❌ Function signature mismatches
- ❌ Parser logic errors
- ❌ Incomplete build configuration

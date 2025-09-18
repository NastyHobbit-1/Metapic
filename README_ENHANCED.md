# MetaPic Enhanced - Ultimate AI Image Metadata Management

*Version 2.0 - Comprehensive CLI + GUI Solution*

## 🚀 Overview

MetaPic Enhanced is a comprehensive AI image metadata management tool that combines the best of modern Python architecture with rich GUI features. Built on a solid foundation of type-safe, performant code, it provides both powerful CLI tools and an intuitive graphical interface for managing AI-generated image metadata.

### Key Features

- **🎯 Dual Interface**: Both CLI and GUI for different workflows
- **📊 Advanced Statistics**: Comprehensive tracking and analytics
- **🔌 Plugin System**: Support for multiple AI platforms (A1111, ComfyUI, NovelAI, General)
- **⚡ Performance**: Fast processing with modern Python stack
- **🛡️ Type Safety**: Full type hints with Pydantic v2 models
- **📦 Portable**: Single executable distribution
- **🎨 Rich GUI**: Tabbed interface with drag & drop, search, and editing

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [CLI Usage](#cli-usage)
- [GUI Usage](#gui-usage)
- [Features](#features)
- [Architecture](#architecture)
- [Build System](#build-system)
- [Contributing](#contributing)

## 💾 Installation

### Option 1: From Source (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd MetaPic1

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install with GUI support
pip install -e ".[ui]"

# Or install CLI only
pip install -e .
```

### Option 2: Portable Executable

Download the portable executable from releases (coming soon).

## 🚀 Quick Start

### CLI Usage

```bash
# Extract metadata from images
metapic extract samples/

# Extract and save to file
metapic extract samples/ --out metadata.ndjson

# View statistics
metapic stats

# Export statistics
metapic stats --export stats.json

# Batch rename with pattern
metapic rename metadata.ndjson --pattern "{model}-{i:04d}"
```

### GUI Usage

```bash
# Launch the enhanced GUI
metapic-gui
```

Or run directly:
```bash
python -m metapic.gui.enhanced_app
```

## 🎯 CLI Usage

### Extract Command

Extract metadata from images with comprehensive parsing:

```bash
# Basic extraction
metapic extract path/to/images

# Save to NDJSON file
metapic extract path/to/images --out metadata.ndjson

# Skip parsing (exiftool only)
metapic extract path/to/images --skip-parse
```

### Statistics Command

View comprehensive processing statistics:

```bash
# Display statistics
metapic stats

# Export to JSON
metapic stats --export statistics.json
```

### Rename Command

Batch rename images based on metadata:

```bash
# Preview rename plan
metapic rename metadata.ndjson --pattern "{model}-{i:04d}"

# Execute rename
metapic rename metadata.ndjson --pattern "{model}-{i:04d}" --no-dry-run
```

## 🎨 GUI Usage

### Library Tab

- **Load Folder**: Browse and load image directories
- **Search**: Real-time search through images and metadata
- **Filter**: Filter by model, sampler, or other criteria
- **Preview**: View metadata for selected images

### Statistics Tab

- **Summary**: Overview of processed images and models
- **Models**: Detailed model usage statistics
- **Tags**: Most common positive and negative tags
- **Analytics**: Comprehensive usage analytics

### Metadata Tab

- **Browse**: Select individual image files
- **Edit**: Modify metadata fields with validation
- **Save**: Write changes back to image files
- **Validation**: Ensure data integrity

## 🔧 Features

### Core Functionality

- **Multi-Platform Support**: Automatic1111, ComfyUI, NovelAI, General AI
- **File Format Support**: PNG, JPEG, WebP, TIFF, HEIC
- **Metadata Extraction**: EXIF, XMP, text chunks, sidecar JSON
- **Advanced Parsing**: Plugin-based system with specialized parsers
- **Statistics Tracking**: Comprehensive analytics and reporting

### CLI Features

- **Rich Terminal Output**: Beautiful tables and progress bars
- **Type-Safe Operations**: Pydantic models ensure data integrity
- **Batch Processing**: Efficient handling of large image collections
- **Export Capabilities**: Multiple output formats (NDJSON, JSON, CSV)
- **Performance**: Fast processing with orjson and optimized algorithms

### GUI Features

- **Tabbed Interface**: Organized workflow with persistent layouts
- **Drag & Drop**: Easy file management
- **Real-time Search**: Instant filtering and search
- **Visual Previews**: Thumbnail previews with metadata overlay
- **Statistics Dashboard**: Comprehensive analytics visualization
- **Metadata Editor**: Full CRUD operations with validation

### Advanced Features

- **Plugin System**: Extensible parser architecture
- **Statistics Consolidation**: Tag normalization and model mapping
- **Performance Optimization**: Lazy loading and caching
- **Error Handling**: Comprehensive error management and logging
- **Cross-Platform**: Windows, macOS, Linux support

## 🏗️ Architecture

### Project Structure

```
src/metapic/
├── cli.py                    # CLI interface with Typer
├── models.py                 # Pydantic v2 data models
├── extract.py                # exiftool integration
├── normalize.py              # Text parsing utilities
├── bulk.py                   # Batch operations
├── utils.py                  # Core utilities
├── gui/                      # GUI components
│   ├── enhanced_app.py       # Main GUI application
│   └── app.py                # Basic GUI (legacy)
├── core/                     # Core functionality
│   └── statistics_tracker.py # Advanced statistics system
└── plugins/                  # Parser plugins
    ├── sd.py                 # Stable Diffusion parser
    ├── automatic1111_parser.py
    ├── comfyui_parser.py
    ├── novelai_parser.py
    └── general_ai_parser.py
```

### Data Models

```python
class ImageMeta(BaseModel):
    path: str
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    size_bytes: Optional[int] = None
    
    # AI Generation Parameters
    model: Optional[str] = None
    base_model: Optional[str] = None
    sampler: Optional[str] = None
    scheduler: Optional[str] = None
    steps: Optional[int] = None
    cfg: Optional[float] = None
    seed: Optional[int] = None
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    method: Optional[str] = None
    
    # Raw Data
    metadata_raw: Dict[str, Any] = Field(default_factory=dict)
    parsed_raw: Dict[str, Any] = Field(default_factory=dict)
```

### Plugin System

Each parser plugin implements:

```python
def detect(metadata: Dict[str, Any]) -> bool:
    """Detect if metadata matches this parser"""
    
def parse(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Parse metadata and return structured data"""
```

## 🔨 Build System

### Development Build

```bash
# Install build dependencies
pip install hatch pyinstaller

# Build with Hatch
hatch build

# Or build executable
pyinstaller MetaPic.spec
```

### Production Build

```bash
# Build both CLI and GUI executables
pyinstaller MetaPic.spec

# Output:
# dist/MetaPic/          # CLI executable
# dist/MetaPicGUI/       # GUI executable
```

### Build Artifacts

- **CLI**: `MetaPic.exe` - Console application
- **GUI**: `MetaPicGUI.exe` - Windowed application
- **Portable**: Single executable with all dependencies

## 📊 Statistics System

### Tracked Metrics

- **Images**: Total processed, unique models, file formats
- **Models**: Usage frequency, model mappings, normalization
- **Tags**: Positive/negative tag frequency, consolidation
- **Technical**: Samplers, CFG ranges, step ranges, dimensions
- **Analytics**: Usage patterns, trends, insights

### Data Persistence

Statistics are automatically saved to:
- `src/metapic/data/metapic_statistics.json`
- `src/metapic/data/model_name_mappings.json`

### Export Formats

- **JSON**: Complete statistics export
- **CSV**: Tabular data for external analysis
- **CLI**: Rich terminal tables and summaries

## 🎯 Supported AI Platforms

### Automatic1111 (Stable Diffusion WebUI)
- Parameters extraction from PNG text chunks
- Enhanced parsing for all generation parameters
- Support for extensions and custom fields
- LoRA, ControlNet, VAE information

### ComfyUI
- Workflow metadata extraction
- Node-based parameter parsing
- JSON workflow preservation
- Complex pipeline support

### NovelAI
- NovelAI-specific metadata format
- Quality tags and artist recognition
- Subscription tier detection
- Specialized prompt parsing

### General AI
- Generic AI metadata extraction
- Fallback parser for unknown formats
- Basic parameter detection
- Text-based parsing

## 🔧 Configuration

### Settings

The application uses QSettings for persistent configuration:

- **Window Geometry**: Restored on startup
- **Layout State**: Splitter positions and tab states
- **Statistics**: Automatic tracking and persistence
- **Model Mappings**: Custom model name normalization

### Data Directory

Statistics and configuration stored in:
- `src/metapic/data/` - Application data
- `~/.config/MetaPic/` - User settings (Linux/Mac)
- `%APPDATA%/MetaPic/` - User settings (Windows)

## 🚀 Performance

### Optimizations

- **Fast JSON**: orjson for high-performance JSON processing
- **Lazy Loading**: GUI components loaded on demand
- **Caching**: Metadata caching for repeated operations
- **Batch Processing**: Efficient handling of large collections
- **Memory Management**: Optimized data structures

### Benchmarks

- **Startup**: < 0.2 seconds
- **Metadata Extraction**: ~100 images/second
- **Statistics**: Real-time updates
- **GUI Responsiveness**: Smooth interactions

## 🐛 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Install missing dependencies
pip install -e ".[ui]"
```

#### GUI Won't Start
```bash
# Check PySide6 installation
pip install PySide6>=6.7
```

#### Statistics Not Loading
- Ensure data directory exists: `src/metapic/data/`
- Check file permissions
- Verify JSON file integrity

#### Parser Issues
- Check exiftool installation
- Verify image file integrity
- Review parser plugin configuration

### Debug Mode

```bash
# Enable debug logging
export DEBUG=1
metapic extract samples/
```

## 🤝 Contributing

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd MetaPic1

# Create development environment
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[ui]"

# Install development tools
pip install pytest black isort mypy
```

### Code Style

- **Type Hints**: Required for all functions
- **Pydantic**: Use for data models
- **Error Handling**: Comprehensive error management
- **Documentation**: Docstrings for all public functions
- **Testing**: Unit tests for core functionality

### Adding New Parsers

1. Create new parser in `src/metapic/plugins/`
2. Implement `detect()` and `parse()` functions
3. Add tests for parser functionality
4. Update documentation

## 📄 License

Open Source - See LICENSE file for details.

## 🙏 Acknowledgments

- **Original MetaPic**: Modern Python foundation
- **Enhanced Features**: Advanced GUI and statistics from H:\Metapic
- **Working Reference**: Proven functionality from portable executable
- **Community**: Open source AI tools and libraries

---

**MetaPic Enhanced v2.0** - *The Ultimate AI Image Metadata Management Solution*

Built with ❤️ using modern Python, PySide6, and comprehensive architecture.

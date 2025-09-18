# MetaPic Enhanced - Ultimate AI Image Metadata Management

*Version 2.0 - Comprehensive CLI + GUI Solution*

## 🚀 Overview

MetaPic Enhanced is a comprehensive AI image metadata management tool that combines modern Python architecture with rich GUI features. Built on a solid foundation of type-safe, performant code, it provides both powerful CLI tools and an intuitive graphical interface for managing AI-generated image metadata.

### Key Features

- **🎯 Dual Interface**: Both CLI and GUI for different workflows
- **📊 Advanced Statistics**: Comprehensive tracking and analytics
- **🔌 Plugin System**: Support for multiple AI platforms (A1111, ComfyUI, NovelAI, General)
- **⚡ Performance**: Fast processing with modern Python stack
- **🛡️ Type Safety**: Full type hints with Pydantic v2 models
- **📦 Portable**: Single executable distribution
- **🎨 Rich GUI**: Tabbed interface with drag & drop, search, and editing

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [CLI Usage](#cli-usage)
- [GUI Usage](#gui-usage)
- [Features](#features)
- [Architecture](#architecture)
- [Build System](#build-system)
- [Documentation](#documentation)

## 🚀 Quick Start

### Option 1: CLI Only
```bash
# 1) Create venv and install
python -m venv .venv && .venv\Scripts\activate
pip install -U pip hatch
hatch env create
hatch run metapic --help

# 2) Extract metadata from images
hatch run metapic extract samples/

# 3) View statistics
hatch run metapic stats
```

### Option 2: Full Installation (CLI + GUI)
```bash
# 1) Create venv and install with GUI support
python -m venv .venv && .venv\Scripts\activate
pip install -U pip hatch
pip install -e ".[ui]"

# 2) Use CLI
metapic extract samples/ --out metadata.ndjson
metapic stats

# 3) Launch GUI
metapic-gui
```

## 💾 Installation

### From Source (Recommended)

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

### Portable Executable

Build portable executables:
```bash
# Build both CLI and GUI executables
pyinstaller MetaPic.spec

# Output:
# dist/MetaPic/          # CLI executable
# dist/MetaPicGUI/       # GUI executable
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

Launch the enhanced GUI:
```bash
metapic-gui
```

### GUI Features
- **Library Tab**: Load folders, search, filter images
- **Statistics Tab**: View analytics and model usage
- **Metadata Tab**: Edit individual image metadata

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

### GUI Features
- **Tabbed Interface**: Organized workflow with persistent layouts
- **Drag & Drop**: Easy file management
- **Real-time Search**: Instant filtering and search
- **Visual Previews**: Thumbnail previews with metadata overlay
- **Statistics Dashboard**: Comprehensive analytics visualization
- **Metadata Editor**: Full CRUD operations with validation

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

## 📚 Documentation

- **[HOWTO.md](HOWTO.md)**: Detailed setup, build, and usage instructions
- **[README_ENHANCED.md](README_ENHANCED.md)**: Comprehensive feature documentation
- **Code Documentation**: All functions and classes are fully documented
- **Type Hints**: Complete type annotations throughout the codebase

## 🎯 Supported AI Platforms

- **Automatic1111**: Parameters extraction from PNG text chunks
- **ComfyUI**: Workflow metadata extraction and node parsing
- **NovelAI**: NovelAI-specific metadata format and quality tags
- **General AI**: Fallback parser for unknown formats

## 🚀 Performance

- **Startup**: < 0.2 seconds
- **Metadata Extraction**: ~100 images/second
- **Statistics**: Real-time updates
- **Memory**: Optimized data structures and lazy loading

## 🤝 Contributing

See [HOWTO.md](HOWTO.md) for development setup and contribution guidelines.

## 📄 License

Open Source - See LICENSE file for details.

---

**MetaPic Enhanced v2.0** - *The Ultimate AI Image Metadata Management Solution*

Built with ❤️ using modern Python, PySide6, and comprehensive architecture.
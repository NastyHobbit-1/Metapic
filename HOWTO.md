# MetaPic Enhanced - Complete Setup, Build, and Usage Guide

*Comprehensive guide for developers and users*

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Development Setup](#development-setup)
- [Installation Options](#installation-options)
- [Building Executables](#building-executables)
- [Usage Guide](#usage-guide)
- [Development Guide](#development-guide)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🔧 Prerequisites

### System Requirements

- **Python**: 3.10 or higher
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 1GB free space for installation

### Required Tools

- **Git**: For version control
- **Python**: Latest stable version
- **pip**: Package installer
- **exiftool**: For metadata extraction (optional, auto-installed)

### Optional Tools

- **PyInstaller**: For building executables
- **Hatch**: For modern Python packaging
- **PySide6**: For GUI functionality

## 🚀 Development Setup

### 1. Clone Repository

```bash
# Clone the repository
git clone <repository-url>
cd MetaPic1

# Verify you're in the correct directory
ls -la  # Should show pyproject.toml, src/, etc.
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Verify activation
which python  # Should point to .venv/bin/python
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install in development mode
pip install -e .

# Or install with GUI support
pip install -e ".[ui]"

# Install development tools
pip install pytest black isort mypy hatch pyinstaller
```

### 4. Verify Installation

```bash
# Test CLI
metapic --help

# Test imports
python -c "from metapic.cli import app; print('CLI import successful')"

# Test with sample data
metapic extract samples/ --out test.ndjson
```

## 💾 Installation Options

### Option 1: Development Installation (Recommended)

```bash
# Clone and setup
git clone <repository-url>
cd MetaPic1
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -e ".[ui]"

# Use immediately
metapic --help
metapic-gui
```

### Option 2: Production Installation

```bash
# Install from source
pip install git+<repository-url>

# Or install specific version
pip install git+<repository-url>@v2.0.0
```

### Option 3: Portable Executable

```bash
# Build portable executable
pyinstaller MetaPic.spec

# Run from dist/
./dist/MetaPic/MetaPic.exe --help
./dist/MetaPicGUI/MetaPicGUI.exe
```

## 🔨 Building Executables

### Prerequisites for Building

```bash
# Install build dependencies
pip install pyinstaller

# Verify PyInstaller
pyinstaller --version
```

### Build Process

#### 1. Development Build

```bash
# Quick development build
pyinstaller --onefile src/metapic/cli.py --name MetaPic

# Output: dist/MetaPic.exe
```

#### 2. Production Build

```bash
# Full production build with all features
pyinstaller MetaPic.spec

# Output:
# dist/MetaPic/          # CLI executable with dependencies
# dist/MetaPicGUI/       # GUI executable with dependencies
```

#### 3. Custom Build

```bash
# Build only CLI
pyinstaller --name MetaPic \
  --add-data "src/metapic/plugins;metapic/plugins" \
  --add-data "src/metapic/core;metapic/core" \
  --hidden-import metapic.plugins \
  --hidden-import metapic.core \
  src/metapic/cli.py

# Build only GUI
pyinstaller --name MetaPicGUI \
  --add-data "src/metapic/plugins;metapic/plugins" \
  --add-data "src/metapic/core;metapic/core" \
  --hidden-import metapic.plugins \
  --hidden-import metapic.core \
  --hidden-import PySide6 \
  --windowed \
  src/metapic/gui/enhanced_app.py
```

### Build Configuration

The `MetaPic.spec` file contains the complete build configuration:

```python
# Key configuration options:
- CLI_ENTRY: 'src/metapic/cli.py'
- GUI_ENTRY: 'src/metapic/gui/enhanced_app.py'
- Hidden imports: All plugins and core modules
- Data files: Plugin and core directories
- Console: True for CLI, False for GUI
```

## 📖 Usage Guide

### CLI Usage

#### Basic Commands

```bash
# Extract metadata
metapic extract samples/
metapic extract samples/ --out metadata.ndjson

# View statistics
metapic stats
metapic stats --export stats.json

# Batch rename
metapic rename metadata.ndjson --pattern "{model}-{i:04d}"
metapic rename metadata.ndjson --pattern "{model}-{i:04d}" --no-dry-run
```

#### Advanced Usage

```bash
# Skip parsing (exiftool only)
metapic extract samples/ --skip-parse

# Custom output format
metapic extract samples/ --out custom.json

# Filter by model
metapic extract samples/ | grep "model_name"

# Process large directories
metapic extract /path/to/large/collection --out big_collection.ndjson
```

#### Command Reference

| Command | Description | Options |
|---------|-------------|---------|
| `extract` | Extract metadata from images | `--out`, `--skip-parse` |
| `stats` | Show processing statistics | `--export` |
| `rename` | Batch rename images | `--pattern`, `--dry-run` |

### GUI Usage

#### Launching GUI

```bash
# Launch enhanced GUI
metapic-gui

# Or run directly
python -m metapic.gui.enhanced_app
```

#### GUI Workflow

1. **Library Tab**
   - Click "Load Folder" to select image directory
   - Use search bar to filter images
   - Select model filter to show specific models
   - Click images to view metadata preview

2. **Statistics Tab**
   - View comprehensive analytics
   - See model usage statistics
   - Analyze tag frequency
   - Export statistics data

3. **Metadata Tab**
   - Browse for individual image files
   - Edit metadata fields
   - Save changes back to images
   - Validate data integrity

#### GUI Features

- **Drag & Drop**: Drag image files directly into the application
- **Real-time Search**: Instant filtering as you type
- **Persistent Layout**: Remembers window size and splitter positions
- **Export Options**: Save data in multiple formats

### File Formats

#### Supported Input Formats

- **PNG**: Text chunk metadata (most common for AI images)
- **JPEG**: EXIF data extraction
- **WebP**: XMP metadata via webpmux
- **TIFF**: Tag-based metadata system
- **HEIC**: Apple format support

#### Supported Output Formats

- **NDJSON**: Newline-delimited JSON for streaming
- **JSON**: Standard JSON format
- **CSV**: Tabular data for spreadsheet applications

### AI Platform Support

#### Automatic1111 (Stable Diffusion WebUI)
- Parameters extraction from PNG text chunks
- Support for all generation parameters
- LoRA, ControlNet, VAE information
- Extension compatibility

#### ComfyUI
- Workflow metadata extraction
- Node-based parameter parsing
- JSON workflow preservation
- Complex pipeline support

#### NovelAI
- NovelAI-specific metadata format
- Quality tags and artist recognition
- Subscription tier detection
- Specialized prompt parsing

#### General AI
- Generic AI metadata extraction
- Fallback parser for unknown formats
- Text-based parameter detection
- Basic parameter extraction

## 🛠️ Development Guide

### Project Structure

```
MetaPic1/
├── src/metapic/              # Main package
│   ├── cli.py                # CLI interface
│   ├── models.py             # Data models
│   ├── extract.py            # Metadata extraction
│   ├── normalize.py          # Text parsing
│   ├── bulk.py               # Batch operations
│   ├── utils.py              # Utilities
│   ├── gui/                  # GUI components
│   │   ├── enhanced_app.py   # Main GUI
│   │   └── app.py            # Basic GUI
│   ├── core/                 # Core functionality
│   │   └── statistics_tracker.py
│   └── plugins/              # Parser plugins
│       ├── sd.py
│       ├── automatic1111_parser.py
│       ├── comfyui_parser.py
│       ├── novelai_parser.py
│       └── general_ai_parser.py
├── pyproject.toml            # Project configuration
├── MetaPic.spec              # PyInstaller configuration
├── README.md                 # Main documentation
├── README_ENHANCED.md        # Detailed features
├── HOWTO.md                  # This file
└── samples/                  # Sample images
```

### Code Style Guidelines

#### Type Hints
```python
from typing import Optional, Dict, List, Any

def process_images(
    image_paths: List[str], 
    output_format: str = "ndjson"
) -> Dict[str, Any]:
    """Process images and return metadata."""
    pass
```

#### Pydantic Models
```python
from pydantic import BaseModel, Field

class ImageMeta(BaseModel):
    """Metadata model for AI-generated images."""
    path: str
    model: Optional[str] = None
    steps: Optional[int] = Field(default=None, ge=1, le=1000)
```

#### Error Handling
```python
import logging

logger = logging.getLogger(__name__)

def safe_operation():
    try:
        # Risky operation
        result = risky_function()
        return result
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        raise
```

### Adding New Features

#### 1. Adding a New Parser

Create `src/metapic/plugins/new_platform_parser.py`:

```python
def detect(metadata: Dict[str, Any]) -> bool:
    """Detect if metadata is from this platform."""
    return "platform_specific_field" in metadata

def parse(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Parse metadata and return structured data."""
    result = {}
    # Parse logic here
    return result
```

#### 2. Adding CLI Commands

Extend `src/metapic/cli.py`:

```python
@app.command()
def new_command(
    input_path: str = typer.Argument(..., help="Input path"),
    option: bool = typer.Option(False, help="Optional flag"),
):
    """New command description."""
    # Command logic here
    pass
```

#### 3. Adding GUI Features

Extend `src/metapic/gui/enhanced_app.py`:

```python
class NewTab(QWidget):
    """New tab for additional functionality."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        # UI setup code here
        pass
```

### Testing

#### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest test/test_cli.py

# Run with coverage
pytest --cov=metapic

# Run with verbose output
pytest -v
```

#### Writing Tests

```python
import pytest
from metapic.models import ImageMeta
from metapic.plugins.sd import detect, parse

def test_sd_detection():
    """Test Stable Diffusion detection."""
    metadata = {"parameters": "Steps: 20, CFG: 7.5"}
    assert detect(metadata) == True

def test_sd_parsing():
    """Test Stable Diffusion parsing."""
    metadata = {"parameters": "Steps: 20, CFG: 7.5, Seed: 123"}
    result = parse(metadata)
    assert result["steps"] == 20
    assert result["cfg"] == 7.5
    assert result["seed"] == 123
```

### Performance Optimization

#### Profiling

```bash
# Profile CLI performance
python -m cProfile -o profile.stats -m metapic.cli extract samples/
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(10)"

# Memory profiling
pip install memory-profiler
python -m memory_profiler src/metapic/cli.py extract samples/
```

#### Optimization Tips

1. **Use orjson**: Fast JSON processing
2. **Lazy Loading**: Load data only when needed
3. **Batch Processing**: Process multiple items together
4. **Caching**: Cache expensive operations
5. **Type Hints**: Enable optimizations

## 🐛 Troubleshooting

### Common Issues

#### Import Errors

```bash
# Error: ModuleNotFoundError: No module named 'typer'
# Solution: Install dependencies
pip install -e ".[ui]"

# Error: ModuleNotFoundError: No module named 'PySide6'
# Solution: Install GUI dependencies
pip install PySide6>=6.7
```

#### GUI Won't Start

```bash
# Check PySide6 installation
python -c "import PySide6; print('PySide6 OK')"

# Check GUI entry point
python -m metapic.gui.enhanced_app

# Debug mode
export DEBUG=1
metapic-gui
```

#### Statistics Not Loading

```bash
# Check data directory
ls -la src/metapic/data/

# Check file permissions
chmod 755 src/metapic/data/

# Clear statistics
rm src/metapic/data/metapic_statistics.json
```

#### Parser Issues

```bash
# Check exiftool installation
exiftool -ver

# Test with single image
metapic extract single_image.png

# Debug parsing
python -c "
from metapic.extract import exiftool_batch
from pathlib import Path
result = exiftool_batch([Path('test.png')])
print(result)
"
```

#### Build Issues

```bash
# Clean build
rm -rf build/ dist/ *.spec

# Reinstall PyInstaller
pip install --upgrade pyinstaller

# Check hidden imports
pyinstaller --debug=imports MetaPic.spec
```

### Debug Mode

#### Enable Debug Logging

```bash
# Set debug environment
export DEBUG=1
export LOG_LEVEL=DEBUG

# Run with debug output
metapic extract samples/ --verbose
```

#### Debug GUI

```bash
# Run GUI with console output
python -m metapic.gui.enhanced_app

# Check Qt installation
python -c "
from PySide6.QtWidgets import QApplication
app = QApplication([])
print('Qt OK')
app.quit()
"
```

### Performance Issues

#### Slow Startup

```bash
# Profile startup time
python -c "
import time
start = time.time()
from metapic.cli import app
print(f'Import time: {time.time() - start:.3f}s')
"

# Check dependencies
pip list | grep -E "(typer|pydantic|rich)"
```

#### Memory Usage

```bash
# Monitor memory usage
python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB')
"
```

## 🤝 Contributing

### Development Workflow

1. **Fork Repository**
   ```bash
   git fork <repository-url>
   git clone <your-fork-url>
   cd MetaPic1
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature
   ```

3. **Make Changes**
   - Follow code style guidelines
   - Add type hints
   - Write tests
   - Update documentation

4. **Test Changes**
   ```bash
   pytest
   python -m metapic.cli --help
   ```

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

6. **Push and Create PR**
   ```bash
   git push origin feature/new-feature
   # Create pull request on GitHub
   ```

### Code Review Process

1. **Automated Checks**
   - Linting (black, isort, mypy)
   - Tests (pytest)
   - Build verification

2. **Manual Review**
   - Code quality
   - Documentation
   - Performance impact
   - Backward compatibility

3. **Approval and Merge**
   - Maintainer approval
   - Automated merge
   - Release preparation

### Release Process

1. **Version Bump**
   ```bash
   # Update version in pyproject.toml
   # Update CHANGELOG.md
   ```

2. **Build Release**
   ```bash
   pyinstaller MetaPic.spec
   # Test executables
   ```

3. **Create Release**
   ```bash
   git tag v2.0.1
   git push origin v2.0.1
   # Create GitHub release
   ```

## 📚 Additional Resources

### Documentation

- **[README.md](README.md)**: Main project documentation
- **[README_ENHANCED.md](README_ENHANCED.md)**: Detailed feature documentation
- **Code Comments**: All functions and classes documented
- **Type Hints**: Complete type annotations

### External Resources

- **[Typer Documentation](https://typer.tiangolo.com/)**: CLI framework
- **[Pydantic Documentation](https://pydantic-docs.helpmanual.io/)**: Data validation
- **[PySide6 Documentation](https://doc.qt.io/qtforpython/)**: GUI framework
- **[PyInstaller Documentation](https://pyinstaller.readthedocs.io/)**: Executable building

### Community

- **Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Pull Requests**: Contribute code and improvements

---

**MetaPic Enhanced v2.0** - *Complete Setup, Build, and Usage Guide*

For questions or support, please open an issue on GitHub.

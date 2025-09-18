# Changelog

All notable changes to MetaPic Enhanced will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-09-18

### Added
- **Comprehensive GUI**: Full tabbed interface with Library, Statistics, and Metadata tabs
- **Advanced Statistics System**: Sophisticated tracking and analytics for processed images
- **Multiple AI Platform Support**: Parsers for Automatic1111, ComfyUI, NovelAI, and General AI
- **Enhanced CLI**: New `stats` command with rich terminal output
- **Type-Safe Data Models**: Pydantic v2 models with comprehensive validation
- **Plugin Architecture**: Extensible parser system for different AI platforms
- **Statistics Tracking**: Automatic collection of model usage, tag frequency, and analytics
- **Rich Terminal Output**: Beautiful tables and progress bars using Rich library
- **Batch Operations**: Enhanced bulk rename with customizable patterns
- **Export Capabilities**: Multiple output formats (NDJSON, JSON, CSV)
- **Performance Optimizations**: Fast JSON processing with orjson
- **Cross-Platform Support**: Windows, macOS, and Linux compatibility
- **Comprehensive Documentation**: Complete setup, build, and usage guides
- **Build System**: PyInstaller configuration for portable executables

### Enhanced
- **CLI Interface**: Upgraded with Typer for better command-line experience
- **Metadata Extraction**: Enhanced exiftool integration with better error handling
- **Text Parsing**: Improved normalization for AI parameter extraction
- **File Utilities**: Better image file detection and processing
- **Project Structure**: Organized modular architecture with clear separation of concerns

### Changed
- **Package Name**: Updated from `metapicpick` to `metapic` for consistency
- **Dependencies**: Upgraded to modern Python stack (Pydantic v2, Typer, Rich)
- **Build Configuration**: Updated PyInstaller spec for new structure
- **Documentation**: Comprehensive rewrite with detailed guides and examples

### Technical Details
- **Python Version**: Requires Python 3.10+
- **GUI Framework**: PySide6 (Qt6) for modern desktop interface
- **Data Validation**: Pydantic v2 for type-safe metadata models
- **CLI Framework**: Typer for beautiful command-line interface
- **JSON Processing**: orjson for high-performance JSON operations
- **Image Processing**: Pillow for image format support
- **Metadata Extraction**: pyexiftool for EXIF data handling

## [1.0.0] - 2025-09-18 (Original)

### Added
- **Basic CLI**: Simple command-line interface for metadata extraction
- **Core Extraction**: exiftool integration for metadata extraction
- **Basic Parsing**: Simple text parsing for AI parameters
- **File Utilities**: Basic image file detection and iteration
- **Bulk Operations**: Simple batch rename functionality
- **Modern Packaging**: Hatch-based build system with pyproject.toml
- **Type Hints**: Basic type annotations throughout codebase

### Technical Details
- **Python Version**: Python 3.10+
- **Dependencies**: Minimal set focused on core functionality
- **Architecture**: Clean, focused design with modern Python practices
- **Build System**: Hatch for development, PyInstaller for distribution

---

## Migration Guide

### From v1.0.0 to v2.0.0

#### Breaking Changes
- Package name changed from `metapicpick` to `metapic`
- CLI command structure updated (new `stats` command)
- Data model structure enhanced (new fields added)

#### Migration Steps
1. **Update Installation**:
   ```bash
   pip uninstall metapicpick
   pip install -e ".[ui]"  # For GUI support
   ```

2. **Update Scripts**:
   ```bash
   # Old
   metapicpick extract samples/
   
   # New
   metapic extract samples/
   ```

3. **New Features**:
   ```bash
   # View statistics
   metapic stats
   
   # Launch GUI
   metapic-gui
   ```

#### Compatibility
- All existing NDJSON files are compatible
- CLI commands maintain backward compatibility where possible
- Data models are backward compatible with additional fields

---

## Development Notes

### Architecture Decisions
- **Pydantic v2**: Chosen for modern data validation and serialization
- **Typer**: Selected for beautiful CLI with automatic help generation
- **PySide6**: Upgraded from PyQt5 for better performance and modern Qt6 features
- **orjson**: Used for high-performance JSON processing
- **Plugin System**: Designed for extensibility and maintainability

### Performance Considerations
- **Batch Processing**: exiftool runs in batch mode for efficiency
- **Lazy Loading**: GUI components loaded on demand
- **Caching**: Metadata caching for repeated operations
- **Memory Management**: Optimized data structures for large collections

### Security Considerations
- **Input Validation**: All user inputs validated through Pydantic models
- **File Operations**: Safe file handling with proper error checking
- **External Dependencies**: exiftool execution with proper subprocess handling

---

## Future Roadmap

### Planned Features
- **Database Support**: SQLite integration for large-scale metadata storage
- **Web Interface**: Browser-based interface for remote access
- **API Server**: REST API for programmatic access
- **Cloud Integration**: Support for cloud storage providers
- **Advanced Analytics**: Machine learning-based metadata analysis
- **Plugin Marketplace**: Community-contributed parsers and extensions

### Performance Improvements
- **Parallel Processing**: Multi-threaded metadata extraction
- **Streaming**: Support for very large image collections
- **Caching**: Advanced caching strategies for better performance
- **Compression**: Metadata compression for storage efficiency

### Platform Support
- **Mobile Apps**: iOS and Android applications
- **Web Extensions**: Browser extensions for web-based workflows
- **Desktop Integration**: Native OS integration features
- **Cloud Deployment**: Containerized deployment options

---

## Contributing

See [HOWTO.md](HOWTO.md) for detailed contribution guidelines.

### Code Standards
- **Type Hints**: Required for all functions and classes
- **Documentation**: Comprehensive docstrings for all public APIs
- **Testing**: Unit tests for all new functionality
- **Style**: Black formatting and isort import organization

### Release Process
1. **Version Bump**: Update version in pyproject.toml
2. **Changelog**: Update this file with new changes
3. **Build**: Test build process with PyInstaller
4. **Release**: Create GitHub release with executables
5. **Documentation**: Update documentation as needed

---

**MetaPic Enhanced v2.0** - *The Ultimate AI Image Metadata Management Solution*

For questions or support, please open an issue on GitHub.

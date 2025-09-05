# MetaPicPick Enhanced v2.0 - Build Instructions

## 🚀 Quick Start

### For Users (Running from Source)
```bash
python launch_metapicpick.py
```

### For Distribution (Creating Executables)
```bash
# Production build (recommended for end users)
build_exe.bat

# Development build (with console output for debugging)
build_dev.bat
```

## 📋 Prerequisites

- **Python 3.7+** (Recommended: Python 3.11+)
- **PyQt5** - GUI framework
- **Pillow** - Image processing
- **piexif** - EXIF metadata handling

## 🔧 Detailed Build Process

### Option 1: Production Executable (Recommended)

1. **Run the main build script:**
   ```bash
   build_exe.bat
   ```

2. **What it does:**
   - Creates/activates virtual environment
   - Installs all required dependencies
   - Runs pre-build tests
   - Creates optimized executable with PyInstaller
   - Bundles all resources and dependencies

3. **Output:**
   - `dist/MetaPicPick_Enhanced/MetaPicPick_Enhanced.exe`
   - Complete folder ready for distribution

### Option 2: Development Build (For Debugging)

1. **Run the development build:**
   ```bash
   build_dev.bat
   ```

2. **Features:**
   - Faster build time
   - Console output for debugging
   - Single-file executable
   - Minimal dependencies

3. **Output:**
   - `dist_dev/MetaPicPick_Dev.exe`

### Option 3: Manual Setup (For Development)

1. **Create virtual environment:**
   ```bash
   python -m venv metapicpick_env
   metapicpick_env\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements_build.txt
   ```

3. **Run from source:**
   ```bash
   python launch_metapicpick.py
   ```

## 📁 Project Structure

```
MetaPicPick_V_1/
├── 📄 launch_metapicpick.py    # Main launcher
├── 📄 gui_main.py              # GUI implementation
├── 📄 build_exe.bat            # Production build script
├── 📄 build_dev.bat            # Development build script
├── 📄 verify_build.bat         # Build verification
├── 📄 organize_project.bat     # Project cleanup
│
├── 📂 config/                  # Configuration management
├── 📂 core/                    # Core application modules
├── 📂 parsers/                 # Parser plugins
├── 📂 utils/                   # Utility modules
├── 📂 tests/                   # Test files
├── 📂 docs/                    # Documentation
├── 📂 data/                    # Application data
├── 📂 logs/                    # Runtime logs
│
├── 📂 dist/                    # Production builds
├── 📂 dist_dev/                # Development builds
└── 📂 metapicpick_env/         # Virtual environment
```

## 🧪 Testing & Verification

### Automated Testing
```bash
# Run all verification tests
verify_build.bat

# Test specific components
verify_build.bat
# Then choose: 1=Quick Launch, 2=Imports, 3=Structure, 4=Config, 5=All
```

### Manual Testing
```bash
# Test from source
python launch_metapicpick.py

# Test production build (after building)
dist/MetaPicPick_Enhanced/MetaPicPick_Enhanced.exe

# Test development build (after building)  
dist_dev/MetaPicPick_Dev.exe
```

## 📦 Distribution

### For End Users
1. Build production executable: `build_exe.bat`
2. Zip the entire `dist/MetaPicPick_Enhanced/` folder
3. Distribute the ZIP file
4. Users extract and run `MetaPicPick_Enhanced.exe`

### System Requirements for End Users
- **Windows 10/11** (64-bit)
- **~100MB disk space**
- **No Python installation required** (self-contained)

## 🔍 Troubleshooting

### Build Issues

**Error: "Python not found"**
- Ensure Python 3.7+ is installed and in PATH
- Try: `python --version`

**Error: "pip not found"**  
- Reinstall Python with pip included
- Or manually install pip

**Error: "PyQt5 installation failed"**
- Try: `pip install --upgrade pip`
- Then: `pip install PyQt5`

**Error: "Build failed"**
- Check the build log output
- Ensure antivirus isn't blocking PyInstaller
- Try development build first: `build_dev.bat`

### Runtime Issues

**Error: "Failed to execute script"**
- Check logs in `logs/metapicpick.log`
- Verify all files are in executable directory
- Try running with `--debug` flag

**Error: "Missing modules"**
- Rebuild executable
- Check `requirements_build.txt` is complete

## 🛠️ Advanced Configuration

### Custom PyInstaller Options

Edit `build_config.spec` to customize:

```python
# Add custom files
datas=[
    ('my_custom_file.txt', '.'),
],

# Add hidden imports
hiddenimports=[
    'my_custom_module',
],

# Exclude modules to reduce size
excludes=[
    'unused_module',
],
```

### Build Optimization

**Reduce executable size:**
- Add more modules to `excludes` in spec file
- Use UPX compression (already enabled)
- Remove unnecessary data files

**Improve startup time:**
- Use `--onefile` for single executable
- Minimize imported modules at startup
- Use lazy loading where possible

## 📊 Build Statistics

**Typical build sizes:**
- Production build: ~150-200MB
- Development build: ~100-150MB
- Source code: ~5MB

**Build times:**
- Production build: 3-8 minutes
- Development build: 1-3 minutes
- Clean rebuild: Add 2-4 minutes

## 🆘 Support

For build issues:
1. Check `BUILD_INSTRUCTIONS.md` (this file)
2. Run `verify_build.bat` for diagnostics
3. Check logs in `logs/metapicpick.log`
4. Review error messages in build output

---

✨ **Ready to build? Run `build_exe.bat` and get started!** ✨

# Scripts Folder Cleanup Summary

## Removed Redundant Files

1. **run_tabbed.bat** - Removed (referenced non-existent `gui_main_tabbed.py`)
2. **MetaPicPick_Tabbed.spec** - Removed (for non-existent tabbed version)
3. **run_metapicpick.bat** - Removed (redundant with run.bat)

## Updated Scripts

### run.bat
- Simplified to run from scripts folder
- Changed to use new `metapicpick.py` launcher
- Added proper error handling

### build.bat
- Updated to work with new folder structure
- Removed obsolete tabbed version option
- Uses updated MetaPicPick.spec with correct paths

### setup.bat
- Updated to run from scripts folder
- Changed validation to use `tests/test_imports.py`
- Updated instructions for new structure

### package.bat
- Enhanced to create proper portable package
- Includes documentation in package
- Creates version-numbered ZIP files
- Adds a simple Run_MetaPicPick.bat in package

### MetaPicPick.spec
- Updated all paths for new folder structure
- Added all required folders to datas
- Updated hiddenimports with full module paths
- Corrected webpmux.exe location to tools folder

## Current Scripts Folder

Now contains only essential, updated scripts:
- **run.bat** - Run the application
- **build.bat** - Build standalone executable
- **setup.bat** - First-time setup
- **package.bat** - Create portable distribution
- **MetaPicPick.spec** - PyInstaller specification

## Usage

### To run MetaPicPick:
```batch
scripts\run.bat
```

### To build executable:
```batch
scripts\build.bat
```

### To create portable package:
```batch
scripts\build.bat       # First build the exe
scripts\package.bat     # Then package it
```

### For first-time setup:
```batch
scripts\setup.bat
```

All scripts now properly handle the new folder structure and work correctly from the scripts directory!

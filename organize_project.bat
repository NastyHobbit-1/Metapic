@echo off
REM MetaPicPick Enhanced - Project Organization Script
REM ==================================================

echo MetaPicPick Enhanced - Project Organization
echo ============================================
echo.
echo This script will:
echo   1. Clean up test files
echo   2. Organize documentation
echo   3. Remove build artifacts
echo   4. Show final project structure
echo.

set /p proceed="Proceed with organization? (y/n): "
if /i not "%proceed%"=="y" (
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo Step 1: Cleaning up test files...
echo ----------------------------------

REM Move test files to tests directory (if not already there)
if exist "test_*.py" (
    if not exist "tests\temp" mkdir "tests\temp"
    move "test_*.py" "tests\temp\" 2>nul
    echo ✓ Moved test files to tests\temp\
)

REM Clean up build artifacts
echo.
echo Step 2: Cleaning build artifacts...
echo -----------------------------------

if exist "__pycache__" rmdir /s /q "__pycache__" 2>nul
if exist "*.pyc" del /q "*.pyc" 2>nul
if exist "build" rmdir /s /q "build" 2>nul
if exist "build_dev" rmdir /s /q "build_dev" 2>nul
if exist "*.spec" (
    if not "%~1"=="keep-spec" (
        del /q "MetaPicPick_Dev.spec" 2>nul
        echo ✓ Cleaned temporary spec files
    )
)

REM Clean up pycache in subdirectories
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
echo ✓ Cleaned Python cache files

echo.
echo Step 3: Organizing documentation...
echo -----------------------------------

REM Ensure docs directory exists and contains important files
if not exist "docs\build" mkdir "docs\build"

REM Create a project info file
echo Creating project information file...
> "PROJECT_INFO.txt" (
    echo MetaPicPick Enhanced v2.0
    echo ==========================
    echo.
    echo A unified GUI application for extracting and managing AI image metadata.
    echo.
    echo Key Features:
    echo - Support for multiple AI image formats ^(Automatic1111, ComfyUI, NovelAI, General^)
    echo - Advanced metadata editing and validation
    echo - Statistics tracking and analysis
    echo - Batch processing capabilities
    echo - Tabbed interface with persistent layouts
    echo - Plugin-based parser architecture
    echo - Enhanced error handling and logging
    echo.
    echo Directory Structure:
    echo -------------------
    echo config/           - Configuration management
    echo core/            - Core application modules
    echo parsers/         - Metadata parser plugins
    echo utils/           - Utility functions and helpers
    echo docs/            - Documentation files
    echo tests/           - Test files and examples
    echo data/            - Application data ^(statistics, etc.^)
    echo logs/            - Application logs
    echo.
    echo Main Files:
    echo -----------
    echo launch_metapicpick.py    - Main application launcher
    echo gui_main.py             - GUI implementation
    echo build_exe.bat           - Build production executable
    echo build_dev.bat           - Build development executable
    echo requirements_build.txt  - Build dependencies
    echo build_config.spec       - PyInstaller configuration
    echo.
    echo Build Instructions:
    echo ------------------
    echo 1. Run 'build_exe.bat' to create production executable
    echo 2. Run 'build_dev.bat' for development/debugging build
    echo 3. Use 'python launch_metapicpick.py' to run from source
    echo.
    echo Generated: %date% %time%
)

echo ✓ Created PROJECT_INFO.txt

echo.
echo Step 4: Final project structure...
echo ----------------------------------

echo.
echo Current project organization:
echo.

tree /f /a | findstr /v "__pycache__" | findstr /v ".pyc"

echo.
echo ✓ Project organization completed!
echo.
echo Summary:
echo - Test files moved to tests\temp\
echo - Build artifacts cleaned
echo - Documentation organized
echo - PROJECT_INFO.txt created
echo.

set /p view_info="View PROJECT_INFO.txt? (y/n): "
if /i "%view_info%"=="y" (
    echo.
    type "PROJECT_INFO.txt"
)

echo.
pause

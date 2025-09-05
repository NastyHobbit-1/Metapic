@echo off
REM MetaPicPick Enhanced - Build Script for Windows Executable
REM ============================================================

echo MetaPicPick Enhanced v2.0 - Build Script
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist "metapicpick_env" (
    echo Creating virtual environment...
    python -m venv metapicpick_env
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call metapicpick_env\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install build requirements
echo Installing build requirements...
pip install -r requirements_build.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

REM Clean previous build
echo Cleaning previous build...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM Run tests to ensure everything works
echo.
echo Running basic tests...
python check_deps.py
if errorlevel 1 (
    echo ERROR: Pre-build tests failed
    pause
    exit /b 1
)

REM Build the executable
echo.
echo Building executable with PyInstaller...
echo This may take several minutes...
echo.

pyinstaller build_config.spec --clean --noconfirm
if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

REM Verify the build
echo.
echo Verifying build...
if exist "dist\MetaPicPick_Enhanced\MetaPicPick_Enhanced.exe" (
    echo ✓ Executable created successfully!
    echo.
    echo Build completed! Your executable is located at:
    echo   dist\MetaPicPick_Enhanced\MetaPicPick_Enhanced.exe
    echo.
    echo You can distribute the entire 'dist\MetaPicPick_Enhanced' folder.
    echo.
    
    REM Get folder size
    for /f "tokens=3" %%i in ('dir "dist\MetaPicPick_Enhanced" /-c ^| find "bytes"') do set size=%%i
    echo Folder size: %size% bytes
    echo.
    
    REM Ask if user wants to test the executable
    set /p test_run="Would you like to test run the executable? (y/n): "
    if /i "%test_run%"=="y" (
        echo.
        echo Starting executable for testing...
        start "" "dist\MetaPicPick_Enhanced\MetaPicPick_Enhanced.exe"
        echo.
        echo Executable started. Check if it loads correctly.
    )
    
) else (
    echo ERROR: Executable not found after build
    exit /b 1
)

echo.
echo Build process completed successfully!
echo.
pause

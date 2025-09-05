@echo off
REM MetaPicPick Enhanced - Quick Development Build
REM ===============================================

echo MetaPicPick Enhanced - Development Build
echo =========================================
echo.
echo This script creates a faster development build with console output for debugging.
echo.

REM Activate virtual environment if it exists
if exist "metapicpick_env\Scripts\activate.bat" (
    echo Activating virtual environment...
    call metapicpick_env\Scripts\activate.bat
) else (
    echo No virtual environment found. Using system Python.
    echo Run build_exe.bat first to set up the environment.
    echo.
)

REM Quick dependency check
echo Checking dependencies...
python check_deps.py
if errorlevel 1 (
    pause
    exit /b 1
)

REM Clean previous dev build
if exist "dist_dev" rmdir /s /q "dist_dev"

REM Build development version (with console, faster build)
echo.
echo Building development executable...
echo.

pyinstaller ^
    --onefile ^
    --console ^
    --name "MetaPicPick_Dev" ^
    --distpath "dist_dev" ^
    --workpath "build_dev" ^
    --specpath "." ^
    --add-data "tag_blacklists.json;." ^
    --add-data "tag_consolidation_rules.json;." ^
    --add-data "config;config" ^
    --add-data "utils;utils" ^
    --add-data "core;core" ^
    --add-data "parsers;parsers" ^
    --add-data "data;data" ^
    --hidden-import "PyQt5.QtCore" ^
    --hidden-import "PyQt5.QtGui" ^
    --hidden-import "PyQt5.QtWidgets" ^
    --hidden-import "PIL.Image" ^
    --hidden-import "piexif" ^
    launch_metapicpick.py

if errorlevel 1 (
    echo ERROR: Development build failed
    pause
    exit /b 1
)

REM Check if executable was created
if exist "dist_dev\MetaPicPick_Dev.exe" (
    echo.
    echo ✓ Development build completed successfully!
    echo   Location: dist_dev\MetaPicPick_Dev.exe
    echo.
    echo This version includes console output for debugging.
    echo.
    
    REM Ask if user wants to run it
    set /p run_dev="Run the development executable now? (y/n): "
    if /i "%run_dev%"=="y" (
        echo.
        echo Starting development executable...
        "dist_dev\MetaPicPick_Dev.exe"
    )
) else (
    echo ERROR: Development executable not created
    exit /b 1
)

echo.
pause

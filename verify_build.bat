@echo off
REM MetaPicPick Enhanced - Build Verification Script
REM ================================================

echo MetaPicPick Enhanced - Build Verification
echo ==========================================
echo.
echo This script will verify that builds work correctly.
echo.

REM Check what builds are available
echo Checking available builds...
echo.

set has_prod=0
set has_dev=0

if exist "dist\MetaPicPick_Enhanced\MetaPicPick_Enhanced.exe" (
    echo ✓ Production build found: dist\MetaPicPick_Enhanced\MetaPicPick_Enhanced.exe
    set has_prod=1
) else (
    echo ✗ Production build not found
)

if exist "dist_dev\MetaPicPick_Dev.exe" (
    echo ✓ Development build found: dist_dev\MetaPicPick_Dev.exe
    set has_dev=1
) else (
    echo ✗ Development build not found
)

if %has_prod%==0 if %has_dev%==0 (
    echo.
    echo No builds found. Please run:
    echo   build_exe.bat     - for production build
    echo   build_dev.bat     - for development build
    echo.
    pause
    exit /b 1
)

echo.
echo Available verification tests:
echo 1. Quick launch test ^(5 second timeout^)
echo 2. Import verification
echo 3. File structure check
echo 4. Configuration test
echo 5. All tests
echo.

set /p test_choice="Choose test (1-5): "

if "%test_choice%"=="1" goto quick_launch
if "%test_choice%"=="2" goto import_test  
if "%test_choice%"=="3" goto structure_test
if "%test_choice%"=="4" goto config_test
if "%test_choice%"=="5" goto all_tests

echo Invalid choice.
pause
exit /b 1

:quick_launch
echo.
echo Running quick launch test...
echo ----------------------------

if %has_prod%==1 (
    echo Testing production build...
    timeout /t 1 >nul
    start /wait /b cmd /c "timeout /t 5 >nul & taskkill /f /im MetaPicPick_Enhanced.exe >nul 2>nul"
    start "" "dist\MetaPicPick_Enhanced\MetaPicPick_Enhanced.exe"
    timeout /t 6 >nul
    tasklist /fi "imagename eq MetaPicPick_Enhanced.exe" | find /i "MetaPicPick_Enhanced.exe" >nul
    if errorlevel 1 (
        echo ✓ Production build launched and closed correctly
    ) else (
        echo ⚠ Production build may still be running
        taskkill /f /im MetaPicPick_Enhanced.exe >nul 2>nul
    )
)

if %has_dev%==1 (
    echo Testing development build...
    timeout /t 1 >nul
    start /wait /b cmd /c "timeout /t 5 >nul & taskkill /f /im MetaPicPick_Dev.exe >nul 2>nul"  
    start "" "dist_dev\MetaPicPick_Dev.exe"
    timeout /t 6 >nul
    tasklist /fi "imagename eq MetaPicPick_Dev.exe" | find /i "MetaPicPick_Dev.exe" >nul
    if errorlevel 1 (
        echo ✓ Development build launched and closed correctly
    ) else (
        echo ⚠ Development build may still be running
        taskkill /f /im MetaPicPick_Dev.exe >nul 2>nul
    )
)

echo.
echo Quick launch test completed.
goto end

:import_test
echo.
echo Running import verification test...
echo -----------------------------------

python -c "
print('Testing core imports...')
try:
    import sys
    from pathlib import Path
    
    # Test core dependencies
    from PyQt5.QtWidgets import QApplication
    from PIL import Image
    import piexif
    print('✓ External dependencies OK')
    
    # Test our modules
    sys.path.insert(0, '.')
    from utils.logger import logger
    from config.settings import get_config  
    from utils.plugin_manager import PluginManager
    from core.optimized_statistics_tracker import optimized_stats_tracker
    print('✓ MetaPicPick modules OK')
    
    # Test plugin loading
    pm = PluginManager('parsers')
    print(f'✓ Loaded {len(pm.plugins)} parser plugins')
    
    print('✓ All import tests passed!')
    
except Exception as e:
    print(f'✗ Import test failed: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
"

if errorlevel 1 (
    echo Import test failed!
) else (
    echo Import test passed!
)
goto end

:structure_test
echo.
echo Running file structure test...
echo ------------------------------

set missing_files=0

echo Checking required directories...
for %%d in (config core parsers utils docs tests data) do (
    if not exist "%%d" (
        echo ✗ Missing directory: %%d
        set /a missing_files+=1
    ) else (
        echo ✓ Directory found: %%d
    )
)

echo.
echo Checking required files...
for %%f in (launch_metapicpick.py gui_main.py requirements_build.txt build_config.spec) do (
    if not exist "%%f" (
        echo ✗ Missing file: %%f
        set /a missing_files+=1
    ) else (
        echo ✓ File found: %%f
    )
)

echo.
if %missing_files%==0 (
    echo ✓ File structure test passed!
) else (
    echo ✗ File structure test failed - %missing_files% missing files/directories
)
goto end

:config_test
echo.
echo Running configuration test...
echo -----------------------------

python -c "
try:
    from config.settings import get_config, get_display_settings, get_performance_settings
    
    # Test configuration access
    config = get_config('test_key', 'default_value')
    print(f'✓ Basic configuration access works: {config}')
    
    # Test display settings
    display = get_display_settings()
    print(f'✓ Display settings loaded: {len(display)} settings')
    
    # Test performance settings
    perf = get_performance_settings()  
    print(f'✓ Performance settings loaded: {len(perf)} settings')
    
    print('✓ Configuration test passed!')
    
except Exception as e:
    print(f'✗ Configuration test failed: {e}')
    exit(1)
"

if errorlevel 1 (
    echo Configuration test failed!
) else (
    echo Configuration test passed!
)
goto end

:all_tests
echo.
echo Running all verification tests...
echo =================================

call :import_test
call :structure_test  
call :config_test
call :quick_launch

echo.
echo All tests completed!

:end
echo.
echo Verification completed.
pause

@echo off
REM Build standalone executable with PyInstaller

echo Building MetaPicPick standalone executable...

REM Change to parent directory
cd ..

REM Check if virtual environment exists
if exist metapicpick_env\ (
    echo Activating virtual environment...
    call metapicpick_env\Scripts\activate.bat
)

REM Install PyInstaller if not already installed
echo Installing/updating PyInstaller...
pip install pyinstaller

REM Build the application
echo Building MetaPicPick...
pyinstaller scripts\MetaPicPick.spec

if %ERRORLEVEL% neq 0 (
    echo Build failed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Build completed successfully!
echo Executable located at: dist\MetaPicPick.exe
echo.
pause

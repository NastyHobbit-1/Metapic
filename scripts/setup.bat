@echo off
REM First-time setup for MetaPicPick

echo ================================================
echo MetaPicPick Setup
echo ================================================

REM Change to parent directory
cd ..

echo.
echo 1. Creating virtual environment...
python -m venv metapicpick_env

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to create virtual environment
    echo Make sure Python is installed and accessible
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo 2. Activating virtual environment...
call metapicpick_env\Scripts\activate.bat

echo.
echo 3. Installing dependencies...
pip install -r requirements.txt

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo 4. Validating installation...
python tests\test_imports.py

echo.
echo ================================================
echo Setup completed successfully!
echo ================================================
echo.
echo To run MetaPicPick:
echo   - Double-click scripts\run.bat
echo   - OR run: python metapicpick.py
echo.
echo To build executable:
echo   - Run: scripts\build.bat
echo.
pause

@echo off
REM Run MetaPicPick from scripts folder

cd ..
echo Starting MetaPicPick...
python metapicpick.py

if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit...
    pause > nul
) else (
    pause
)

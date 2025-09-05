@echo off
REM Run MetaPicPick
cd /d "%~dp0"
python metapicpick.py
if errorlevel 1 pause

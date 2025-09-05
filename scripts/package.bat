@echo off
REM Package MetaPicPick executable and documentation into a ZIP file

REM Change to parent directory
cd ..

set DIST_DIR=dist
set EXE_NAME=MetaPicPick.exe
set VERSION=1.0
set OUTPUT_ZIP=MetaPicPick_v%VERSION%_Portable.zip

REM Check if executable exists
if not exist "%DIST_DIR%\%EXE_NAME%" (
    echo ERROR: Executable %EXE_NAME% not found in %DIST_DIR%
    echo Please run build.bat first
    pause
    exit /b 1
)

echo Creating portable package...

REM Create a temp folder for packaging
set TEMP_DIR=MetaPicPick_Portable
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"

REM Copy executable
echo Copying executable...
copy "%DIST_DIR%\%EXE_NAME%" "%TEMP_DIR%\"

REM Copy documentation
echo Copying documentation...
copy "README.md" "%TEMP_DIR%\README.txt"
copy "requirements.txt" "%TEMP_DIR%\"
mkdir "%TEMP_DIR%\docs"
copy "docs\*.md" "%TEMP_DIR%\docs\"

REM Create a simple run batch file
echo @echo off > "%TEMP_DIR%\Run_MetaPicPick.bat"
echo start MetaPicPick.exe >> "%TEMP_DIR%\Run_MetaPicPick.bat"

REM Create ZIP archive
echo Creating ZIP archive...
powershell -Command "Compress-Archive -Path '%TEMP_DIR%' -DestinationPath '%OUTPUT_ZIP%' -Force"

REM Clean up temp folder
rmdir /s /q "%TEMP_DIR%"

echo.
echo ================================================
echo Packaging complete: %OUTPUT_ZIP%
echo ================================================
echo.
pause

@echo off
setlocal
title Building FileConverterPro Standalone EXE

echo ================================================================
echo           Building FileConverterPro Standalone EXE
echo ================================================================
echo.

cd /d "%~dp0"

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not found in PATH! Please install Python 3.10+ and try again.
    pause
    exit /b 1
)

echo [2/4] Ensuring required packages are installed...
python -m pip install --quiet -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install required packages from requirements.txt!
    pause
    exit /b 1
)

echo [3/4] Generating application icon (if missing)...
if not exist "icon.ico" (
    python create_icon.py
)

echo [4/4] Compiling with PyInstaller...
pyinstaller --clean FileConverterPro.spec
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Build failed! Check the log messages above.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo   SUCCESS! Standalone EXE generated at:
echo   %~dp0dist\FileConverterPro.exe
echo ================================================================
echo.
pause

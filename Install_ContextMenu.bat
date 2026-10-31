@echo off
echo ===================================================
echo   Installing FileConverterPro Right-Click Menu...
echo ===================================================
"%~dp0dist\FileConverterPro.exe" --register-menu
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] FileConverterPro is now available in your Windows right-click menu!
) else (
    echo.
    echo [ERROR] Failed to register menu.
)
pause

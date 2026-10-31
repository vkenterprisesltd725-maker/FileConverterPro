@echo off
echo =====================================================
echo   Uninstalling FileConverterPro Right-Click Menu...
echo =====================================================
"%~dp0dist\FileConverterPro.exe" --unregister-menu
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] FileConverterPro was removed from your Windows right-click menu!
) else (
    echo.
    echo [ERROR] Failed to unregister menu.
)
pause

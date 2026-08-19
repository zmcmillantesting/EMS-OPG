@echo off
setlocal

echo ============================================
echo  EMS-OPG Installer
echo ============================================
echo.
echo This installs EMS-OPG to your Windows user profile
echo and creates a shortcut on the Desktop.
echo.
pause

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install_windows.ps1"

if errorlevel 1 (
    echo.
    echo ============================================
    echo  Install FAILED - see the error above.
    echo ============================================
    pause >nul
    exit /b 1
)

echo.
echo ============================================
echo  Done. Press any key to close this window.
echo ============================================
pause >nul
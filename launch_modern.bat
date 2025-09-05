@echo off
echo =======================================
echo   Smart Shelf Monitor Pro - Launcher
echo =======================================
echo.
echo Starting the modern shelf monitoring system...
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Run the modern GUI
echo Loading Smart Shelf Monitor Pro...
python modern_gui.py

if errorlevel 1 (
    echo.
    echo An error occurred while running the application.
    echo Please check the console output above for details.
    echo.
    pause
)

echo.
echo Application closed.
pause

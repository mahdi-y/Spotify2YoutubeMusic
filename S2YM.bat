@echo off
title Spotify2YoutubeMusic Auto-Setup and Launcher
color 07

setlocal enabledelayedexpansion

REM Store the starting directory
set STARTDIR=%CD%

echo ========================================
echo    Spotify2YoutubeMusic Auto-Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check Python version (must be 3.8+)
for /f "tokens=2 delims= " %%v in ('python --version') do set PYVER=%%v
for /f "tokens=1,2 delims=." %%a in ("!PYVER!") do (
    set MAJOR=%%a
    set MINOR=%%b
)
if !MAJOR! LSS 3 (
    echo [ERROR] Python 3.8+ is required. Detected: !PYVER!
    pause
    exit /b 1
)
if !MAJOR! EQU 3 if !MINOR! LSS 8 (
    echo [ERROR] Python 3.8+ is required. Detected: !PYVER!
    pause
    exit /b 1
)

echo [OK] Python found: !PYVER!

REM Check if Git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git is not installed or not in PATH!
    echo.
    echo Two options:
    echo 1. Install Git from https://git-scm.com/download/win
    echo 2. Or download the ZIP file manually from GitHub
    pause
    exit /b 1
)

echo [OK] Git found
git --version
echo.

REM Check if directory exists
if exist "Spotify2YoutubeMusic" (
    echo [INFO] Found existing Spotify2YoutubeMusic directory
    echo [UPDATE] Pulling latest changes...
    cd Spotify2YoutubeMusic
    git pull origin master
    if errorlevel 1 (
        echo [WARN] Git pull failed, continuing with existing files...
    ) else (
        echo [OK] Successfully updated to latest version
    )
) else (
    echo [DOWNLOAD] Cloning repository...
    git clone https://github.com/mahdi-y/Spotify2YoutubeMusic.git
    if errorlevel 1 (
        echo [ERROR] Failed to clone repository!
        echo Please check your internet connection or download manually
        pause
        exit /b 1
    )
    echo [OK] Repository cloned successfully
    cd Spotify2YoutubeMusic
)

echo.
echo [SETUP] Setting up Python virtual environment...

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        cd /d "%STARTDIR%"
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    cd /d "%STARTDIR%"
    pause
    exit /b 1
)

echo [OK] Virtual environment activated
echo.

REM Check for requirements.txt
if not exist requirements.txt (
    echo [ERROR] requirements.txt not found!
    echo Please make sure you are in the correct directory.
    cd /d "%STARTDIR%"
    pause
    exit /b 1
)

REM Install/upgrade dependencies
echo [INSTALL] Installing/updating dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Failed to install some dependencies!
    echo Trying to continue anyway...
) else (
    echo [OK] All dependencies installed successfully
)

echo.
echo [LAUNCH] Starting Spotify2YoutubeMusic...
echo.
echo ========================================
echo    Setup Complete! Starting App...
echo ========================================
echo.

REM Start the application
python ui.py

echo.
echo [DONE] Thanks for using Spotify2YoutubeMusic!
echo You can re-run this file anytime to update and launch the app.
echo Press any key to exit...
pause >nul

REM Return to original directory
cd /d "%STARTDIR%"
endlocal
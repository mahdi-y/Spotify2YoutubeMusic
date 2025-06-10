#!/bin/bash

# Spotify2YoutubeMusic Auto-Setup and Launcher (macOS/Linux)

STARTDIR="$PWD"

echo "========================================"
echo "   Spotify2YoutubeMusic Auto-Setup"
echo "========================================"
echo

# Check Python 3.8+ is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3.8+ is not installed or not in PATH!"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

PYVER=$(python3 --version 2>&1 | awk '{print $2}')
MAJOR=$(echo "$PYVER" | cut -d. -f1)
MINOR=$(echo "$PYVER" | cut -d. -f2)

if [ "$MAJOR" -lt 3 ] || { [ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 8 ]; }; then
    echo "[ERROR] Python 3.8+ is required. Detected: $PYVER"
    exit 1
fi

echo "[OK] Python found: $PYVER"

# Check Git
if ! command -v git &> /dev/null; then
    echo "[ERROR] Git is not installed or not in PATH!"
    echo "Install Git with: sudo apt install git   OR   brew install git"
    exit 1
fi

echo "[OK] Git found: $(git --version)"
echo

# Clone or update repo
if [ -d "Spotify2YoutubeMusic" ]; then
    echo "[INFO] Found existing Spotify2YoutubeMusic directory"
    echo "[UPDATE] Pulling latest changes..."
    cd Spotify2YoutubeMusic || exit 1
    git pull origin master || echo "[WARN] Git pull failed, continuing with existing files..."
else
    echo "[DOWNLOAD] Cloning repository..."
    git clone https://github.com/mahdi-y/Spotify2YoutubeMusic.git || { echo "[ERROR] Failed to clone repository!"; exit 1; }
    echo "[OK] Repository cloned successfully"
    cd Spotify2YoutubeMusic || exit 1
fi

echo
echo "[SETUP] Setting up Python virtual environment..."

# Create venv if needed
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv || { echo "[ERROR] Failed to create virtual environment!"; cd "$STARTDIR"; exit 1; }
    echo "[OK] Virtual environment created"
else
    echo "[OK] Virtual environment already exists"
fi

# Activate venv
echo "Activating virtual environment..."
# shellcheck disable=SC1091
source .venv/bin/activate || { echo "[ERROR] Failed to activate virtual environment!"; cd "$STARTDIR"; exit 1; }
echo "[OK] Virtual environment activated"
echo

# Check for requirements.txt
if [ ! -f requirements.txt ]; then
    echo "[ERROR] requirements.txt not found!"
    cd "$STARTDIR"
    exit 1
fi

# Install dependencies
echo "[INSTALL] Installing/updating dependencies..."
python3 -m pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install some dependencies! Trying to continue anyway..."
else
    echo "[OK] All dependencies installed successfully"
fi

echo
echo "[LAUNCH] Starting Spotify2YoutubeMusic..."
echo "========================================"
echo "   Setup Complete! Starting App..."
echo "========================================"
echo

python3 ui.py

echo
echo "[DONE] Thanks for using Spotify2YoutubeMusic!"
echo "You can re-run this script anytime to update and launch the app."
read -n 1 -s -r -p "Press any key to exit..."

cd "$STARTDIR"
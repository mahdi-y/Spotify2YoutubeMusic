# Spotify ➡️ YouTube Music Playlist Copier

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Spotify API](https://img.shields.io/badge/Spotify-API-green?logo=spotify)
![YouTube Music](https://img.shields.io/badge/YouTube%20Music-API-red?logo=youtube)
![License](https://img.shields.io/badge/License-MIT-yellow)
![GitHub Repo stars](https://img.shields.io/github/stars/mahdi-y/Spotify2YoutubeMusic?style=social)


<p align="center">
  <img src="./S2YM.gif" width="700"/>
</p>

---

<p align="center">
  <img src="./s2ym.png" alt="Spotify2YoutubeMusic Logo" width="800"/>
</p>

### ✨ New: Easy Setup Scripts

- **S2YM.bat** (Windows) and **S2YM.sh** (macOS/Linux) now provide a one-step setup and launch experience.
- No need to manually clone the repo or install dependencies—just run the script!
- The scripts check for Python 3.8+, Git, set up a virtual environment, install all requirements, and launch the app.
- ASCII art and clear progress messages make the setup process friendlier and more visual.

---

## Table of Contents

1. [Introduction](#introduction)
2. [✨ What's New](#-whats-new)
3. [Features](#features)
4. [Requirements](#requirements)
5. [Installation](#installation)
6. [Usage](#usage)
7. [User Interface](#user-interface)
8. [Advanced Features](#advanced-features)
9. [Troubleshooting](#troubleshooting)
10. [Acknowledgments](#acknowledgments)
11. [License](#license)

---

## Introduction

**Spotify2YoutubeMusic** is a powerful Python tool that seamlessly transfers your music library from Spotify to YouTube Music. It features both a modern graphical interface and a command-line interface, making it easy to copy playlists, liked songs, and followed artists between platforms.

---

## ✨ What's New

### **Batch Size Control (NEW)**
- **Adjustable Batch Size:** You can now set how many tracks are processed together (1–20) using a slider in the main interface.
- **Quick Presets:** Instantly set Safe, Balanced, Fast, or Max batch sizes with one click.
- **Live Guidance:** Color-coded descriptions help you pick the best setting for your connection and reliability needs.

### **Smart Resume System**
- **Automatic Header Expiration Detection:** Detects when YouTube Music headers expire and pauses gracefully.
- **Progress Saving:** Automatically saves progress after each batch, not just on errors.
- **Seamless Resume:** After updating expired headers, transfers resume exactly where they left off at the batch level.

### **Real-time Progress Tracking**
- **Batch-level Progress:** Shows detailed progress for each batch being processed and verified.
- **Live Status Updates:** Real-time feedback on search, add, and verification operations.
- **Success Rate Reporting:** Shows exact transfer success rates and detailed logs of any failed tracks.

### **Improved Verification**
- **Whole Playlist Verification:** After any interruption, the app verifies all tracks that should be in the playlist, not just those added after resuming, for accurate success reporting.

### **API Management**
- **Dedicated Quota Testing:** New "Test API Quota" functionality to check quotas without running transfers.
- **Intelligent Quota Detection:** Correctly distinguishes between real quota exhaustion and YouTube Music backend delays.
- **Header Validation:** Real-time validation of YouTube Music headers before saving.

### **Improved Transfer Process**
- **Not Found Track Display:** All tracks that couldn't be found on YouTube Music are now displayed in the UI logs.
- **Backend Delay Handling:** Properly handles YouTube Music's playlist count delays (no more false quota warnings).
- **Optimized Timing:** Smart 3-second delays between batches to balance speed and reliability.

---

## Features

- **Playlist Transfer** - Copy individual or all playlists from Spotify to YouTube Music
- **Liked Songs Import** - Transfer all your Spotify liked songs to a dedicated playlist
- **Artist Following** - Subscribe to your followed Spotify artists on YouTube Music
- **Smart Duplicate Prevention** - Automatically detects existing playlists and only adds new songs
- **Incremental Updates** - Run multiple times without creating duplicates
- **Real-time Progress Tracking** - Visual progress bars and detailed status updates
- **Modern GUI Interface** - Beautiful, dark-themed graphical user interface
- **Cross-platform** - Works on Windows, Linux, and macOS
- **Resume Capability** - Automatically resume interrupted transfers
- **Header Expiration Detection** - Smart handling of expired YouTube Music headers
- **Batch Size Control** - Fine-tune reliability and speed for large playlists (NEW)

---

## Requirements

- **Python 3.8+**
- **Spotify API Credentials** (Client ID & Secret)
- **YouTube Music Browser Headers** (for authentication)
- **Internet Connection** (for API access)

### Required Python Packages:
- `spotipy` - Spotify Web API wrapper
- `ytmusicapi` - YouTube Music API wrapper
- `tqdm` - Progress bars
- `tkinter` - GUI framework (usually included with Python)

---

## Installation (Manual)

### 1. Clone the Repository

```bash
git clone https://github.com/mahdi-y/Spotify2YoutubeMusic.git
cd Spotify2YoutubeMusic
```

### 2. Set Up Virtual Environment (Recommended)

#### Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Linux/macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

### Quick Start

1. **Get Spotify API Credentials**
2. **Extract YouTube Music Headers**
3. **Run the Application**

### 1. Generate Spotify Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Create a new app
3. Note your **Client ID** and **Client Secret**
4. Set **Redirect URI** to: `http://127.0.0.1:8888/callback`
5. Enter credentials in the Settings dialog when prompted

### 2. Generate YouTube Music Headers

1. Open **Firefox** and navigate to [YouTube Music](https://music.youtube.com)
2. Log in to your account
3. Press **F12** to open Developer Tools
4. Go to **Network** tab
5. Click **Library** in YouTube Music
6. Filter by `/browse` and find a **POST** request
7. Right-click → Copy → Copy Request Headers
8. Paste headers in the Settings dialog

### 3. Run the Application

#### Graphical Interface (Recommended):
```bash
python ui.py
```

---

## User Interface

### Modern GUI Features

- **Dark Theme** - Easy on the eyes with modern styling
- **Tabbed Interface** - Organized sections for different transfer types
- **Real-time Progress** - Live progress bars and status updates
- **Output Logging** - Detailed transfer logs with clear indicators
- **Playlist Selection** - Choose specific playlists or transfer all at once
- **Settings Management** - Built-in credentials and headers management with validation
- **Batch Size Control** - Instantly adjust batch size with a slider and quick preset buttons (NEW)

### Batch Size Control (NEW)
- **Adjustable Batch Size:** Choose how many tracks are processed together (1–20) using a slider in the main interface.
- **Quick Presets:** Instantly set Safe, Balanced, Fast, or Max batch sizes with one click.
- **Live Guidance:** Color-coded descriptions help you pick the best setting for your connection and reliability needs.

### Playlists Tab
- Load and view all your Spotify playlists
- Select multiple playlists for transfer
- One-click "Copy All" functionality
- Real-time search progress with track names
- **Resume Support:** Automatically resumes interrupted transfers

### Liked Songs Tab
- Transfer all liked songs to YouTube Music
- Creates a dedicated "Liked Songs from Spotify" playlist
- Handles large libraries efficiently
- **Smart Batching:** Processes in batches for better reliability

### Artists Tab
- Subscribe to followed Spotify artists
- Batch processing for multiple artists
- Automatic matching and subscription

### Settings Dialog
- **Spotify Configuration:** Enter Client ID, Secret, and Redirect URI
- **YouTube Music Headers:** Paste raw browser headers with real-time validation
- **Header Testing:** Built-in header validation before saving
- **Built-in Instructions:** Step-by-step guides for getting credentials

---


## Troubleshooting

### Common Issues

**Header Expiration (New Handling)**
- Headers typically expire every 20-30 minutes
- The app now automatically detects expiration and pauses gracefully
- Progress is saved at the batch level, so you resume exactly where you left off
- Simply update headers in Settings and the transfer continues automatically

**Transfer Interruptions (Enhanced)**
- Resume functionality works at the batch level for maximum efficiency
- Check the `progress_*.json` files to see saved state

**Missing Tracks (Improved Display)**
- Missing tracks are now clearly displayed in the UI output log
- Each playlist shows exactly which tracks couldn't be found
- Some tracks may not be available on YouTube Music due to licensing
- Alternative versions might be found instead

**Backend Delays (No More False Warnings)**
- YouTube Music sometimes delays updating playlist track counts
- The app now correctly identifies this as a backend delay, not quota exhaustion
- Wait a few minutes (sometimes it may take a while) and check your playlist - the tracks should appear
- No longer shows misleading "quota exhaustion" messages for this issue

**Authentication Problems**
- **Spotify:** Verify Client ID, Secret, and Redirect URI in Settings
- **YouTube Music:** Re-extract headers if they expire or validation fails
- **Settings now validate headers in real-time before saving**
- Delete the `.cache` file if you get Spotify authentication errors

### New Features for Debugging

1. **Enhanced Logging:** More detailed output shows exactly what's happening at each step
2. **Progress Files:** Check `progress_*.json` files to see exactly where transfers stopped
3. **Header Validation:** Settings dialog now validates headers before saving

---

## File Structure

```
Spotify2YoutubeMusic/
├── copy_playlists.py      # Main script with CLI interface
├── ui.py                  # Modern GUI application
├── config.json           # Configuration file (auto-generated)
├── progress_*.json       # Progress files for resume functionality (auto-generated)
├── browser.json          # YouTube Music API config (auto-generated)
├── requirements.txt      # Python dependencies
├── S2YM.bat              # Windows auto-setup & launcher script (NEW)
├── S2YM.sh               # macOS/Linux auto-setup & launcher script (NEW)
├── README.md             # This file
└── LICENSE               # MIT License
```

---

## Contributing

We welcome contributions! Please feel free to:
- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

---

## Acknowledgments

- **[sigma67](https://github.com/sigma67/ytmusicapi)** - Creator of ytmusicapi
- **[Spotipy Team](https://spotipy.readthedocs.io/)** - Spotify Web API wrapper
- **Community Contributors** - Bug reports and feature suggestions

---

## License

This project is licensed under the [MIT License](LICENSE).

```
MIT License - Feel free to use, modify, and distribute
See LICENSE file for full details
```

---

## Disclaimer

This tool is for personal use only. Please respect the terms of service of both Spotify and YouTube Music. The developers are not responsible for any violations of these services' terms of use.

---

<div align="center">

### **Enjoy Your Music Everywhere!**

*Transfer your music library seamlessly between platforms with smart resume, verification, and progress tracking*

**Latest: Batch size control • Automatic resume on header expiration • Batch verification • Real-time progress tracking • Enhanced reliability • Easy setup scripts**

</div>


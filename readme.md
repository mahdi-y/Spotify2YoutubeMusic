# Spotify to YouTube Music Playlist Copier

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Troubleshooting](#troubleshooting)
7. [Acknowledgments](#acknowledgments)

## Introduction

This Python script allows you to copy playlists from Spotify to YouTube Music. It fetches your Spotify playlists, retrieves their tracks, searches for them on YouTube Music, and creates a new playlist on YouTube Music with the found tracks. This makes it easier to transfer your favorite music between platforms without manual effort.

## Features

- Batch import your Spotify playlists
- Import all playlists at once
- Import Liked Songs from Spotify
- Import Followed Artists from Spotify
- Progress bar

## Requirements

- Python 3.8+
- Spotify API credentials
- YouTube Music authentication headers
- Command Prompt (cmd) or PowerShell (for Windows users)
- Terminal (for Linux/macOS users)


## Installation

### Clone the Repository

```sh
git clone https://github.com/mahdi-y/Spotify2YoutubeMusic.git
```
```sh
cd Spotify2YoutubeMusic
```

### Set Up a Virtual Environment (Recommended)

##### For Linux/macOS:

```sh
python -m venv .venv
```
```sh
source .venv/bin/activate  
```
```sh
pip install -r requirements.txt
```

##### For Windows:

```sh
python -m venv .venv
```
```sh
.venv\Scripts\activate  
```
```sh
pip install -r requirements.txt
```

## Usage

### Generate Spotify Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
2. Create an app and obtain the **Client ID** and **Client Secret**.
3. Set the **Redirect URI** to `http://127.0.0.1:8888/callback`.
4. Check **Web API** in the section right under **Redirect URI**.
5. Replace the placeholders in the script with your credentials (In **copy_playlists.py** file).
   
    `SPOTIFY_CLIENT_ID = 'Your-Spotify-Client-ID'`

    `SPOTIFY_CLIENT_SECRET = 'Your-Spotify-Client-Secret'`

### Generate YouTube Music Credentials

1. Open YouTube Music in **Firefox** and log in.
2. Press **F12** or right-click and select **Inspect** to open the browser's developer tools.
3. Go to the **Network** tab and click on **Reload**.
4. Go back to YouTube Music's interface and click on **Library**.
5. Go to the **Network** tab again and filter requests by `/browse`.
6. Select a request and locate the **Request Headers** section (It must be a **POST** request and of **Status 200**).
7. Click the **RAW** toggle button to view raw headers.
8. Copy the content and paste it into `raw_headers.txt` in the project directory.

### Run the Script

```sh
python copy_playlists.py
```

Follow the on-screen instructions to select and copy a playlist, liked songs or followed artists.

## Troubleshooting

- If an error occurs related to **invalid YouTube Music credentials**, it might be because they expire after some time. You will need to regenerate the credentials by following the **Generate YouTube Music Credentials** steps again.

## Acknowledgments

Special thanks to **Sigma67** for developing [ytmusicapi](https://github.com/sigma67/ytmusicapi), which enables programmatic access to YouTube Music.


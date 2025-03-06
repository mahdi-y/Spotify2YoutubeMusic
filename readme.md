# Spotify to YouTube Music Playlist Copier

## Table of Contents
- [Spotify to YouTube Music Playlist Copier](#spotify-to-youtube-music-playlist-copier)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Features](#features)
  - [Requirements](#requirements)
    - [Python Packages](#python-packages)
    - [Generate Spotify Credentials](#generate-spotify-credentials)
    - [Generate YouTube Music Credentials](#generate-youtube-music-credentials)
  - [Installation](#installation)
    - [Clone the Repository](#clone-the-repository)
  - [Usage](#usage)
  - [Troubleshooting](#troubleshooting)
  - [Acknowledgments](#acknowledgments)

## Introduction
This Python script allows you to copy playlists from Spotify to YouTube Music. It fetches your Spotify playlists, retrieves their tracks, searches for them on YouTube Music, and creates a new playlist on YouTube Music with the found tracks. This makes it easier to transfer your favorite music between platforms without manual effort.

## Features

- Authenticate with Spotify and YouTube Music
- Fetch your Spotify playlists
- Search for tracks on YouTube Music
- Create a new playlist on YouTube Music
- Add matched tracks to the newly created YouTube Music playlist

## Requirements

Ensure you have the following dependencies installed:

### Python Packages

Install the required dependencies using:

```sh
pip install -r requirements.txt
```

**requirements.txt:**

```
spotipy
ytmusicapi
```

### Generate Spotify Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
2. Create an app and obtain the **Client ID** and **Client Secret**.
3. Set the **Redirect URI** to `http://127.0.0.1:8888/callback`.
4. Replace the placeholders in the script with your credentials.

### Generate YouTube Music Credentials

1. Open YouTube Music in **Firefox** and log in.
2. Press **F12** or right-click and select **Inspect** to open the browser's developer tools.
3. Go to the **Network** tab and filter requests by `/browse`.
4. Select a request and locate the **Request Headers** section.
5. Click the **RAW** toggle button to view raw headers.
6. Copy the content and paste it into `raw_headers.txt` in the project directory.

## Installation

### Clone the Repository

```sh
git clone https://github.com/mahdi-y/Spotify2YoutubeMusic.git
cd Spotify2YoutubeMusic
```

## Usage

Run the script using:

```sh
python copy_playlists.py
```

Follow the on-screen instructions to select and copy a playlist.

## Troubleshooting

- If an error occurs related to **invalid YouTube Music credentials**, it might be because they expire after some time. You will need to regenerate the credentials by following the **Generate YouTube Music Credentials** steps again.

## Acknowledgments

Special thanks to **Sigma67** for developing [ytmusicapi](https://github.com/sigma67/ytmusicapi), which enables programmatic access to YouTube Music.


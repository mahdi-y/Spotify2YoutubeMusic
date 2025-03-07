import spotipy
from spotipy.oauth2 import SpotifyOAuth
from ytmusicapi import YTMusic
import ytmusicapi
import time
import json
from ytmusicapi import setup

headers_file = "raw_headers.txt"

# === SPOTIFY CONFIGURATION ===
SPOTIFY_CLIENT_ID = 'Your-Spotify-Client-ID'
SPOTIFY_CLIENT_SECRET = 'Your-Spotify-Client-Secret'
SPOTIFY_REDIRECT_URI = 'http://127.0.0.1:8888/callback'
SPOTIFY_SCOPE = "playlist-read-private playlist-read-collaborative user-library-read user-follow-read"  # Added user-follow-read for followed artists

with open(headers_file, "r", encoding="utf-8") as file:
    headers_raw = file.read()
    
setup(filepath="browser.json", headers_raw=headers_raw)

# Authenticate with Spotify
sp_oauth = SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                        client_secret=SPOTIFY_CLIENT_SECRET,
                        redirect_uri=SPOTIFY_REDIRECT_URI,
                        scope=SPOTIFY_SCOPE)
sp = spotipy.Spotify(auth_manager=sp_oauth)

# === YOUTUBE MUSIC CONFIGURATION ===
YTMUSIC_HEADERS_FILE = 'browser.json'  # Path to your headers file
ytmusic = YTMusic(YTMUSIC_HEADERS_FILE)

# Function to list Spotify playlists
def list_spotify_playlists():
    results = sp.current_user_playlists()
    if results['items']:
        print("Your Playlists on Spotify:")
        playlists = []
        for idx, playlist in enumerate(results['items']):
            print(f"{idx + 1}. {playlist['name']} (ID: {playlist['id']})")
            playlists.append(playlist)
        return playlists
    else:
        print("No playlists found!")
        return []

# Function to fetch liked songs from Spotify
def get_spotify_liked_songs():
    liked_songs = []
    results = sp.current_user_saved_tracks()
    while results:
        for item in results['items']:
            track = item['track']
            if track:
                artist_name = track['artists'][0]['name']
                track_name = track['name']
                liked_songs.append(f"{artist_name} - {track_name}")
        # Handle pagination
        if results['next']:
            results = sp.next(results)
        else:
            break
    return liked_songs

# Function to fetch tracks from a Spotify playlist
def get_spotify_playlist_tracks(playlist_id):
    tracks = []
    results = sp.playlist_items(playlist_id)
    while results:
        for item in results['items']:
            track = item['track']
            if track:
                artist_name = track['artists'][0]['name']
                track_name = track['name']
                tracks.append(f"{artist_name} - {track_name}")
        # Handle pagination
        if results['next']:
            results = sp.next(results)
        else:
            break
    return tracks

# Function to create a YouTube Music playlist
def create_ytm_playlist(playlist_name):
    try:
        playlist_id = ytmusic.create_playlist(title=playlist_name, description="Copied from Spotify")
        print(f"Created YouTube Music playlist: {playlist_name} (ID: {playlist_id})")
        return playlist_id
    except Exception as e:
        print(f"Failed to create playlist: {playlist_name}")
        print(e)
        return None

# Function to search for a track on YouTube Music
def search_track_on_ytm(track_query):
    try:
        search_results = ytmusic.search(query=track_query, filter="songs")
        print(f"Search results for '{track_query}': {search_results}")  # Debugging
        if search_results:
            video_id = search_results[0]['videoId']
            return video_id
        else:
            print(f"No results found for: {track_query}")
            return None
    except Exception as e:
        print(f"Error searching for track: {track_query}")
        print(e)
        return None

# Function to add tracks to a YouTube Music playlist
def add_tracks_to_ytm_playlist(playlist_id, track_ids, batch_size=10, retry_attempts=3):
    try:
        # Split track IDs into smaller batches
        for i in range(0, len(track_ids), batch_size):
            batch = track_ids[i:i + batch_size]
            attempt = 0
            while attempt < retry_attempts:
                try:
                    # Attempt to add the batch
                    ytmusic.add_playlist_items(playlistId=playlist_id, videoIds=batch)
                    print(f"Added tracks {i + 1} to {i + len(batch)} to YouTube Music playlist.")
                    break  # Exit the retry loop if successful
                except Exception as e:
                    if "HTTP 409" in str(e):
                        print(f"Conflict error for tracks {i + 1} to {i + len(batch)}. Skipping...")
                        break  # Skip this batch if it causes a conflict
                    else:
                        attempt += 1
                        print(f"Attempt {attempt} failed for tracks {i + 1} to {i + len(batch)}. Retrying in 5 seconds...")
                        time.sleep(5)  # Wait before retrying
            else:
                print(f"Failed to add tracks {i + 1} to {i + len(batch)} after {retry_attempts} attempts.")
            
            # Add a delay between batches to avoid rate-limiting
            time.sleep(2)

    except Exception as e:
        print(f"Failed to add tracks to playlist ID: {playlist_id}")
        print(e)

# Function to fetch followed artists from Spotify
def get_spotify_followed_artists():
    followed_artists = []
    results = sp.current_user_followed_artists(limit=50)  # Fetch up to 50 artists at a time
    while results:
        for artist in results['artists']['items']:
            followed_artists.append(artist['name'])
        # Handle pagination
        if results['artists']['next']:
            results = sp.next(results['artists'])
        else:
            break
    return followed_artists

# Function to subscribe to artists on YouTube Music
def subscribe_to_ytm_artists(artist_names):
    for artist_name in artist_names:
        try:
            # Search for the artist on YouTube Music
            search_results = ytmusic.search(query=artist_name, filter="artists")
            if search_results:
                # Get the first result (most relevant artist)
                artist_id = search_results[0]['browseId']
                # Subscribe to the artist
                ytmusic.subscribe_artists([artist_id])
                print(f"Subscribed to artist: {artist_name} (ID: {artist_id})")
            else:
                print(f"No results found for artist: {artist_name}")
        except Exception as e:
            print(f"Failed to subscribe to artist: {artist_name}")
            print(e)

# Main function to copy playlists, liked songs, and followed artists
def copy_spotify_to_ytm():
    while True:  # Loop to allow the user to choose again after finishing
        # Ask user to choose whether to copy playlists, liked songs, or followed artists
        choice = input("Do you want to copy (1) Playlists, (2) Liked Songs, or (3) Followed Artists from Spotify? Enter 1, 2, or 3 (or type 'exit' to quit): ")

        if choice.lower() == 'exit':
            print("Exiting...")
            break  # Exit the loop and end the program

        if choice == "1":
            # Copy playlists
            spotify_playlists = list_spotify_playlists()
            if not spotify_playlists:
                return

            # Select a playlist to copy
            playlist_choice = int(input("Enter the number of the playlist you want to copy: ")) - 1
            selected_playlist = spotify_playlists[playlist_choice]
            playlist_name = selected_playlist['name']
            playlist_id = selected_playlist['id']

            # Fetch tracks from the selected Spotify playlist
            print(f"Fetching tracks from Spotify playlist: {playlist_name}")
            spotify_tracks = get_spotify_playlist_tracks(playlist_id)
            if not spotify_tracks:
                print("No tracks found in the selected playlist.")
                return

            # Create a new YouTube Music playlist
            ytm_playlist_id = create_ytm_playlist(playlist_name)
            if not ytm_playlist_id:
                return

            # Search for each track on YouTube Music and collect video IDs
            print("Searching for tracks on YouTube Music...")
            ytm_video_ids = []
            for track in spotify_tracks:
                video_id = search_track_on_ytm(track)
                if video_id:
                    ytm_video_ids.append(video_id)
                else:
                    print(f"Skipping track: {track}")

            # Debugging: Print collected video IDs
            print(f"Collected video IDs: {ytm_video_ids}")

            # Add the found tracks to the YouTube Music playlist
            if ytm_video_ids:
                add_tracks_to_ytm_playlist(ytm_playlist_id, ytm_video_ids)
            else:
                print("No tracks were found on YouTube Music.")

        elif choice == "2":
            # Copy liked songs
            liked_songs = get_spotify_liked_songs()
            if not liked_songs:
                print("No liked songs found on Spotify.")
                return

            # Create a new YouTube Music playlist
            playlist_name = "Liked Songs from Spotify"
            ytm_playlist_id = create_ytm_playlist(playlist_name)
            if not ytm_playlist_id:
                return

            # Search for each track on YouTube Music and collect video IDs
            print("Searching for liked songs on YouTube Music...")
            ytm_video_ids = []
            for track in liked_songs:
                video_id = search_track_on_ytm(track)
                if video_id:
                    ytm_video_ids.append(video_id)
                else:
                    print(f"Skipping track: {track}")

            # Debugging: Print collected video IDs
            print(f"Collected video IDs: {ytm_video_ids}")

            # Add the found tracks to the YouTube Music playlist
            if ytm_video_ids:
                add_tracks_to_ytm_playlist(ytm_playlist_id, ytm_video_ids)
            else:
                print("No liked songs were found on YouTube Music.")

        elif choice == "3":
            # Copy followed artists
            followed_artists = get_spotify_followed_artists()
            if not followed_artists:
                print("No followed artists found on Spotify.")
                return

            # Subscribe to the artists on YouTube Music
            print("Subscribing to artists on YouTube Music...")
            subscribe_to_ytm_artists(followed_artists)
            print("Finished subscribing to artists.")

if __name__ == "__main__":
    copy_spotify_to_ytm()
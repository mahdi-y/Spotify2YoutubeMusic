import spotipy
from spotipy.oauth2 import SpotifyOAuth
from ytmusicapi import YTMusic
import time
from ytmusicapi import setup
from tqdm import tqdm

headers_file = "raw_headers.txt"

# === SPOTIFY CONFIGURATION ===
SPOTIFY_CLIENT_ID = 'Your-Spotify-Client-ID'
SPOTIFY_CLIENT_SECRET = 'Your-Spotify-Client-Secret'
SPOTIFY_REDIRECT_URI = 'http://127.0.0.1:8888/callback'
SPOTIFY_SCOPE = "playlist-read-private playlist-read-collaborative user-library-read user-follow-read"  

with open(headers_file, "r", encoding="utf-8") as file:
    headers_raw = file.read()
    
setup(filepath="browser.json", headers_raw=headers_raw)

sp_oauth = SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                        client_secret=SPOTIFY_CLIENT_SECRET,
                        redirect_uri=SPOTIFY_REDIRECT_URI,
                        scope=SPOTIFY_SCOPE)
sp = spotipy.Spotify(auth_manager=sp_oauth)

YTMUSIC_HEADERS_FILE = 'browser.json'  
ytmusic = YTMusic(YTMUSIC_HEADERS_FILE)

def get_ytm_playlist_by_name(playlist_name):
    """
    Returns the playlist dict if a playlist with the given name exists, else None.
    """
    try:
        playlists = ytmusic.get_library_playlists()
        for playlist in playlists:
            if playlist['title'].strip().lower() == playlist_name.strip().lower():
                return playlist
        return None
    except Exception as e:
        print(f"Error fetching YouTube Music playlists: {e}")
        return None

def get_ytm_playlist_song_video_ids(playlist_id):
    """
    Returns a set of videoIds for all songs in the given YouTube Music playlist.
    """
    video_ids = set()
    try:
        playlist = ytmusic.get_playlist(playlist_id, limit=10000)
        for track in playlist.get('tracks', []):
            if track and 'videoId' in track:
                video_ids.add(track['videoId'])
    except Exception as e:
        print(f"Error fetching playlist tracks: {e}")
    return video_ids

def create_or_get_ytm_playlist(playlist_name):
    """
    Returns (playlist_id, already_exists)
    """
    existing = get_ytm_playlist_by_name(playlist_name)
    if existing:
        print(f"Found existing YouTube Music playlist: {playlist_name} (ID: {existing['playlistId']})")
        return existing['playlistId'], True
    else:
        playlist_id = create_ytm_playlist(playlist_name)
        return playlist_id, False

def list_spotify_playlists():
    playlists = []
    limit = 50  
    offset = 0

    while True:
        results = sp.current_user_playlists(limit=limit, offset=offset)
        if not results['items']:
            break  

        for idx, playlist in enumerate(results['items'], start=len(playlists) + 1):
            print(f"{idx}. {playlist['name']} (ID: {playlist['id']})")
            playlists.append(playlist)

        offset += limit  

    if not playlists:
        print("No playlists found!")
    
    return playlists

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
        if results['next']:
            results = sp.next(results)
        else:
            break
    return liked_songs

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
        if results['next']:
            results = sp.next(results)
        else:
            break
    return tracks

def create_ytm_playlist(playlist_name):
    try:
        playlist_id = ytmusic.create_playlist(title=playlist_name, description="Copied from Spotify")
        print(f"Created YouTube Music playlist: {playlist_name} (ID: {playlist_id})")
        return playlist_id
    except Exception as e:
        print(f"Failed to create playlist: {playlist_name}")
        print(e)
        return None

def search_track_on_ytm(track_query):
    try:
        search_results = ytmusic.search(query=track_query, filter="songs")
        if search_results:
            video_id = search_results[0]['videoId']
            return video_id
        else:
            return None
    except Exception as e:
        print(f"Error searching for track: {track_query}")
        print(e)
        return None

def add_tracks_to_ytm_playlist(playlist_id, track_ids, batch_size=10, retry_attempts=3):
    try:        
        for i in range(0, len(track_ids), batch_size):
            batch = track_ids[i:i + batch_size]
            attempt = 0
            while attempt < retry_attempts:
                try:                    
                    ytmusic.add_playlist_items(playlistId=playlist_id, videoIds=batch)
                    print(f"Added tracks {i + 1} to {i + len(batch)} to YouTube Music playlist.")
                    break  
                except Exception as e:
                    if "HTTP 409" in str(e):
                        print(f"Conflict error for tracks {i + 1} to {i + len(batch)}. Skipping...")
                        break  
                    else:
                        attempt += 1
                        print(f"Attempt {attempt} failed for tracks {i + 1} to {i + len(batch)}. Retrying in 5 seconds...")
                        time.sleep(5)  
            else:
                print(f"Failed to add tracks {i + 1} to {i + len(batch)} after {retry_attempts} attempts.")
                        
            time.sleep(2)

    except Exception as e:
        print(f"Failed to add tracks to playlist ID: {playlist_id}")
        print(e)

def get_spotify_followed_artists():
    followed_artists = []
    results = sp.current_user_followed_artists(limit=50)  
    while results:
        for artist in results['artists']['items']:
            followed_artists.append(artist['name'])        
        if results['artists']['next']:
            results = sp.next(results['artists'])
        else:
            break
    return followed_artists

def subscribe_to_ytm_artists(artist_names):
    for artist_name in artist_names:
        try:            
            search_results = ytmusic.search(query=artist_name, filter="artists")
            if search_results:                
                artist_id = search_results[0]['browseId']                
                ytmusic.subscribe_artists([artist_id])
                print(f"Subscribed to artist: {artist_name} (ID: {artist_id})")
            else:
                print(f"No results found for artist: {artist_name}")
        except Exception as e:
            print(f"Failed to subscribe to artist: {artist_name}")
            print(e)

def parse_playlist_selection(selection_input, max_playlists):
    """
    Parse user input for playlist selection including range support.
    Examples:
    - "1,3,5" -> [0, 2, 4]
    - "1-5" -> [0, 1, 2, 3, 4]
    - "1-3,7,9-10" -> [0, 1, 2, 6, 8, 9]
    """
    selected_indices = set()
    
    # Split by comma
    parts = [p.strip() for p in selection_input.split(",")]
    
    for part in parts:
        # Check if it's a range (contains "-")
        if "-" in part:
            try:
                start, end = map(int, part.split("-"))
                if start < 1 or end > max_playlists or start > end:
                    print(f"Invalid range: {part}. Valid range is 1-{max_playlists}.")
                    continue
                # Add all indices in the range (adjusting for 0-based indexing)
                for i in range(start-1, end):
                    selected_indices.add(i)
            except ValueError:
                print(f"Invalid range format: {part}")
        else:
            # Handle single number
            try:
                idx = int(part) - 1  # Convert to 0-based index
                if idx < 0 or idx >= max_playlists:
                    print(f"Invalid playlist number: {part}")
                    continue
                selected_indices.add(idx)
            except ValueError:
                print(f"Invalid input: {part}")
    
    return sorted(list(selected_indices))

def copy_spotify_to_ytm():
    while True:
        choice = input("Do you want to copy (1) Playlists, (2) Liked Songs, or (3) Followed Artists from Spotify? Enter 1, 2, or 3 (or type 'exit' to quit): ")
        if choice.lower() == 'exit':
            print("Exiting...")
            break
        
        if choice == "1":            
            spotify_playlists = list_spotify_playlists()
            if not spotify_playlists:
                return
            copy_all = input("Do you want to copy all playlists? (yes/no): ").strip().lower()
            if copy_all == 'yes':                
                for playlist in spotify_playlists:
                    playlist_name = playlist['name']
                    playlist_id = playlist['id']                    
                    print(f"Fetching tracks from Spotify playlist: {playlist_name}")
                    spotify_tracks = get_spotify_playlist_tracks(playlist_id)
                    if not spotify_tracks:
                        print(f"No tracks found in the playlist: {playlist_name}. Skipping this playlist.")
                        continue
                    
                    # Check if playlist already exists
                    ytm_playlist_id, already_exists = create_or_get_ytm_playlist(playlist_name)
                    if not ytm_playlist_id:
                        continue
                    
                    # Get existing songs if playlist already exists
                    existing_video_ids = set()
                    if already_exists:
                        print("Checking for already existing songs in the YouTube Music playlist...")
                        existing_video_ids = get_ytm_playlist_song_video_ids(ytm_playlist_id)
                    
                    print(f"Searching for tracks from {playlist_name} on YouTube Music...")
                    ytm_video_ids = []
                    not_found_tracks = [] 
                    for track in tqdm(spotify_tracks, desc=f"Processing {playlist_name}", unit="track"):
                        video_id = search_track_on_ytm(track)
                        if video_id:
                            if video_id not in existing_video_ids:
                                ytm_video_ids.append(video_id)
                        else:
                            not_found_tracks.append(track) 
                            print(f"Skipping track: {track}")
                    
                    if ytm_video_ids:
                        add_tracks_to_ytm_playlist(ytm_playlist_id, ytm_video_ids)
                        print(f"Added {len(ytm_video_ids)} new tracks to playlist: {playlist_name}")
                    else:
                        print(f"No new tracks to add for playlist: {playlist_name}")
                    
                    if not_found_tracks:
                        print(f"\nTracks not found on YouTube Music for playlist '{playlist_name}':")
                        for track in not_found_tracks:
                            print(f"- {track}")
                        print()
            else:
                selection_input = input("Enter the numbers of the playlists you want to copy (comma-separated with range support, e.g., 1,3-5,8): ")
                selected_indices = parse_playlist_selection(selection_input, len(spotify_playlists))
                
                if not selected_indices:
                    print("No valid playlists selected.")
                    continue
                    
                print(f"Selected {len(selected_indices)} playlists.")
                for idx in selected_indices:
                    selected_playlist = spotify_playlists[idx]
                    playlist_name = selected_playlist['name']
                    playlist_id = selected_playlist['id']
                    print(f"Fetching tracks from Spotify playlist: {playlist_name}")
                    spotify_tracks = get_spotify_playlist_tracks(playlist_id)
                    if not spotify_tracks:
                        print("No tracks found in the selected playlist.")
                        continue
                    
                    # Check if playlist already exists
                    ytm_playlist_id, already_exists = create_or_get_ytm_playlist(playlist_name)
                    if not ytm_playlist_id:
                        continue
                    
                    # Get existing songs if playlist already exists
                    existing_video_ids = set()
                    if already_exists:
                        print("Checking for already existing songs in the YouTube Music playlist...")
                        existing_video_ids = get_ytm_playlist_song_video_ids(ytm_playlist_id)
                    
                    print("Searching for tracks on YouTube Music...")
                    ytm_video_ids = []
                    not_found_tracks = []  
                    for track in tqdm(spotify_tracks, desc=f"Processing {playlist_name}", unit="track"):
                        video_id = search_track_on_ytm(track)
                        if video_id:
                            if video_id not in existing_video_ids:
                                ytm_video_ids.append(video_id)
                        else:
                            not_found_tracks.append(track)  
                            print(f"Skipping track: {track}")
                    
                    if ytm_video_ids:
                        add_tracks_to_ytm_playlist(ytm_playlist_id, ytm_video_ids)
                        print(f"Added {len(ytm_video_ids)} new tracks to playlist: {playlist_name}")
                    else:
                        print(f"No new tracks to add for playlist: {playlist_name}")
                    
                    if not_found_tracks:
                        print(f"\nTracks not found on YouTube Music for playlist '{playlist_name}':")
                        for track in not_found_tracks:
                            print(f"- {track}")
                        print()
                        
        elif choice == "2":
            liked_songs = get_spotify_liked_songs()
            if not liked_songs:
                print("No liked songs found on Spotify.")
                return
            playlist_name = "Liked Songs from Spotify"
            
            # Check if playlist already exists
            ytm_playlist_id, already_exists = create_or_get_ytm_playlist(playlist_name)
            if not ytm_playlist_id:
                return

            # Get existing songs in the playlist to avoid duplicates
            existing_video_ids = set()
            if already_exists:
                print("Checking for already existing songs in the YouTube Music playlist...")
                existing_video_ids = get_ytm_playlist_song_video_ids(ytm_playlist_id)

            print("Searching for liked songs on YouTube Music...")
            ytm_video_ids = []
            not_found_tracks = []  
            for track in tqdm(liked_songs, desc="Processing Liked Songs", unit="track"):
                video_id = search_track_on_ytm(track)
                if video_id:
                    if video_id not in existing_video_ids:
                        ytm_video_ids.append(video_id)
                else:
                    not_found_tracks.append(track) 
                    print(f"Skipping track: {track}")
            
            if ytm_video_ids:
                add_tracks_to_ytm_playlist(ytm_playlist_id, ytm_video_ids)
                print(f"Added {len(ytm_video_ids)} new liked songs to YouTube Music.")
            else:
                print("No new liked songs to add to YouTube Music.")

            if not_found_tracks:
                print(f"\nLiked songs not found on YouTube Music:")
                for track in not_found_tracks:
                    print(f"- {track}")
                print()
                
        elif choice == "3":
            followed_artists = get_spotify_followed_artists()
            if not followed_artists:
                print("No followed artists found on Spotify.")
                return
            print("Subscribing to artists on YouTube Music...")
            subscribe_to_ytm_artists(followed_artists)
            print("Finished subscribing to artists.")

if __name__ == "__main__":
    copy_spotify_to_ytm()
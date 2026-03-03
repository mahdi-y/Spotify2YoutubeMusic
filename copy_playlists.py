import spotipy
from spotipy.oauth2 import SpotifyOAuth
from ytmusicapi import YTMusic
import time
from ytmusicapi import setup
from tqdm import tqdm
import json
import os

sp = None
ytmusic = None

def load_config():
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r") as f:
                return json.load(f)
        except:
            pass
    return None

def validate_youtube_headers(headers_text):
    if not headers_text or not headers_text.strip():
        return False, "Headers are empty"
    
    headers = headers_text.strip()
    
    required_fields = ['cookie', 'user-agent']
    headers_lower = headers.lower()
    
    missing_fields = []
    for field in required_fields:
        if field not in headers_lower:
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"Missing required header fields: {', '.join(missing_fields)}"
    
    lines = headers.split('\n')
    valid_lines = 0
    for line in lines:
        line = line.strip()
        if line and ':' in line:
            valid_lines += 1
    
    if valid_lines < 5:
        return False, "Headers don't appear to be in the correct format"
    
    return True, "Headers appear valid"

def initialize_clients(config_data=None):
    global sp, ytmusic
    
    if config_data is None:
        config_data = load_config()
    
    if not config_data:
        print("No configuration found. Please run the UI to set up credentials.")
        return False
    
    try:
        sp_oauth = SpotifyOAuth(
            client_id=config_data["spotify_client_id"],
            client_secret=config_data["spotify_client_secret"],
            redirect_uri=config_data["spotify_redirect_uri"],
            scope="playlist-read-private playlist-read-collaborative user-library-read user-follow-read"
        )
        sp = spotipy.Spotify(auth_manager=sp_oauth)
        
        if config_data.get("youtube_headers"):
            try:
                headers = config_data["youtube_headers"].strip()
                
                if not headers:
                    print("YouTube Music headers are empty")
                    ytmusic = None
                    return False
                
                required_fields = ['cookie', 'user-agent']
                headers_lower = headers.lower()
                if not any(field in headers_lower for field in required_fields):
                    print("YouTube Music headers appear to be invalid - missing required fields")
                    ytmusic = None
                    return False
                
                with open("raw_headers.txt", "w", encoding="utf-8") as f:
                    f.write(headers)
                
                try:
                    setup(filepath="browser.json", headers_raw=headers)
                except Exception as setup_error:
                    print(f"Failed to parse headers: {setup_error}")
                    print("Please check that your headers are in the correct format")
                    ytmusic = None
                    return False
                
                ytmusic = YTMusic("browser.json")
                
                try:
                    test_result = ytmusic.get_library_playlists(limit=1)
                    if test_result is None:
                        print("YouTube Music client test failed - headers may be expired")
                        ytmusic = None
                        return False
                except Exception as test_error:
                    print(f"YouTube Music connection test failed: {test_error}")
                    ytmusic = None
                    return False
                    
            except Exception as e:
                print(f"Failed to initialize YouTube Music client: {e}")
                ytmusic = None
                return False
        else:
            print("No YouTube Music headers provided")
            return False
        
        return True
        
    except Exception as e:
        print(f"Error initializing clients: {e}")
        return False

def get_spotify_client():
    global sp
    if sp is None:
        initialize_clients()
    return sp

def get_ytmusic_client():
    global ytmusic
    if ytmusic is None:
        if not initialize_clients():
            return None
    return ytmusic

initialize_clients()

def get_ytm_playlist_by_name(playlist_name):
    try:
        playlists = get_ytmusic_client().get_library_playlists()
        for playlist in playlists:
            if playlist['title'].strip().lower() == playlist_name.strip().lower():
                return playlist
        return None
    except Exception as e:
        print(f"Error fetching YouTube Music playlists: {e}")
        return None

def fetch_all_ytm_playlists():
    try:
        client = get_ytmusic_client()
        if not client:
            return {}
        
        playlists = client.get_library_playlists(limit=None)
        playlist_map = {}
        
        for p in playlists:
            title_key = p['title'].strip().lower()
            playlist_map[title_key] = p
            
        return playlist_map
    except Exception as e:
        print(f"Error fetching YTM playlists: {e}")
        return {}

def get_ytm_playlist_song_video_ids(playlist_id):
    video_ids = set()
    try:
        playlist = get_ytmusic_client().get_playlist(playlist_id, limit=10000)
        for track in playlist.get('tracks', []):
            if track and 'videoId' in track:
                video_ids.add(track['videoId'])
    except Exception as e:
        print(f"Error fetching playlist tracks: {e}")
    return video_ids

def _is_auth_error(exception):
    error_str = str(exception).lower()
    return "401" in error_str or "403" in error_str or "unauthorized" in error_str

def _normalize_delay_seconds(delay_seconds, default=1.5):
    try:
        delay = float(delay_seconds)
        return max(0.0, delay)
    except (TypeError, ValueError):
        return default

def _deduplicate_video_ids(video_ids):
    unique_video_ids = []
    seen = set()
    for video_id in video_ids:
        if not video_id or video_id in seen:
            continue
        seen.add(video_id)
        unique_video_ids.append(video_id)
    return unique_video_ids

def _extract_like_targets_from_playlist(playlist_id, ytm_client):
    targets = []
    playlist = ytm_client.get_playlist(playlist_id, limit=None)
    for track in playlist.get('tracks', []):
        if not track:
            continue
        video_id = track.get('videoId')
        if not video_id:
            continue
        title = track.get('title', 'Unknown track')
        artist_names = ", ".join(
            artist.get('name', '') for artist in track.get('artists', []) if artist.get('name')
        )
        targets.append({
            "video_id": video_id,
            "title": title,
            "artists": artist_names
        })
    return targets

def like_tracks_on_ytm(
    track_video_ids=None,
    playlist_id=None,
    delay_seconds=1.5,
    progress_callback=None,
    error_callback=None,
    control_callback=None,
    ytm_client=None
):
    if track_video_ids is None and not playlist_id:
        raise ValueError("Either track_video_ids or playlist_id must be provided.")

    client = ytm_client if ytm_client is not None else get_ytmusic_client()
    if client is None:
        raise ValueError("YouTube Music client is not initialized.")

    targets = []
    if track_video_ids is not None:
        for video_id in _deduplicate_video_ids(track_video_ids):
            targets.append({
                "video_id": video_id,
                "title": "Unknown track",
                "artists": ""
            })

    if playlist_id:
        targets.extend(_extract_like_targets_from_playlist(playlist_id, client))

    unique_targets = []
    seen = set()
    for target in targets:
        video_id = target.get("video_id")
        if not video_id or video_id in seen:
            continue
        seen.add(video_id)
        unique_targets.append(target)

    total = len(unique_targets)
    like_delay = _normalize_delay_seconds(delay_seconds)

    result = {
        "total": total,
        "liked": 0,
        "failed": 0,
        "skipped": max(0, len(targets) - total),
        "cancelled": False,
        "failed_items": []
    }

    for idx, target in enumerate(unique_targets, start=1):
        if control_callback and not control_callback():
            result["cancelled"] = True
            break

        video_id = target["video_id"]
        title = target.get("title", "Unknown track")
        artists = target.get("artists", "")
        display_name = f"{artists} - {title}" if artists else title

        try:
            client.rate_song(video_id, "LIKE")
            result["liked"] += 1
            print(f"[{idx}/{total}] Liked: {display_name}")
        except Exception as e:
            if _is_auth_error(e):
                raise HeaderExpiredError("Headers expired during like operation")

            result["failed"] += 1
            result["failed_items"].append({
                "video_id": video_id,
                "track": display_name,
                "error": str(e)
            })
            error_message = f"[{idx}/{total}] Failed to like '{display_name}': {e}"
            print(error_message)
            if error_callback:
                error_callback(error_message)

        if progress_callback:
            progress_callback(idx, total, target)

        if idx < total and like_delay > 0:
            time.sleep(like_delay)

    return result

def create_or_get_ytm_playlist(playlist_name):
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
        results = get_spotify_client().current_user_playlists(limit=limit, offset=offset)
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
    results = get_spotify_client().current_user_saved_tracks()
    while results:
        for item in results['items']:
            track = item['track']
            if track:
                artist_name = track['artists'][0]['name']
                track_name = track['name']
                liked_songs.append(f"{artist_name} - {track_name}")        
        if results['next']:
            results = get_spotify_client().next(results)
        else:
            break
    return liked_songs

def get_spotify_playlist_tracks(playlist_id):
    tracks = []
    results = get_spotify_client().playlist_items(playlist_id)
    while results:
        for item in results['items']:
            track = item['track']
            if track:
                artist_name = track['artists'][0]['name']
                track_name = track['name']
                tracks.append(f"{artist_name} - {track_name}")        
        if results['next']:
            results = get_spotify_client().next(results)
        else:
            break
    return tracks

def create_ytm_playlist(playlist_name):
    try:
        playlist_id = get_ytmusic_client().create_playlist(title=playlist_name, description="Copied from Spotify")
        print(f"Created YouTube Music playlist: {playlist_name} (ID: {playlist_id})")
        return playlist_id
    except Exception as e:
        print(f"Failed to create playlist: {playlist_name}")
        print(e)
        return None

SEARCH_CACHE_FILE = "song_cache.json"
search_cache = {}

def load_search_cache():
    global search_cache
    if os.path.exists(SEARCH_CACHE_FILE):
        try:
            with open(SEARCH_CACHE_FILE, "r", encoding="utf-8") as f:
                search_cache = json.load(f)
        except:
            pass

def save_search_cache():
    try:
        with open(SEARCH_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(search_cache, f, indent=2)
    except:
        pass

def search_track_on_ytm(track_query):
    global search_cache
    if not search_cache:
        load_search_cache()
    
    if track_query in search_cache:
        return search_cache[track_query]

    try:
        time.sleep(0.1)
        search_results = get_ytmusic_client().search(query=track_query, filter="songs")
        if search_results:
            video_id = search_results[0]['videoId']
            search_cache[track_query] = video_id
            save_search_cache()
            return video_id
        else:
            search_cache[track_query] = None
            save_search_cache()
            return None
    except Exception as e:
        print(f"Error searching for track: {track_query}")
        print(e)
        return None

def test_ytmusic_connection():
    try:
        ytmusic = get_ytmusic_client()
        ytmusic.get_library_playlists(limit=1)
        return True
    except Exception as e:
        if "401" in str(e) or "403" in str(e) or "unauthorized" in str(e).lower():
            return False
        return True

def save_progress(playlist_name, current_track_index, total_tracks, ytm_video_ids, not_found_tracks, operation_type="playlist", current_batch_index=0):
    progress_data = {
        "playlist_name": playlist_name,
        "current_track_index": current_track_index,
        "total_tracks": total_tracks,
        "ytm_video_ids": ytm_video_ids,
        "not_found_tracks": not_found_tracks,
        "operation_type": operation_type,
        "current_batch_index": current_batch_index,
        "timestamp": time.time()
    }
    filename = f"progress_{playlist_name.replace(' ', '_').replace('/', '_')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(progress_data, f, indent=2)
    return filename

def load_progress(playlist_name):
    try:
        filename = f"progress_{playlist_name.replace(' ', '_').replace('/', '_')}.json"
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading progress: {e}")
    return None

def delete_progress(playlist_name):
    try:
        filename = f"progress_{playlist_name.replace(' ', '_').replace('/', '_')}.json"
        if os.path.exists(filename):
            os.remove(filename)
    except:
        pass

class HeaderExpiredError(Exception):
    def __init__(self, message, batch_index=None):
        super().__init__(message)
        self.batch_index = batch_index

def add_tracks_to_ytm_playlist_with_header_check(
    playlist_id, track_ids, batch_size=10, retry_attempts=3, batch_delay=3, start_batch_index=0, progress_callback=None
):
    try:
        total_batches = (len(track_ids) + batch_size - 1) // batch_size
        for batch_num, i in enumerate(range(0, len(track_ids), batch_size)):
            if batch_num < start_batch_index:
                continue

            batch = track_ids[i:i + batch_size]
            attempt = 0
            while attempt < retry_attempts:
                try:
                    if not test_ytmusic_connection():
                        raise HeaderExpiredError("Headers expired", batch_index=batch_num)
                    get_ytmusic_client().add_playlist_items(playlistId=playlist_id, videoIds=batch)
                    print(f"Added tracks {i + 1} to {i + len(batch)} to YouTube Music playlist.")
                    break
                except Exception as e:
                    error_str = str(e).lower()
                    if "401" in error_str or "403" in error_str or "unauthorized" in error_str:
                        print("Detected expired headers during batch add.")
                        raise HeaderExpiredError("Headers expired during batch add", batch_index=batch_num)
                    if "HTTP 409" in str(e):
                        print(f"Conflict error for tracks {i + 1} to {i + len(batch)}. Skipping...")
                        break
                    else:
                        attempt += 1
                        print(f"Attempt {attempt} failed for tracks {i + 1} to {i + len(batch)}. Retrying in 5 seconds...")
                        time.sleep(5)
            else:
                print(f"Failed to add tracks {i + 1} to {i + len(batch)} after {retry_attempts} attempts.")

            if progress_callback:
                progress_callback(i + len(batch))

            time.sleep(batch_delay)

    except HeaderExpiredError as e:
        raise e
    except Exception as e:
        print(f"Failed to add tracks to playlist ID: {playlist_id}")
        print(e)

def add_tracks_to_ytm_playlist(playlist_id, track_ids, batch_size=10, retry_attempts=3):
    try:        
        for i in range(0, len(track_ids), batch_size):
            batch = track_ids[i:i + batch_size]
            attempt = 0
            while attempt < retry_attempts:
                try:                    
                    get_ytmusic_client().add_playlist_items(playlistId=playlist_id, videoIds=batch)
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
    results = get_spotify_client().current_user_followed_artists(limit=50)  
    while results:
        for artist in results['artists']['items']:
            followed_artists.append(artist['name'])        
        if results['artists']['next']:
            results = get_spotify_client().next(results['artists'])
        else:
            break
    return followed_artists

def subscribe_to_ytm_artists(artist_names, control_callback=None):
    for artist_name in artist_names:
        if control_callback:
            if not control_callback():
                print("🛑 Artist subscription cancelled.")
                return

        try:            
            search_results = get_ytmusic_client().search(query=artist_name, filter="artists")
            if search_results:                
                artist_id = search_results[0]['browseId']                
                get_ytmusic_client().subscribe_artists([artist_id])
                print(f"Subscribed to artist: {artist_name} (ID: {artist_id})")
            else:
                print(f"No results found for artist: {artist_name}")
        except Exception as e:
            print(f"Failed to subscribe to artist: {artist_name}")
            print(e)

def parse_playlist_selection(selection_input, max_playlists):
    selected_indices = set()
    
    parts = [p.strip() for p in selection_input.split(",")]
    
    for part in parts:
        if "-" in part:
            try:
                start, end = map(int, part.split("-"))
                if start < 1 or end > max_playlists or start > end:
                    print(f"Invalid range: {part}. Valid range is 1-{max_playlists}.")
                    continue
                for i in range(start-1, end):
                    selected_indices.add(i)
            except ValueError:
                print(f"Invalid range format: {part}")
        else:
            try:
                idx = int(part) - 1
                if idx < 0 or idx >= max_playlists:
                    print(f"Invalid playlist number: {part}")
                    continue
                selected_indices.add(idx)
            except ValueError:
                print(f"Invalid input: {part}")
    
    return sorted(list(selected_indices))

def copy_spotify_to_ytm():
    if not perform_quota_check():
        print("\n⚠️ Cannot proceed due to API quota/connection issues.")
        print("Please try again later or check your credentials.")
        return
    
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
                        
                    original_playlist_name = playlist_name
                    playlist_name = playlist_name[:150]
                    
                    ytm_playlist_id, already_exists = create_or_get_ytm_playlist(playlist_name)
                    if not ytm_playlist_id:
                        continue
                    
                    existing_video_ids = set()
                    if already_exists:
                        print("Checking for already existing songs in the YouTube Music playlist...")
                        existing_video_ids = get_ytm_playlist_song_video_ids(ytm_playlist_id)
                    
                    print(f"Searching for tracks from {playlist_name} on YouTube Music...")
                    ytm_video_ids = []
                    not_found_tracks = [] 

                    progress = load_progress(playlist_name)
                    if progress:
                        print(f"📁 Found saved progress for '{playlist_name}'. Resuming...")
                        start_index = progress["current_track_index"]
                        ytm_video_ids = progress["ytm_video_ids"]
                        not_found_tracks = progress["not_found_tracks"]
                        current_batch_index = progress.get("current_batch_index", 0)
                    else:
                        start_index = 0
                        current_batch_index = 0

                    try:
                        for idx in range(start_index, len(spotify_tracks)):
                            track = spotify_tracks[idx]
                            video_id = search_track_on_ytm(track)
                            if video_id:
                                if video_id not in existing_video_ids:
                                    ytm_video_ids.append(video_id)
                            else:
                                not_found_tracks.append(track) 
                                print(f"Skipping track: {track}")

                        if ytm_video_ids:
                            try:
                                print(f"Adding {len(ytm_video_ids)} tracks to YouTube Music...")
                                add_tracks_to_ytm_playlist_with_header_check(
                                    ytm_playlist_id, 
                                    ytm_video_ids, 
                                    start_batch_index=current_batch_index
                                )

                                if detect_quota_exhaustion(ytm_playlist_id, ytm_video_ids):
                                    print("\n⚠️ DAILY API QUOTA EXCEEDED!")
                                    print("The playlist transfer appears successful but no tracks were actually added.")
                                    print("Please wait 24 hours for your quota to reset and try again.")
                                    return
                                else:
                                    print(f"✅ Successfully added {len(ytm_video_ids)} tracks to: {playlist_name}")
                                    
                            except HeaderExpiredError:
                                progress_file = save_progress(playlist_name, len(spotify_tracks), len(spotify_tracks), 
                                                            ytm_video_ids, not_found_tracks, "playlist")
                                print(f"\n🔑 YouTube Music headers have expired!")
                                print(f"💾 Progress saved to: {progress_file}")
                                print("Please update your headers using the UI and run the script again.")
                                print("The script will automatically resume from where it left off.")
                                return
                        else:
                            print(f"No new tracks to add for playlist: {playlist_name}")
                        
                        delete_progress(playlist_name)
                        verify_transfer_completeness(spotify_tracks, ytm_playlist_id, playlist_name)
                        
                    except HeaderExpiredError:
                        progress_file = save_progress(playlist_name, idx, len(spotify_tracks), 
                                                    ytm_video_ids, not_found_tracks, "playlist")
                        print(f"\n🔑 YouTube Music headers have expired!")
                        print(f"💾 Progress saved to: {progress_file}")
                        print("Please update your headers using the UI and run the script again.")
                        print("The script will automatically resume from where it left off.")
                        return
            
        elif choice == "2":
            liked_songs = get_spotify_liked_songs()
            if not liked_songs:
                print("No liked songs found on Spotify.")
                return

            like_choice = input(
                "Also mark matched tracks as liked in YouTube Music? (yes/no): "
            ).strip().lower()
            like_on_transfer = like_choice in ("y", "yes")
            like_delay_seconds = 1.5
            if like_on_transfer:
                delay_value = input("Delay between like requests in seconds (default 1.5): ").strip()
                if delay_value:
                    like_delay_seconds = _normalize_delay_seconds(delay_value)

            playlist_name = "Liked Songs from Spotify"
            
            ytm_playlist_id, already_exists = create_or_get_ytm_playlist(playlist_name)
            if not ytm_playlist_id:
                return

            existing_video_ids = set()
            if already_exists:
                print("Checking for already existing songs in the YouTube Music playlist...")
                existing_video_ids = get_ytm_playlist_song_video_ids(ytm_playlist_id)

            print("Searching for liked songs on YouTube Music...")
            ytm_video_ids = []
            matched_video_ids = []
            not_found_tracks = []  
            for track in tqdm(liked_songs, desc="Processing Liked Songs", unit="track"):
                video_id = search_track_on_ytm(track)
                if video_id:
                    matched_video_ids.append(video_id)
                    if video_id not in existing_video_ids:
                        ytm_video_ids.append(video_id)
                else:
                    not_found_tracks.append(track) 
                    print(f"Skipping track: {track}")
            
            if ytm_video_ids:
                print(f"\nAdding {len(ytm_video_ids)} liked songs to YouTube Music with verification...")
                add_tracks_to_ytm_playlist_with_verification(ytm_playlist_id, ytm_video_ids)
            else:
                print("No new liked songs to add to YouTube Music.")

            if like_on_transfer:
                like_targets = matched_video_ids if matched_video_ids else ytm_video_ids
                if like_targets:
                    print(f"\nApplying likes for {len(_deduplicate_video_ids(like_targets))} matched tracks...")
                    like_result = like_tracks_on_ytm(
                        track_video_ids=like_targets,
                        delay_seconds=like_delay_seconds
                    )
                    print(
                        "Like sync completed: "
                        f"{like_result['liked']}/{like_result['total']} liked, "
                        f"{like_result['failed']} failed, {like_result['skipped']} skipped."
                    )
                else:
                    print("No matched tracks available for liking.")

            if not_found_tracks:
                print(f"\nLiked songs not found on YouTube Music:")
                for track in not_found_tracks:
                    print(f"- {track}")
                print()
            
            verify_transfer_completeness(liked_songs, ytm_playlist_id, playlist_name)
                
        elif choice == "3":
            followed_artists = get_spotify_followed_artists()
            if not followed_artists:
                print("No followed artists found on Spotify.")
                return
            print("Subscribing to artists on YouTube Music...")
            subscribe_to_ytm_artists(followed_artists)
            print("Finished subscribing to artists.")

def verify_batch_added(playlist_id, expected_video_ids, max_retries=3):
    for attempt in range(max_retries):
        try:
            current_playlist_ids = get_ytm_playlist_song_video_ids(playlist_id)
            missing_ids = [vid for vid in expected_video_ids if vid not in current_playlist_ids]
            
            if not missing_ids:
                return True, []
            else:
                print(f"Verification attempt {attempt + 1}: {len(missing_ids)} tracks missing")
                if attempt < max_retries - 1:
                    time.sleep(3)
                
        except Exception as e:
            print(f"Verification attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(3)
    
    try:
        current_playlist_ids = get_ytm_playlist_song_video_ids(playlist_id)
        missing_ids = [vid for vid in expected_video_ids if vid not in current_playlist_ids]
        return len(missing_ids) == 0, missing_ids
    except:
        return False, expected_video_ids

def add_tracks_to_ytm_playlist_with_verification(playlist_id, track_ids, batch_size=10, retry_attempts=3):
    if not track_ids:
        return
        
    total_added = 0
    failed_tracks = []
    
    try:        
        for i in range(0, len(track_ids), batch_size):
            batch = track_ids[i:i + batch_size]
            batch_attempt = 0
            current_batch = batch.copy()
            
            while batch_attempt < retry_attempts and current_batch:
                try:
                    if not test_ytmusic_connection():
                        raise HeaderExpiredError("Headers expired")
                    
                    print(f"Adding batch {i//batch_size + 1}: {len(current_batch)} tracks (attempt {batch_attempt + 1})")
                    get_ytmusic_client().add_playlist_items(playlistId=playlist_id, videoIds=current_batch)
                    
                    time.sleep(3)
                    
                    verification_success, missing_ids = verify_batch_added(playlist_id, current_batch)
                    
                    if verification_success:
                        print(f"✅ Batch {i//batch_size + 1}: All {len(current_batch)} tracks added successfully")
                        total_added += len(current_batch)
                        break
                    else:
                        added_count = len(current_batch) - len(missing_ids)
                        total_added += added_count
                        print(f"⚠️ Batch {i//batch_size + 1}: {added_count}/{len(current_batch)} tracks added, {len(missing_ids)} missing")
                        
                        if batch_attempt < retry_attempts - 1:
                            current_batch = missing_ids
                            print(f"🔄 Retrying {len(missing_ids)} missing tracks...")
                            time.sleep(5)
                        else:
                            print(f"❌ Failed to add {len(missing_ids)} tracks after {retry_attempts} attempts")
                            failed_tracks.extend(missing_ids)
                    
                except HeaderExpiredError:
                    raise
                except Exception as e:
                    if "HTTP 409" in str(e):
                        print(f"Conflict error for batch {i//batch_size + 1}. Checking which tracks were added...")
                        verification_success, missing_ids = verify_batch_added(playlist_id, current_batch)
                        added_count = len(current_batch) - len(missing_ids)
                        total_added += added_count
                        if missing_ids and batch_attempt < retry_attempts - 1:
                            current_batch = missing_ids
                            print(f"🔄 Retrying {len(missing_ids)} tracks that weren't added...")
                        else:
                            failed_tracks.extend(missing_ids)
                        break
                    else:
                        batch_attempt += 1
                        if batch_attempt < retry_attempts:
                            print(f"Batch attempt {batch_attempt} failed: {e}. Retrying in 5 seconds...")
                            time.sleep(5)
                        else:
                            print(f"❌ Batch failed after {retry_attempts} attempts: {e}")
                            failed_tracks.extend(current_batch)
                
                batch_attempt += 1
            
            time.sleep(2)

        print(f"\n📊 Final Results:")
        print(f"   • Successfully added: {total_added}/{len(track_ids)} tracks")
        print(f"   • Failed to add: {len(failed_tracks)} tracks")
        
        if failed_tracks:
            print(f"   • Success rate: {(total_added/len(track_ids)*100):.1f}%")
        else:
            print(f"   • Success rate: 100%")

    except HeaderExpiredError:
        raise
    except Exception as e:
        print(f"Failed to add tracks to playlist ID: {playlist_id}")
        print(e)

def verify_transfer_completeness(spotify_tracks, ytm_playlist_id, playlist_name):
    print(f"\n📊 Verification Analysis for: {playlist_name}")
    
    report = {
        "playlist_name": playlist_name,
        "ytm_playlist_id": ytm_playlist_id,
        "timestamp": time.ctime(),
        "stats": {
            "total_spotify_tracks": len(spotify_tracks),
            "found_on_ytm": 0,
            "successfully_in_playlist": 0,
            "missing_from_playlist": 0
        },
        "missing_tracks": [],
        "track_details": []
    }

    try:
        current_ids = get_ytm_playlist_song_video_ids(ytm_playlist_id)
        
        missing_from_playlist = []
        found_on_ytm_count = 0
        
        global search_cache
        if not search_cache:
            load_search_cache()
            
        for track in spotify_tracks:
            ytm_id = search_cache.get(track)
            status = "not_found"
            
            if ytm_id:
                status = "found_but_missing"
                found_on_ytm_count += 1
                if ytm_id in current_ids:
                    status = "success"
                else:
                    missing_from_playlist.append(track)
            
            report["track_details"].append({
                "spotify_name": track,
                "ytm_id": ytm_id,
                "status": status
            })
        
        report["stats"]["found_on_ytm"] = found_on_ytm_count
        report["stats"]["successfully_in_playlist"] = len(current_ids) 
        report["stats"]["missing_from_playlist"] = len(missing_from_playlist)
        report["missing_tracks"] = missing_from_playlist

        print(f"   • Total Spotify Tracks: {len(spotify_tracks)}")
        print(f"   • Found on YouTube Music: {found_on_ytm_count}")
        print(f"   • Actually in Playlist: {len(current_ids)}")
        
        if missing_from_playlist:
            print(f"⚠️  The following {len(missing_from_playlist)} tracks were found on YTM but are NOT in the playlist:")
            for t in missing_from_playlist[:10]:
                print(f"   - {t}")
            if len(missing_from_playlist) > 10:
                print(f"   ... and {len(missing_from_playlist) - 10} more.")
        else:
            print("✅  All found tracks are present in the playlist.")
            
        safe_name = "".join([c for c in playlist_name if c.isalpha() or c.isdigit() or c==' ']).rstrip().replace(" ", "_")
        filename = f"migration_report_{safe_name}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"📄 Detailed migration report saved to: {filename}")
            
    except Exception as e:
        print(f"Error during verification: {e}")

def check_api_quota():
    try:
        ytmusic = get_ytmusic_client()
        if ytmusic is None:
            return False, "YouTube Music client not initialized - check headers"

        test_playlist_id = ytmusic.create_playlist(
            title="API_QUOTA_TEST_DELETE_ME",
            description="Testing API quota - will be deleted"
        )
        if not test_playlist_id:
            return False, "Failed to create test playlist (quota or headers issue)"

        test_video_id = 'lYBUbBu4W08'
        try:
            ytmusic.add_playlist_items(test_playlist_id, [test_video_id])
        except Exception as e:
            try: ytmusic.delete_playlist(test_playlist_id)
            except: pass
            return False, f"Failed to add test song: {e}"

        time.sleep(2)
        playlist = ytmusic.get_playlist(test_playlist_id)
        found = False
        for track in playlist.get('tracks', []):
            if track.get('videoId') == test_video_id:
                found = True
                break

        track_count = playlist.get('trackCount', 0)
        try: ytmusic.delete_playlist(test_playlist_id)
        except: pass

        if found and track_count > 0:
            return True, "API quota available (playlist create/add/verify succeeded, track count correct)"
        elif found and track_count == 0:
            return False, "⚠️ Song is present in playlist but track count is 0 (YouTube Music cache delay or API quirk). Try again in a few minutes, or proceed if you see this only in the test."
        else:
            return False, "Test song not found in playlist after add - quota likely exhausted or headers invalid"

    except Exception as e:
        return False, f"API quota check failed: {e}"

def check_spotify_quota():
    try:
        sp = get_spotify_client()
        
        user_info = sp.current_user()
        
        if user_info:
            return True, "Spotify API available"
        else:
            return False, "Spotify API connection failed"
        
    except Exception as e:
        error_str = str(e).lower()
        
        if "429" in error_str or "rate limit" in error_str:
            return False, f"Spotify rate limit exceeded: {e}"
        elif "401" in error_str or "unauthorized" in error_str:
            return False, f"Spotify authentication failed - check credentials: {e}"
        elif "403" in error_str or "forbidden" in error_str:
            return False, f"Spotify access denied - check permissions: {e}"
        else:
            return False, f"Spotify API error: {e}"       

def verify_playlist_actually_updated(playlist_id, expected_minimum_tracks):
    try:
        time.sleep(3)
        
        actual_tracks = get_ytm_playlist_song_video_ids(playlist_id)
        actual_count = len(actual_tracks)
        
        print(f"🔍 Verification: Expected at least {expected_minimum_tracks}, found {actual_count}")
        
        if actual_count >= expected_minimum_tracks:
            return True, actual_count
        else:
            return False, actual_count
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False, 0

def detect_quota_exhaustion(playlist_id, video_ids_added):
    try:
        success, actual_count = verify_playlist_actually_updated(playlist_id, len(video_ids_added))

        if actual_count == 0 and len(video_ids_added) > 0:
            print("⚠️ Playlist appears empty, but this is likely a YouTube Music backend delay.")
            print("   - All tracks were added, but the playlist count is not updated yet.")
            print("   - Please wait a few minutes and check again in YouTube Music.")
            print("   - This is NOT a quota exhaustion issue.")
            return False
        elif actual_count < len(video_ids_added):
            print("⚠️ Partial success: Some tracks were not added. This may be due to API delays or silent drops, not necessarily quota exhaustion.")
            print(f"   - Expected: {len(video_ids_added)} tracks")
            print(f"   - Actual: {actual_count} tracks")
            return False
        return False

    except Exception as e:
        print(f"Error detecting quota exhaustion: {e}")
        return False

def perform_quota_check():
    print("🔍 Checking API quotas...")
    
    spotify_ok, spotify_msg = check_spotify_quota()
    if spotify_ok:
        print(f"✅ Spotify: {spotify_msg}")
    else:
        print(f"❌ Spotify: {spotify_msg}")
        return False, f"Spotify: {spotify_msg}"
    
    ytm_ok, ytm_msg = check_api_quota()
    if ytm_ok:
        print(f"✅ YouTube Music: {ytm_msg}")
        return True, f"Spotify: {spotify_msg}\nYouTube Music: {ytm_msg}"
    else:
        print(f"❌ YouTube Music: {ytm_msg}")
        return False, f"Spotify: {spotify_msg}\nYouTube Music: {ytm_msg}"

def add_tracks_with_delayed_verification(
    playlist_id, track_ids, batch_size=5, retry_attempts=3, 
    batch_delay=5, verification_delay=15, progress_callback=None,
    start_batch_index=0, error_callback=None, control_callback=None
):
    
    successfully_added = []
    failed_batches = []
    
    try:
        total_batches = (len(track_ids) + batch_size - 1) // batch_size
        
        for i in range(start_batch_index * batch_size, len(track_ids), batch_size):
            if control_callback:
                if not control_callback():
                    if error_callback:
                        error_callback("🛑 Transfer cancelled or stopped by user.")
                    return successfully_added, failed_batches

            batch = track_ids[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            current_batch_index = i // batch_size  
            
            attempt = 0
            last_error = None
            while attempt < retry_attempts:
                try:
                    if not test_ytmusic_connection():
                        raise HeaderExpiredError("Headers expired", batch_index=current_batch_index)
                    
                    print(f"Adding batch {batch_num}/{total_batches}: {len(batch)} tracks")
                    get_ytmusic_client().add_playlist_items(playlistId=playlist_id, videoIds=batch)
                    successfully_added.extend(batch)
                    break
                    
                except Exception as e:
                    last_error = e
                    error_str = str(e).lower()
                    if "401" in error_str or "403" in error_str or "unauthorized" in error_str:
                        raise HeaderExpiredError("Headers expired", batch_index=current_batch_index)
                    elif "HTTP 409" in str(e):
                        print(f"Conflict error for batch {batch_num}. Assuming success...")
                        successfully_added.extend(batch)
                        break
                    else:
                        attempt += 1
                        error_msg = f"Batch {batch_num} attempt {attempt} failed: {e}"
                        print(error_msg)
                        
                        if error_callback:
                            if "Maximum playlist size exceeded" in str(e):
                                error_callback(f"⛔ CRITICAL: Playlist limit reached! (Max 5000 tracks). Cannot add more.")
                            elif "400" in str(e) and "Bad Request" in str(e):
                                error_callback(f"⚠️ Batch {batch_num} failed: Bad Request (Possible limit or invalid track).")
                        
                        if attempt < retry_attempts:
                            time.sleep(batch_delay * attempt)
            else:
                print(f"❌ Batch {batch_num} failed after all attempts")
                if error_callback:
                     error_callback(f"❌ Batch {batch_num} failed permanently after {retry_attempts} retries.")
                failed_batches.append(batch)

                if last_error and "Maximum playlist size exceeded" in str(last_error):
                    print("🛑 Stopping transfer: Playlist limit reached.")
                    if error_callback:
                        error_callback("🛑 Transfer stopped: Playlist reached 5000 song limit.")
                    return successfully_added, failed_batches
            
            if progress_callback:
                progress_callback(len(successfully_added))
            
            time.sleep(batch_delay)
        
        if start_batch_index > 0:
            try:
                progress_file = f"progress_{playlist_id.replace(' ', '_').replace('/', '_')}.json"
                if os.path.exists(progress_file):
                    with open(progress_file, "r", encoding="utf-8") as f:
                        progress_data = json.load(f)
                    all_track_ids = progress_data.get("ytm_video_ids", track_ids)
                else:
                    all_track_ids = track_ids
            except Exception:
                all_track_ids = track_ids
        else:
            all_track_ids = track_ids.copy()

        if successfully_added or start_batch_index > 0:
            print(f"\n⏳ Waiting {verification_delay}s before final verification...")
            time.sleep(verification_delay)

            print("🔍 Performing final verification...")
            final_tracks = get_ytm_playlist_song_video_ids(playlist_id)
            actually_added = [vid for vid in all_track_ids if vid in final_tracks]

            print(f"📊 Final Results:")
            print(f"   Attempted: {len(all_track_ids)} tracks")
            print(f"   Verified: {len(actually_added)} tracks")
            print(f"   Missing: {len(all_track_ids) - len(actually_added)} tracks")
            print(f"   Success Rate: {(len(actually_added)/len(all_track_ids)*100):.1f}%")

            return actually_added, failed_batches

        return successfully_added, failed_batches
        
        
    except HeaderExpiredError as e:
        raise e
    except Exception as e:
        print(f"Error in delayed verification method: {e}")
        return successfully_added, failed_batches

if __name__ == "__main__":
    copy_spotify_to_ytm()

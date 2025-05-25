import tkinter as tk
from tkinter import messagebox, ttk
import threading
import copy_playlists

class Spotify2YTMUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Spotify ➡️ YouTube Music Playlist Copier")
        self.geometry("700x800")
        self.resizable(True, True)
        self.configure(bg='#1e1e1e')
        
        # Configure style for modern look
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure custom styles
        self.style.configure('Custom.TNotebook', background='#1e1e1e', borderwidth=0)
        self.style.configure('Custom.TNotebook.Tab', 
                           background='#2d2d2d', 
                           foreground='white',
                           padding=[20, 10],
                           font=('Segoe UI', 10))
        self.style.map('Custom.TNotebook.Tab',
                      background=[('selected', '#0078d4'), ('active', '#404040')])
        
        self.style.configure('Custom.TFrame', background='#1e1e1e')
        self.style.configure('Custom.TButton', 
                           background='#0078d4',
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           font=('Segoe UI', 10))
        self.style.map('Custom.TButton',
                      background=[('active', '#106ebe'), ('pressed', '#005a9e')])
        
        self.style.configure('Green.TButton',
                           background='#107c10',
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           font=('Segoe UI', 10))
        self.style.map('Green.TButton',
                      background=[('active', '#0e6e0e'), ('pressed', '#0c5d0c')])
        
        self.style.configure('Red.TButton',
                           background='#d13438',
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           font=('Segoe UI', 9))
        self.style.map('Red.TButton',
                      background=[('active', '#b92b2f'), ('pressed', '#a02327')])

        # Main container
        main_frame = tk.Frame(self, bg='#1e1e1e')
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = tk.Label(main_frame, 
                              text="Spotify ➡️ YouTube Music", 
                              font=('Segoe UI', 18, 'bold'),
                              fg='white',
                              bg='#1e1e1e')
        title_label.pack(pady=(0, 10))

        subtitle_label = tk.Label(main_frame, 
                                 text="Transfer your music seamlessly", 
                                 font=('Segoe UI', 10),
                                 fg='#cccccc',
                                 bg='#1e1e1e')
        subtitle_label.pack(pady=(0, 20))

        # Notebook with custom style
        self.notebook = ttk.Notebook(main_frame, style='Custom.TNotebook')
        self.notebook.pack(fill="both", expand=True, pady=(0, 15))

        self.playlists_tab = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.liked_tab = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.artists_tab = ttk.Frame(self.notebook, style='Custom.TFrame')

        self.notebook.add(self.playlists_tab, text="🎵 Playlists")
        self.notebook.add(self.liked_tab, text="❤️ Liked Songs")
        self.notebook.add(self.artists_tab, text="👤 Artists")

        self.create_playlists_tab()
        self.create_liked_tab()
        self.create_artists_tab()

        # Status section
        status_frame = tk.Frame(main_frame, bg='#2d2d2d', relief='flat', bd=1)
        status_frame.pack(fill="x", pady=(0, 10))

        self.progress = tk.StringVar()
        self.progress.set("Ready to transfer your music")
        status_label = tk.Label(status_frame, 
                               textvariable=self.progress, 
                               anchor="w",
                               font=('Segoe UI', 9),
                               fg='#cccccc',
                               bg='#2d2d2d')
        status_label.pack(fill="x", padx=15, pady=8)

        # Progress bar
        self.progressbar = ttk.Progressbar(main_frame, 
                                         orient="horizontal", 
                                         mode="determinate",
                                         style='Custom.Horizontal.TProgressbar')
        self.progressbar.pack(fill="x", pady=(0, 15))

        # Configure progress bar style
        self.style.configure('Custom.Horizontal.TProgressbar',
                           background='#0078d4',
                           troughcolor='#404040',
                           borderwidth=0,
                           lightcolor='#0078d4',
                           darkcolor='#0078d4')

        # Output section
        output_frame = tk.Frame(main_frame, bg='#1e1e1e')
        output_frame.pack(fill="both", expand=True)

        output_header = tk.Frame(output_frame, bg='#1e1e1e')
        output_header.pack(fill="x", pady=(0, 5))

        tk.Label(output_header, 
                text="Output Log", 
                font=('Segoe UI', 11, 'bold'),
                fg='white',
                bg='#1e1e1e').pack(side="left")

        ttk.Button(output_header, 
                  text="Clear", 
                  command=self.clear_output,
                  style='Red.TButton').pack(side="right")

        # Text widget with modern styling
        text_frame = tk.Frame(output_frame, bg='#2d2d2d', relief='flat', bd=1)
        text_frame.pack(fill="both", expand=True)

        self.response_text = tk.Text(text_frame, 
                                   height=8, 
                                   state="disabled", 
                                   wrap="word",
                                   bg='#2d2d2d',
                                   fg='#ffffff',
                                   font=('Consolas', 9),
                                   insertbackground='white',
                                   selectbackground='#0078d4',
                                   relief='flat',
                                   bd=0)
        
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.response_text.yview)
        self.response_text.configure(yscrollcommand=scrollbar.set)
        
        self.response_text.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

    def append_response(self, msg):
        self.response_text.config(state="normal")
        self.response_text.insert(tk.END, msg + "\n")
        self.response_text.see(tk.END)
        self.response_text.config(state="disabled")

    def clear_output(self):
        self.response_text.config(state="normal")
        self.response_text.delete(1.0, tk.END)
        self.response_text.config(state="disabled")

    def create_playlists_tab(self):
        # Main container for playlists tab
        container = tk.Frame(self.playlists_tab, bg='#1e1e1e')
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Instructions
        instruction_label = tk.Label(container,
                                   text="Select playlists to transfer from Spotify to YouTube Music",
                                   font=('Segoe UI', 11),
                                   fg='#cccccc',
                                   bg='#1e1e1e')
        instruction_label.pack(pady=(0, 15))

        # Listbox with modern styling
        listbox_frame = tk.Frame(container, bg='#2d2d2d', relief='flat', bd=1)
        listbox_frame.pack(fill="both", expand=True, pady=(0, 15))

        self.playlists_listbox = tk.Listbox(listbox_frame,
                                          selectmode=tk.MULTIPLE,
                                          bg='#2d2d2d',
                                          fg='white',
                                          font=('Segoe UI', 10),
                                          selectbackground='#0078d4',
                                          selectforeground='white',
                                          relief='flat',
                                          bd=0,
                                          highlightthickness=0)
        
        listbox_scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.playlists_listbox.yview)
        self.playlists_listbox.configure(yscrollcommand=listbox_scrollbar.set)
        
        self.playlists_listbox.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        listbox_scrollbar.pack(side="right", fill="y", pady=10)

        # Button frame
        btn_frame = tk.Frame(container, bg='#1e1e1e')
        btn_frame.pack(fill="x")

        ttk.Button(btn_frame, 
                  text="🔄 Load Playlists", 
                  command=self.load_playlists,
                  style='Custom.TButton').pack(side="left", padx=(0, 10))

        ttk.Button(btn_frame, 
                  text="📋 Copy Selected", 
                  command=self.copy_selected_playlists,
                  style='Green.TButton').pack(side="left", padx=(0, 10))

        ttk.Button(btn_frame, 
                  text="📚 Copy All", 
                  command=self.copy_all_playlists,
                  style='Green.TButton').pack(side="left")

    def create_liked_tab(self):
        container = tk.Frame(self.liked_tab, bg='#1e1e1e')
        container.pack(expand=True)

        # Icon and description
        tk.Label(container,
                text="❤️",
                font=('Segoe UI', 48),
                fg='#ff6b6b',
                bg='#1e1e1e').pack(pady=(40, 20))

        tk.Label(container,
                text="Transfer Your Liked Songs",
                font=('Segoe UI', 16, 'bold'),
                fg='white',
                bg='#1e1e1e').pack(pady=(0, 10))

        tk.Label(container,
                text="Copy all your Spotify liked songs to a YouTube Music playlist",
                font=('Segoe UI', 11),
                fg='#cccccc',
                bg='#1e1e1e').pack(pady=(0, 30))

        ttk.Button(container,
                  text="💖 Transfer Liked Songs",
                  command=self.copy_liked_songs,
                  style='Green.TButton').pack()

    def create_artists_tab(self):
        container = tk.Frame(self.artists_tab, bg='#1e1e1e')
        container.pack(expand=True)

        # Icon and description
        tk.Label(container,
                text="👤",
                font=('Segoe UI', 48),
                fg='#4ecdc4',
                bg='#1e1e1e').pack(pady=(40, 20))

        tk.Label(container,
                text="Follow Your Artists",
                font=('Segoe UI', 16, 'bold'),
                fg='white',
                bg='#1e1e1e').pack(pady=(0, 10))

        tk.Label(container,
                text="Subscribe to your followed Spotify artists on YouTube Music",
                font=('Segoe UI', 11),
                fg='#cccccc',
                bg='#1e1e1e').pack(pady=(0, 30))

        ttk.Button(container,
                  text="👥 Follow Artists",
                  command=self.copy_followed_artists,
                  style='Green.TButton').pack()

    def load_playlists(self):
        self.playlists_listbox.delete(0, tk.END)
        self.progress.set("Loading playlists from Spotify...")
        self.playlists = copy_playlists.list_spotify_playlists()
        for idx, playlist in enumerate(self.playlists):
            name = playlist['name']
            total = playlist['tracks']['total'] if 'tracks' in playlist and 'total' in playlist['tracks'] else "?"
            self.playlists_listbox.insert(tk.END, f"🎵 {name} ({total} tracks)")
        self.append_response("✅ Loaded playlists successfully")
        self.progress.set(f"Loaded {len(self.playlists)} playlists")

    def copy_selected_playlists(self):
        selected = self.playlists_listbox.curselection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select at least one playlist.")
            return
        playlists = [self.playlists[i] for i in selected]
        threading.Thread(target=self._copy_playlists, args=(playlists,)).start()

    def copy_all_playlists(self):
        if not hasattr(self, "playlists"):
            self.load_playlists()
        threading.Thread(target=self._copy_playlists, args=(self.playlists,)).start()

    def _copy_playlists(self, playlists):
        for playlist in playlists:
            name = playlist['name']
            playlist_id = playlist['id']
            self.progress.set(f"Processing: {name}")
            self.append_response(f"🎵 Processing playlist: {name}")
            tracks = copy_playlists.get_spotify_playlist_tracks(playlist_id)
            if not tracks:
                self.append_response(f"⚠️ No tracks found in playlist: {name}")
                continue
            ytm_playlist_id, already_exists = copy_playlists.create_or_get_ytm_playlist(name)
            if not ytm_playlist_id:
                self.append_response(f"❌ Failed to create playlist: {name}")
                continue
            existing_video_ids = set()
            if already_exists:
                self.append_response(f"📋 Playlist exists, checking for new songs...")
                existing_video_ids = copy_playlists.get_ytm_playlist_song_video_ids(ytm_playlist_id)
            ytm_video_ids = []
            not_found_tracks = []

            self.progressbar["maximum"] = len(tracks)
            self.progressbar["value"] = 0

            for idx, track in enumerate(tracks, 1):
                video_id = copy_playlists.search_track_on_ytm(track)
                if video_id and video_id not in existing_video_ids:
                    ytm_video_ids.append(video_id)
                elif not video_id:
                    not_found_tracks.append(track)
                self.progressbar["value"] = idx
                self.progress.set(f"Searching: {idx}/{len(tracks)} - {track[:50]}...")
                self.update_idletasks()

            self.progressbar["value"] = 0

            if ytm_video_ids:
                copy_playlists.add_tracks_to_ytm_playlist(ytm_playlist_id, ytm_video_ids)
                self.append_response(f"✅ Added {len(ytm_video_ids)} new tracks to: {name}")
            else:
                self.append_response(f"ℹ️ No new tracks to add for: {name}")
            
            if not_found_tracks:
                self.append_response(f"⚠️ {len(not_found_tracks)} tracks not found on YouTube Music")
                
        self.progress.set("✅ Playlist transfer completed")
        self.append_response("🎉 Finished copying all playlists!")
        messagebox.showinfo("Success", "Playlists transferred successfully!")

    def copy_liked_songs(self):
        threading.Thread(target=self._copy_liked_songs).start()

    def _copy_liked_songs(self):
        self.progress.set("Fetching liked songs...")
        self.append_response("💖 Fetching liked songs from Spotify...")
        liked_songs = copy_playlists.get_spotify_liked_songs()
        if not liked_songs:
            self.progress.set("No liked songs found")
            self.append_response("⚠️ No liked songs found on Spotify")
            messagebox.showinfo("No Liked Songs", "No liked songs found on Spotify.")
            return
        
        playlist_name = "Liked Songs from Spotify"
        ytm_playlist_id, already_exists = copy_playlists.create_or_get_ytm_playlist(playlist_name)
        if not ytm_playlist_id:
            self.progress.set("Failed to create playlist")
            self.append_response("❌ Failed to create playlist on YouTube Music")
            return
        
        existing_video_ids = set()
        if already_exists:
            self.append_response("📋 Playlist exists, checking for new songs...")
            existing_video_ids = copy_playlists.get_ytm_playlist_song_video_ids(ytm_playlist_id)
        
        ytm_video_ids = []
        not_found_tracks = []

        self.progressbar["maximum"] = len(liked_songs)
        self.progressbar["value"] = 0

        for idx, track in enumerate(liked_songs, 1):
            video_id = copy_playlists.search_track_on_ytm(track)
            if video_id and video_id not in existing_video_ids:
                ytm_video_ids.append(video_id)
            elif not video_id:
                not_found_tracks.append(track)
            self.progressbar["value"] = idx
            self.progress.set(f"Searching: {idx}/{len(liked_songs)} - {track[:50]}...")
            self.update_idletasks()

        self.progressbar["value"] = 0

        if ytm_video_ids:
            copy_playlists.add_tracks_to_ytm_playlist(ytm_playlist_id, ytm_video_ids)
            self.append_response(f"✅ Added {len(ytm_video_ids)} liked songs to YouTube Music")
        else:
            self.append_response("ℹ️ No new liked songs to add")
        
        if not_found_tracks:
            self.append_response(f"⚠️ {len(not_found_tracks)} songs not found on YouTube Music")
            
        self.progress.set("✅ Liked songs transfer completed")
        self.append_response("🎉 Finished copying liked songs!")
        messagebox.showinfo("Success", "Liked songs transferred successfully!")

    def copy_followed_artists(self):
        threading.Thread(target=self._copy_followed_artists).start()

    def _copy_followed_artists(self):
        self.progress.set("Fetching followed artists...")
        self.append_response("👤 Fetching followed artists from Spotify...")
        artists = copy_playlists.get_spotify_followed_artists()
        if not artists:
            self.progress.set("No followed artists found")
            self.append_response("⚠️ No followed artists found on Spotify")
            messagebox.showinfo("No Artists", "No followed artists found on Spotify.")
            return
        
        self.append_response(f"🔄 Subscribing to {len(artists)} artists...")
        copy_playlists.subscribe_to_ytm_artists(artists)
        self.progress.set("✅ Artist subscription completed")
        self.append_response("🎉 Finished subscribing to artists!")
        messagebox.showinfo("Success", "Artists followed successfully!")

if __name__ == "__main__":
    app = Spotify2YTMUI()
    app.mainloop()
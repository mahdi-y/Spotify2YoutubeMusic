import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time
import copy_playlists
import json
import os

def load_config():
    defaults = {
        "spotify_client_id": "",
        "spotify_client_secret": "",
        "spotify_redirect_uri": "http://127.0.0.1:8888/callback",
        "youtube_headers": "",
        "batch_size": 5,
        "like_liked_songs_on_transfer": False,
        "like_rate_delay_seconds": 1.5
    }

    if os.path.exists("config.json"):
        try:
            with open("config.json", "r") as f:
                stored = json.load(f)
            if isinstance(stored, dict):
                defaults.update(stored)
                return defaults
        except:
            pass
    return defaults

def save_config(config):
    try:
        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

class SettingsDialog:
    def __init__(self, parent, config_data, callback):
        self.parent = parent
        self.callback = callback
        self.config_data = config_data.copy()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Settings - Credentials & Headers")
        self.dialog.geometry("600x700")
        self.dialog.configure(bg='#1e1e1e')
        self.dialog.resizable(False, False)
        self.dialog.grab_set()
        
        self.dialog.transient(parent)
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = tk.Frame(self.dialog, bg='#1e1e1e')
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = tk.Label(main_frame, 
                              text="⚙️ Settings", 
                              font=('Segoe UI', 16, 'bold'),
                              fg='white',
                              bg='#1e1e1e')
        title_label.pack(pady=(0, 20))
        
        spotify_frame = tk.LabelFrame(main_frame, 
                                     text="🎵 Spotify Configuration",
                                     bg='#2d2d2d',
                                     fg='white',
                                     font=('Segoe UI', 11, 'bold'))
        spotify_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(spotify_frame, text="Client ID:", bg='#2d2d2d', fg='white', font=('Segoe UI', 10)).pack(anchor="w", padx=10, pady=(10, 5))
        self.client_id_entry = tk.Entry(spotify_frame, width=70, bg='#404040', fg='white', font=('Consolas', 9))
        self.client_id_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.client_id_entry.insert(0, self.config_data.get("spotify_client_id", ""))
        
        tk.Label(spotify_frame, text="Client Secret:", bg='#2d2d2d', fg='white', font=('Segoe UI', 10)).pack(anchor="w", padx=10, pady=(5, 5))
        self.client_secret_entry = tk.Entry(spotify_frame, width=70, show="*", bg='#404040', fg='white', font=('Consolas', 9))
        self.client_secret_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.client_secret_entry.insert(0, self.config_data.get("spotify_client_secret", ""))
        
        tk.Label(spotify_frame, text="Redirect URI:", bg='#2d2d2d', fg='white', font=('Segoe UI', 10)).pack(anchor="w", padx=10, pady=(5, 5))
        self.redirect_uri_entry = tk.Entry(spotify_frame, width=70, bg='#404040', fg='white', font=('Consolas', 9))
        self.redirect_uri_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.redirect_uri_entry.insert(0, self.config_data.get("spotify_redirect_uri", "http://127.0.0.1:8888/callback"))
        
        instructions_btn = tk.Button(spotify_frame, 
                                   text="📖 How to get Spotify credentials",
                                   command=self.show_spotify_instructions,
                                   bg='#0078d4', fg='white', 
                                   font=('Segoe UI', 9))
        instructions_btn.pack(pady=5)
        
        youtube_frame = tk.LabelFrame(main_frame, 
                                     text="🎼 YouTube Music Headers",
                                     bg='#2d2d2d',
                                     fg='white',
                                     font=('Segoe UI', 11, 'bold'))
        youtube_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        tk.Label(youtube_frame, text="Raw Headers:", bg='#2d2d2d', fg='white', font=('Segoe UI', 10)).pack(anchor="w", padx=10, pady=(10, 5))
        
        headers_frame = tk.Frame(youtube_frame, bg='#2d2d2d')
        headers_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.headers_text = tk.Text(headers_frame, 
                                  height=8, 
                                  wrap="word",
                                  bg='#404040',
                                  fg='white',
                                  font=('Consolas', 8))
        headers_scrollbar = tk.Scrollbar(headers_frame, orient="vertical", command=self.headers_text.yview)
        self.headers_text.configure(yscrollcommand=headers_scrollbar.set)
        
        self.headers_text.pack(side="left", fill="both", expand=True)
        headers_scrollbar.pack(side="right", fill="y")
        
        self.headers_text.insert("1.0", self.config_data.get("youtube_headers", ""))
        
        youtube_instructions_btn = tk.Button(youtube_frame, 
                                           text="📖 How to get YouTube Music headers",
                                           command=self.show_youtube_instructions,
                                           bg='#ff6b6b', fg='white', 
                                           font=('Segoe UI', 9))
        youtube_instructions_btn.pack(pady=5)
        
        button_frame = tk.Frame(main_frame, bg='#1e1e1e')
        button_frame.pack(fill="x", pady=(10, 0))
        
        save_btn = tk.Button(button_frame, 
                           text="💾 Save Configuration",
                           command=self.save_config,
                           bg='#107c10', fg='white', 
                           font=('Segoe UI', 10, 'bold'))
        save_btn.pack(side="left", padx=(0, 10))
        
        cancel_btn = tk.Button(button_frame, 
                             text="❌ Cancel",
                             command=self.dialog.destroy,
                             bg='#d13438', fg='white', 
                             font=('Segoe UI', 10))
        cancel_btn.pack(side="right")
        
    def update_delay_description(self, value):
        delay = int(float(value))
        
        self.current_value_label.config(text=f"Current: {delay}s")
        
        if delay <= 3:
            description = "⚡ Fast (2-3s): Quick transfer but higher chance of missing tracks due to YouTube Music rate limits."
            color = '#ff6b6b'
        elif delay <= 6:
            description = "🚀 Moderate (4-6s): Balanced speed and reliability. Some tracks might still be missed occasionally."
            color = '#ffd93d'
        elif delay <= 10:
            description = "✅ Recommended (7-10s): Good balance of speed and completeness. Most reliable for most playlists."
            color = '#6bcf7f'
        elif delay <= 15:
            description = "🐌 Slow (11-15s): Very reliable but slower transfer. Best for large playlists or unstable connections."
            color = '#4ecdc4'
        else:
            description = "🕰️ Very Slow (16s+): Maximum reliability but very slow. Use only if experiencing frequent issues."
            color = '#a8dadc'
        
        self.delay_description.config(text=description, fg=color)

    def save_config(self):
        self.config_data["spotify_client_id"] = self.client_id_entry.get().strip()
        self.config_data["spotify_client_secret"] = self.client_secret_entry.get().strip()
        self.config_data["spotify_redirect_uri"] = self.redirect_uri_entry.get().strip()
        self.config_data["youtube_headers"] = self.headers_text.get("1.0", tk.END).strip()
        
        if not self.config_data["spotify_client_id"]:
            messagebox.showerror("Error", "Spotify Client ID is required!")
            return
        if not self.config_data["spotify_client_secret"]:
            messagebox.showerror("Error", "Spotify Client Secret is required!")
            return
        if not self.config_data["youtube_headers"]:
            messagebox.showerror("Error", "YouTube Music headers are required!")
            return
        
        headers_valid, validation_msg = copy_playlists.validate_youtube_headers(self.config_data["youtube_headers"])
        if not headers_valid:
            messagebox.showerror("Invalid Headers", f"YouTube Music headers are invalid:\n{validation_msg}")
            return
        
        try:
            from ytmusicapi import setup, YTMusic
            
            with open("test_headers.txt", "w", encoding="utf-8") as f:
                f.write(self.config_data["youtube_headers"])
            
            setup(filepath="test_browser.json", headers_raw=self.config_data["youtube_headers"])
            test_ytmusic = YTMusic("test_browser.json")
            
            test_result = test_ytmusic.get_library_playlists(limit=1)
            
            try:
                os.remove("test_headers.txt")
                os.remove("test_browser.json")
            except:
                pass
                
            if test_result is None:
                messagebox.showerror("Invalid Headers", 
                                   "Headers test failed!\n"
                                   "The headers appear to be expired or invalid.\n"
                                   "Please get fresh headers from YouTube Music.")
                return
                
        except Exception as e:
            try:
                os.remove("test_headers.txt")
                os.remove("test_browser.json")
            except:
                pass
            messagebox.showerror("Headers Test Failed", 
                               f"Failed to validate headers:\n{str(e)}\n\n"
                               "Please ensure you copied the complete headers correctly.")
            return
    
        if save_config(self.config_data):
            messagebox.showinfo("Success", 
                              "Configuration saved and headers validated successfully!\n"
                              "Your YouTube Music connection is working.")
            self.callback(self.config_data)
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to save configuration!")
    
    def show_spotify_instructions(self):
        instructions = """
🎵 How to get Spotify credentials:

1. Go to https://developer.spotify.com/dashboard
2. Log in with your Spotify account
3. Click "Create App"
4. Fill in:
   - App name: "My Playlist Copier" (or any name)
   - App description: "Playlist transfer tool"
   - Redirect URI: http://127.0.0.1:8888/callback
5. Check the boxes and click "Save"
6. Click on your new app
7. Copy the "Client ID" and "Client Secret"
8. Paste them in the fields above

Note: Keep your Client Secret private!
        """
        
        msg_window = tk.Toplevel(self.dialog)
        msg_window.title("Spotify Setup Instructions")
        msg_window.geometry("500x400")
        msg_window.configure(bg='#1e1e1e')
        
        text_widget = tk.Text(msg_window, wrap="word", bg='#2d2d2d', fg='white', font=('Segoe UI', 10))
        text_widget.pack(fill="both", expand=True, padx=20, pady=20)
        text_widget.insert("1.0", instructions)
        text_widget.config(state="disabled")
    
    def show_youtube_instructions(self):
        instructions = """
🎼 How to get YouTube Music headers:

STEP-BY-STEP GUIDE:

1. Open YouTube Music in your browser (music.youtube.com)
2. Make sure you're logged in to your account
3. Press F12 to open Developer Tools
4. Click on the "Network" tab
5. Press F5 to reload the page
6. In the network list, look for a request called "browse"
7. Click on the "browse" request
8. In the right panel, click "Headers"
9. Scroll down to "Request Headers"
10. Right-click in the Request Headers section
11. Select "Copy all as cURL" or "Copy request headers"
12. Paste EVERYTHING in the text box above

IMPORTANT NOTES:
• Your headers MUST include these fields:
  - cookie: (with VISITOR_INFO1_LIVE, PREF, etc.)
  - user-agent: (browser information)
  - authorization: (SAPISIDHASH...)
  - x-client-name: WEB_REMIX
  
• Headers expire every 20-30 minutes - you'll need to update them
• Make sure you copy ALL headers, not just some
• If you get errors, try using an incognito/private browser window
• The headers contain your login info - keep them private

EXAMPLE of what your headers should look like:
accept: */*
accept-encoding: gzip, deflate, br
accept-language: en-US,en;q=0.9
authorization: SAPISIDHASH 1234567890_abcdef...
cookie: VISITOR_INFO1_LIVE=abc123; PREF=f1=50000000...
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)...
x-client-name: WEB_REMIX
x-client-version: 1.20231115.01.00
        """
        
        msg_window = tk.Toplevel(self.dialog)
        msg_window.title("YouTube Music Headers - Detailed Instructions")
        msg_window.geometry("700x650")
        msg_window.configure(bg='#1e1e1e')
        
        text_widget = tk.Text(msg_window, wrap="word", bg='#2d2d2d', fg='white', font=('Segoe UI', 9))
        text_widget.pack(fill="both", expand=True, padx=20, pady=20)
        text_widget.insert("1.0", instructions)
        text_widget.config(state="disabled")

class Spotify2YTMUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.progress_bar_state = {
            "current_value": 0,
            "maximum_value": 0,
            "paused": False
        }
        
        self.is_paused = False
        self.is_cancelled = False
        
        self.playlists_data = [] 
        self.config_data = load_config()
        
        self.title("Spotify ➡️ YouTube Music Playlist Copier")
        self.geometry("700x900")
        self.minsize(600, 600) 
        self.resizable(True, True)
        self.configure(bg='#1e1e1e')
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure('Custom.TNotebook', background='#1e1e1e', borderwidth=0)
        self.style.configure('Custom.TNotebook.Tab', 
                           background='#2d2d2d', 
                           foreground='white',
                           padding=[20, 10],
                           font=('Segoe UI', 10))
        self.style.map('Custom.TNotebook.Tab',
                      background=[('selected', '#0078d4'), ('active', '#404044')])

        self.style.configure("Treeview", 
                           background="#2d2d2d", 
                           foreground="white", 
                           fieldbackground="#2d2d2d",
                           font=('Segoe UI', 10),
                           borderwidth=0)
        self.style.map('Treeview', background=[('selected', '#0078d4')])
        
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

        main_frame = tk.Frame(self, bg='#1e1e1e')
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        main_frame.grid_rowconfigure(0, weight=0)  # Title
        main_frame.grid_rowconfigure(1, weight=0)  # Subtitle
        main_frame.grid_rowconfigure(2, weight=0)  # Settings button
        main_frame.grid_rowconfigure(3, weight=0)  # Batch size section
        main_frame.grid_rowconfigure(4, weight=1)  # Notebook/tabs (expandable)
        main_frame.grid_rowconfigure(5, weight=0)  # Status bar
        main_frame.grid_rowconfigure(6, weight=0)  # Progress bar
        main_frame.grid_columnconfigure(0, weight=1)

        title_label = tk.Label(main_frame, 
                              text="Spotify ➡️ YouTube Music", 
                              font=('Segoe UI', 18, 'bold'),
                              fg='white',
                              bg='#1e1e1e')
        title_label.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        subtitle_label = tk.Label(main_frame, 
                                 text="Transfer your music seamlessly", 
                                 font=('Segoe UI', 10),
                                 fg='#cccccc',
                                 bg='#1e1e1e')
        subtitle_label.grid(row=1, column=0, sticky="ew", pady=(0, 20))

        btn_frame = tk.Frame(main_frame, bg='#1e1e1e')
        btn_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))

        settings_btn = ttk.Button(btn_frame, 
                             text="⚙️ Settings", 
                             command=self.open_settings,
                             style='Custom.TButton')
        settings_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)

        logs_btn = ttk.Button(btn_frame, 
                             text="📜 View Logs", 
                             command=self.show_log_window,
                             style='Custom.TButton')
        logs_btn.pack(side="left", fill="x", expand=True)

        batch_frame = tk.Frame(main_frame, bg='#1e1e1e')
        batch_frame.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        self.create_batch_size_section(batch_frame)

        self.notebook = ttk.Notebook(main_frame, style='Custom.TNotebook')
        self.notebook.grid(row=4, column=0, sticky="nsew", pady=(0, 15))

        self.playlists_tab = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.liked_tab = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.artists_tab = ttk.Frame(self.notebook, style='Custom.TFrame')

        self.notebook.add(self.playlists_tab, text="🎵 Playlists")
        self.notebook.add(self.liked_tab, text="❤️ Liked Songs")
        self.notebook.add(self.artists_tab, text="👤 Artists")

        self.create_playlists_tab()
        self.create_liked_tab()
        self.create_artists_tab()

        status_frame = tk.Frame(main_frame, bg='#2d2d2d', relief='flat', bd=1)
        status_frame.grid(row=5, column=0, sticky="ew", pady=(0, 10))

        control_frame = tk.Frame(status_frame, bg='#2d2d2d')
        control_frame.pack(side="right", padx=10, pady=5)
        
        self.pause_btn = ttk.Button(control_frame, 
                                  text="⏸️ Pause", 
                                  command=self.toggle_pause,
                                  style='Custom.TButton')
        self.pause_btn.pack(side="left", padx=(0, 5))
        
        self.cancel_btn = ttk.Button(control_frame, 
                                   text="❌ Cancel", 
                                   command=self.cancel_transfer,
                                   style='Red.TButton')
        self.cancel_btn.pack(side="left")
        
        self.hide_control_buttons()

        self.progress = tk.StringVar()
        self.progress.set("Ready to transfer your music")
        status_label = tk.Label(status_frame, 
                               textvariable=self.progress, 
                               anchor="w",
                               font=('Segoe UI', 9),
                               fg='#cccccc',
                               bg='#2d2d2d')
        status_label.pack(side="left", fill="x", expand=True, padx=15, pady=8)

        self.progressbar = ttk.Progressbar(main_frame, 
                                         orient="horizontal", 
                                         mode="determinate",
                                         style='Custom.Horizontal.TProgressbar')
        self.progressbar.grid(row=6, column=0, sticky="ew", pady=(0, 15))

        self.style.configure('Custom.Horizontal.TProgressbar',
                           background='#0078d4',
                           troughcolor='#404040',
                           borderwidth=0,
                           lightcolor='#0078d4',
                           darkcolor='#0078d4')

        self.setup_log_window()

    def setup_log_window(self):
        self.log_window = tk.Toplevel(self)
        self.log_window.title("📜 Output Logs")
        self.log_window.geometry("700x500")
        self.log_window.configure(bg='#1e1e1e')
        self.log_window.protocol("WM_DELETE_WINDOW", self.hide_log_window)
        self.log_window.withdraw()

        header_frame = tk.Frame(self.log_window, bg='#1e1e1e')
        header_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(header_frame, text="Activity Log", font=('Segoe UI', 12, 'bold'), fg='white', bg='#1e1e1e').pack(side="left")
        ttk.Button(header_frame, text="Clear", command=self.clear_output, style='Red.TButton').pack(side="right")

        text_frame = tk.Frame(self.log_window, bg='#2d2d2d', relief='flat', bd=1)
        text_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.response_text = tk.Text(text_frame, height=20, state="disabled", wrap="word", bg='#2d2d2d', fg='#ffffff', font=('Consolas', 9), insertbackground='white', selectbackground='#0078d4', relief='flat', bd=0)
        
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.response_text.yview)
        self.response_text.configure(yscrollcommand=scrollbar.set)
        
        self.response_text.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

    def show_log_window(self):
        self.log_window.deiconify()
        self.log_window.lift()

    def hide_log_window(self):
        self.log_window.withdraw()

    def show_control_buttons(self):
        self.pause_btn.pack(side="left", padx=(0, 5))
        self.cancel_btn.pack(side="left")

    def hide_control_buttons(self):
        self.pause_btn.pack_forget()
        self.cancel_btn.pack_forget()

    def toggle_pause(self):
        if self.is_paused:
            self.is_paused = False
            self.pause_btn.config(text="⏸️ Pause")
            status = self.progress.get().replace(" (Paused)", "")
            self.progress.set(status)
            self.resume_progress_bar()
            self.append_response("▶️ Resumed")
        else:
            self.is_paused = True
            self.pause_btn.config(text="▶️ Resume")
            self.progress.set(self.progress.get() + " (Paused)")
            self.pause_progress_bar()
            self.append_response("⏸️ Paused")

    def cancel_transfer(self):
        if messagebox.askyesno("Cancel Transfer", "Are you sure you want to cancel the current operation?"):
            self.is_cancelled = True
            self.is_paused = False 
            self.pause_btn.config(text="⏸️ Pause")
            self.resume_progress_bar()
            self.append_response("🛑 Cancelling...")
            self.hide_control_buttons()

    def check_control_status(self):
        while self.is_paused and not self.is_cancelled:
            time.sleep(0.1)
        
        if self.is_cancelled:
            return False 
        return True

    def create_batch_size_section(self, parent):
        frame = tk.LabelFrame(parent, text="Batch Size", bg='#2d2d2d', fg='white', font=('Segoe UI', 11, 'bold'))
        frame.pack(fill="x", pady=(0, 15))

        tk.Label(frame, text="Batch size (tracks per batch):", bg='#2d2d2d', fg='white', font=('Segoe UI', 10)).pack(anchor="w", padx=10, pady=(10, 0))

        self.batch_slider = tk.Scale(
            frame, from_=1, to=20, orient=tk.HORIZONTAL,
            bg='#2d2d2d', fg='white', highlightthickness=0,
            showvalue=0, command=self.update_batch_display
        )
        self.batch_slider.set(self.config_data.get("batch_size", 5))
        self.batch_slider.pack(fill="x", padx=20, pady=(0, 0))

        self.batch_value_label = tk.Label(frame, text="", bg='#2d2d2d', fg='#4ecdc4', font=('Segoe UI', 10, 'bold'))
        self.batch_value_label.pack(anchor="w", padx=20, pady=(0, 0))

        self.batch_description = tk.Label(
            frame, text="", bg='#2d2d2d', fg='#cccccc', 
            font=('Segoe UI', 9), justify="left", wraplength=500
        )
        self.batch_description.pack(anchor="w", fill="x", padx=20, pady=(0, 10))

        presets_frame = tk.Frame(frame, bg='#2d2d2d')
        presets_frame.pack(anchor="w", padx=20, pady=(0, 10))
        tk.Label(presets_frame, text="Presets:", bg='#2d2d2d', fg='#cccccc', font=('Segoe UI', 9)).pack(side="left")
        for text, value in [("🔒 Safe", 3), ("✅ Balanced", 5), ("🚀 Fast", 10), ("⚡ Max", 15)]:
            tk.Button(
                presets_frame, text=text, font=('Segoe UI', 8, 'bold'),
                command=lambda v=value: self.set_batch_preset(v),
                bg='#404040', fg='white', relief='flat', padx=8, pady=2
            ).pack(side="left", padx=4)

        self.update_batch_display(self.batch_slider.get())
        

    def update_batch_display(self, value):
        batch_size = int(float(value))
        self.batch_value_label.config(text=f"Current: {batch_size} tracks per batch")
        if batch_size == 1:
            desc = "🐌 Single Track: Maximum reliability, very slow. Use only if having major issues."
            color = '#a8dadc'
        elif batch_size <= 3:
            desc = "🔒 Very Safe: High reliability, slower speed. Best for unstable connections."
            color = '#4ecdc4'
        elif batch_size <= 5:
            desc = "✅ Recommended: Good balance of speed and reliability. Works well for most users."
            color = '#6bcf7f'
        elif batch_size <= 8:
            desc = "🚀 Moderate Speed: Faster transfer, may occasionally miss tracks."
            color = '#ffd93d'
        elif batch_size <= 12:
            desc = "⚡ Fast: Quick transfer, higher chance of missing tracks due to rate limits."
            color = '#ff9500'
        else:
            desc = "🔥 Maximum Speed: Fastest but riskiest. May miss many tracks."
            color = '#ff6b6b'
        self.batch_description.config(text=desc, fg=color)
        self.config_data["batch_size"] = batch_size
        save_config(self.config_data)

    def set_batch_preset(self, value):
        self.batch_slider.set(value)
        self.update_batch_display(value)
        self.append_response(f"⚙️ Batch size set to {value} tracks per batch")

    def get_like_delay_seconds(self):
        try:
            delay = float(self.like_delay_var.get())
            if delay < 0:
                raise ValueError("Delay cannot be negative")
        except Exception:
            delay = 1.5
            if hasattr(self, "like_delay_var"):
                self.like_delay_var.set(f"{delay:.1f}")
        return delay

    def update_liked_delay_state(self):
        if not hasattr(self, "like_delay_spin"):
            return
        state = tk.NORMAL if self.like_liked_songs_var.get() else tk.DISABLED
        self.like_delay_spin.config(state=state)

    def on_liked_options_changed(self):
        self.config_data["like_liked_songs_on_transfer"] = bool(self.like_liked_songs_var.get())
        self.config_data["like_rate_delay_seconds"] = self.get_like_delay_seconds()
        self.update_liked_delay_state()
        save_config(self.config_data)

    def on_liked_delay_input(self, _event=None):
        self.on_liked_options_changed()

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
        container = tk.Frame(self.playlists_tab, bg='#1e1e1e')
        container.pack(fill="both", expand=True, padx=20, pady=20)

        instruction_label = tk.Label(container,
                                   text="Select playlists to transfer from Spotify to YouTube Music",
                                   font=('Segoe UI', 11),
                                   fg='#cccccc',
                                   bg='#1e1e1e')
        instruction_label.pack(side="top", pady=(0, 15), fill="x")

        btn_frame = tk.Frame(container, bg='#1e1e1e')
        btn_frame.pack(side="bottom", fill="x", pady=(15, 0))

        ttk.Button(btn_frame, 
                  text="🔄 Load Playlists", 
                  command=self.load_playlists,
                  style='Custom.TButton').pack(side="left", padx=(0, 10), fill="x", expand=True)

        ttk.Button(btn_frame, 
                  text="📋 Copy Selected", 
                  command=self.copy_selected_playlists,
                  style='Green.TButton').pack(side="left", padx=(0, 10), fill="x", expand=True)

        ttk.Button(btn_frame, 
                  text="📚 Copy All", 
                  command=self.copy_all_playlists,
                  style='Green.TButton').pack(side="left", fill="x", expand=True)

        controls_frame = tk.Frame(container, bg='#1e1e1e')
        controls_frame.pack(side="top", fill="x", pady=(0, 10))
        
        tk.Label(controls_frame, text="🔍 Filter:", bg='#1e1e1e', fg='white').pack(side="left", padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_playlists)
        search_entry = tk.Entry(controls_frame, textvariable=self.search_var, bg='#404040', fg='white', width=30)
        search_entry.pack(side="left", padx=(0, 20))
        
        tk.Label(controls_frame, text="Sort by:", bg='#1e1e1e', fg='white').pack(side="left", padx=(0, 5))
        self.sort_var = tk.StringVar(value="Default")
        sort_options = ["Default", "Name (A-Z)", "Name (Z-A)", "Tracks (High-Low)", "Tracks (Low-High)", "Status"]
        sort_combo = ttk.Combobox(controls_frame, textvariable=self.sort_var, values=sort_options, state="readonly", width=15)
        sort_combo.bind("<<ComboboxSelected>>", self.sort_playlists)
        sort_combo.pack(side="left")

        listbox_frame = tk.Frame(container, bg='#2d2d2d', relief='flat', bd=1)
        listbox_frame.pack(side="top", fill="both", expand=True)

        self.playlists_tree = ttk.Treeview(listbox_frame, 
                                         columns=("name", "status"), 
                                         show="tree", 
                                         selectmode="extended",
                                         style="Treeview")
        
        self.playlists_tree.column("#0", width=0, stretch=tk.NO)
        self.playlists_tree.column("name", anchor=tk.W, stretch=tk.YES)
        self.playlists_tree.column("status", anchor=tk.E, width=150, stretch=tk.NO)
        
        self.playlists_tree.tag_configure('odd', background='#252525')
        self.playlists_tree.tag_configure('even', background='#2d2d2d')

        listbox_scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.playlists_tree.yview)
        self.playlists_tree.configure(yscrollcommand=listbox_scrollbar.set)
        
        self.playlists_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        listbox_scrollbar.pack(side="right", fill="y", pady=10)

    def create_liked_tab(self):
        container = tk.Frame(self.liked_tab, bg='#1e1e1e')
        container.pack(fill="both", expand=True)
        
        content = tk.Frame(container, bg='#1e1e1e')
        content.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(content,
                text="❤️",
                font=('Segoe UI', 48),
                fg='#ff6b6b',
                bg='#1e1e1e').pack(pady=(40, 20))

        tk.Label(content,
                text="Transfer Your Liked Songs",
                font=('Segoe UI', 16, 'bold'),
                fg='white',
                bg='#1e1e1e').pack(pady=(0, 10))

        tk.Label(content,
                text="Copy all your Spotify liked songs to a YouTube Music playlist",
                font=('Segoe UI', 11),
                fg='#cccccc',
                bg='#1e1e1e').pack(pady=(0, 20))

        options_frame = tk.Frame(content, bg='#1e1e1e')
        options_frame.pack(pady=(0, 20))

        self.like_liked_songs_var = tk.BooleanVar(
            value=bool(self.config_data.get("like_liked_songs_on_transfer", False))
        )
        like_checkbox = tk.Checkbutton(
            options_frame,
            text="Also mark matched tracks as liked in YouTube Music",
            variable=self.like_liked_songs_var,
            command=self.on_liked_options_changed,
            bg='#1e1e1e',
            fg='white',
            activebackground='#1e1e1e',
            activeforeground='white',
            selectcolor='#2d2d2d',
            font=('Segoe UI', 10)
        )
        like_checkbox.pack(anchor="w")

        delay_row = tk.Frame(options_frame, bg='#1e1e1e')
        delay_row.pack(anchor="w", pady=(8, 0))

        tk.Label(
            delay_row,
            text="Like delay (sec):",
            bg='#1e1e1e',
            fg='#cccccc',
            font=('Segoe UI', 9)
        ).pack(side="left", padx=(0, 8))

        self.like_delay_var = tk.StringVar(
            value=str(self.config_data.get("like_rate_delay_seconds", 1.5))
        )
        self.like_delay_spin = tk.Spinbox(
            delay_row,
            from_=0,
            to=10,
            increment=0.1,
            width=6,
            textvariable=self.like_delay_var,
            command=self.on_liked_options_changed,
            bg='#404040',
            fg='white',
            insertbackground='white'
        )
        self.like_delay_spin.pack(side="left")
        self.like_delay_spin.bind("<FocusOut>", self.on_liked_delay_input)
        self.like_delay_spin.bind("<Return>", self.on_liked_delay_input)
        self.update_liked_delay_state()

        ttk.Button(content,
                  text="💖 Transfer Liked Songs",
                  command=self.copy_liked_songs,
                  style='Green.TButton').pack()

    def create_artists_tab(self):
        container = tk.Frame(self.artists_tab, bg='#1e1e1e')
        container.pack(fill="both", expand=True)

        content = tk.Frame(container, bg='#1e1e1e')
        content.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(content,
                text="👤",
                font=('Segoe UI', 48),
                fg='#4ecdc4',
                bg='#1e1e1e').pack(pady=(40, 20))

        tk.Label(content,
                text="Follow Your Artists",
                font=('Segoe UI', 16, 'bold'),
                fg='white',
                bg='#1e1e1e').pack(pady=(0, 10))

        tk.Label(content,
                text="Subscribe to your followed Spotify artists on YouTube Music",
                font=('Segoe UI', 11),
                fg='#cccccc',
                bg='#1e1e1e').pack(pady=(0, 30))

        ttk.Button(content,
                  text="👥 Follow Artists",
                  command=self.copy_followed_artists,
                  style='Green.TButton').pack()

    def load_playlists(self):
        if not self.check_configuration():
            return
            
        self.progress.set("Loading playlists from Spotify... (and checking YTM)")
        self.update_idletasks()
        
        ytm_playlists_map = copy_playlists.fetch_all_ytm_playlists()
        
        self.playlists = copy_playlists.list_spotify_playlists()
        self.playlists_data = [] 
        
        for idx, playlist in enumerate(self.playlists):
            name = playlist['name']
            total = playlist['tracks']['total'] if 'tracks' in playlist and 'total' in playlist['tracks'] else 0
            
            display_name = f"🎵 {name} ({total} tracks)"
            status_text = ""
            is_copied = False
            
            if name.strip().lower() in ytm_playlists_map:
                status_text = "✅ Copied"
                is_copied = True
            
            self.playlists_data.append({
                'original_index': idx,
                'name': name,
                'track_count': total,
                'display_name': display_name,
                'status_text': status_text,
                'is_copied': is_copied
            })

        self.refresh_playlists_view()
        self.append_response("✅ Loaded playlists successfully")
        self.progress.set(f"Loaded {len(self.playlists)} playlists")

    def filter_playlists(self, *args):
        self.refresh_playlists_view()

    def sort_playlists(self, event=None):
        self.refresh_playlists_view()

    def refresh_playlists_view(self):
        for item in self.playlists_tree.get_children():
            self.playlists_tree.delete(item)
            
        search_term = self.search_var.get().lower().strip()
        sort_mode = self.sort_var.get()
        
        filtered_data = [
            item for item in self.playlists_data 
            if search_term in item['name'].lower()
        ]
        
        if sort_mode == "Name (A-Z)":
            filtered_data.sort(key=lambda x: x['name'].lower())
        elif sort_mode == "Name (Z-A)":
            filtered_data.sort(key=lambda x: x['name'].lower(), reverse=True)
        elif sort_mode == "Tracks (High-Low)":
            filtered_data.sort(key=lambda x: x['track_count'], reverse=True)
        elif sort_mode == "Tracks (Low-High)":
            filtered_data.sort(key=lambda x: x['track_count'])
        elif sort_mode == "Status":

            filtered_data.sort(key=lambda x: x['is_copied'])
            
        for i, item in enumerate(filtered_data):
            tag = 'even' if i % 2 == 0 else 'odd'
            self.playlists_tree.insert(
                "", 
                "end", 
                iid=str(item['original_index']), 
                values=(item['display_name'], item['status_text']), 
                tags=(tag,)
            )

    def copy_selected_playlists(self):
        if not self.check_configuration():
            return
        if not self.check_api_quotas():
            return
            
        selected_iids = self.playlists_tree.selection()
        if not selected_iids:
            messagebox.showinfo("No Selection", "Please select at least one playlist.")
            return
        
        self.is_cancelled = False
        self.is_paused = False
        self.pause_btn.config(text="⏸️ Pause")
        self.show_control_buttons()
        
        playlists = [self.playlists[int(iid)] for iid in selected_iids]
        threading.Thread(target=self._copy_playlists, args=(playlists,)).start()

    def copy_all_playlists(self):
        if not self.check_configuration():
            return
        if not self.check_api_quotas():
            return
            
        self.is_cancelled = False
        self.is_paused = False
        self.pause_btn.config(text="⏸️ Pause")
        self.show_control_buttons()
        
        threading.Thread(target=self._copy_playlists, args=(self.playlists,)).start()

    def pause_progress_bar(self):
        self.progress_bar_state["current_value"] = self.progressbar["value"]
        self.progress_bar_state["maximum_value"] = self.progressbar["maximum"]
        self.progress_bar_state["paused"] = True
        
    def resume_progress_bar(self):
        if self.progress_bar_state["paused"]:
            self.progressbar["maximum"] = self.progress_bar_state["maximum_value"]
            self.progressbar["value"] = self.progress_bar_state["current_value"]
            self.progress_bar_state["paused"] = False

    def reset_progress_bar(self):
        self.progress_bar_state = {
            "current_value": 0,
            "maximum_value": 0,
            "paused": False
        }
        self.progressbar["value"] = 0
        self.progressbar["maximum"] = 100

    def show_header_expired_dialog(self, playlist_name, progress_file, operation_type="playlist"):
        self.pause_progress_bar()
        
        result = messagebox.askyesno(
            "Headers Expired", 
            f"🔑 YouTube Music headers have expired!\n\n"
            f"Progress has been saved for: {playlist_name}\n\n"
            f"Would you like to update your headers now?\n"
            f"Click 'Yes' to open settings, or 'No' to stop the transfer.",
            icon='warning'
        )
        
        if result:
            self.pending_resume = {
                "playlist_name": playlist_name,
                "operation_type": operation_type
            }
            
            def on_save(new_config):
                self.config_data = new_config
                self.update_copy_playlists_config()
                self.resume_progress_bar()
                messagebox.showinfo("Headers Updated", 
                                  "Headers updated successfully!\n"
                                  "The transfer will now resume automatically.")
                self._resume_transfer()
            
            SettingsDialog(self, self.config_data, on_save)
        else:
            self.reset_progress_bar()
            self.progress.set("Transfer stopped - headers expired")
            self.append_response(f"⏸️ Transfer stopped. Progress saved to: {progress_file}")

    def _resume_transfer(self):
        if not hasattr(self, 'pending_resume'):
            return

        resume_info = self.pending_resume
        playlist_name = resume_info["playlist_name"]
        operation_type = resume_info["operation_type"]
        remaining_playlists = resume_info.get("remaining_playlists", [])

        self.append_response(f"🔄 Resuming transfer for: {playlist_name}")

        if operation_type == "playlist":
            if hasattr(self, 'playlists'):
                for playlist in self.playlists:
                    if playlist['name'] == playlist_name:
                        threading.Thread(target=self._copy_playlists, args=([playlist],)).start()
                        break
                if remaining_playlists:
                    for pl_name in remaining_playlists:
                        for playlist in self.playlists:
                            if playlist['name'] == pl_name:
                                threading.Thread(target=self._copy_playlists, args=([playlist],)).start()
        elif operation_type == "liked_songs":
            threading.Thread(target=self._copy_liked_songs).start()

        delattr(self, 'pending_resume')

    def _copy_playlists(self, playlists):
        for playlist in playlists:
            if not self.check_control_status():
                self.append_response("🛑 Operation cancelled.")
                self.reset_progress_bar()
                return

            name = playlist['name']
            playlist_id = playlist['id']

            progress = copy_playlists.load_progress(name)
            if progress:
                self.append_response(f"📁 Found saved progress for '{name}'. Resuming...")
                tracks = copy_playlists.get_spotify_playlist_tracks(playlist_id)
                start_index = progress.get("current_track_index", 0)
                ytm_video_ids = progress["ytm_video_ids"]
                not_found_tracks = progress["not_found_tracks"]
                current_batch_index = progress.get("current_batch_index", 0)

                if current_batch_index is None:
                    current_batch_index = 0
                    self.append_response(f"⚠️ Batch index was null, starting from beginning of batching phase")
            else:
                self.progress.set(f"Processing: {name}")
                self.append_response(f"🎵 Processing playlist: {name}")
                tracks = copy_playlists.get_spotify_playlist_tracks(playlist_id)
                if not tracks:
                    self.append_response(f"⚠️ No tracks found in playlist: {name}")
                    continue
                start_index = 0
                ytm_video_ids = []
                not_found_tracks = []
                current_batch_index = 0

            ytm_playlist_id, already_exists = copy_playlists.create_or_get_ytm_playlist(name)
            if not ytm_playlist_id:
                self.append_response(f"❌ Failed to create playlist: {name}")
                continue

            existing_video_ids = set()
            if already_exists and not progress:
                self.append_response(f"📋 Playlist exists, checking for new songs...")
                existing_video_ids = copy_playlists.get_ytm_playlist_song_video_ids(ytm_playlist_id)

            if not self.progress_bar_state["paused"]:
                self.progressbar["maximum"] = len(tracks)
                self.progressbar["value"] = start_index

            batch_size = int(self.batch_slider.get())

            try:
                if progress and ytm_video_ids:
                    self.append_response(
                        f"📤 Resuming: adding remaining tracks from batch {current_batch_index + 1}..."
                    )
                    self.append_response(f"⚙️ Using batch size: {batch_size} tracks per batch")

                    if not self.progress_bar_state["paused"]:
                        self.progressbar["maximum"] = len(ytm_video_ids)
                        completed_tracks = current_batch_index * batch_size
                        self.progressbar["value"] = completed_tracks

                    def progress_callback(current):
                        base = current_batch_index * batch_size
                        total_progress = base + current
                        if not self.progress_bar_state["paused"]:
                            self.progressbar["value"] = min(total_progress, len(ytm_video_ids))
                            self.progress.set(f"Adding tracks: {total_progress}/{len(ytm_video_ids)}")
                            self.update_idletasks()

                    def error_callback(msg):
                        self.append_response(msg)

                    try:
                        actually_added, failed_batches = copy_playlists.add_tracks_with_delayed_verification(
                            ytm_playlist_id,
                            ytm_video_ids,
                            batch_size=batch_size,
                            batch_delay=5,
                            verification_delay=30,
                            progress_callback=progress_callback,
                            start_batch_index=current_batch_index,
                            error_callback=error_callback,
                            control_callback=self.check_control_status
                        )

                        if self.is_cancelled:
                            self.append_response("🛑 Operation cancelled during batch processing.")
                            self.reset_progress_bar()
                            return

                        if not self.progress_bar_state["paused"]:
                            self.progressbar["value"] = len(ytm_video_ids)

                        if len(actually_added) == len(ytm_video_ids):
                            self.append_response(
                                f"✅ Perfect success! All {len(actually_added)} tracks added to: {name}"
                            )
                        elif len(actually_added) > 0:
                            success_rate = (len(actually_added) / len(ytm_video_ids)) * 100
                            self.append_response(
                                f"⚠️ Partial success: {len(actually_added)}/{len(ytm_video_ids)} "
                                f"tracks added ({success_rate:.1f}%)"
                            )
                            self.append_response(
                                f"Missing {len(ytm_video_ids) - len(actually_added)} tracks may appear later "
                                "due to YouTube Music delays"
                            )
                        else:
                            self.append_response(f"❌ No tracks were successfully added to: {name}")

                        if failed_batches:
                            failed_count = sum(len(batch) for batch in failed_batches)
                            self.append_response(
                                f"⚠️ {failed_count} tracks failed during batch adding (network/API issues)"
                            )

                    except copy_playlists.HeaderExpiredError as e:
                        expired_batch_index = getattr(e, "batch_index", current_batch_index)
                        self.append_response(f"🔑 Headers expired during batch {expired_batch_index + 1}")
                        
                        progress_file = copy_playlists.save_progress(
                            name, len(tracks), len(tracks), ytm_video_ids, not_found_tracks, "playlist",
                            current_batch_index=expired_batch_index
                        )
                        self.show_header_expired_dialog(name, progress_file, "playlist")
                        return

                else:
                    for idx in range(start_index, len(tracks)):
                        if not self.check_control_status():
                            self.append_response("Operation cancelled.")
                            self.reset_progress_bar()
                            return

                        track = tracks[idx]
                        video_id = copy_playlists.search_track_on_ytm(track)
                        if video_id and video_id not in existing_video_ids:
                            ytm_video_ids.append(video_id)
                        elif not video_id:
                            not_found_tracks.append(track)

                        if not self.progress_bar_state["paused"]:
                            self.progressbar["value"] = idx + 1
                            self.progress.set(f"Searching: {idx + 1}/{len(tracks)} - {track[:50]}...")
                            self.update_idletasks()

                    if ytm_video_ids and not self.progress_bar_state["paused"]:
                        self.progressbar["maximum"] = len(ytm_video_ids)
                        self.progressbar["value"] = 0

                    if ytm_video_ids:
                        try:
                            self.append_response(
                                f"📤 Adding {len(ytm_video_ids)} tracks with batch size {batch_size}..."
                            )

                            def progress_callback(current):
                                base = current_batch_index * batch_size
                                total_progress = base + current
                                if not self.progress_bar_state["paused"]:
                                    self.progressbar["value"] = min(total_progress, len(ytm_video_ids))
                                    self.progress.set(
                                        f"Adding tracks: {total_progress}/{len(ytm_video_ids)}"
                                    )
                                    self.update_idletasks()

                            def error_callback(msg):
                                self.append_response(msg)

                            actually_added, failed_batches = copy_playlists.add_tracks_with_delayed_verification(
                                ytm_playlist_id,
                                ytm_video_ids,
                                batch_size=batch_size,
                                batch_delay=5,
                                verification_delay=30,
                                progress_callback=progress_callback,
                                start_batch_index=0,
                                error_callback=error_callback,
                                control_callback=self.check_control_status
                            )

                            if self.is_cancelled:
                                self.append_response("🛑 Operation cancelled during batch processing.")
                                self.reset_progress_bar()
                                return

                            if not self.progress_bar_state["paused"]:
                                self.progressbar["value"] = len(ytm_video_ids)

                            if len(actually_added) == len(ytm_video_ids):
                                self.append_response(
                                    f"✅ Perfect success! All {len(actually_added)} tracks added to: {name}"
                                )
                            elif len(actually_added) > 0:
                                success_rate = (len(actually_added) / len(ytm_video_ids)) * 100
                                self.append_response(
                                    f"⚠️ Partial success: {len(actually_added)}/{len(ytm_video_ids)} "
                                    f"tracks added ({success_rate:.1f}%)"
                                )
                                self.append_response(
                                    f"Missing {len(ytm_video_ids) - len(actually_added)} tracks may appear later "
                                    "due to YouTube Music delays"
                                )
                            else:
                                self.append_response(f"❌ No tracks were successfully added to: {name}")

                            if failed_batches:
                                failed_count = sum(len(batch) for batch in failed_batches)
                                self.append_response(
                                    f"⚠️ {failed_count} tracks failed during batch adding (network/API issues)"
                                )

                        except copy_playlists.HeaderExpiredError as e:
                            expired_batch_index = getattr(e, "batch_index", 0)
                            self.append_response(f"🔑 Headers expired during batch {expired_batch_index + 1}")

                            progress_file = copy_playlists.save_progress(
                                name, len(tracks), len(tracks), ytm_video_ids, not_found_tracks, "playlist",
                                current_batch_index=expired_batch_index
                            )
                            self.show_header_expired_dialog(name, progress_file, "playlist")
                            return
                    else:
                        self.append_response(f"ℹ️ No new tracks to add for: {name}")
                        if not self.progress_bar_state["paused"]:
                            self.progressbar["maximum"] = 1
                            self.progressbar["value"] = 1

                if not_found_tracks:
                    self.append_response(f"⚠️ {len(not_found_tracks)} tracks not found on YouTube Music")
                    for track in not_found_tracks[:10]:
                        self.append_response(f"   {track}")
                    if len(not_found_tracks) > 10:
                        self.append_response(f"   ... and {len(not_found_tracks) - 10} more")

                try:
                    self.append_response(f"📊 Generating verification report for '{name}'...")
                    copy_playlists.verify_transfer_completeness(tracks, ytm_playlist_id, name)
                    safe_name = "".join(
                        [c for c in name if c.isalpha() or c.isdigit() or c == ' ']
                    ).rstrip().replace(" ", "_")
                    self.append_response(f"📄 Report saved to: migration_report_{safe_name}.json")
                except Exception as e:
                    self.append_response(f"⚠️ Failed to generate report: {e}")

                copy_playlists.delete_progress(name)
                self.reset_progress_bar()

            except copy_playlists.HeaderExpiredError:
                progress_file = copy_playlists.save_progress(
                    name, idx, len(tracks), ytm_video_ids, not_found_tracks, "playlist"
                )
                self.show_header_expired_dialog(name, progress_file, "playlist")
                return

        self.progress.set("✅ Playlist transfer completed")
        self.append_response("🎉 Finished copying all playlists")
        self.after(0, self.hide_control_buttons)
        messagebox.showinfo("Success", "Playlists transferred successfully!")
    def _copy_liked_songs(self):
        playlist_name = "Liked Songs from Spotify"
        like_on_transfer = bool(
            self.like_liked_songs_var.get()
            if hasattr(self, "like_liked_songs_var")
            else self.config_data.get("like_liked_songs_on_transfer", False)
        )
        like_delay_seconds = self.get_like_delay_seconds() if hasattr(self, "like_delay_var") else 1.5
        last_processed_index = 0
        liked_video_candidates = []

        progress = copy_playlists.load_progress(playlist_name)
        if progress:
            self.append_response(f"📁 Found saved progress for '{playlist_name}'. Resuming...")
            liked_songs = copy_playlists.get_spotify_liked_songs()
            start_index = progress["current_track_index"]
            last_processed_index = start_index
            ytm_video_ids = progress["ytm_video_ids"]
            not_found_tracks = progress["not_found_tracks"]
            current_batch_index = progress.get("current_batch_index", 0)
            liked_video_candidates = list(ytm_video_ids)

            if current_batch_index is None:
                current_batch_index = 0
                self.append_response(f"⚠️ Batch index was null, starting from beginning of batching phase")
        else:
            self.progress.set("Fetching liked songs...")
            self.append_response("💖 Fetching liked songs from Spotify...")
            liked_songs = copy_playlists.get_spotify_liked_songs()
            if not liked_songs:
                self.progress.set("No liked songs found")
                self.append_response("⚠️ No liked songs found on Spotify")
                messagebox.showinfo("No Liked Songs", "No liked songs found on Spotify.")
                return
            start_index = 0
            ytm_video_ids = []
            not_found_tracks = []
            current_batch_index = 0

        ytm_playlist_id, already_exists = copy_playlists.create_or_get_ytm_playlist(playlist_name)
        if not ytm_playlist_id:
            self.progress.set("Failed to create playlist")
            self.append_response("❌ Failed to create playlist on YouTube Music")
            return

        existing_video_ids = set()
        if already_exists and not progress:
            self.append_response("Playlist exists, checking for new songs...")
            existing_video_ids = copy_playlists.get_ytm_playlist_song_video_ids(ytm_playlist_id)

        if not self.progress_bar_state["paused"]:
            self.progressbar["maximum"] = len(liked_songs)
            self.progressbar["value"] = start_index

        batch_size = int(self.batch_slider.get())

        try:
            if progress and ytm_video_ids:
                self.append_response(
                    f"📤 Resuming: adding remaining liked songs from batch {current_batch_index + 1}..."
                )
                self.append_response(f"⚙️ Using batch size: {batch_size} tracks per batch")

                if not self.progress_bar_state["paused"]:
                    self.progressbar["maximum"] = len(ytm_video_ids)
                    completed_tracks = current_batch_index * batch_size
                    self.progressbar["value"] = completed_tracks

                def progress_callback(current):
                    base = current_batch_index * batch_size
                    total_progress = base + current
                    if not self.progress_bar_state["paused"]:
                        self.progressbar["value"] = min(total_progress, len(ytm_video_ids))
                        self.progress.set(f"Adding tracks: {total_progress}/{len(ytm_video_ids)}")
                        self.update_idletasks()

                def error_callback(msg):
                    self.append_response(msg)

                try:
                    actually_added, _failed_batches = copy_playlists.add_tracks_with_delayed_verification(
                        ytm_playlist_id,
                        ytm_video_ids,
                        batch_size=batch_size,
                        batch_delay=5,
                        verification_delay=30,
                        progress_callback=progress_callback,
                        start_batch_index=current_batch_index,
                        error_callback=error_callback,
                        control_callback=self.check_control_status
                    )

                    if self.is_cancelled:
                        self.append_response("🛑 Operation cancelled during batch processing.")
                        self.reset_progress_bar()
                        return

                    if not self.progress_bar_state["paused"]:
                        self.progressbar["value"] = len(ytm_video_ids)

                    if len(actually_added) == len(ytm_video_ids):
                        self.append_response(f"✅ Perfect success! All {len(actually_added)} liked songs added")
                    elif len(actually_added) > 0:
                        success_rate = (len(actually_added) / len(ytm_video_ids)) * 100
                        self.append_response(
                            f"⚠️ Partial success: {len(actually_added)}/{len(ytm_video_ids)} "
                            f"liked songs added ({success_rate:.1f}%)"
                        )
                    else:
                        self.append_response("❌ No liked songs were successfully added")

                except copy_playlists.HeaderExpiredError as e:
                    expired_batch_index = getattr(e, "batch_index", current_batch_index)
                    self.append_response(f"🔑 Headers expired during batch {expired_batch_index + 1}")

                    progress_file = copy_playlists.save_progress(
                        playlist_name,
                        len(liked_songs),
                        len(liked_songs),
                        ytm_video_ids,
                        not_found_tracks,
                        "liked_songs",
                        current_batch_index=expired_batch_index
                    )
                    self.show_header_expired_dialog(playlist_name, progress_file, "liked_songs")
                    return
            else:
                for idx in range(start_index, len(liked_songs)):
                    if not self.check_control_status():
                        self.append_response("🛑 Operation cancelled.")
                        self.reset_progress_bar()
                        return

                    last_processed_index = idx
                    track = liked_songs[idx]
                    video_id = copy_playlists.search_track_on_ytm(track)
                    if video_id:
                        liked_video_candidates.append(video_id)
                        if video_id not in existing_video_ids:
                            ytm_video_ids.append(video_id)
                    else:
                        not_found_tracks.append(track)

                    if not self.progress_bar_state["paused"]:
                        self.progressbar["value"] = idx + 1
                        self.progress.set(f"Searching: {idx + 1}/{len(liked_songs)} - {track[:50]}...")
                        self.update_idletasks()

                if ytm_video_ids and not self.progress_bar_state["paused"]:
                    self.progressbar["maximum"] = len(ytm_video_ids)
                    self.progressbar["value"] = 0

                if ytm_video_ids:
                    try:
                        self.append_response(
                            f"📤 Adding {len(ytm_video_ids)} liked songs with batch size {batch_size}..."
                        )

                        def progress_callback(current):
                            base = current_batch_index * batch_size
                            total_progress = base + current
                            if not self.progress_bar_state["paused"]:
                                self.progressbar["value"] = min(total_progress, len(ytm_video_ids))
                                self.progress.set(
                                    f"Adding tracks: {total_progress}/{len(ytm_video_ids)}"
                                )
                                self.update_idletasks()

                        def error_callback(msg):
                            self.append_response(msg)

                        actually_added, _failed_batches = copy_playlists.add_tracks_with_delayed_verification(
                            ytm_playlist_id,
                            ytm_video_ids,
                            batch_size=batch_size,
                            batch_delay=5,
                            verification_delay=30,
                            progress_callback=progress_callback,
                            start_batch_index=0,
                            error_callback=error_callback,
                            control_callback=self.check_control_status
                        )

                        if self.is_cancelled:
                            self.append_response("🛑 Operation cancelled during batch processing.")
                            self.reset_progress_bar()
                            return

                        if not self.progress_bar_state["paused"]:
                            self.progressbar["value"] = len(ytm_video_ids)

                        if len(actually_added) == len(ytm_video_ids):
                            self.append_response(f"✅ Perfect success! All {len(actually_added)} liked songs added")
                        elif len(actually_added) > 0:
                            success_rate = (len(actually_added) / len(ytm_video_ids)) * 100
                            self.append_response(
                                f"⚠️ Partial success: {len(actually_added)}/{len(ytm_video_ids)} "
                                f"liked songs added ({success_rate:.1f}%)"
                            )
                        else:
                            self.append_response("❌ No liked songs were successfully added")

                    except copy_playlists.HeaderExpiredError as e:
                        expired_batch_index = getattr(e, "batch_index", 0)
                        self.append_response(f"🔑 Headers expired during batch {expired_batch_index + 1}")

                        progress_file = copy_playlists.save_progress(
                            playlist_name,
                            len(liked_songs),
                            len(liked_songs),
                            ytm_video_ids,
                            not_found_tracks,
                            "liked_songs",
                            current_batch_index=expired_batch_index
                        )
                        self.show_header_expired_dialog(playlist_name, progress_file, "liked_songs")
                        return
                else:
                    self.append_response("ℹ️ No new liked songs to add")
                    if not self.progress_bar_state["paused"]:
                        self.progressbar["maximum"] = 1
                        self.progressbar["value"] = 1

            if like_on_transfer:
                unique_like_targets = list(
                    dict.fromkeys(liked_video_candidates if liked_video_candidates else ytm_video_ids)
                )
                if unique_like_targets:
                    self.append_response(
                        f"Applying likes for {len(unique_like_targets)} matched tracks "
                        f"(delay {like_delay_seconds:.1f}s)..."
                    )

                    if not self.progress_bar_state["paused"]:
                        self.progressbar["maximum"] = len(unique_like_targets)
                        self.progressbar["value"] = 0

                    def like_progress_callback(current, total, _target):
                        if not self.progress_bar_state["paused"]:
                            self.progressbar["maximum"] = total
                            self.progressbar["value"] = current
                            self.progress.set(f"Liking tracks: {current}/{total}")
                            self.update_idletasks()

                    def like_error_callback(message):
                        self.append_response(message)

                    like_result = copy_playlists.like_tracks_on_ytm(
                        track_video_ids=unique_like_targets,
                        delay_seconds=like_delay_seconds,
                        progress_callback=like_progress_callback,
                        error_callback=like_error_callback,
                        control_callback=self.check_control_status
                    )

                    if like_result.get("cancelled"):
                        self.append_response("Operation cancelled while applying likes.")
                        self.reset_progress_bar()
                        return

                    self.append_response(
                        "Like sync completed: "
                        f"{like_result['liked']}/{like_result['total']} liked, "
                        f"{like_result['failed']} failed, {like_result['skipped']} skipped."
                    )
                else:
                    self.append_response("No matched tracks available for like sync.")

            if not_found_tracks:
                self.append_response(f"⚠️ {len(not_found_tracks)} songs not found on YouTube Music")
                for track in not_found_tracks[:10]:
                    self.append_response(f"   {track}")
                if len(not_found_tracks) > 10:
                    self.append_response(f"   ... and {len(not_found_tracks) - 10} more")

            try:
                self.append_response(f"📊 Generating verification report for '{playlist_name}'...")
                copy_playlists.verify_transfer_completeness(liked_songs, ytm_playlist_id, playlist_name)
                safe_name = "".join(
                    [c for c in playlist_name if c.isalpha() or c.isdigit() or c == ' ']
                ).rstrip().replace(" ", "_")
                self.append_response(f"📄 Report saved to: migration_report_{safe_name}.json")
            except Exception as e:
                self.append_response(f"⚠️ Failed to generate report: {e}")

            copy_playlists.delete_progress(playlist_name)
            self.reset_progress_bar()

        except copy_playlists.HeaderExpiredError:
            progress_file = copy_playlists.save_progress(
                playlist_name,
                last_processed_index,
                len(liked_songs),
                ytm_video_ids,
                not_found_tracks,
                "liked_songs"
            )
            self.show_header_expired_dialog(playlist_name, progress_file, "liked_songs")
            return
            
        self.progress.set("✅ Liked songs transfer completed")
        self.append_response("🎉 Finished copying liked songs!")
        self.after(0, self.hide_control_buttons)
        messagebox.showinfo("Success", "Liked songs transferred successfully!")
    def copy_liked_songs(self):
        if not self.check_configuration():
            return
        if not self.check_api_quotas():
            return

        self.is_cancelled = False
        self.is_paused = False
        self.pause_btn.config(text="⏸️ Pause")
        self.show_control_buttons()

        threading.Thread(target=self._copy_liked_songs).start()
    def copy_followed_artists(self):
        if not self.check_configuration():
            return
            
        self.is_cancelled = False
        self.is_paused = False
        self.pause_btn.config(text="⏸️ Pause")
        self.show_control_buttons()

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
        copy_playlists.subscribe_to_ytm_artists(artists, control_callback=self.check_control_status)
        
        if self.is_cancelled:
            self.append_response("🛑 Operation cancelled.")
            return

        self.progress.set("✅ Artist subscription completed")
        self.append_response("🎉 Finished subscribing to artists!")
        self.after(0, self.hide_control_buttons)
        messagebox.showinfo("Success", "Artists followed successfully!")

    def open_settings(self):
        def on_save(new_config):
            self.config_data = new_config
            self.update_copy_playlists_config()
            
        SettingsDialog(self, self.config_data, on_save)

    def update_copy_playlists_config(self):
        try:
            if self.config_data.get("youtube_headers"):
                with open("raw_headers.txt", "w", encoding="utf-8") as f:
                    f.write(self.config_data["youtube_headers"])
            
            from ytmusicapi import setup
            if self.config_data.get("youtube_headers"):
                setup(filepath="browser.json", headers_raw=self.config_data["youtube_headers"])
            
            copy_playlists.initialize_clients(self.config_data)
            
            self.append_response("✅ Configuration updated successfully!")
            
        except Exception as e:
            self.append_response(f"❌ Error updating configuration: {e}")
            messagebox.showerror("Configuration Error", f"Failed to update configuration:\n{e}")

    def check_configuration(self):
        if not self.config_data.get("spotify_client_id") or not self.config_data.get("spotify_client_secret"):
            messagebox.showerror("Configuration Required", 
                               "Please configure your Spotify credentials in Settings first!")
            return False
        
        if not self.config_data.get("youtube_headers"):
            messagebox.showerror("Configuration Required", 
                               "Please configure your YouTube Music headers in Settings first!")
            return False
        
        return True

    def check_api_quotas(self):
        self.append_response("🔍 Checking API quotas...")
        try:
            ok, feedback = copy_playlists.perform_quota_check()
            self.append_response(feedback)
            if "track count is 0" in feedback.lower():
                proceed = messagebox.askyesno(
                    "YouTube Music Quota/Cache Warning",
                    feedback + "\n\nDo you want to continue anyway?"
                )
                if proceed:
                    self.append_response("⚠️ Proceeding despite track count/cache warning.")
                    return True
                else:
                    self.append_response("❌ User cancelled due to track count/cache warning.")
                    return False
            elif ok:
                self.append_response("✅ All APIs ready!")
                return True
            else:
                self.append_response("❌ API quota check failed!")
                messagebox.showerror("API Quota Error", feedback)
                return False
        except Exception as e:
            self.append_response(f"❌ Quota check error: {e}")
            messagebox.showerror("Quota Check Failed", f"Failed to check API quotas:\n{e}")
            return False

    def update_verification_progress(self, current_batch, total_batches, added_count, total_tracks):
        self.progress.set(f"Verifying batch {current_batch}/{total_batches} - {added_count}/{total_tracks} tracks added")
        self.update_idletasks()

    def update_batch_progress(self, current, total):
        self.progressbar["value"] = current
        self.progress.set(f"Adding tracks: {current}/{total}")
        self.update_idletasks()
        
if __name__ == "__main__":
    config = load_config()
    app = Spotify2YTMUI()
    app.mainloop()



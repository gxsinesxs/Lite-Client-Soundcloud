import customtkinter as ctk
import requests
import threading
import vlc
import json
import os

class LiteCloud(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("LiteCloud v1.4 | UX Improved")
        self.geometry("1100x750")
        ctk.set_appearance_mode("dark")
        
        # Colors
        self.accent_color = "#FF5500"
        self.bg_color = "#0F0F0F"
        self.card_color = "#1A1A1A"
        self.hover_color = "#2A2A2A"

        self.client_id = "WU4bVxk5Df0g5JC8ULzW77Ry7OM10Lyj"
        self.db_file = "playlists.json"
        
        self.current_queue = [] 
        self.current_track_index = -1
        
        self.instance = vlc.Instance('--no-video', '--quiet')
        self.player = self.instance.media_player_new()
        
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.vlc_end_callback)

        self.load_playlists()

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.configure(fg_color=self.bg_color)

        # SIDEBAR
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#050505")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo = ctk.CTkLabel(self.sidebar, text="LITECLOUD", font=("Segoe UI", 24, "bold"), text_color=self.accent_color)
        self.logo.pack(pady=40)

        self.search_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Search tracks...", height=35, corner_radius=10)
        self.search_entry.pack(fill="x", padx=20, pady=5)
        
        self.search_btn = ctk.CTkButton(self.sidebar, text="Explore", font=("Segoe UI", 13, "bold"),
                                        fg_color=self.accent_color, hover_color="#CC4400", 
                                        height=35, corner_radius=10, command=self.start_search)
        self.search_btn.pack(padx=20, pady=15, fill="x")

        self.nav_label = ctk.CTkLabel(self.sidebar, text="YOUR LIBRARY", font=("Segoe UI", 11, "bold"), text_color="#666")
        self.nav_label.pack(pady=(20, 10), padx=25, anchor="w")

        self.btn_fav = ctk.CTkButton(self.sidebar, text="  ❤  Liked Tracks", font=("Segoe UI", 14),
                                     fg_color="transparent", hover_color=self.hover_color, 
                                     anchor="w", height=40, command=self.show_favorites)
        self.btn_fav.pack(fill="x", padx=10)

        # MAIN VIEW
        self.main_view = ctk.CTkScrollableFrame(self, corner_radius=15, fg_color=self.bg_color)
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # PLAYER BAR
        self.player_bar = ctk.CTkFrame(self, height=110, fg_color="#111111", border_width=1, border_color="#222")
        self.player_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.track_info = ctk.CTkFrame(self.player_bar, fg_color="transparent", width=250)
        self.track_info.pack_propagate(False)
        self.track_info.pack(side="left", padx=30)
        self.now_playing_title = ctk.CTkLabel(self.track_info, text="Not Playing", font=("Segoe UI", 14, "bold"), anchor="w")
        self.now_playing_title.pack(fill="x", pady=(20, 0))
        self.now_playing_artist = ctk.CTkLabel(self.track_info, text="Select a track", font=("Segoe UI", 12), text_color="#888", anchor="w")
        self.now_playing_artist.pack(fill="x")

        self.controls = ctk.CTkFrame(self.player_bar, fg_color="transparent")
        self.controls.pack(side="left", expand=True)
        self.play_btn = ctk.CTkButton(self.controls, text="▶", width=50, height=50, 
                                      corner_radius=25, font=("Arial", 20),
                                      fg_color="white", text_color="black", hover_color="#DDD", 
                                      command=self.toggle_playback)
        self.play_btn.pack(pady=5)

        self.progress = ctk.CTkSlider(self.controls, from_=0, to=100, width=450, 
                                      button_color=self.accent_color, progress_color=self.accent_color, height=15)
        self.progress.set(0)
        self.progress.pack()

        ctk.CTkLabel(self.player_bar, text="powered by\nSOUNDCLOUD", font=("Segoe UI", 9, "bold"), text_color="#444").pack(side="right", padx=20)

        # New Features:
        self.search_entry.bind("<Return>", lambda e: self.start_search())
        self.bind_all("<MouseWheel>", self.on_mousewheel)
        
        self.update_slider_loop()

    # --- LOGIC ---

    def on_mousewheel(self, event):
        try:
            self.main_view._parent_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except: pass

    def vlc_end_callback(self, event):
        self.after(100, self.play_next_track)

    def play_next_track(self):
        if self.current_track_index + 1 < len(self.current_queue):
            next_idx = self.current_track_index + 1
            track = self.current_queue[next_idx]
            self.play_track(track['title'], track['artist'], track['stream_url'], next_idx)

    def update_slider_loop(self):
        try:
            if self.player.is_playing():
                length = self.player.get_length()
                if length > 0:
                    pos = self.player.get_time()
                    self.progress.set((pos / length) * 100)
            self.after(1000, self.update_slider_loop)
        except: pass

    def load_playlists(self):
        if os.path.exists(self.db_file):
            with open(self.db_file, "r", encoding="utf-8") as f: self.favorites = json.load(f)
        else: self.favorites = []

    def save_playlists(self):
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, indent=4, ensure_ascii=False)

    def toggle_playback(self):
        if self.player.is_playing():
            self.player.pause()
            self.play_btn.configure(text="▶")
        else:
            self.player.play()
            self.play_btn.configure(text="⏸")

    def start_search(self):
        query = self.search_entry.get()
        if query:
            self.search_btn.configure(state="disabled", text="Searching...")
            threading.Thread(target=self.run_manual_search, args=(query,), daemon=True).start()

    def run_manual_search(self, query):
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            params = {"q": query, "client_id": self.client_id, "limit": 25}
            resp = requests.get("https://api-v2.soundcloud.com/search/tracks", headers=headers, params=params, timeout=10)
            tracks = resp.json().get("collection", [])

            self.after(0, self.clear_main_view)
            self.current_queue = [] 

            self.after(0, lambda: ctk.CTkLabel(self.main_view, text=f"Results for '{query}'", font=("Segoe UI", 24, "bold")).pack(pady=20, padx=20, anchor="w"))

            for track in tracks:
                if not isinstance(track, dict): continue
                title = track.get("title", "Unknown")
                artist = track.get("user", {}).get("username", "Unknown")
                media = track.get("media", {})
                if not media: continue
                
                transcodings = media.get("transcodings", [])
                s_url = next((t.get("url") for t in transcodings if isinstance(t, dict) and t.get("format", {}).get("protocol") == "hls"), None)
                
                if s_url:
                    track_data = {"title": title, "artist": artist, "stream_url": s_url}
                    self.current_queue.append(track_data)
                    self.after(0, self.add_track_card, title, artist, s_url, len(self.current_queue)-1)
        except Exception as e: print(f"Search Error: {e}")
        finally: self.after(0, lambda: self.search_btn.configure(state="normal", text="Explore"))

    def show_favorites(self):
        self.clear_main_view()
        self.current_queue = self.favorites
        ctk.CTkLabel(self.main_view, text="Liked Songs", font=("Segoe UI", 32, "bold")).pack(pady=20, padx=20, anchor="w")
        if not self.favorites:
            ctk.CTkLabel(self.main_view, text="Empty library.", font=("Segoe UI", 14), text_color="#666").pack(pady=40)
            return
        for i, track in enumerate(self.favorites):
            self.add_track_card(track['title'], track['artist'], track['stream_url'], i, is_fav_view=True)

    def add_track_card(self, title, artist, stream_url, index, is_fav_view=False):
        card = ctk.CTkFrame(self.main_view, height=80, fg_color=self.card_color, corner_radius=12)
        card.pack(fill="x", pady=6, padx=10)
        
        txt = ctk.CTkFrame(card, fg_color="transparent")
        txt.pack(side="left", padx=20, fill="both", expand=True)
        ctk.CTkLabel(txt, text=title[:50], font=("Segoe UI", 14, "bold"), anchor="w").pack(fill="x", pady=(10, 0))
        ctk.CTkLabel(txt, text=artist, font=("Segoe UI", 12), text_color="#aaa", anchor="w").pack(fill="x")
        
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(side="right", padx=15)

        if is_fav_view:
            ctk.CTkButton(btn_frame, text="🗑", width=35, height=35, corner_radius=10, fg_color="transparent", 
                          text_color="#ff4444", hover_color="#331111", command=lambda s=stream_url: self.remove_from_favorites(s)).pack(side="left", padx=5)
        else:
            track_data = {"title": title, "artist": artist, "stream_url": stream_url}
            ctk.CTkButton(btn_frame, text="❤", width=35, height=35, corner_radius=10, fg_color="transparent", 
                          text_color=self.accent_color, hover_color=self.hover_color, command=lambda td=track_data: self.add_to_favorites(td)).pack(side="left", padx=5)

        ctk.CTkButton(btn_frame, text="Play", width=80, height=35, corner_radius=10, fg_color="#333", 
                      hover_color=self.accent_color, command=lambda: self.play_track(title, artist, stream_url, index)).pack(side="left", padx=5)
        
    def remove_from_favorites(self, stream_url):
        self.favorites = [f for f in self.favorites if f['stream_url'] != stream_url]
        self.save_playlists()
        self.show_favorites()

    def add_to_favorites(self, track_data):
        if not any(f['stream_url'] == track_data['stream_url'] for f in self.favorites):
            self.favorites.append(track_data)
            self.save_playlists()

    def play_track(self, title, artist, stream_url, index):
        if not stream_url: return
        self.current_track_index = index
        def async_play():
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                resp = requests.get(f"{stream_url}?client_id={self.client_id}", headers=headers, timeout=7)
                if resp.status_code == 200:
                    m3u8 = resp.json().get("url")
                    if m3u8:
                        self.player.set_media(self.instance.media_new(m3u8))
                        self.player.play()
                        self.after(0, lambda: self.now_playing_title.configure(text=title[:40]))
                        self.after(0, lambda: self.now_playing_artist.configure(text=artist))
                        self.after(0, lambda: self.play_btn.configure(text="⏸"))
            except Exception as e: print(f"Playback Thread Error: {e}")
        threading.Thread(target=async_play, daemon=True).start()

    def clear_main_view(self):
        for widget in self.main_view.winfo_children(): widget.destroy()

if __name__ == "__main__":
    app = LiteCloud()
    app.mainloop()
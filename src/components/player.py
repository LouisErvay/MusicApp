import dearpygui.dearpygui as dpg
import pygame
import time
from threading import Thread, Event
from mutagen.mp3 import MP3
import ntpath

class MusicPlayer:
    def __init__(self):
        self.state = None
        self.current_song = None
        self.playing_thread = None
        self.playing_event = Event()
        self._DEFAULT_MUSIC_VOLUME = 0.5
        pygame.mixer.music.set_volume(self._DEFAULT_MUSIC_VOLUME)
        self.END_EVENT = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.END_EVENT)
        self.slider_value = 0
        self.slider_dragging = False
        self.current_position = 0
        self.thread_lock = Event()
        self.song_list = None  # Sera défini lors de la connexion des composants

    def cleanup_thread(self):
        """Nettoie proprement le thread en cours"""
        if self.playing_thread and self.playing_thread.is_alive():
            self.playing_event.set()
            self.playing_thread.join(timeout=1.0)
            self.playing_event.clear()
            self.playing_thread = None

    def create(self):
        with dpg.group(tag="center_header"):
            with dpg.child_window(autosize_x=True, height=60, no_scrollbar=True, width=20):
                with dpg.group(horizontal=True):
                    with dpg.group(horizontal=False):
                        with dpg.group(horizontal=True):
                            dpg.add_button(label="Random", width=65, height=30, tag="play", callback=self.play_pause)
                            dpg.add_button(label="Stop", callback=self.stop, width=65, height=30)
                        dpg.add_spacer()
                        dpg.add_slider_float(tag="volume", width=140, height=10, format="%.0f%.0%",
                                         default_value=self._DEFAULT_MUSIC_VOLUME * 100, callback=self.update_volume)
                    with dpg.group(horizontal=False):
                        dpg.add_slider_int(tag="song_pos_slider", width=-1, 
                                         callback=self.on_slider_change,
                                         drag_callback=self.on_slider_drag,
                                         format="")
                        dpg.add_text("00:00 of 00:00", tag="song_timer")

            dpg.add_separator()
            dpg.add_spacer(height=3)

            with dpg.group(horizontal=False):
                dpg.add_text("Now Playing: ", tag="csong")
                dpg.add_text("Folder: ", tag="sfolder")
                dpg.add_text("State: None", tag="player_state")
                with dpg.group(horizontal=True):
                    dpg.add_text("Tags: ", tag="stag")

    def update_volume(self, sender, app_data):
        pygame.mixer.music.set_volume(app_data / 100.0)

    def update_slider(self, current_time=0):
        if not self.current_song:
            return

        self.playing_event.clear()
        song_path = self.current_song[2]
        song_length = round(MP3(song_path).info.length)
        converted_song_length = self.format_time(song_length)
        song_id = self.current_song[0]
        current_time = round(current_time)
        self.current_position = current_time

        while pygame.mixer.music.get_busy() and not self.playing_event.is_set() and song_id == self.current_song[0]:
            if current_time >= song_length:
                break
                
            converted_current_time = self.format_time(current_time)
            timer_text = f"{converted_current_time} of {converted_song_length}"
            dpg.configure_item("song_timer", default_value=timer_text)
            if not self.slider_dragging:
                dpg.configure_item("song_pos_slider", default_value=current_time)
            current_time += 1
            self.current_position = current_time
            time.sleep(1)

    def format_time(self, seconds):
        return time.strftime('%M:%S', time.gmtime(seconds))

    def on_slider_drag(self, sender, app_data):
        """Appelé pendant le glissement de la slidebar"""
        if not self.current_song:
            return
            
        self.slider_dragging = True
        self.slider_value = app_data
        song_length = round(MP3(self.current_song[2]).info.length)
        converted_song_length = self.format_time(song_length)
        converted_current_time = self.format_time(app_data)
        dpg.configure_item("song_timer", default_value=f"{converted_current_time} of {converted_song_length}")

    def on_slider_change(self, sender, app_data):
        """Appelé quand on relâche la slidebar"""
        if not self.current_song:
            return
            
        self.slider_dragging = False
        self.current_position = app_data
        if self.state in ["playing", "paused"]:
            self.cleanup_thread()
            time.sleep(0.1)
            pygame.mixer.music.play(0, app_data)
            self.playing_thread = Thread(target=self.update_slider, args=(app_data,), daemon=True)
            self.playing_thread.start()

    def play(self, song_data):
        if isinstance(song_data, tuple) and len(song_data) > 2:
            song_path = song_data[2]
            print(f"Tentative de lecture de la musique: {song_path}")
            try:
                self.cleanup_thread()
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play()
                song_length = round(MP3(song_path).info.length)
                converted_song_length = self.format_time(song_length)
                
                if pygame.mixer.music.get_busy():
                    print("La musique a commencé à jouer avec succès")
                    self.state = "playing"
                    self.current_song = song_data
                    self.current_position = 0
                    dpg.configure_item("song_pos_slider", max_value=song_length)
                    self.playing_thread = Thread(target=self.update_slider, daemon=True)
                    self.playing_thread.start()
                    dpg.configure_item("play", label="Pause")
                    dpg.configure_item("sfolder", default_value=f"Folder: {song_data[4]}")
                    dpg.configure_item("player_state", default_value="State: Playing")
                    dpg.configure_item("csong", default_value=f"Now Playing: {ntpath.basename(song_path)}")
                    dpg.configure_item("song_timer", default_value=f"0:0 of {converted_song_length}")
            except Exception as e:
                print(f"Erreur lors de la lecture de la musique: {str(e)}")

    def play_pause(self):
        if self.state == "playing":
            self.state = "paused"
            pygame.mixer.music.pause()
            dpg.configure_item("play", label="Play")
            dpg.configure_item("player_state", default_value="State: Paused")
        elif self.state == "paused":
            self.state = "playing"
            pygame.mixer.music.unpause()
            self.cleanup_thread()
            self.playing_thread = Thread(target=self.update_slider, args=(self.current_position,), daemon=True)
            self.playing_thread.start()
            dpg.configure_item("play", label="Pause")
            dpg.configure_item("player_state", default_value="State: Playing")
        else:
            # État initial ou après stop, on joue une musique aléatoire
            if self.song_list:
                random_song = self.song_list.get_random_song()
                if random_song:
                    self.play(random_song)

    def stop(self):
        self.cleanup_thread()
        pygame.mixer.music.stop()
        dpg.configure_item("csong", default_value="Now Playing: ")
        dpg.configure_item("player_state", default_value="State: None")
        dpg.configure_item("play", label="Random")
        dpg.configure_item("song_timer", default_value="00:00 of 00:00")
        self.state = None
        self.current_song = None
        self.current_position = 0 
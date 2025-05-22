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
                        dpg.add_slider_int(tag="song_pos_slider", width=-1, callback=self.go_on_timing)
                        dpg.add_text("00:00 of 00:00", tag="song_timer")

            dpg.add_separator()
            dpg.add_spacer(height=3)

            with dpg.group(horizontal=False):
                dpg.add_text("Now Playing: ", tag="csong")
                dpg.add_text("Folder: ", tag="sfolder")
                with dpg.group(horizontal=True):
                    dpg.add_text("Tags: ", tag="stag")

    def update_volume(self, sender, app_data):
        pygame.mixer.music.set_volume(app_data / 100.0)

    def update_slider(self, current_time=0):
        self.playing_event.clear()
        song_length = round(MP3(self.current_song[2]).info.length)
        converted_song_length = time.strftime('%M:%S', time.gmtime(song_length))
        song_id = self.current_song[0]
        current_time = round(current_time)

        while pygame.mixer.music.get_busy() and not self.playing_event.is_set() and song_id is self.current_song[0]:
            converted_current_time = time.strftime('%M:%S', time.gmtime(current_time))
            dpg.configure_item("song_timer", default_value=f"{converted_current_time} of {converted_song_length}")
            dpg.configure_item("song_pos_slider", default_value=current_time)
            current_time += 1
            time.sleep(1)

    def play(self, song_data):
        if song_data[2]:
            pygame.mixer.music.load(song_data[2])
            pygame.mixer.music.play()
            song_length = round(MP3(song_data[2]).info.length)
            converted_song_length = time.strftime('%M:%S', time.gmtime(song_length))
            
            if pygame.mixer.music.get_busy():
                self.state = "playing"
                self.current_song = song_data
                dpg.configure_item("song_pos_slider", max_value=song_length)
                self.playing_thread = Thread(target=self.update_slider, daemon=False).start()
                dpg.configure_item("play", label="Pause")
                dpg.configure_item("sfolder", default_value=f"Folder: {song_data[4]}")
                dpg.configure_item("cstate", default_value="State: Playing")
                dpg.configure_item("csong", default_value=f"Now Playing: {ntpath.basename(song_data[2])}")
                dpg.configure_item("song_timer", default_value=f"0:0 of {converted_song_length}")

    def go_on_timing(self, sender):
        clicked_timing = dpg.get_value(sender)
        if self.state in ["playing", "paused"]:
            self.playing_event.set()
            time.sleep(1)
            pygame.mixer.music.play(0, clicked_timing)
            self.playing_thread = Thread(target=self.update_slider, args=(clicked_timing,), daemon=False).start()

    def play_pause(self):
        if self.state == "playing":
            self.state = "paused"
            pygame.mixer.music.pause()
            dpg.configure_item("play", label="Play")
            dpg.configure_item("cstate", default_value="State: Paused")
        elif self.state == "paused":
            self.state = "playing"
            pygame.mixer.music.unpause()
            self.playing_thread = Thread(target=self.update_slider, 
                                       args=(pygame.mixer.music.get_pos(),), 
                                       daemon=False).start()
            dpg.configure_item("play", label="Pause")
            dpg.configure_item("cstate", default_value="State: Playing")

    def stop(self):
        pygame.mixer.music.stop()
        dpg.configure_item("csong", default_value="Now Playing: ")
        dpg.configure_item("cstate", default_value="State: None")
        dpg.configure_item("play", label="Random")
        dpg.configure_item("song_timer", default_value="00:00 of 00:00")
        self.state = None 
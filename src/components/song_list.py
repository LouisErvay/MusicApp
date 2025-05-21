import dearpygui.dearpygui as dpg
from typing import List, Optional, Callable
import random

class SongList:
    def __init__(self, db_handler):
        self.db_handler = db_handler
        self.current_song_list = []
        self._filter_table_id = "song_table"
        self.play_song = None

    def create(self):
        """Crée l'interface de la liste des chansons."""
        with dpg.child_window(autosize_x=True, delay_search=True, tag="center_main"):
            with dpg.tab_bar():
                with dpg.tab(label="Songs", tag="song_list_tab"):
                    with dpg.group(horizontal=True):
                        dpg.add_checkbox(label="", callback=self.checkall)
                        dpg.add_input_text(hint="Search for a song", width=-1, 
                                         user_data=self._filter_table_id,
                                         callback=self.update_search, tag="song_search")

                    with dpg.child_window(autosize_x=True, delay_search=True, tag="list"):
                        self.increment_song_list()

    def update_search(self, sender=None, app_data=None, user_data=None):
        """Met à jour la recherche dans la liste des chansons."""
        dpg.set_value(self._filter_table_id, dpg.get_value("song_search"))

    def increment_song_list(self, data: Optional[List] = None):
        """
        Met à jour la liste des chansons.
        
        Args:
            data (Optional[List]): Données des chansons à afficher
        """
        if data is None:
            data = self.db_handler.get_all_songs()

        dpg.delete_item("list", children_only=True)
        self.current_song_list = []

        with dpg.table(header_row=True, resizable=True, policy=dpg.mvTable_SizingFixedFit,
                      hideable=True, no_host_extendX=True, borders_outerH=True,
                      borders_innerV=False, borders_innerH=False, borders_outerV=True,
                      row_background=True, reorderable=True, tag=self._filter_table_id,
                      parent="list") as song_table:

            dpg.add_table_column(label="", width_fixed=True)
            dpg.add_table_column(label="Play", width_fixed=True)
            dpg.add_table_column(label="ID", width_fixed=True)
            dpg.add_table_column(label="Song name", width_stretch=True)
            dpg.add_table_column(label="Folder", width_fixed=True, init_width_or_weight=200)

            for song in data:
                self.current_song_list.append(song)
                with dpg.table_row(tag=f"row_{song[0]}", filter_key=f"{song[0]}{song[1]}"):
                    dpg.add_checkbox(tag=f"checkbox_{song[0]}")
                    dpg.add_button(label="Play", width=50, callback=self.play_song,
                                 height=24, user_data=song)
                    dpg.add_text(f"{song[0]}")
                    dpg.add_text(f"{song[1]}")
                    dpg.add_text(f"{song[4]}")

        if len(dpg.get_value("song_search")) > 0:
            self.update_search()

    def play_song(self, sender, app_data, user_data):
        # Cette méthode sera connectée au MusicPlayer
        pass

    def get_random_song(self):
        if self.current_song_list:
            return random.choice(self.current_song_list)
        return None

    def checkall(self, sender, app_data):
        """Coche ou décoche toutes les chansons."""
        for song in self.db_handler.get_all_songs():
            dpg.set_value(f"checkbox_{song[0]}", app_data) 
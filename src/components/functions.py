import dearpygui.dearpygui as dpg

class Functions:
    def __init__(self, song_list):
        self.song_list = song_list

    def create(self):
        """Creates the functions interface."""
        dpg.add_spacer(height=5)
        dpg.add_text("Functions")
        dpg.add_spacer(height=5)
        dpg.add_separator()
        dpg.add_spacer(height=5)

        # Function buttons
        dpg.add_button(label="Clear all songs", width=-1, callback=self.clear_songs)
        dpg.add_button(label="Reload all songs", width=-1, callback=self.reload_songs)
        dpg.add_spacer(height=5)
        dpg.add_separator()
        dpg.add_spacer(height=5)

    def clear_songs(self, sender=None):
        """Clears all songs from the song list."""
        self.song_list.clear_list()

    def reload_songs(self, sender=None):
        """Reloads songs in the song list, respecting active filters."""
        # Récupérer les filtres actifs
        folder_list = self.song_list.filters.get_item_list("folder_list")
        tag_list = self.song_list.filters.get_item_list("tag_list")

        # Recharger en fonction des filtres
        if not folder_list and not tag_list:
            self.song_list.increment_song_list()
        elif not folder_list:
            tag_ids = eval(tag_list)
            if isinstance(tag_ids, int):
                tag_ids = [tag_ids]
            self.song_list.increment_song_list(data=self.song_list.db_handler.get_songs_by_tag(tag_ids))
        elif not tag_list:
            folder_ids = eval(folder_list)
            if isinstance(folder_ids, int):
                folder_ids = [folder_ids]
            self.song_list.increment_song_list(data=self.song_list.db_handler.get_songs_by_folder(folder_ids))
        else:
            folder_ids = eval(folder_list)
            tag_ids = eval(tag_list)
            if isinstance(folder_ids, int):
                folder_ids = [folder_ids]
            if isinstance(tag_ids, int):
                tag_ids = [tag_ids]
            self.song_list.increment_song_list(data=self.song_list.db_handler.get_songs_by_folder_and_tag(
                folder_ids, tag_ids
            )) 
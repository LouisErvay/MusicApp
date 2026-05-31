import dearpygui.dearpygui as dpg

class SearchBar:
    def __init__(self, song_list):
        self.song_list = song_list

    def create(self):
        with dpg.group(horizontal=True):
            dpg.add_input_text(
                hint="Search for a song",
                width=-1,
                callback=self.search_song,
                tag="search_input"
            )
            dpg.add_button(
                label="Search",
                callback=self.search_song,
                width=100
            )

    def search_song(self, sender, app_data, user_data):
        search_text = dpg.get_value("search_input")
        if search_text:
            self.song_list.filter_songs(search_text)
        else:
            self.song_list.reset_filter() 
import dearpygui.dearpygui as dpg
from typing import List, Optional

class Filters:
    def __init__(self, local_db):
        self.local_db = local_db
        self.increment_song_list = None

    def create(self):
        """Creates the filters interface."""
        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=75)  # Pour centrer le titre
            dpg.add_text("Filters")
        dpg.add_spacer(height=5)

        # Search section
        with dpg.group(horizontal=True):
            dpg.add_input_text(hint="Search for a folder or tag", width=-1, callback=self.filter_search)
        dpg.add_spacer(height=5)

        # Filter management buttons
        dpg.add_button(label="Clear filters", width=-1, callback=self.reset_filter)
        dpg.add_button(label="Reload filters", width=-1, callback=self.increment_filter)
        dpg.add_spacer(height=5)

        # Filter lists
        with dpg.child_window(tag="filters"):
            self.increment_filter()

    def get_item_list(self, item_type: str) -> List[int]:
        """
        Gets the list of selected items.
        
        Args:
            item_type (str): Type of item ('folder_list' or 'tag_list')
            
        Returns:
            List[int]: List of selected item IDs
        """
        selected_ids = []
        for item in dpg.get_item_children(item_type)[1]:
            if dpg.get_value(item):
                selected_ids.append(dpg.get_item_user_data(item)[0])
        return selected_ids

    def increment_song_from_filter(self, sender, app_data):
        """Updates the song list based on selected filters."""
        folder_ids = self.get_item_list("folder_list")
        tag_ids = self.get_item_list("tag_list")

        if not folder_ids and not tag_ids:
            self.increment_song_list()
        elif not folder_ids:
            self.increment_song_list(data=self.local_db.get_songs_by_tag(tag_ids))
        elif not tag_ids:
            self.increment_song_list(data=self.local_db.get_songs_by_folder(folder_ids))
        else:
            self.increment_song_list(data=self.local_db.get_songs_by_folder_and_tag(
                folder_ids, tag_ids
            ))

    def reset_filter(self, sender=None):
        """Resets all filters."""
        for folder in dpg.get_item_children("folder_list")[1]:
            dpg.set_value(folder, False)

        for tag in dpg.get_item_children("tag_list")[1]:
            dpg.set_value(tag, False)

        self.increment_song_list()

    def filter_search(self, sender, app_data):
        """Filters folders and tags based on search."""
        # Update folders
        folders = self.local_db.get_all_folders()
        dpg.delete_item("folder_list", children_only=True)
        for folder in folders:
            if app_data.lower() in folder[1].lower():  # Search in folder name
                dpg.add_checkbox(
                    label=folder[1],
                    callback=self.increment_song_from_filter,
                    user_data=folder,
                    parent="folder_list"
                )

        # Update tags
        tags = self.local_db.get_all_tags()
        dpg.delete_item("tag_list", children_only=True)
        for tag in tags:
            if app_data.lower() in tag[1].lower():  # Search in tag name
                dpg.add_checkbox(
                    label=tag[1],
                    callback=self.increment_song_from_filter,
                    user_data=tag,
                    parent="tag_list"
                )

    def increment_filter(self):
        """Initializes or updates filter lists."""
        # Sauvegarder l'état actuel des checkboxes
        folder_states = {}
        tag_states = {}
        
        # Sauvegarder l'état des dossiers si la liste existe
        if dpg.does_item_exist("folder_list"):
            for item in dpg.get_item_children("folder_list")[1]:
                folder_states[dpg.get_item_user_data(item)[0]] = dpg.get_value(item)
            
        # Sauvegarder l'état des tags si la liste existe
        if dpg.does_item_exist("tag_list"):
            for item in dpg.get_item_children("tag_list")[1]:
                tag_states[dpg.get_item_user_data(item)[0]] = dpg.get_value(item)

        dpg.delete_item("filters", children_only=True)

        # Folder list
        with dpg.collapsing_header(label="Folders", tag="folder_list", parent="filters"):
            for folder in self.local_db.get_all_folders():
                checkbox = dpg.add_checkbox(
                    label=folder[1],
                    callback=self.increment_song_from_filter,
                    user_data=folder,
                    parent="folder_list"
                )
                # Restaurer l'état précédent si le dossier était sélectionné
                if folder[0] in folder_states:
                    dpg.set_value(checkbox, folder_states[folder[0]])

        # Tag list
        with dpg.collapsing_header(label="Tags", tag="tag_list", parent="filters"):
            for tag in self.local_db.get_all_tags():
                checkbox = dpg.add_checkbox(
                    label=tag[1],
                    callback=self.increment_song_from_filter,
                    user_data=tag,
                    parent="tag_list"
                )
                # Restaurer l'état précédent si le tag était sélectionné
                if tag[0] in tag_states:
                    dpg.set_value(checkbox, tag_states[tag[0]]) 
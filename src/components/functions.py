import dearpygui.dearpygui as dpg

class Functions:
    def __init__(self, song_list):
        self.song_list = song_list
        self.local_db = song_list.local_db

    def show_message(self, message: str, is_error: bool = False):
        """Affiche un message dans un texte avec une couleur appropriée."""
        if is_error:
            dpg.configure_item("message_text", default_value=message, color=[255, 0, 0])  # Rouge pour les erreurs
        else:
            dpg.configure_item("message_text", default_value=message, color=[0, 255, 0])  # Vert pour les succès

    def create(self):
        """Creates the functions interface."""
        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=75)  # Pour centrer le titre
            dpg.add_text("Functions")
        dpg.add_spacer(height=5)

        # Function buttons
        dpg.add_button(label="Clear all songs", width=-1, callback=self.clear_songs)
        dpg.add_button(label="Reload all songs", width=-1, callback=self.reload_songs)
        dpg.add_spacer(height=5)
        dpg.add_separator()
        dpg.add_spacer(height=5)

        # Tag management section
        dpg.add_text("Tag Management")
        dpg.add_spacer(height=5)
        dpg.add_input_text(tag="tag_input", hint="Enter tag name", width=-1)
        dpg.add_spacer(height=5)
        dpg.add_button(label="Add Tag", width=-1, callback=self.add_tag)
        dpg.add_button(label="Delete Tag", width=-1, callback=self.delete_tag)
        dpg.add_spacer(height=5)
        dpg.add_text("", tag="message_text")  # Texte pour les messages
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
            self.song_list.increment_song_list(data=self.song_list.local_db.get_songs_by_tag(tag_ids))
        elif not tag_list:
            folder_ids = eval(folder_list)
            if isinstance(folder_ids, int):
                folder_ids = [folder_ids]
            self.song_list.increment_song_list(data=self.song_list.local_db.get_songs_by_folder(folder_ids))
        else:
            folder_ids = eval(folder_list)
            tag_ids = eval(tag_list)
            if isinstance(folder_ids, int):
                folder_ids = [folder_ids]
            if isinstance(tag_ids, int):
                tag_ids = [tag_ids]
            self.song_list.increment_song_list(data=self.song_list.local_db.get_songs_by_folder_and_tag(
                folder_ids, tag_ids
            ))

    def add_tag(self, sender=None):
        """Adds a new tag to the database."""
        tag_name = dpg.get_value("tag_input")
        if not tag_name or tag_name.strip() == "":
            self.show_message("Please enter a tag name", True)
            return

        try:
            if self.local_db.tag_exists(tag_name):
                self.show_message(f"Tag '{tag_name}' already exists", True)
                return

            self.local_db.add_tag(tag_name)
            self.show_message(f"Tag '{tag_name}' added successfully")
            dpg.set_value("tag_input", "")  # Clear input
            # Recharger les filtres pour mettre à jour la liste des tags
            self.song_list.filters.increment_filter()
        except Exception as e:
            self.show_message(f"Error adding tag: {str(e)}", True)

    def delete_tag(self, sender=None):
        """Deletes a tag from the database."""
        tag_name = dpg.get_value("tag_input")
        if not tag_name or tag_name.strip() == "":
            self.show_message("Please enter a tag name", True)
            return

        try:
            if not self.local_db.delete_tag_by_name(tag_name):
                self.show_message(f"Tag '{tag_name}' not found in database", True)
                return

            self.show_message(f"Tag '{tag_name}' deleted successfully")
            dpg.set_value("tag_input", "")  # Clear input
            # Recharger les filtres pour mettre à jour la liste des tags
            self.song_list.filters.increment_filter()
        except Exception as e:
            self.show_message(f"Error deleting tag: {str(e)}", True) 
import dearpygui.dearpygui as dpg
from typing import List, Optional, Callable, Dict
import random

class SongList:
    def __init__(self, local_db):
        self.local_db = local_db
        self.current_song_list = []
        self._filter_table_id = "song_table"
        self.play_song = None
        self.filters = None  # Sera défini lors de la connexion des composants
        self.music_folder_path = local_db.root_folder
        self.tag_popup_state = {}  # Pour stocker l'état des checkboxes

    def create(self):
        """Crée l'interface de la liste des chansons."""
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

    def show_tag_popup(self, song_id: int):
        """Affiche la popup de gestion des tags pour une chanson."""
        # Récupérer les tags actuels de la chanson
        current_tags = {tag[0]: True for tag in self.local_db.get_song_tags(song_id)}
        # Initialiser l'état des checkboxes
        self.tag_popup_state = {tag[0]: tag[0] in current_tags for tag in self.local_db.get_all_tags()}
        
        # Récupérer le nom de la chanson
        song_name = next((song[1] for song in self.current_song_list if song[0] == song_id), f"Song #{song_id}")

        # Récupérer les dimensions de la fenêtre principale
        viewport_width = dpg.get_viewport_client_width()
        viewport_height = dpg.get_viewport_client_height()

        # Calculer la position pour centrer la popup
        popup_width = 400
        popup_height = 300
        pos_x = (viewport_width - popup_width) // 2
        pos_y = (viewport_height - popup_height) // 2

        with dpg.window(label=f"Tags for {song_name}", modal=True, no_close=True, 
                       width=popup_width, height=popup_height,
                       pos=[pos_x, pos_y],
                       tag=f"tag_popup_{song_id}"):
            # Liste des tags avec checkboxes dans un groupe scrollable
            with dpg.child_window(height=200, width=-1):  # Hauteur fixe, largeur adaptative
                for tag_id, tag_name in self.local_db.get_all_tags():
                    dpg.add_checkbox(
                        label=tag_name,
                        default_value=self.tag_popup_state[tag_id],
                        callback=lambda s, a, u: self.update_tag_state(u, a),
                        user_data=tag_id
                    )

            dpg.add_spacer(height=10)
            dpg.add_text("", tag=f"tag_status_{song_id}")  # Texte pour les messages de statut
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_button(label="Cancel", callback=lambda: self.cancel_tag_changes(song_id))
                dpg.add_button(label="Close", callback=lambda: dpg.delete_item(f"tag_popup_{song_id}"))
                dpg.add_button(label="Confirm", callback=lambda: self.confirm_tag_changes(song_id))

    def update_tag_state(self, tag_id: int, value: bool):
        """Met à jour l'état d'une checkbox de tag."""
        self.tag_popup_state[tag_id] = value
        # Effacer le message de statut de la popup actuelle
        # On récupère l'ID de la chanson à partir du tag de la popup parente
        popup_tag = dpg.get_item_alias(dpg.get_item_parent(dpg.get_item_parent(dpg.last_item())))
        if popup_tag and popup_tag.startswith("tag_popup_"):
            song_id = int(popup_tag.split("_")[-1])
            dpg.configure_item(f"tag_status_{song_id}", default_value="")

    def cancel_tag_changes(self, song_id: int):
        """Annule les modifications et ferme la popup."""
        dpg.delete_item(f"tag_popup_{song_id}")

    def confirm_tag_changes(self, song_id: int):
        """Confirme les modifications des tags."""
        try:
            # Récupérer les IDs des tags cochés
            selected_tag_ids = [tag_id for tag_id, is_checked in self.tag_popup_state.items() if is_checked]
            # Mettre à jour la base de données
            self.local_db.update_song_tags(song_id, selected_tag_ids)
            # Afficher le message de succès en vert
            dpg.configure_item(f"tag_status_{song_id}", default_value="Tags updated successfully", color=[0, 255, 0])
        except Exception as e:
            # Afficher le message d'erreur en rouge
            dpg.configure_item(f"tag_status_{song_id}", default_value=f"Error updating tags: {str(e)}", color=[255, 0, 0])

    def increment_song_list(self, data: Optional[List] = None):
        """
        Met à jour la liste des chansons.
        
        Args:
            data (Optional[List]): Données des chansons à afficher
        """
        if data is None:
            data = self.local_db.get_all_songs()

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
            dpg.add_table_column(label="Tags", width_fixed=True)

            for song in data:
                # Le chemin est déjà complet dans la base de données
                self.current_song_list.append(song)
                
                with dpg.table_row(tag=f"row_{song[0]}", filter_key=f"{song[0]}{song[1]}"):
                    dpg.add_checkbox(tag=f"checkbox_{song[0]}")
                    dpg.add_button(label="Play", width=50, callback=self._play_song,
                                 height=24, user_data=song)
                    dpg.add_text(f"{song[0]}")
                    dpg.add_text(f"{song[1]}")
                    dpg.add_text(f"{song[4]}")
                    dpg.add_button(label="Edit Tags", width=80, callback=lambda s, a, u: self.show_tag_popup(u),
                                 user_data=song[0])

        if len(dpg.get_value("song_search")) > 0:
            self.update_search()

    def _play_song(self, sender, app_data, user_data):
        """Méthode interne pour jouer une chanson."""
        if self.play_song:
            self.play_song(user_data)

    def get_random_song(self):
        if self.current_song_list:
            return random.choice(self.current_song_list)
        return None

    def checkall(self, sender, app_data):
        """Coche ou décoche toutes les chansons."""
        for song in self.local_db.get_all_songs():
            dpg.set_value(f"checkbox_{song[0]}", app_data)

    def clear_list(self):
        """Clears the song list."""
        dpg.delete_item("list", children_only=True)
        self.current_song_list = [] 
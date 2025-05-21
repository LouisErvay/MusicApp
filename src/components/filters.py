import dearpygui.dearpygui as dpg
from typing import List, Optional

class Filters:
    def __init__(self, db_handler):
        self.db_handler = db_handler
        self.increment_song_list = None

    def create(self):
        """Crée l'interface des filtres."""
        dpg.add_spacer(height=5)
        dpg.add_text("Filtres")
        dpg.add_spacer(height=5)
        dpg.add_separator()
        dpg.add_spacer(height=5)

        # Boutons de gestion
        dpg.add_button(label="Supprimer tous les filtres", width=-1, callback=self.reset_filter)
        dpg.add_button(label="Recharger les filtres", width=-1, callback=self.increment_filter)
        dpg.add_spacer(height=5)
        dpg.add_separator()
        dpg.add_spacer(height=5)

        # Barre de recherche
        with dpg.group(horizontal=True):
            dpg.add_input_text(hint="Rechercher un dossier ou un tag", width=-1, callback=self.filter_search)
        dpg.add_spacer(height=5)

        # Liste des filtres
        with dpg.child_window(tag="filters"):
            self.increment_filter()

    def get_item_list(self, item_type: str) -> str:
        """
        Récupère la liste des éléments sélectionnés.
        
        Args:
            item_type (str): Type d'élément ('folder_list' ou 'tag_list')
            
        Returns:
            str: Liste des IDs au format SQL (ex: "(1,2,3)")
        """
        item_list = ""
        for item in dpg.get_item_children(item_type)[1]:
            if dpg.get_value(item):
                if len(item_list) == 0:
                    item_list = "(" + str(dpg.get_item_user_data(item)[0]) + ","
                else:
                    item_list += str(dpg.get_item_user_data(item)[0]) + ","
        if len(item_list) > 0:
            item_list = item_list[:-1] + ")"
        return item_list

    def increment_song_from_filter(self, sender, app_data):
        """Met à jour la liste des chansons en fonction des filtres sélectionnés."""
        folder_list = dpg.get_value("folder_list")
        tag_list = dpg.get_value("tag_list")

        if folder_list and tag_list:
            # Filtre par dossier et tag
            self.increment_song_list(data=self.db_handler.get_songs_by_folder_and_tag(
                eval(folder_list), eval(tag_list)
            ))
        elif folder_list:
            # Filtre par dossier uniquement
            folder_ids = eval(folder_list)
            if isinstance(folder_ids, tuple):
                folder_ids = list(folder_ids)
            self.increment_song_list(data=self.db_handler.get_songs_by_folder(folder_ids))
        elif tag_list:
            # Filtre par tag uniquement
            self.increment_song_list(data=self.db_handler.get_songs_by_tag(eval(tag_list)))
        else:
            # Aucun filtre
            self.increment_song_list()

    def reset_filter(self, sender=None):
        """Réinitialise tous les filtres."""
        for folder in dpg.get_item_children("folder_list")[1]:
            dpg.set_value(folder, False)

        for tag in dpg.get_item_children("tag_list")[1]:
            dpg.set_value(tag, False)

        self.increment_song_list()

    def filter_search(self, sender, app_data):
        """Filtre les dossiers et tags en fonction de la recherche."""
        # Mise à jour des dossiers
        folders = self.db_handler.get_all_folders()
        dpg.delete_item("folder_list", children_only=True)
        for folder in folders:
            if app_data.lower() in folder[1].lower():  # Recherche dans le nom du dossier
                dpg.add_checkbox(
                    label=folder[1],
                    callback=self.increment_song_from_filter,
                    user_data=folder,
                    parent="folder_list"
                )

        # Mise à jour des tags
        tags = self.db_handler.get_all_tags()
        dpg.delete_item("tag_list", children_only=True)
        for tag in tags:
            if app_data.lower() in tag[1].lower():  # Recherche dans le nom du tag
                dpg.add_checkbox(
                    label=tag[1],
                    callback=self.increment_song_from_filter,
                    user_data=tag,
                    parent="tag_list"
                )

    def increment_filter(self):
        """Initialise ou met à jour les listes de filtres."""
        dpg.delete_item("filters", children_only=True)

        # Liste des dossiers
        with dpg.collapsing_header(label="Dossiers", tag="folder_list", parent="filters"):
            for folder in self.db_handler.get_all_folders():
                dpg.add_checkbox(
                    label=folder[1],
                    callback=self.increment_song_from_filter,
                    user_data=folder,
                    parent="folder_list"
                )

        # Liste des tags
        with dpg.collapsing_header(label="Tags", tag="tag_list", parent="filters"):
            for tag in self.db_handler.get_all_tags():
                dpg.add_checkbox(
                    label=tag[1],
                    callback=self.increment_song_from_filter,
                    user_data=tag,
                    parent="tag_list"
                ) 
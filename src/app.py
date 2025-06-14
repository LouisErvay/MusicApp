import dearpygui.dearpygui as dpg
from src.theme.theme import create_theme, apply_themes

class App:
    def __init__(self, player=None, song_list=None, filters=None, functions=None, search_bar=None):
        self.player = player
        self.song_list = song_list
        self.filters = filters
        self.functions = functions
        self.search_bar = search_bar

    def create_ui(self):
        """Crée l'interface utilisateur principale."""
        # Création du contexte DearPyGui
        dpg.create_context()
        dpg.create_viewport(title="MusicApp", large_icon="icon.ico", small_icon="icon.ico")

        # Création des thèmes
        create_theme()

        # Création de la fenêtre principale
        with dpg.window(label="MusicApp", tag="Primary Window"):
            # Configuration de la mise en page
            with dpg.group(horizontal=True):
                # Panneau de gauche (filtres)
                with dpg.child_window(width=250, tag="filters_panel"):
                    if self.filters:
                        self.filters.create()

                # Panneau central (lecteur et tabs)
                with dpg.child_window(width=-250, border=True, tag="center_panel"):
                    # En-tête avec le lecteur
                    if self.player:
                        self.player.create()

                    # Séparateur
                    dpg.add_spacer(height=1)
                    dpg.add_separator()
                    dpg.add_spacer(height=1)

                    # Tab bar avec les différents onglets
                    with dpg.child_window(autosize_x=True, delay_search=True, tag="center_main"):
                        with dpg.tab_bar():
                            with dpg.tab(label="Songs", tag="song_list_tab"):
                                if self.song_list:
                                    self.song_list.create()

                # Panneau de droite (fonctions)
                with dpg.child_window(border=True, tag="right_panel"):
                    if self.functions:
                        self.functions.create()

        # Configuration de la fenêtre principale
        dpg.set_primary_window("Primary Window", True)
        dpg.setup_dearpygui()
        dpg.show_viewport()

        # Application des thèmes après que tous les éléments soient créés
        apply_themes()

        # Chargement initial de la liste des chansons après création complète de l'UI
        if self.song_list:
            self.song_list.increment_song_list()

    def run(self):
        """Lance l'application DearPyGui."""
        dpg.start_dearpygui()
        dpg.destroy_context()

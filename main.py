import dearpygui.dearpygui as dpg
import pygame
from src.components.player import MusicPlayer
from src.components.song_list import SongList
from src.components.filters import Filters
from src.components.search_bar import SearchBar
from src.theme.theme import create_theme, apply_themes
from project.Settings import Settings
import project.Db_handler as dbh

def main():
    # Initialisation des paramètres et de la base de données
    settings = Settings()
    db_handler = dbh.Db_handler()

    # Initialisation de pygame pour la lecture audio
    pygame.mixer.init()
    pygame.init()
    pygame.mixer.music.set_volume(0.5)

    # Création du contexte DearPyGui
    dpg.create_context()
    dpg.create_viewport(title="Rainy Music", large_icon="icon.ico", small_icon="icon.ico")

    # Création des thèmes
    create_theme()

    # Création de la fenêtre principale
    with dpg.window(label="Rainy Music", tag="Primary Window"):
        # Initialisation des composants
        player = MusicPlayer()
        song_list = SongList(db_handler)
        filters = Filters(db_handler)
        search_bar = SearchBar(song_list)

        # Connexion des composants
        song_list.play_song = player.play
        filters.increment_song_list = song_list.increment_song_list
        search_bar.song_list = song_list

        # Configuration de la mise en page
        with dpg.group(horizontal=True):
            # Panneau de gauche (filtres)
            with dpg.child_window(width=250, tag="filters_panel"):
                filters.create()

            # Panneau central (lecteur et liste des chansons)
            with dpg.child_window(width=-250, border=True, tag="center_panel"):
                # En-tête avec le lecteur
                player.create()

                # Séparateur
                dpg.add_spacer(height=1)
                dpg.add_separator()
                dpg.add_spacer(height=1)

                # Liste des chansons
                song_list.create()

            # Panneau de droite (vide pour l'instant)
            with dpg.child_window(border=True, tag="right_panel"):
                pass

        # Chargement initial de la liste des chansons
        song_list.increment_song_list()

    # Configuration de la fenêtre principale
    dpg.set_primary_window("Primary Window", True)
    dpg.setup_dearpygui()
    dpg.show_viewport()

    # Application des thèmes après que tous les éléments soient créés
    apply_themes()

    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()

import pygame
import os
from dotenv import load_dotenv
from src.app import App
from src.components.player import MusicPlayer
from src.components.song_list import SongList
from src.components.filters import Filters
from src.components.functions import Functions
from src.components.search_bar import SearchBar
from src.db.local.local_db import LocalDb

def main():
    # Chargement des variables d'environnement
    load_dotenv()
    music_folder_path = os.getenv('SONG_FOLDER_PATH')
    if not music_folder_path:
        raise ValueError("La variable d'environnement SONG_FOLDER_PATH n'est pas définie")

    # Initialisation de la base de données
    local_db = LocalDb(music_folder_path)

    # Initialisation de pygame pour la lecture audio
    pygame.mixer.init()
    pygame.init()
    pygame.mixer.music.set_volume(0.5)

    # Initialisation des composants
    player = MusicPlayer()
    song_list = SongList(local_db)
    filters = Filters(local_db)
    functions = Functions(song_list)
    search_bar = SearchBar(song_list)

    # Connexion des composants
    song_list.play_song = player.play
    player.song_list = song_list
    song_list.filters = filters
    filters.increment_song_list = song_list.increment_song_list
    search_bar.song_list = song_list

    # Création et lancement de l'application
    app = App(player=player, song_list=song_list, filters=filters, 
              functions=functions, search_bar=search_bar)
    
    # Création de l'interface et lancement
    app.create_ui()
    app.run()

if __name__ == "__main__":
    main()

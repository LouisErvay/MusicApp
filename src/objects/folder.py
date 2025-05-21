import os
from typing import List, Optional, Any
from .base import BaseObject
from .song import Song

class Folder(BaseObject):
    """Classe de base pour les dossiers."""
    
    def __init__(self, name: str, path: str):
        super().__init__(name, path)
        self.folders: List[Folder] = []
        self.songs: List[Song] = []

    def add_folder(self, folder: 'Folder') -> None:
        """Ajoute un sous-dossier."""
        self.folders.append(folder)
        self.add_element(folder)

    def add_song(self, song: Song) -> None:
        """Ajoute une chanson."""
        self.songs.append(song)
        self.add_element(song)

    def get_folders(self) -> List['Folder']:
        """Retourne la liste des sous-dossiers."""
        return self.folders

    def get_songs(self) -> List[Song]:
        """Retourne la liste des chansons."""
        return self.songs

class LocalFolder(Folder):
    """Dossier local du système de fichiers."""
    
    def load(self) -> None:
        """Charge le contenu du dossier depuis le système de fichiers."""
        if not os.path.exists(self.path):
            return

        for item in os.listdir(self.path):
            item_path = os.path.join(self.path, item)
            
            if os.path.isdir(item_path):
                folder = LocalFolder(item, item_path)
                folder.load()
                self.add_folder(folder)
            elif item.lower().endswith(('.mp3', '.wav', '.ogg', '.flac')):
                song = Song(item, item_path)
                self.add_song(song)

class DriveFolder(Folder):
    """Dossier Google Drive."""
    
    def __init__(self, name: str, path: str, drive_id: str):
        super().__init__(name, path)
        self.drive_id = drive_id

    def load(self) -> None:
        """Charge le contenu du dossier depuis Google Drive."""
        # TODO: Implémenter le chargement depuis Google Drive
        pass 
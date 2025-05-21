import os

from project.objects.songs.Song import Song
from project.objects.folders.Folder import Folder

class Folder_from_gdrive(Folder):
    def __init__(self, path, name, parent=None, id=None, id_gdrive=None):
        super().__init__(path, name, parent=parent, id=id)

        self.id_gdrive = id_gdrive
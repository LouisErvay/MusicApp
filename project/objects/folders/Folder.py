import os

from project.objects.songs.Song import Song


class Folder:

    def __init__(self, path, name, parent=None, id=None):
        self.id = id
        self.path = path
        self.parent = parent
        self.name = name
        self.elements = []
        self.compatible_audio_ext = [".mp3",".wav",".flac",".ogg"]
        self.non_compatible_audio_ext = [".wma",".m4a",".3gpp",".amr"]
        # tout ce que j'ai : [".mp3",".m4a",".wma",".wav",".flac",".amr",".3gpp",".ogg"]
        # Fichiers que j'ai, non pris en compte : wma, m4a, 3gpp, amr

    def get_folder(self):
        folders = []
        for element in self.elements:
            if isinstance(element, Folder):
                folders.append(element)
        return folders

    def get_song(self):
        songs = []
        for element in self.elements:
            if isinstance(element, Song):
                songs.append(element)
        return songs


    # TODO comprendre mieu ces deux def, quand je print mon instance, c'est repr qui répond, srt jsp a quoi elle sert
    def __str__(self):
        return "Folder " + self.name

    def __repr__(self):
        return self.name
import os

from project.objects.songs.Song import Song
from project.objects.folders.Folder import Folder

class Folder_from_os(Folder):
    def __init__(self, path, name, parent=None, id=None):
        super().__init__(path, name, parent=parent, id=id)


    def load_from_os(self):
        try:
            incompatibleList = []
            for element in os.listdir(self.path):
                extension = os.path.splitext(element)
                if os.path.isdir(os.path.join(self.path, element)):
                    self.elements.append(Folder_from_os(path=os.path.join(self.path, element), name=element, parent=self).load_from_os())
                elif extension[1] in self.compatible_audio_ext:
                    self.elements.append(Song(folder=self, name=os.path.splitext(element)[0], path=os.path.join(self.path, element), parent_id=self.id))
                elif extension[1] in self.non_compatible_audio_ext:
                    incompatibleList.append(os.path.join(self.path, element))
                elif extension[1] in [".jpg", ".db"]:
                    pass
                else:
                    print("ERROR : un fichier n'est pas compatible, nom : " + element)
        #     TODO Je fait quoi de cette merde de liste des incompatibles ?
        except Exception as e:
            print("Erreur lors de la lecture du dossier '" + self.name + "': " + str(e))
        return self

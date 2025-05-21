import project.Db_handler as dbh
db_handler = dbh.Db_handler()
from project.objects.songs.Song import Song
from project.objects.folders.Folder import Folder

class Folder_from_db(Folder):
    def __init__(self, path, name, parent=None, id=1):
        super().__init__(path, name, parent=parent, id=id)


    def load_from_db(self):
        try:
            folders = db_handler.exe(f"SELECT * FROM Folder WHERE parent_id = {self.id}")
            for folder in folders:
                new_folder = Folder_from_db(name=folder[2],path=folder[3],parent=folder[4], id=folder[0])
                new_folder.load_from_db()
                self.elements.append(new_folder)

            songs = db_handler.exe(f"SELECT * FROM Song WHERE parent_id = {self.id}")
            for song in songs:
                self.elements.append(Song(id=song[0], name=song[2], path=song[3], folder=self, parent_id=self.id))

        except Exception as e:
            print("Erreur lors de la lecture du dossier '" + self.name + "': " + str(e))
        return self

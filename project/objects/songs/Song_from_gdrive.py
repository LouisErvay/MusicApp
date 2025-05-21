from project.objects.songs import Song

class Song_from_gdrive(Song):

    def __init__(self, folder, name, path, parent_id, id=None, id_gdrive=None):
        super().__init__(folder, name, path, parent_id, id=id)

        self.id_gdrive = id_gdrive
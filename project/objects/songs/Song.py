class Song:

    def __init__(self, folder, name, path, parent_id, id=None):
        self.id = id
        self.folder = folder
        self.name = name
        self.path = path
        self.parent_id = parent_id



    # TODO comprendre mieu ces deux def, quand je print mon instance, c'est repr qui répond, srt jsp a quoi elle sert
    def __str__(self):
        return self.name

    def __repr__(self):
        return "\n\t\t" + self.name
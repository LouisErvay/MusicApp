import os

class Settings:
    def __init__(self):
        self.path = "../settings.txt"
        self.settings = {0: "path",
                         1: "theme",
                         2: "playlist_preload_scroll"
                         }

        try:
            # Si on a option, on le recupère sous un tableau de str [""]
            if os.path.exists(self.path):
                file_opts = open(self.path, "r")
                opts = file_opts.read().split("\n")
                for i in range(len(opts)):
                    if not opts[i].split("=")[1] == "":
                        self.settings[i] = opts[i]

            # Si pas option, on le crée
            # On ecrit dans le ficher crée la liste des settings de base
            else:
                new_file = open(self.path, "w+")
                for i in range(len(self.settings)):
                    new_file.write(str(self.settings.get(i)) + "=\n")

        except Exception as e:
            print(e)

    def get(self, index):
        return self.settings[index].split("=")[1] if len(self.settings[index].split("="))==2 else ""

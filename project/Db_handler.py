import os
import sqlite3

from project.objects.songs.Song import Song
from project.objects.folders.Folder import Folder
from project.objects.folders.Folder_from_os import Folder_from_os

from project.Settings import Settings

settings = Settings()

class Db_handler:

    def __init__(self):
        # Chemin vers le dossier contenant les musiques et la base de données
        self.root_folder = settings.get(0)

        # Chemin vers la base de données
        self.db_path = os.path.join(self.root_folder, "MusicApp_database.db")

        # Vérifier si la base de données existe
        if not os.path.exists(self.db_path):
            # Créer la base de données et les tables correspondantes
            self.get_conn()
            self.db_exe.execute("""CREATE TABLE IF NOT EXISTS folder (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                id_gdrive VARCHAR(50),
                                name VARCHAR(100),
                                path VARCHAR(255),
                                parent_id INT DEFAULT NULL)""")
            self.db_exe.execute("""CREATE TABLE IF NOT EXISTS song (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                id_gdrive VARCHAR(50),
                                name VARCHAR(100),
                                path VARCHAR(255),
                                parent_id INT)""")
            self.db_exe.execute("""CREATE TABLE IF NOT EXISTS playlist (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name VARCHAR(100))""")
            self.db_exe.execute("""CREATE TABLE IF NOT EXISTS tag (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name VARCHAR(100),
                                desc VARCHAR(255))""")
            self.db_exe.execute("""CREATE TABLE IF NOT EXISTS main_tag (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name VARCHAR(100),
                                desc VARCHAR(255))""")
            self.db_exe.execute("""CREATE TABLE IF NOT EXISTS tag_main_tag (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                id_tag INT,
                                id_main_tag INT)""")
            self.db_exe.execute("""CREATE TABLE IF NOT EXISTS song_tag (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                id_song INT,
                                id_tag INT)""")
            self.db_exe.execute("""CREATE TABLE IF NOT EXISTS song_playlist (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                id_song INT,
                                id_playlist INT)""")

            folder = Folder_from_os(path=self.root_folder, name="MUSIC")
            folder.load_from_os()
            self.increment_db(folder)

            self.db_log.commit()
            self.db_log.close()
        else:
            # On récupère notre folder racine garde a parent_id = NULL
            # A partir de ce folder on remplis sa liste d'elements
            # Ouvrir la base de données et récupérer la liste des musiques
            self.get_conn()
            self.db_log.close()

    def get_conn(self):
        self.db_log = sqlite3.connect(self.db_path)
        self.db_log.execute('pragma encoding = "UTF-8"')
        self.db_log.execute("PRAGMA foreign_keys = ON")
        self.db_exe = self.db_log.cursor()

    def fetchall(self, exe):
        try:
            self.db_exe.execute(exe)
            return self.db_exe.fetchall()
        except Exception as e:
            print("SQL ERROR: fetchall, req: " + str(exe) + "\n err:" + str(e))


    def exe(self, req, where=None):
        try:
            self.get_conn()
            self.db_exe.execute(req)
            data =  self.db_exe.fetchall()
            self.db_log.close()
            return data
        except Exception as e:
            print("SQL ERROR: exe '" + req + "' : " + str(where) + "\n err:" + str(e))

    def exe_commit(self, req):
        try:
            self.get_conn()
            self.db_exe.execute(req)
            self.db_log.commit()
            self.db_log.close()
        except Exception as e:
            print("SQL ERROR: exe '" + req + "' : " + str(where) + "\n err:" + str(e))

    def exe_one(self, req, where=None):
        try:
            self.get_conn()
            self.db_exe.execute(req)
            data =  self.db_exe.fetchone()
            self.db_log.close()
            return data
        except Exception as e:
            print("SQL ERROR: exe '" + req + "' : " + str(where) + "\n err:" + str(e))

    def increment_db(self, folder, parent_id=None):
        # ajoute le folder dans la DB
        if parent_id:
            self.push_folder(folder, parent_id=parent_id)
        else:
            self.push_folder(folder)

        # Récupère son ID dans la DB
        self.db_exe.execute("SELECT id FROM folder WHERE name = '" + folder.name + "'")
        folder_id = self.db_exe.fetchone()[0]

        # pour chaque element, SI c'est un folder, on recommence, si song on l'ajoute à la DB avec l'id du folder
        for element in folder.elements:
            if isinstance(element, Folder):
                self.increment_db(element, parent_id=folder_id)

            elif isinstance(element, Song):
                self.push_song(element, parent_id=folder_id)

    def push_folder(self, folder, parent_id=None):
        name = folder.name.replace("'", "''")
        path = folder.path.replace("'", "''")

        if parent_id is not None:
            req = (f"INSERT INTO folder (name,path,parent_id) VALUES ('{name}','{path}',{"NULL" if parent_id is None else str(parent_id)})")
        else:
            req = ("INSERT INTO folder (name,path,parent_id) VALUES ('" + name + "','" + path + "', NULL)")

        try:
            self.db_exe.execute(req)
        except Exception as e:
            print("SQL ERROR: Ajout d'un dossier en DB: " + folder.name + "\n err:" + str(e))


    def push_song(self, song, parent_id):
        # Rajoute le song dans la database dans la table song

        name = song.name.replace("'", "''")
        path = song.path.replace("'", "''")

        req = "INSERT INTO song (name,path,parent_id) VALUES ('" + name + "','" + path + "', " + str(
            parent_id) + ")"

        try:
            self.db_exe.execute(req)
        except Exception as e:
            print("SQL ERROR: " + req + "\n err:" + str(e))

    def push_tag(self, req, name,  parent_tags):
        self.get_conn()
        self.db_exe.execute(req)
        self.db_log.commit()

        self.db_exe.execute(f"SELECT * FROM tag WHERE name = '{name}'")
        new_tag = self.db_exe.fetchone()

        if parent_tags:
            for parent_tag in parent_tags:
                self.db_exe.execute(f"INSERT INTO tag_main_tag (id_tag, id_main_tag) VALUES ({new_tag[0]}, {parent_tag})")

        self.db_log.commit()

        self.db_log.close()


    def get_all_song(self):
        try:
            self.get_conn()
            self.db_exe.execute("SELECT "
                                "song.id , "
                                "song.name , "
                                "song.path , "
                                "song.parent_id , "
                                "folder.name AS 'folder name' , "
                                "CASE WHEN COUNT(tag.id) > 0 THEN json_group_array(json_object('name', tag.name, 'desc', tag.desc)) "
                                "ELSE NULL END AS 'tags' "
                                "FROM song "
                                "LEFT JOIN song_tag ON song.id = song_tag.id_song "
                                "LEFT JOIN tag ON song_tag.id_tag  = tag.id "
                                "INNER JOIN folder ON song.parent_id = folder.id "
                                "GROUP BY song.id "
                                "ORDER BY song.name")
            data = self.db_exe.fetchall()
            self.db_log.close()
            return data
        except Exception as e:
            print("SQL ERROR: select all song: \n err:" + str(e))


    def get_song_where_folder(self, folder_list="()"):
        try:
            self.get_conn()
            self.db_exe.execute("SELECT "
                                "song.id , "
                                "song.name , "
                                "song.path , "
                                "song.parent_id , "
                                "folder.name AS 'folder name' , "
                                "CASE WHEN COUNT(tag.id) > 0 THEN json_group_array(json_object('name', tag.name, 'desc', tag.desc)) "
                                "ELSE NULL END AS 'tags' "
                                "FROM song "
                                "LEFT JOIN song_tag ON song.id = song_tag.id_song "
                                "LEFT JOIN tag ON song_tag.id_tag  = tag.id "
                                "INNER JOIN folder ON song.parent_id = folder.id "
                                "WHERE song.parent_id IN " + str(folder_list) + " "
                                "GROUP BY song.id "
                                "ORDER BY song.name")
            data = self.db_exe.fetchall()
            self.db_log.close()
            return data
        except Exception as e:
            print("SQL ERROR: select all song: \n err:" + str(e))


    def get_song_where_tag(self, tag_list="()"):
        try:
            self.get_conn()
            self.db_exe.execute("SELECT "
                                "song.id , "
                                "song.name , "
                                "song.path , "
                                "song.parent_id , "
                                "folder.name AS 'folder name' , "
                                "CASE WHEN COUNT(tag.id) > 0 THEN "
                                    "(SELECT json_group_array(json_object('name', t.name, 'desc', t.desc)) "
                                    "FROM song_tag AS st "
                                    "LEFT JOIN tag AS t ON st.id_tag = t.id "
                                    "WHERE st.id_song = song.id) "
                                "ELSE NULL END AS 'tags' "
                                "FROM song "
                                "LEFT JOIN song_tag AS specific_tag ON song.id = specific_tag.id_song "
                                "AND specific_tag.id_tag IN " + str(tag_list) + " "
                                "LEFT JOIN song_tag ON song.id = song_tag.id_song "
                                "LEFT JOIN tag ON song_tag.id_tag  = tag.id "
                                "INNER JOIN folder ON song.parent_id = folder.id "
                                "WHERE specific_tag.id_tag IS NOT NULL "
                                "GROUP BY song.id "
                                "ORDER BY song.name")
            data = self.db_exe.fetchall()
            self.db_log.close()
            return data
        except Exception as e:
            print("SQL ERROR: select all song: \n err:" + str(e))


    def get_song_where_tag_folder(self, folder_list="()", tag_list="()"):
        try:
            self.get_conn()
            self.db_exe.execute("SELECT "
                                "song.id , "
                                "song.name , "
                                "song.path , "
                                "song.parent_id , "
                                "folder.name AS 'folder name' , "
                                "CASE WHEN COUNT(tag.id) > 0 THEN "
                                    "(SELECT json_group_array(json_object('name', t.name, 'desc', t.desc)) "
                                    "FROM song_tag AS st "
                                    "LEFT JOIN tag AS t ON st.id_tag = t.id "
                                    "WHERE st.id_song = song.id) "
                                "ELSE NULL END AS 'tags' "
                                "FROM song "
                                "LEFT JOIN song_tag AS specific_tag ON song.id = specific_tag.id_song "
                                "AND specific_tag.id_tag IN " + str(tag_list) + " "
                                "LEFT JOIN song_tag ON song.id = song_tag.id_song "
                                "LEFT JOIN tag ON song_tag.id_tag  = tag.id "
                                "INNER JOIN folder ON song.parent_id = folder.id "
                                "WHERE song.parent_id IN " + str(folder_list) + " AND specific_tag.id_tag IS NOT NULL "
                                "GROUP BY song.id "
                                "ORDER BY song.name")
            data = self.db_exe.fetchall()
            self.db_log.close()
            return data
        except Exception as e:
            print("SQL ERROR: select all song: \n err:" + str(e))


    def get_all_folder(self, where=None):
        try:
            self.db_exe.execute("SELECT * FROM folder " + str(where) + " ORDER BY name")
            return self.db_exe.fetchall()
        except Exception as e:
            print("SQL ERROR: select all folder: " + str(where) + "\n err:" + str(e))

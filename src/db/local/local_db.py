import os
import sqlite3
import hashlib
import time
from typing import List, Tuple, Optional, Dict, Any
from src.objects.folder import LocalFolder, DriveFolder
from src.objects.song import Song
from .song_query import SongQuery
from .folder_query import FolderQuery
from .tag_query import TagQuery
from .playlist_query import PlaylistQuery
from .song_history_query import SongHistoryQuery

class LocalDb:
    def __init__(self, root_folder: str):
        """
        Initialise le gestionnaire de base de données.
        
        Args:
            root_folder (str): Chemin vers le dossier racine contenant les musiques
        """
        print("\n=== Initialisation de LocalDb ===")
        print(f"Dossier racine: {root_folder}")
        self.root_folder = root_folder
        self.db_path = os.path.join(root_folder, "MusicApp_database.db")
        print(f"Chemin de la base de données: {self.db_path}")
        
        # Initialiser les gestionnaires de requêtes
        self.song_query = SongQuery(self.db_path)
        self.folder_query = FolderQuery(self.db_path)
        self.tag_query = TagQuery(self.db_path)
        self.playlist_query = PlaylistQuery(self.db_path)
        self.song_history_query = SongHistoryQuery(self.db_path)
        
        self._init_db()

    def _init_db(self) -> None:
        """Initialise la base de données si elle n'existe pas."""
        print("\n=== Initialisation de la base de données ===")
        db_exists = os.path.exists(self.db_path)
        print(f"La base de données existe: {db_exists}")
        
        if not db_exists:
            print("Création des tables...")
            self._create_tables()
        
        print("Migration de la base de données...")
        self._migrate_database()
        
        if not db_exists:
            print("Initialisation du dossier racine...")
            self._init_root_folder()

    def _create_tables(self) -> None:
        """Crée les tables nécessaires dans la base de données."""
        print("\n=== Création des tables ===")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Table des dossiers
            print("Création de la table 'folder'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS folder (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    path VARCHAR(255) NOT NULL,
                    path_hash VARCHAR(64) NOT NULL UNIQUE,
                    parent_id INTEGER,
                    FOREIGN KEY (parent_id) REFERENCES folder(id)
                )
            """)
            
            # Table des tags
            print("Création de la table 'tag'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tag (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL UNIQUE
                )
            """)
            
            # Table des playlists
            print("Création de la table 'playlist'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS playlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL UNIQUE
                )
            """)
            
            # Table des chansons
            print("Création de la table 'song'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS song (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    full_path VARCHAR(500) NOT NULL,
                    rel_path VARCHAR(500) NOT NULL,
                    rel_path_hash VARCHAR(64) NOT NULL UNIQUE,
                    file_hash VARCHAR(64) NOT NULL,
                    folder_id INTEGER NOT NULL,
                    last_modified INTEGER NOT NULL,
                    present_locally INTEGER NOT NULL DEFAULT 1,
                    synced_at INTEGER,
                    FOREIGN KEY (folder_id) REFERENCES folder(id)
                )
            """)
            
            # Table de liaison chanson-tag
            print("Création de la table 'song_tag'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS song_tag (
                    song_id INTEGER NOT NULL,
                    tag_id INTEGER NOT NULL,
                    PRIMARY KEY (song_id, tag_id),
                    FOREIGN KEY (song_id) REFERENCES song(id),
                    FOREIGN KEY (tag_id) REFERENCES tag(id)
                )
            """)
            
            # Table de liaison playlist-song
            print("Création de la table 'playlist_song'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS playlist_song (
                    playlist_id INTEGER NOT NULL,
                    song_id INTEGER NOT NULL,
                    PRIMARY KEY (playlist_id, song_id),
                    FOREIGN KEY (playlist_id) REFERENCES playlist(id),
                    FOREIGN KEY (song_id) REFERENCES song(id)
                )
            """)
            
            # Table de liaison playlist-tag
            print("Création de la table 'playlist_tag'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS playlist_tag (
                    playlist_id INTEGER NOT NULL,
                    tag_id INTEGER NOT NULL,
                    PRIMARY KEY (playlist_id, tag_id),
                    FOREIGN KEY (playlist_id) REFERENCES playlist(id),
                    FOREIGN KEY (tag_id) REFERENCES tag(id)
                )
            """)
            
            # Table d'historique des chansons
            print("Création de la table 'song_history'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS song_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    song_id INTEGER NOT NULL,
                    operation_type VARCHAR(50) NOT NULL,
                    timestamp INTEGER NOT NULL,
                    from_path VARCHAR(500),
                    to_path VARCHAR(500),
                    FOREIGN KEY (song_id) REFERENCES song(id)
                )
            """)
            
            conn.commit()
            print("Tables créées avec succès!")

    def _migrate_database(self) -> None:
        """Migre la base de données vers la nouvelle structure si nécessaire."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Vérifier si l'ancienne structure existe et la migrer si nécessaire
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            # Si les nouvelles tables n'existent pas, les créer
            if 'folder' not in existing_tables:
                self._create_tables()
            else:
                # Vérifier si la nouvelle structure est en place
                cursor.execute("PRAGMA table_info(folder)")
                folder_columns = [column[1] for column in cursor.fetchall()]
                
                if 'path_hash' not in folder_columns:
                    # Migration nécessaire - recréer les tables avec la nouvelle structure
                    print("Migration de l'ancienne structure vers la nouvelle...")
                    self._migrate_old_structure()

    def _migrate_old_structure(self) -> None:
        """Migre l'ancienne structure vers la nouvelle."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Sauvegarde des données existantes si nécessaire
            # Pour cette migration, on recrée tout depuis le début
            cursor.execute("DROP TABLE IF EXISTS song_tag")
            cursor.execute("DROP TABLE IF EXISTS song")
            cursor.execute("DROP TABLE IF EXISTS folder")
            cursor.execute("DROP TABLE IF EXISTS tag")
            
            # Recréer les tables avec la nouvelle structure
            self._create_tables()
            conn.commit()

    def _generate_path_hash(self, path: str) -> str:
        """Génère un hash SHA256 pour un chemin."""
        return hashlib.sha256(path.encode('utf-8')).hexdigest()

    def _generate_file_hash(self, file_path: str) -> str:
        """Génère un hash SHA256 pour le contenu d'un fichier."""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
        except (IOError, OSError):
            # Si le fichier ne peut pas être lu, utiliser le chemin comme hash
            hash_sha256.update(file_path.encode('utf-8'))
        return hash_sha256.hexdigest()

    def _get_relative_path(self, full_path: str) -> str:
        """Convertit un chemin absolu en chemin relatif par rapport au dossier racine."""
        try:
            return os.path.relpath(full_path, self.root_folder)
        except ValueError:
            # Si le chemin n'est pas sous le dossier racine, retourner le chemin complet
            return full_path

    def _init_root_folder(self) -> None:
        """Initialise le dossier racine dans la base de données et charge son contenu."""
        print(f"\nInitialisation du dossier racine: {self.root_folder}")
        
        # Extraire le nom du dossier à partir du chemin
        folder_name = os.path.basename(self.root_folder)
        print(f"Nom du dossier racine: {folder_name}")

        # Créer le dossier racine dans la base de données
        root_rel_path = ""  # Le dossier racine a un chemin relatif vide
        root_path_hash = self._generate_path_hash(root_rel_path)
        
        root_id = self.folder_query.add_folder(folder_name, root_rel_path, root_path_hash)
        print(f"Dossier racine créé dans la DB avec l'ID: {root_id}")

        # Créer et charger le dossier racine
        print("Création de l'objet LocalFolder...")
        root_folder = LocalFolder(folder_name, self.root_folder)
        print("Chargement du contenu du dossier racine...")
        root_folder.load()
        print(f"Nombre d'éléments trouvés: {len(root_folder.elements)}")

        # Récursivement ajouter tous les dossiers et chansons à la base de données
        print("\nDébut de l'ajout récursif des éléments...")
        self.increment_db(root_folder, root_id)
        print("Fin de l'ajout récursif des éléments.")

    def _get_connection(self) -> sqlite3.Connection:
        """Crée et retourne une connexion à la base de données."""
        conn = sqlite3.connect(self.db_path)
        conn.execute('PRAGMA foreign_keys = ON')
        conn.execute('PRAGMA encoding = "UTF-8"')
        return conn

    def increment_db(self, folder: LocalFolder, parent_id: Optional[int] = None) -> None:
        """
        Ajoute récursivement un dossier et son contenu à la base de données.
        
        Args:
            folder (LocalFolder): Le dossier à ajouter
            parent_id (Optional[int]): ID du dossier parent
        """
        # Si parent_id est None, c'est le dossier racine qui est déjà créé
        folder_id = parent_id

        # Ajoute les sous-dossiers et les chansons
        for element in folder.elements:
            if isinstance(element, LocalFolder):
                # Pour les sous-dossiers, on crée toujours un nouveau dossier
                rel_path = self._get_relative_path(element.path)
                path_hash = self._generate_path_hash(rel_path)
                subfolder_id = self.folder_query.add_folder(element.name, rel_path, path_hash, folder_id)
                # Récursion pour les sous-dossiers
                self.increment_db(element, subfolder_id)
            elif isinstance(element, Song):
                # Ajout des chansons
                rel_path = self._get_relative_path(element.path)
                rel_path_hash = self._generate_path_hash(rel_path)
                file_hash = self._generate_file_hash(element.path)
                last_modified = int(os.path.getmtime(element.path)) if os.path.exists(element.path) else 0
                
                song_id = self.song_query.add_song(
                    name=element.name,
                    full_path=element.path,
                    rel_path=rel_path,
                    rel_path_hash=rel_path_hash,
                    file_hash=file_hash,
                    folder_id=folder_id,
                    last_modified=last_modified
                )
                
                # Enregistrer l'opération dans l'historique
                self.song_history_query.add_song_history(song_id, "added", int(time.time()), to_path=rel_path)
                
                # Ajout des tags de la chanson s'il y en a
                for tag in element.tags:
                    tag_id = self.tag_query.add_tag(tag)
                    self.song_query.add_song_tag(song_id, tag_id)

    # Méthodes de délégation vers les gestionnaires de requêtes spécialisés
    
    # Délégation pour les chansons
    def get_song_by_id(self, song_id: int) -> Optional[Tuple]:
        return self.song_query.get_song_by_id(song_id)
    
    def get_all_songs(self) -> List[Tuple]:
        return self.song_query.get_all_songs()
    
    def add_song_tag(self, song_id: int, tag_id: int) -> None:
        return self.song_query.add_song_tag(song_id, tag_id)
    
    def remove_song_tag(self, song_id: int, tag_id: int) -> None:
        return self.song_query.remove_song_tag(song_id, tag_id)
    
    def get_song_tags(self, song_id: int) -> List[Tuple]:
        return self.song_query.get_song_tags(song_id)
    
    def update_song_tags(self, song_id: int, tag_ids: List[int]) -> None:
        return self.song_query.update_song_tags(song_id, tag_ids)
    
    def update_song_sync_status(self, song_id: int, synced_at: int) -> None:
        return self.song_query.update_song_sync_status(song_id, synced_at)
    
    def mark_song_as_missing(self, song_id: int) -> None:
        return self.song_query.mark_song_as_missing(song_id)
    
    def delete_song(self, song_id: int) -> None:
        # Enregistrer l'historique avant suppression
        self.song_history_query.add_song_history(song_id, "deleted", int(time.time()))
        return self.song_query.delete_song(song_id)
    
    # Délégation pour les dossiers
    def get_folder_by_id(self, folder_id: int) -> Optional[Tuple]:
        return self.folder_query.get_folder_by_id(folder_id)
    
    def get_all_folders(self) -> List[Tuple]:
        return self.folder_query.get_all_folders()
    
    def delete_folder(self, folder_id: int) -> None:
        return self.folder_query.delete_folder(folder_id)
    
    # Délégation pour les tags
    def get_all_tags(self) -> List[Tuple]:
        return self.tag_query.get_all_tags()
    
    def tag_exists(self, tag_name: str) -> bool:
        return self.tag_query.tag_exists(tag_name)
    
    def delete_tag_by_name(self, tag_name: str) -> bool:
        return self.tag_query.delete_tag_by_name(tag_name)
    
    # Délégation pour les playlists
    def get_all_playlists(self) -> List[Tuple]:
        return self.playlist_query.get_all_playlists()
    
    def add_playlist(self, name: str) -> int:
        return self.playlist_query.add_playlist(name)
    
    def delete_playlist(self, playlist_id: int) -> None:
        return self.playlist_query.delete_playlist(playlist_id)
    
    def get_playlist_songs(self, playlist_id: int) -> List[Tuple]:
        return self.playlist_query.get_playlist_songs(playlist_id)
    
    def get_playlist_tags(self, playlist_id: int) -> List[Tuple]:
        return self.playlist_query.get_playlist_tags(playlist_id)
    
    def add_playlist_song(self, playlist_id: int, song_id: int) -> None:
        return self.playlist_query.add_playlist_song(playlist_id, song_id)
    
    def remove_playlist_song(self, playlist_id: int, song_id: int) -> None:
        return self.playlist_query.remove_playlist_song(playlist_id, song_id)
    
    def add_playlist_tag(self, playlist_id: int, tag_id: int) -> None:
        return self.playlist_query.add_playlist_tag(playlist_id, tag_id)
    
    # Délégation pour l'historique
    def get_song_history(self, song_id: Optional[int] = None, limit: int = 100) -> List[Tuple]:
        return self.song_history_query.get_song_history(song_id, limit) 
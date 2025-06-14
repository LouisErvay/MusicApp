import os
import sqlite3
from typing import List, Tuple, Optional, Dict, Any
from src.objects.folder import LocalFolder, DriveFolder
from src.objects.song import Song

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
                    parent_id INTEGER,
                    drive_id VARCHAR(100),
                    FOREIGN KEY (parent_id) REFERENCES folder(id)
                )
            """)
            
            # Table des chansons
            print("Création de la table 'song'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS song (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    path VARCHAR(255) NOT NULL,
                    parent_id INTEGER NOT NULL,
                    FOREIGN KEY (parent_id) REFERENCES folder(id)
                )
            """)
            
            # Table des tags
            print("Création de la table 'tag'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tag (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT
                )
            """)
            
            # Table de liaison chanson-tag
            print("Création de la table 'song_tag'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS song_tag (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    song_id INTEGER NOT NULL,
                    tag_id INTEGER NOT NULL,
                    FOREIGN KEY (song_id) REFERENCES song(id),
                    FOREIGN KEY (tag_id) REFERENCES tag(id),
                    UNIQUE(song_id, tag_id)
                )
            """)
            
            conn.commit()
            print("Tables créées avec succès!")

    def _migrate_database(self) -> None:
        """Migre la base de données vers la nouvelle structure si nécessaire."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Vérifie si la colonne drive_id existe
            cursor.execute("PRAGMA table_info(folder)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'drive_id' not in columns:
                # Ajoute la colonne drive_id
                cursor.execute("ALTER TABLE folder ADD COLUMN drive_id VARCHAR(100)")
                conn.commit()

            # Vérifie si la colonne description existe dans la table tag
            cursor.execute("PRAGMA table_info(tag)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'description' not in columns:
                # Ajoute la colonne description
                cursor.execute("ALTER TABLE tag ADD COLUMN description TEXT")
                conn.commit()

    def _init_root_folder(self) -> None:
        """Initialise le dossier racine dans la base de données et charge son contenu."""
        print(f"\nInitialisation du dossier racine: {self.root_folder}")
        
        # Extraire le nom du dossier à partir du chemin
        folder_name = os.path.basename(self.root_folder)
        print(f"Nom du dossier racine: {folder_name}")

        # Créer le dossier racine dans la base de données
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO folder (name, path, parent_id) VALUES (?, ?, NULL)",
                (folder_name, self.root_folder)
            )
            conn.commit()
            root_id = cursor.lastrowid
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
        folder_id = parent_id if parent_id is not None else self.add_folder(folder.name, folder.path, parent_id)

        # Ajoute les sous-dossiers et les chansons
        for element in folder.elements:
            if isinstance(element, LocalFolder):
                # Pour les sous-dossiers, on crée toujours un nouveau dossier
                subfolder_id = self.add_folder(element.name, element.path, folder_id)
                # Récursion pour les sous-dossiers
                self.increment_db(element, subfolder_id)
            elif isinstance(element, Song):
                # Ajout des chansons
                song_id = self.add_song(element.name, element.path, folder_id)
                # Ajout des tags de la chanson s'il y en a
                for tag in element.tags:
                    tag_id = self.add_tag(tag)
                    self.add_song_tag(song_id, tag_id)

    def get_folder_by_id(self, folder_id: int) -> Optional[Tuple]:
        """
        Récupère un dossier par son ID.
        
        Args:
            folder_id (int): ID du dossier
            
        Returns:
            Optional[Tuple]: Informations du dossier ou None si non trouvé
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, path, parent_id, drive_id
                FROM folder
                WHERE id = ?
            """, (folder_id,))
            return cursor.fetchone()

    def get_song_by_id(self, song_id: int) -> Optional[Tuple]:
        """
        Récupère une chanson par son ID.
        
        Args:
            song_id (int): ID de la chanson
            
        Returns:
            Optional[Tuple]: Informations de la chanson ou None si non trouvée
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.id, s.name, s.path, s.parent_id, f.name as folder_name,
                       GROUP_CONCAT(t.name) as tags
                FROM song s
                JOIN folder f ON s.parent_id = f.id
                LEFT JOIN song_tag st ON s.id = st.song_id
                LEFT JOIN tag t ON st.tag_id = t.id
                WHERE s.id = ?
                GROUP BY s.id
            """, (song_id,))
            return cursor.fetchone()

    def get_all_songs(self) -> List[Tuple]:
        """
        Récupère toutes les chansons avec leurs informations.
        
        Returns:
            List[Tuple]: Liste des chansons avec leurs informations
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    s.id,
                    s.name,
                    s.path,
                    s.parent_id,
                    f.name as folder_name
                FROM song s
                JOIN folder f ON s.parent_id = f.id
                ORDER BY s.name
            """)
            return cursor.fetchall()

    def get_songs_by_folder(self, folder_ids: List[int]) -> List[Tuple]:
        """
        Récupère les chansons d'un ou plusieurs dossiers.
        
        Args:
            folder_ids (List[int]): Liste des IDs des dossiers
            
        Returns:
            List[Tuple]: Liste des chansons trouvées
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(folder_ids))
            cursor.execute(f"""
                SELECT 
                    s.id,
                    s.name,
                    s.path,
                    s.parent_id,
                    f.name as folder_name
                FROM song s
                JOIN folder f ON s.parent_id = f.id
                WHERE s.parent_id IN ({placeholders})
                ORDER BY s.name
            """, folder_ids)
            return cursor.fetchall()

    def get_songs_by_tag(self, tag_ids: List[int]) -> List[Tuple]:
        """
        Récupère les chansons ayant certains tags.
        
        Args:
            tag_ids (List[int]): Liste des IDs des tags
            
        Returns:
            List[Tuple]: Liste des chansons trouvées
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(tag_ids))
            cursor.execute(f"""
                SELECT 
                    s.id,
                    s.name,
                    s.path,
                    s.parent_id,
                    f.name as folder_name
                FROM song s
                JOIN folder f ON s.parent_id = f.id
                JOIN song_tag st ON s.id = st.song_id
                WHERE st.tag_id IN ({placeholders})
                GROUP BY s.id
                ORDER BY s.name
            """, tag_ids)
            return cursor.fetchall()

    def get_songs_by_folder_and_tag(self, folder_ids: List[int], tag_ids: List[int]) -> List[Tuple]:
        """
        Récupère les chansons ayant certains tags et appartenant à certains dossiers.
        
        Args:
            folder_ids (List[int]): Liste des IDs des dossiers
            tag_ids (List[int]): Liste des IDs des tags
            
        Returns:
            List[Tuple]: Liste des chansons trouvées
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            folder_placeholders = ','.join('?' * len(folder_ids))
            tag_placeholders = ','.join('?' * len(tag_ids))
            
            cursor.execute(f"""
                SELECT 
                    s.id,
                    s.name,
                    s.path,
                    s.parent_id,
                    f.name as folder_name
                FROM song s
                LEFT JOIN song_tag AS specific_tag ON s.id = specific_tag.song_id
                AND specific_tag.tag_id IN ({tag_placeholders})
                LEFT JOIN song_tag ON s.id = song_tag.song_id
                LEFT JOIN tag ON song_tag.tag_id = tag.id
                INNER JOIN folder f ON s.parent_id = f.id
                WHERE s.parent_id IN ({folder_placeholders})
                AND specific_tag.tag_id IS NOT NULL
                GROUP BY s.id
                ORDER BY s.name
            """, tag_ids + folder_ids)
            return cursor.fetchall()

    def get_all_folders(self) -> List[Tuple]:
        """
        Récupère tous les dossiers.
        
        Returns:
            List[Tuple]: Liste des dossiers
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, path, parent_id
                FROM folder
                ORDER BY name
            """)
            return cursor.fetchall()

    def get_all_tags(self) -> List[Tuple]:
        """
        Récupère tous les tags.
        
        Returns:
            List[Tuple]: Liste des tags
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name
                FROM tag
                ORDER BY name
            """)
            return cursor.fetchall()

    def add_song(self, name: str, path: str, parent_id: int) -> int:
        """
        Ajoute une nouvelle chanson.
        
        Args:
            name (str): Nom de la chanson
            path (str): Chemin de la chanson
            parent_id (int): ID du dossier parent
            
        Returns:
            int: ID de la chanson créée
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO song (name, path, parent_id) VALUES (?, ?, ?)",
                (name, path, parent_id)
            )
            conn.commit()
            return cursor.lastrowid

    def add_folder(self, name: str, path: str, parent_id: Optional[int] = None, drive_id: Optional[str] = None) -> int:
        """
        Ajoute un nouveau dossier.
        
        Args:
            name (str): Nom du dossier
            path (str): Chemin du dossier
            parent_id (Optional[int]): ID du dossier parent
            drive_id (Optional[str]): ID Google Drive si applicable
            
        Returns:
            int: ID du dossier créé
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO folder (name, path, parent_id, drive_id) VALUES (?, ?, ?, ?)",
                (name, path, parent_id, drive_id)
            )
            conn.commit()
            return cursor.lastrowid

    def add_tag(self, name: str, description: Optional[str] = None) -> int:
        """
        Ajoute un nouveau tag.
        
        Args:
            name (str): Nom du tag
            description (Optional[str]): Description du tag
            
        Returns:
            int: ID du tag créé
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tag (name, description) VALUES (?, ?)",
                (name, description)
            )
            conn.commit()
            return cursor.lastrowid

    def add_song_tag(self, song_id: int, tag_id: int) -> None:
        """
        Associe un tag à une chanson.
        
        Args:
            song_id (int): ID de la chanson
            tag_id (int): ID du tag
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO song_tag (song_id, tag_id) VALUES (?, ?)",
                (song_id, tag_id)
            )
            conn.commit()

    def remove_song_tag(self, song_id: int, tag_id: int) -> None:
        """
        Retire un tag d'une chanson.
        
        Args:
            song_id (int): ID de la chanson
            tag_id (int): ID du tag
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM song_tag WHERE song_id = ? AND tag_id = ?",
                (song_id, tag_id)
            )
            conn.commit()

    def delete_song(self, song_id: int) -> None:
        """
        Supprime une chanson.
        
        Args:
            song_id (int): ID de la chanson
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM song_tag WHERE song_id = ?", (song_id,))
            cursor.execute("DELETE FROM song WHERE id = ?", (song_id,))
            conn.commit()

    def delete_folder(self, folder_id: int) -> None:
        """
        Supprime un dossier et son contenu.
        
        Args:
            folder_id (int): ID du dossier
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Supprime d'abord les chansons et leurs tags
            cursor.execute("""
                DELETE FROM song_tag 
                WHERE song_id IN (SELECT id FROM song WHERE parent_id = ?)
            """, (folder_id,))
            cursor.execute("DELETE FROM song WHERE parent_id = ?", (folder_id,))
            # Supprime les sous-dossiers
            cursor.execute("DELETE FROM folder WHERE parent_id = ?", (folder_id,))
            # Supprime le dossier lui-même
            cursor.execute("DELETE FROM folder WHERE id = ?", (folder_id,))
            conn.commit()

    def tag_exists(self, tag_name: str) -> bool:
        """
        Vérifie si un tag existe déjà dans la base de données.
        
        Args:
            tag_name (str): Nom du tag à vérifier
            
        Returns:
            bool: True si le tag existe, False sinon
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM tag WHERE name = ?", (tag_name,))
            return cursor.fetchone() is not None

    def delete_tag_by_name(self, tag_name: str) -> bool:
        """
        Supprime un tag et ses associations par son nom.
        
        Args:
            tag_name (str): Nom du tag à supprimer
            
        Returns:
            bool: True si le tag a été supprimé, False s'il n'existe pas
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Récupérer l'ID du tag
            cursor.execute("SELECT id FROM tag WHERE name = ?", (tag_name,))
            tag = cursor.fetchone()
            if not tag:
                return False

            # Supprimer les associations du tag avec les chansons
            cursor.execute("DELETE FROM song_tag WHERE tag_id = ?", (tag[0],))
            # Supprimer le tag
            cursor.execute("DELETE FROM tag WHERE id = ?", (tag[0],))
            conn.commit()
            return True

    def get_song_tags(self, song_id: int) -> List[Tuple]:
        """
        Récupère tous les tags d'une chanson.
        
        Args:
            song_id (int): ID de la chanson
            
        Returns:
            List[Tuple]: Liste des tags (id, name) de la chanson
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.id, t.name
                FROM tag t
                JOIN song_tag st ON t.id = st.tag_id
                WHERE st.song_id = ?
                ORDER BY t.name
            """, (song_id,))
            return cursor.fetchall()

    def update_song_tags(self, song_id: int, tag_ids: List[int]) -> None:
        """
        Met à jour les tags d'une chanson.
        
        Args:
            song_id (int): ID de la chanson
            tag_ids (List[int]): Liste des IDs des tags à associer à la chanson
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Supprimer toutes les associations existantes
            cursor.execute("DELETE FROM song_tag WHERE song_id = ?", (song_id,))
            # Ajouter les nouvelles associations
            for tag_id in tag_ids:
                cursor.execute(
                    "INSERT INTO song_tag (song_id, tag_id) VALUES (?, ?)",
                    (song_id, tag_id)
                )
            conn.commit() 
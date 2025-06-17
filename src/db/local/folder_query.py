import sqlite3
from typing import List, Tuple, Optional

class FolderQuery:
    def __init__(self, db_path: str):
        """
        Initialise le gestionnaire de requêtes pour les dossiers.
        
        Args:
            db_path (str): Chemin vers la base de données SQLite
        """
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Crée et retourne une connexion à la base de données."""
        conn = sqlite3.connect(self.db_path)
        conn.execute('PRAGMA foreign_keys = ON')
        conn.execute('PRAGMA encoding = "UTF-8"')
        return conn

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
                SELECT id, name, path, path_hash, parent_id
                FROM folder
                WHERE id = ?
            """, (folder_id,))
            return cursor.fetchone()

    def get_all_folders(self) -> List[Tuple]:
        """
        Récupère tous les dossiers.
        
        Returns:
            List[Tuple]: Liste des dossiers
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, path, path_hash, parent_id
                FROM folder
                ORDER BY name
            """)
            return cursor.fetchall()

    def add_folder(self, name: str, path: str, path_hash: str, parent_id: Optional[int] = None) -> int:
        """
        Ajoute un nouveau dossier.
        
        Args:
            name (str): Nom du dossier
            path (str): Chemin relatif du dossier
            path_hash (str): Hash du chemin
            parent_id (Optional[int]): ID du dossier parent
            
        Returns:
            int: ID du dossier créé
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO folder (name, path, path_hash, parent_id) VALUES (?, ?, ?, ?)",
                (name, path, path_hash, parent_id)
            )
            conn.commit()
            return cursor.lastrowid

    def delete_folder(self, folder_id: int) -> None:
        """
        Supprime un dossier et son contenu.
        
        Args:
            folder_id (int): ID du dossier
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Récupérer les IDs des chansons à supprimer
            cursor.execute("SELECT id FROM song WHERE folder_id = ?", (folder_id,))
            song_ids = [row[0] for row in cursor.fetchall()]
            
            # Supprimer les associations des chansons
            for song_id in song_ids:
                cursor.execute("DELETE FROM song_tag WHERE song_id = ?", (song_id,))
                cursor.execute("DELETE FROM playlist_song WHERE song_id = ?", (song_id,))
            
            # Supprimer les chansons
            cursor.execute("DELETE FROM song WHERE folder_id = ?", (folder_id,))
            
            # Supprimer les sous-dossiers récursivement
            cursor.execute("SELECT id FROM folder WHERE parent_id = ?", (folder_id,))
            subfolder_ids = [row[0] for row in cursor.fetchall()]
            for subfolder_id in subfolder_ids:
                self.delete_folder(subfolder_id)
            
            # Supprimer le dossier lui-même
            cursor.execute("DELETE FROM folder WHERE id = ?", (folder_id,))
            conn.commit()

    def get_folder_by_path_hash(self, path_hash: str) -> Optional[Tuple]:
        """
        Récupère un dossier par son hash de chemin.
        
        Args:
            path_hash (str): Hash du chemin du dossier
            
        Returns:
            Optional[Tuple]: Informations du dossier ou None si non trouvé
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, path, path_hash, parent_id
                FROM folder
                WHERE path_hash = ?
            """, (path_hash,))
            return cursor.fetchone()

    def get_subfolders(self, parent_id: int) -> List[Tuple]:
        """
        Récupère tous les sous-dossiers d'un dossier parent.
        
        Args:
            parent_id (int): ID du dossier parent
            
        Returns:
            List[Tuple]: Liste des sous-dossiers
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, path, path_hash, parent_id
                FROM folder
                WHERE parent_id = ?
                ORDER BY name
            """, (parent_id,))
            return cursor.fetchall()

    def get_root_folders(self) -> List[Tuple]:
        """
        Récupère tous les dossiers racine (sans parent).
        
        Returns:
            List[Tuple]: Liste des dossiers racine
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, path, path_hash, parent_id
                FROM folder
                WHERE parent_id IS NULL
                ORDER BY name
            """)
            return cursor.fetchall() 
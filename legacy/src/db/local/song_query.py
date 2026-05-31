import sqlite3
import time
from typing import List, Tuple, Optional

class SongQuery:
    def __init__(self, db_path: str):
        """
        Initialise le gestionnaire de requêtes pour les chansons.
        
        Args:
            db_path (str): Chemin vers la base de données SQLite
        """
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Crée et retourne une connexion à la base de données."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('PRAGMA foreign_keys = ON')
            conn.execute('PRAGMA encoding = "UTF-8"')
            return conn
        except sqlite3.Error as e:
            print(f"Erreur lors de la connexion à la base de données: {e}")
            raise

    def get_song_by_id(self, song_id: int) -> Optional[Tuple]:
        """
        Récupère une chanson par son ID.
        
        Args:
            song_id (int): ID de la chanson
            
        Returns:
            Optional[Tuple]: Informations de la chanson ou None si non trouvée
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT s.id, s.name, s.full_path, s.rel_path, s.rel_path_hash, 
                           s.file_hash, s.folder_id, s.last_modified, s.present_locally, 
                           s.synced_at, f.name as folder_name,
                           GROUP_CONCAT(t.name) as tags
                    FROM song s
                    JOIN folder f ON s.folder_id = f.id
                    LEFT JOIN song_tag st ON s.id = st.song_id
                    LEFT JOIN tag t ON st.tag_id = t.id
                    WHERE s.id = ?
                    GROUP BY s.id
                """, (song_id,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération de la chanson {song_id}: {e}")
            return None

    def get_all_songs(self) -> List[Tuple]:
        """
        Récupère toutes les chansons avec leurs informations.
        
        Returns:
            List[Tuple]: Liste des chansons avec leurs informations
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        s.id,
                        s.name,
                        s.full_path,
                        s.rel_path,
                        s.folder_id,
                        f.name as folder_name,
                        s.present_locally
                    FROM song s
                    JOIN folder f ON s.folder_id = f.id
                    ORDER BY s.name
                """)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération de toutes les chansons: {e}")
            return []

    def get_songs_by_folder(self, folder_ids: List[int]) -> List[Tuple]:
        """
        Récupère les chansons d'un ou plusieurs dossiers.
        
        Args:
            folder_ids (List[int]): Liste des IDs des dossiers
            
        Returns:
            List[Tuple]: Liste des chansons trouvées
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                placeholders = ','.join('?' * len(folder_ids))
                cursor.execute(f"""
                    SELECT 
                        s.id,
                        s.name,
                        s.full_path,
                        s.rel_path,
                        s.folder_id,
                        f.name as folder_name,
                        s.present_locally
                    FROM song s
                    JOIN folder f ON s.folder_id = f.id
                    WHERE s.folder_id IN ({placeholders})
                    ORDER BY s.name
                """, folder_ids)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération des chansons par dossiers: {e}")
            return []

    def get_songs_by_tag(self, tag_ids: List[int]) -> List[Tuple]:
        """
        Récupère les chansons ayant certains tags.
        
        Args:
            tag_ids (List[int]): Liste des IDs des tags
            
        Returns:
            List[Tuple]: Liste des chansons trouvées
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                placeholders = ','.join('?' * len(tag_ids))
                cursor.execute(f"""
                    SELECT 
                        s.id,
                        s.name,
                        s.full_path,
                        s.rel_path,
                        s.folder_id,
                        f.name as folder_name,
                        s.present_locally
                    FROM song s
                    JOIN folder f ON s.folder_id = f.id
                    JOIN song_tag st ON s.id = st.song_id
                    WHERE st.tag_id IN ({placeholders})
                    GROUP BY s.id
                    ORDER BY s.name
                """, tag_ids)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération des chansons par tags: {e}")
            return []

    def get_songs_by_folder_and_tag(self, folder_ids: List[int], tag_ids: List[int]) -> List[Tuple]:
        """
        Récupère les chansons ayant certains tags et appartenant à certains dossiers.
        
        Args:
            folder_ids (List[int]): Liste des IDs des dossiers
            tag_ids (List[int]): Liste des IDs des tags
            
        Returns:
            List[Tuple]: Liste des chansons trouvées
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                folder_placeholders = ','.join('?' * len(folder_ids))
                tag_placeholders = ','.join('?' * len(tag_ids))
                
                cursor.execute(f"""
                    SELECT 
                        s.id,
                        s.name,
                        s.full_path,
                        s.rel_path,
                        s.folder_id,
                        f.name as folder_name,
                        s.present_locally
                    FROM song s
                    LEFT JOIN song_tag AS specific_tag ON s.id = specific_tag.song_id
                    AND specific_tag.tag_id IN ({tag_placeholders})
                    LEFT JOIN song_tag ON s.id = song_tag.song_id
                    LEFT JOIN tag ON song_tag.tag_id = tag.id
                    INNER JOIN folder f ON s.folder_id = f.id
                    WHERE s.folder_id IN ({folder_placeholders})
                    AND specific_tag.tag_id IS NOT NULL
                    GROUP BY s.id
                    ORDER BY s.name
                """, tag_ids + folder_ids)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération des chansons par dossiers et tags: {e}")
            return []

    def add_song(self, name: str, full_path: str, rel_path: str, rel_path_hash: str, 
                 file_hash: str, folder_id: int, last_modified: int, 
                 present_locally: bool = True) -> int:
        """
        Ajoute une nouvelle chanson.
        
        Args:
            name (str): Nom de la chanson
            full_path (str): Chemin absolu de la chanson
            rel_path (str): Chemin relatif de la chanson
            rel_path_hash (str): Hash du chemin relatif
            file_hash (str): Hash du contenu du fichier
            folder_id (int): ID du dossier parent
            last_modified (int): Timestamp de dernière modification
            present_locally (bool): Si le fichier est présent localement
            
        Returns:
            int: ID de la chanson créée
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO song (name, full_path, rel_path, rel_path_hash, file_hash, 
                                    folder_id, last_modified, present_locally)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, full_path, rel_path, rel_path_hash, file_hash, 
                      folder_id, last_modified, 1 if present_locally else 0))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erreur lors de l'ajout de la chanson '{name}': {e}")
            return -1

    def delete_song(self, song_id: int) -> None:
        """
        Supprime une chanson.
        
        Args:
            song_id (int): ID de la chanson
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Supprimer les associations
                cursor.execute("DELETE FROM song_tag WHERE song_id = ?", (song_id,))
                cursor.execute("DELETE FROM playlist_song WHERE song_id = ?", (song_id,))
                
                # Supprimer la chanson
                cursor.execute("DELETE FROM song WHERE id = ?", (song_id,))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de la suppression de la chanson {song_id}: {e}")

    def get_song_tags(self, song_id: int) -> List[Tuple]:
        """
        Récupère tous les tags d'une chanson.
        
        Args:
            song_id (int): ID de la chanson
            
        Returns:
            List[Tuple]: Liste des tags (id, name) de la chanson
        """
        try:
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
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération des tags de la chanson {song_id}: {e}")
            return []

    def update_song_tags(self, song_id: int, tag_ids: List[int]) -> None:
        """
        Met à jour les tags d'une chanson.
        
        Args:
            song_id (int): ID de la chanson
            tag_ids (List[int]): Liste des IDs des tags à associer à la chanson
        """
        try:
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
        except sqlite3.Error as e:
            print(f"Erreur lors de la mise à jour des tags de la chanson {song_id}: {e}")

    def add_song_tag(self, song_id: int, tag_id: int) -> None:
        """
        Associe un tag à une chanson.
        
        Args:
            song_id (int): ID de la chanson
            tag_id (int): ID du tag
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO song_tag (song_id, tag_id) VALUES (?, ?)",
                    (song_id, tag_id)
                )
                conn.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de l'ajout du tag {tag_id} à la chanson {song_id}: {e}")

    def remove_song_tag(self, song_id: int, tag_id: int) -> None:
        """
        Retire un tag d'une chanson.
        
        Args:
            song_id (int): ID de la chanson
            tag_id (int): ID du tag
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM song_tag WHERE song_id = ? AND tag_id = ?",
                    (song_id, tag_id)
                )
                conn.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de la suppression du tag {tag_id} de la chanson {song_id}: {e}")

    def update_song_sync_status(self, song_id: int, synced_at: int) -> None:
        """
        Met à jour le statut de synchronisation d'une chanson.
        
        Args:
            song_id (int): ID de la chanson
            synced_at (int): Timestamp de synchronisation
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE song SET synced_at = ? WHERE id = ?",
                    (synced_at, song_id)
                )
                conn.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de la mise à jour du statut de sync de la chanson {song_id}: {e}")

    def mark_song_as_missing(self, song_id: int) -> None:
        """
        Marque une chanson comme non présente localement.
        
        Args:
            song_id (int): ID de la chanson
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE song SET present_locally = 0 WHERE id = ?",
                    (song_id,)
                )
                conn.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors du marquage comme manquante de la chanson {song_id}: {e}") 
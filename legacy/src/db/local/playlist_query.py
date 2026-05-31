import sqlite3
from typing import List, Tuple, Optional

class PlaylistQuery:
    def __init__(self, db_path: str):
        """
        Initialise le gestionnaire de requêtes pour les playlists.
        
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

    def get_all_playlists(self) -> List[Tuple]:
        """
        Récupère toutes les playlists.
        
        Returns:
            List[Tuple]: Liste des playlists
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name
                    FROM playlist
                    ORDER BY name
                """)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération de toutes les playlists: {e}")
            return []

    def get_playlist_by_id(self, playlist_id: int) -> Optional[Tuple]:
        """
        Récupère une playlist par son ID.
        
        Args:
            playlist_id (int): ID de la playlist
            
        Returns:
            Optional[Tuple]: Informations de la playlist ou None si non trouvée
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name
                    FROM playlist
                    WHERE id = ?
                """, (playlist_id,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération de la playlist {playlist_id}: {e}")
            return None

    def get_playlist_by_name(self, name: str) -> Optional[Tuple]:
        """
        Récupère une playlist par son nom.
        
        Args:
            name (str): Nom de la playlist
            
        Returns:
            Optional[Tuple]: Informations de la playlist ou None si non trouvée
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name
                    FROM playlist
                    WHERE name = ?
                """, (name,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération de la playlist '{name}': {e}")
            return None

    def add_playlist(self, name: str) -> int:
        """
        Ajoute une nouvelle playlist.
        
        Args:
            name (str): Nom de la playlist
            
        Returns:
            int: ID de la playlist créée
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO playlist (name) VALUES (?)", (name,))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erreur lors de l'ajout de la playlist '{name}': {e}")
            return -1

    def delete_playlist(self, playlist_id: int) -> None:
        """
        Supprime une playlist.
        
        Args:
            playlist_id (int): ID de la playlist
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM playlist_song WHERE playlist_id = ?", (playlist_id,))
                cursor.execute("DELETE FROM playlist_tag WHERE playlist_id = ?", (playlist_id,))
                cursor.execute("DELETE FROM playlist WHERE id = ?", (playlist_id,))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de la suppression de la playlist {playlist_id}: {e}")

    def get_playlist_songs(self, playlist_id: int) -> List[Tuple]:
        """
        Récupère toutes les chansons d'une playlist.
        
        Args:
            playlist_id (int): ID de la playlist
            
        Returns:
            List[Tuple]: Liste des chansons de la playlist
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT s.id, s.name, s.full_path, s.rel_path, 
                           s.folder_id, f.name as folder_name, s.present_locally
                    FROM song s
                    JOIN folder f ON s.folder_id = f.id
                    JOIN playlist_song ps ON s.id = ps.song_id
                    WHERE ps.playlist_id = ?
                    ORDER BY s.name
                """, (playlist_id,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération des chansons de la playlist {playlist_id}: {e}")
            return []

    def get_playlist_tags(self, playlist_id: int) -> List[Tuple]:
        """
        Récupère tous les tags d'une playlist.
        
        Args:
            playlist_id (int): ID de la playlist
            
        Returns:
            List[Tuple]: Liste des tags (id, name) de la playlist
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT t.id, t.name
                    FROM tag t
                    JOIN playlist_tag pt ON t.id = pt.tag_id
                    WHERE pt.playlist_id = ?
                    ORDER BY t.name
                """, (playlist_id,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération des tags de la playlist {playlist_id}: {e}")
            return []

    def add_playlist_song(self, playlist_id: int, song_id: int) -> None:
        """
        Ajoute une chanson à une playlist.
        
        Args:
            playlist_id (int): ID de la playlist
            song_id (int): ID de la chanson
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO playlist_song (playlist_id, song_id) VALUES (?, ?)",
                    (playlist_id, song_id)
                )
                conn.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de l'ajout de la chanson {song_id} à la playlist {playlist_id}: {e}")

    def remove_playlist_song(self, playlist_id: int, song_id: int) -> None:
        """
        Retire une chanson d'une playlist.
        
        Args:
            playlist_id (int): ID de la playlist
            song_id (int): ID de la chanson
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM playlist_song WHERE playlist_id = ? AND song_id = ?",
                    (playlist_id, song_id)
                )
                conn.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de la suppression de la chanson {song_id} de la playlist {playlist_id}: {e}")

    def add_playlist_tag(self, playlist_id: int, tag_id: int) -> None:
        """
        Associe un tag à une playlist.
        
        Args:
            playlist_id (int): ID de la playlist
            tag_id (int): ID du tag
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO playlist_tag (playlist_id, tag_id) VALUES (?, ?)",
                    (playlist_id, tag_id)
                )
                conn.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de l'ajout du tag {tag_id} à la playlist {playlist_id}: {e}")

    def remove_playlist_tag(self, playlist_id: int, tag_id: int) -> None:
        """
        Retire un tag d'une playlist.
        
        Args:
            playlist_id (int): ID de la playlist
            tag_id (int): ID du tag
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM playlist_tag WHERE playlist_id = ? AND tag_id = ?",
                    (playlist_id, tag_id)
                )
                conn.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de la suppression du tag {tag_id} de la playlist {playlist_id}: {e}")

    def update_playlist_songs(self, playlist_id: int, song_ids: List[int]) -> None:
        """
        Met à jour les chansons d'une playlist.
        
        Args:
            playlist_id (int): ID de la playlist
            song_ids (List[int]): Liste des IDs des chansons à associer à la playlist
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Supprimer toutes les associations existantes
                cursor.execute("DELETE FROM playlist_song WHERE playlist_id = ?", (playlist_id,))
                # Ajouter les nouvelles associations
                for song_id in song_ids:
                    cursor.execute(
                        "INSERT INTO playlist_song (playlist_id, song_id) VALUES (?, ?)",
                        (playlist_id, song_id)
                    )
                conn.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de la mise à jour des chansons de la playlist {playlist_id}: {e}")

    def update_playlist_tags(self, playlist_id: int, tag_ids: List[int]) -> None:
        """
        Met à jour les tags d'une playlist.
        
        Args:
            playlist_id (int): ID de la playlist
            tag_ids (List[int]): Liste des IDs des tags à associer à la playlist
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Supprimer toutes les associations existantes
                cursor.execute("DELETE FROM playlist_tag WHERE playlist_id = ?", (playlist_id,))
                # Ajouter les nouvelles associations
                for tag_id in tag_ids:
                    cursor.execute(
                        "INSERT INTO playlist_tag (playlist_id, tag_id) VALUES (?, ?)",
                        (playlist_id, tag_id)
                    )
                conn.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de la mise à jour des tags de la playlist {playlist_id}: {e}")

    def get_playlists_with_song_count(self) -> List[Tuple]:
        """
        Récupère toutes les playlists avec le nombre de chansons qu'elles contiennent.
        
        Returns:
            List[Tuple]: Liste des playlists avec leur nombre de chansons (id, name, song_count)
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        p.id, 
                        p.name,
                        COALESCE(COUNT(ps.song_id), 0) as song_count
                    FROM playlist p
                    LEFT JOIN playlist_song ps ON p.id = ps.playlist_id
                    GROUP BY p.id, p.name
                    ORDER BY p.name
                """)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération des playlists avec compteur: {e}")
            return []

    def playlist_exists(self, name: str) -> bool:
        """
        Vérifie si une playlist avec ce nom existe déjà.
        
        Args:
            name (str): Nom de la playlist à vérifier
            
        Returns:
            bool: True si la playlist existe, False sinon
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM playlist WHERE name = ?", (name,))
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"Erreur lors de la vérification d'existence de la playlist '{name}': {e}")
            return False 
import sqlite3
from typing import List, Tuple, Optional

class TagQuery:
    def __init__(self, db_path: str):
        """
        Initialise le gestionnaire de requêtes pour les tags.
        
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

    def get_all_tags(self) -> List[Tuple]:
        """
        Récupère tous les tags.
        
        Returns:
            List[Tuple]: Liste des tags
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name
                    FROM tag
                    ORDER BY name
                """)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération de tous les tags: {e}")
            return []

    def get_tag_by_id(self, tag_id: int) -> Optional[Tuple]:
        """
        Récupère un tag par son ID.
        
        Args:
            tag_id (int): ID du tag
            
        Returns:
            Optional[Tuple]: Informations du tag ou None si non trouvé
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name
                    FROM tag
                    WHERE id = ?
                """, (tag_id,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération du tag {tag_id}: {e}")
            return None

    def get_tag_by_name(self, name: str) -> Optional[Tuple]:
        """
        Récupère un tag par son nom.
        
        Args:
            name (str): Nom du tag
            
        Returns:
            Optional[Tuple]: Informations du tag ou None si non trouvé
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name
                    FROM tag
                    WHERE name = ?
                """, (name,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération du tag '{name}': {e}")
            return None

    def add_tag(self, name: str) -> int:
        """
        Ajoute un nouveau tag ou retourne l'ID du tag existant.
        
        Args:
            name (str): Nom du tag
            
        Returns:
            int: ID du tag créé ou existant
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Vérifier si le tag existe déjà
                cursor.execute("SELECT id FROM tag WHERE name = ?", (name,))
                existing = cursor.fetchone()
                if existing:
                    return existing[0]
                
                # Créer le nouveau tag
                cursor.execute("INSERT INTO tag (name) VALUES (?)", (name,))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erreur lors de l'ajout du tag '{name}': {e}")
            return -1

    def tag_exists(self, tag_name: str) -> bool:
        """
        Vérifie si un tag existe déjà dans la base de données.
        
        Args:
            tag_name (str): Nom du tag à vérifier
            
        Returns:
            bool: True si le tag existe, False sinon
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM tag WHERE name = ?", (tag_name,))
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"Erreur lors de la vérification d'existence du tag '{tag_name}': {e}")
            return False

    def delete_tag_by_name(self, tag_name: str) -> bool:
        """
        Supprime un tag et ses associations par son nom.
        
        Args:
            tag_name (str): Nom du tag à supprimer
            
        Returns:
            bool: True si le tag a été supprimé, False s'il n'existe pas
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Récupérer l'ID du tag
                cursor.execute("SELECT id FROM tag WHERE name = ?", (tag_name,))
                tag = cursor.fetchone()
                if not tag:
                    return False

                # Supprimer les associations du tag
                cursor.execute("DELETE FROM song_tag WHERE tag_id = ?", (tag[0],))
                cursor.execute("DELETE FROM playlist_tag WHERE tag_id = ?", (tag[0],))
                # Supprimer le tag
                cursor.execute("DELETE FROM tag WHERE id = ?", (tag[0],))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Erreur lors de la suppression du tag '{tag_name}': {e}")
            return False

    def delete_tag_by_id(self, tag_id: int) -> bool:
        """
        Supprime un tag et ses associations par son ID.
        
        Args:
            tag_id (int): ID du tag à supprimer
            
        Returns:
            bool: True si le tag a été supprimé, False s'il n'existe pas
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Vérifier si le tag existe
                cursor.execute("SELECT id FROM tag WHERE id = ?", (tag_id,))
                if not cursor.fetchone():
                    return False

                # Supprimer les associations du tag
                cursor.execute("DELETE FROM song_tag WHERE tag_id = ?", (tag_id,))
                cursor.execute("DELETE FROM playlist_tag WHERE tag_id = ?", (tag_id,))
                # Supprimer le tag
                cursor.execute("DELETE FROM tag WHERE id = ?", (tag_id,))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Erreur lors de la suppression du tag {tag_id}: {e}")
            return False

    def get_tags_usage_count(self) -> List[Tuple]:
        """
        Récupère tous les tags avec leur nombre d'utilisations (chansons + playlists).
        
        Returns:
            List[Tuple]: Liste des tags avec leur compteur d'usage (id, name, song_count, playlist_count, total_count)
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        t.id, 
                        t.name,
                        COALESCE(song_count, 0) as song_count,
                        COALESCE(playlist_count, 0) as playlist_count,
                        COALESCE(song_count, 0) + COALESCE(playlist_count, 0) as total_count
                    FROM tag t
                    LEFT JOIN (
                        SELECT tag_id, COUNT(*) as song_count
                        FROM song_tag
                        GROUP BY tag_id
                    ) st ON t.id = st.tag_id
                    LEFT JOIN (
                        SELECT tag_id, COUNT(*) as playlist_count
                        FROM playlist_tag
                        GROUP BY tag_id
                    ) pt ON t.id = pt.tag_id
                    ORDER BY total_count DESC, t.name
                """)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération des statistiques d'usage des tags: {e}")
            return []

    def get_unused_tags(self) -> List[Tuple]:
        """
        Récupère tous les tags qui ne sont utilisés par aucune chanson ni playlist.
        
        Returns:
            List[Tuple]: Liste des tags non utilisés
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT t.id, t.name
                    FROM tag t
                    LEFT JOIN song_tag st ON t.id = st.tag_id
                    LEFT JOIN playlist_tag pt ON t.id = pt.tag_id
                    WHERE st.tag_id IS NULL AND pt.tag_id IS NULL
                    ORDER BY t.name
                """)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération des tags non utilisés: {e}")
            return [] 
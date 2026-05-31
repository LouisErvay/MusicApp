import sqlite3
from typing import List, Tuple, Optional

class SongHistoryQuery:
    def __init__(self, db_path: str):
        """
        Initialise le gestionnaire de requêtes pour l'historique des chansons.
        
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

    def add_song_history(self, song_id: int, operation_type: str, timestamp: int, 
                        from_path: Optional[str] = None, to_path: Optional[str] = None) -> None:
        """
        Ajoute une entrée dans l'historique des chansons.
        
        Args:
            song_id (int): ID de la chanson
            operation_type (str): Type d'opération (added, deleted, moved, etc.)
            timestamp (int): Timestamp Unix de l'opération
            from_path (Optional[str]): Chemin source pour les déplacements
            to_path (Optional[str]): Chemin destination pour les déplacements
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO song_history (song_id, operation_type, timestamp, from_path, to_path)
                    VALUES (?, ?, ?, ?, ?)
                """, (song_id, operation_type, timestamp, from_path, to_path))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Erreur lors de l'ajout de l'historique pour la chanson {song_id}: {e}")

    def get_song_history(self, song_id: Optional[int] = None, limit: int = 100) -> List[Tuple]:
        """
        Récupère l'historique des opérations sur les chansons.
        
        Args:
            song_id (Optional[int]): ID de la chanson (None pour toutes)
            limit (int): Nombre maximum d'entrées à retourner
            
        Returns:
            List[Tuple]: Liste des entrées d'historique
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if song_id is not None:
                    cursor.execute("""
                        SELECT id, song_id, operation_type, timestamp, from_path, to_path
                        FROM song_history
                        WHERE song_id = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    """, (song_id, limit))
                else:
                    cursor.execute("""
                        SELECT id, song_id, operation_type, timestamp, from_path, to_path
                        FROM song_history
                        ORDER BY timestamp DESC
                        LIMIT ?
                    """, (limit,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération de l'historique des chansons: {e}")
            return []

    def get_history_by_operation(self, operation_type: str, limit: int = 100) -> List[Tuple]:
        """
        Récupère l'historique filtré par type d'opération.
        
        Args:
            operation_type (str): Type d'opération à filtrer
            limit (int): Nombre maximum d'entrées à retourner
            
        Returns:
            List[Tuple]: Liste des entrées d'historique
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, song_id, operation_type, timestamp, from_path, to_path
                    FROM song_history
                    WHERE operation_type = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (operation_type, limit))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération de l'historique par opération '{operation_type}': {e}")
            return []

    def get_recent_history(self, hours: int = 24) -> List[Tuple]:
        """
        Récupère l'historique récent des dernières heures.
        
        Args:
            hours (int): Nombre d'heures dans le passé
            
        Returns:
            List[Tuple]: Liste des entrées d'historique récentes
        """
        try:
            import time
            cutoff_timestamp = int(time.time()) - (hours * 3600)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, song_id, operation_type, timestamp, from_path, to_path
                    FROM song_history
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                """, (cutoff_timestamp,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération de l'historique récent ({hours}h): {e}")
            return []

    def clear_old_history(self, days: int = 30) -> int:
        """
        Supprime l'historique plus ancien que le nombre de jours spécifié.
        
        Args:
            days (int): Nombre de jours à conserver
            
        Returns:
            int: Nombre d'entrées supprimées
        """
        try:
            import time
            cutoff_timestamp = int(time.time()) - (days * 24 * 3600)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM song_history
                    WHERE timestamp < ?
                """, (cutoff_timestamp,))
                deleted_count = cursor.rowcount
                conn.commit()
                return deleted_count
        except sqlite3.Error as e:
            print(f"Erreur lors de la suppression de l'ancien historique (>{days} jours): {e}")
            return 0 
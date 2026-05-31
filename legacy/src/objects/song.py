from typing import List, Optional, Dict, Any
from .base import BaseObject

class Song(BaseObject):
    """Classe représentant une chanson."""
    
    def __init__(self, name: str, path: str):
        super().__init__(name, path)
        self.tags: List[str] = []
        self.metadata: Dict[str, Any] = {}

    def load(self) -> None:
        """Charge les métadonnées de la chanson."""
        # TODO: Implémenter le chargement des métadonnées (ID3, etc.)
        pass

    def add_tag(self, tag: str) -> None:
        """Ajoute un tag à la chanson."""
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        """Retire un tag de la chanson."""
        if tag in self.tags:
            self.tags.remove(tag)

    def get_tags(self) -> List[str]:
        """Retourne la liste des tags."""
        return self.tags

    def set_metadata(self, key: str, value: Any) -> None:
        """Définit une métadonnée."""
        self.metadata[key] = value

    def get_metadata(self, key: str) -> Optional[Any]:
        """Récupère une métadonnée."""
        return self.metadata.get(key)

    def get_all_metadata(self) -> Dict[str, Any]:
        """Retourne toutes les métadonnées."""
        return self.metadata.copy() 
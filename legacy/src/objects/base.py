from abc import ABC, abstractmethod
from typing import List, Optional, Any

class BaseObject(ABC):
    """Classe de base pour tous les objets du système."""
    
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        self.elements: List[Any] = []
        self.parent: Optional['BaseObject'] = None

    @abstractmethod
    def load(self) -> None:
        """Charge les données de l'objet depuis sa source."""
        pass

    def add_element(self, element: Any) -> None:
        """Ajoute un élément à la liste des éléments."""
        self.elements.append(element)
        if hasattr(element, 'parent'):
            element.parent = self

    def get_elements(self) -> List[Any]:
        """Retourne la liste des éléments."""
        return self.elements

    def get_parent(self) -> Optional['BaseObject']:
        """Retourne le parent de l'objet."""
        return self.parent

    def set_parent(self, parent: 'BaseObject') -> None:
        """Définit le parent de l'objet."""
        self.parent = parent 
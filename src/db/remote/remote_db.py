import requests
import os
from typing import Dict, Optional, Any
from dotenv import load_dotenv

class RemoteDb:
    def __init__(self):
        """
        Initialise le gestionnaire de base de données distante.
        """
        load_dotenv()
        self.api_url = os.getenv('API_URL')
        if not self.api_url:
            raise ValueError("La variable d'environnement API_URL n'est pas définie")
        
        # Supprimer le slash final s'il existe
        self.api_url = self.api_url.rstrip('/')
        
        # Tokens d'authentification
        self.access_token = None
        self.refresh_token = None
        self.user_data = None
        
        print(f"RemoteDb initialisée avec l'URL: {self.api_url}")

    def _get_headers(self) -> Dict[str, str]:
        """
        Génère les headers pour les requêtes HTTP avec authentification automatique.
        
        Returns:
            Dict[str, str]: Headers avec token d'authentification si disponible
        """
        headers = {'Content-Type': 'application/json'}
        
        if self.access_token:
            headers['Authorization'] = f'Token {self.access_token}'
            
        return headers

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     retry_on_token_error: bool = True) -> requests.Response:
        """
        Effectue une requête HTTP vers l'API avec gestion automatique du refresh des tokens.
        
        Args:
            method (str): Méthode HTTP (GET, POST, etc.)
            endpoint (str): Point de terminaison de l'API
            data (Optional[Dict]): Données à envoyer
            retry_on_token_error (bool): Si True, tente un refresh automatique sur erreur 498
            
        Returns:
            requests.Response: Réponse de l'API
            
        Raises:
            requests.exceptions.RequestException: En cas d'erreur de requête
        """
        url = f"{self.api_url}{endpoint}"
        headers = self._get_headers()
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=data)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Méthode HTTP non supportée: {method}")
            
            # Gestion automatique du refresh des tokens sur code d'erreur 498
            if response.status_code == 498 and retry_on_token_error and self.refresh_token:
                print("Token expiré (code 498), tentative de refresh automatique...")
                if self.refresh_access_token():
                    print("Token refreshé avec succès, nouvelle tentative de requête...")
                    # Nouvelle tentative avec le token rafraîchi
                    return self._make_request(method, endpoint, data, retry_on_token_error=False)
                else:
                    print("Échec du refresh automatique, déconnexion nécessaire")
                    self.logout()
                    raise requests.exceptions.HTTPError("Token invalide et refresh impossible")
            
            return response
            
        except requests.exceptions.RequestException as e:
            self._handle_request_error(e)
            raise

    def _handle_request_error(self, error: requests.exceptions.RequestException) -> None:
        """
        Gère les erreurs de requête.
        
        Args:
            error: L'erreur de requête à traiter
        """
        if hasattr(error, 'response') and error.response is not None:
            # Erreur de réponse API
            print(f"Erreur de réponse API: Status {error.response.status_code}")
            
            if error.response.status_code == 498:
                print("Code 498: Token non valide détecté")
                
        elif hasattr(error, 'request'):
            # Erreur de requête (pas de réponse reçue)
            print("Erreur de requête API: Aucune réponse reçue")
            
        else:
            # Autres types d'erreurs
            print(f"Erreur: {str(error)}")

    def _get_user_friendly_error(self, exception: Exception) -> str:
        """
        Convertit une exception en message d'erreur convivial pour l'utilisateur.
        
        Args:
            exception (Exception): L'exception à convertir
            
        Returns:
            str: Message d'erreur convivial
        """
        error_str = str(exception).lower()
        
        if "connection refused" in error_str or "connexion" in error_str and "refusée" in error_str:
            return "Impossible de se connecter au serveur. Vérifiez que le serveur est démarré."
        elif "timeout" in error_str:
            return "Délai d'attente dépassé. Le serveur met trop de temps à répondre."
        elif "name or service not known" in error_str or "nodename nor servname provided" in error_str:
            return "Adresse du serveur introuvable. Vérifiez l'URL dans la configuration."
        elif "max retries exceeded" in error_str:
            return "Impossible de joindre le serveur après plusieurs tentatives."
        elif "network is unreachable" in error_str:
            return "Réseau inaccessible. Vérifiez votre connexion internet."
        elif "token invalide" in error_str:
            return "Session expirée. Veuillez vous reconnecter."
        else:
            return "Erreur de connexion au serveur. Vérifiez votre configuration réseau."

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authentifie l'utilisateur auprès de l'API.
        
        Args:
            username (str): Nom d'utilisateur
            password (str): Mot de passe
            
        Returns:
            Dict[str, Any]: Réponse de l'API avec les tokens et les données utilisateur
        """
        endpoint = "/user/login/"
        data = {
            "username": username,
            "password": password
        }
        
        try:
            response = self._make_request('POST', endpoint, data, retry_on_token_error=False)
            
            if response.status_code == 200:
                response_data = response.json()
                self.access_token = response_data.get('access')
                self.refresh_token = response_data.get('refresh')
                self.user_data = response_data.get('user')
                
                print(f"Connexion réussie pour l'utilisateur: {self.user_data.get('username')}")
                return {
                    'success': True,
                    'data': response_data,
                    'message': 'Connexion réussie'
                }
            else:
                error_data = response.json() if response.content else {'error': 'Erreur inconnue'}
                return {
                    'success': False,
                    'error': error_data.get('error', 'Identifiants invalides'),
                    'status_code': response.status_code
                }
                
        except requests.exceptions.ConnectionError as e:
            user_error = self._get_user_friendly_error(e)
            print(f"Erreur de connexion: {user_error}")
            return {
                'success': False,
                'error': user_error,
                'status_code': None
            }
        except requests.exceptions.Timeout as e:
            user_error = "Le serveur met trop de temps à répondre."
            print(f"Erreur de timeout: {user_error}")
            return {
                'success': False,
                'error': user_error,
                'status_code': None
            }
        except requests.exceptions.RequestException as e:
            user_error = self._get_user_friendly_error(e)
            print(f"Erreur de requête: {user_error}")
            return {
                'success': False,
                'error': user_error,
                'status_code': None
            }
        except Exception as e:
            user_error = "Une erreur inattendue s'est produite."
            print(f"Erreur inattendue lors de la connexion: {str(e)}")
            return {
                'success': False,
                'error': user_error,
                'status_code': None
            }

    def refresh_access_token(self) -> bool:
        """
        Rafraîchit le token d'accès en utilisant le token de rafraîchissement.
        
        Returns:
            bool: True si le rafraîchissement a réussi, False sinon
        """
        if not self.refresh_token:
            print("Aucun token de rafraîchissement disponible")
            return False
        
        endpoint = "/token/refresh/"
        data = {"refresh": self.refresh_token}
        
        try:
            # Requête sans retry automatique pour éviter la récursion
            response = self._make_request('POST', endpoint, data, retry_on_token_error=False)
            
            if response.status_code == 200:
                response_data = response.json()
                self.access_token = response_data.get('access')
                
                # Mettre à jour aussi le refresh token s'il est fourni
                if 'refresh' in response_data:
                    self.refresh_token = response_data.get('refresh')
                
                print("Token rafraîchi avec succès")
                return True
            else:
                print(f"Échec du rafraîchissement du token: Status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors du rafraîchissement du token: {self._get_user_friendly_error(e)}")
            return False
        except Exception as e:
            print(f"Erreur inattendue lors du rafraîchissement: {str(e)}")
            return False

    def logout(self) -> None:
        """
        Déconnecte l'utilisateur en supprimant les tokens.
        """
        self.access_token = None
        self.refresh_token = None
        self.user_data = None
        print("Utilisateur déconnecté")

    def is_authenticated(self) -> bool:
        """
        Vérifie si l'utilisateur est authentifié.
        
        Returns:
            bool: True si l'utilisateur est authentifié, False sinon
        """
        return self.access_token is not None

    def get_user_data(self) -> Optional[Dict[str, Any]]:
        """
        Retourne les données de l'utilisateur connecté.
        
        Returns:
            Optional[Dict[str, Any]]: Données utilisateur ou None si non connecté
        """
        return self.user_data

    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """
        Effectue une requête GET avec gestion automatique des tokens.
        
        Args:
            endpoint (str): Point de terminaison de l'API
            params (Optional[Dict]): Paramètres de requête
            
        Returns:
            requests.Response: Réponse de l'API
        """
        return self._make_request('GET', endpoint, params)

    def post(self, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        """
        Effectue une requête POST avec gestion automatique des tokens.
        
        Args:
            endpoint (str): Point de terminaison de l'API
            data (Optional[Dict]): Données à envoyer
            
        Returns:
            requests.Response: Réponse de l'API
        """
        return self._make_request('POST', endpoint, data)

    def put(self, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        """
        Effectue une requête PUT avec gestion automatique des tokens.
        
        Args:
            endpoint (str): Point de terminaison de l'API
            data (Optional[Dict]): Données à envoyer
            
        Returns:
            requests.Response: Réponse de l'API
        """
        return self._make_request('PUT', endpoint, data)

    def delete(self, endpoint: str) -> requests.Response:
        """
        Effectue une requête DELETE avec gestion automatique des tokens.
        
        Args:
            endpoint (str): Point de terminaison de l'API
            
        Returns:
            requests.Response: Réponse de l'API
        """
        return self._make_request('DELETE', endpoint)

import dearpygui.dearpygui as dpg
from src.db.remote.remote_db import RemoteDb

class Remote:
    def __init__(self):
        """
        Initialise le composant Remote pour la gestion de l'authentification distante.
        """
        self.remote_db = RemoteDb()
        self.is_authenticated = False
        self.current_user = None
        
        # Variables pour les champs de saisie
        self.username_value = ""
        self.password_value = ""
        self.status_message = "Entrez vos identifiants pour vous connecter"
        
        print("Composant Remote initialisé")

    def create(self):
        """
        Crée l'interface utilisateur du composant Remote.
        """
        with dpg.group(tag="remote_container"):
            with dpg.child_window(autosize_x=True, height=400, no_scrollbar=True, tag="remote_main_window"):
                dpg.add_text("Connexion à distance", color=(255, 255, 255))
                dpg.add_separator()
                dpg.add_spacer(height=10)
                
                # Créer un conteneur pour le contenu dynamique
                with dpg.group(tag="remote_content"):
                    if not self.is_authenticated:
                        # Interface de connexion
                        self._create_login_interface()
                    else:
                        # Interface utilisateur connecté
                        self._create_authenticated_interface()

    def _create_login_interface(self):
        """
        Crée l'interface de connexion.
        """
        with dpg.group(tag="login_interface", parent="remote_content"):
            # Champ nom d'utilisateur
            dpg.add_text("Nom d'utilisateur:")
            dpg.add_input_text(
                tag="username_input",
                width=200,
                hint="Entrez votre nom d'utilisateur",
                callback=self._on_username_change
            )
            
            dpg.add_spacer(height=5)
            
            # Champ mot de passe
            dpg.add_text("Mot de passe:")
            dpg.add_input_text(
                tag="password_input",
                width=200,
                password=True,
                hint="Entrez votre mot de passe",
                callback=self._on_password_change
            )
            
            dpg.add_spacer(height=10)
            
            # Boutons
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Se connecter",
                    width=100,
                    height=30,
                    callback=self._attempt_login
                )
                dpg.add_button(
                    label="Effacer",
                    width=100,
                    height=30,
                    callback=self._clear_fields
                )
            
            dpg.add_spacer(height=10)
            
            # Message de statut
            dpg.add_text(
                self.status_message,
                tag="status_message",
                color=(200, 200, 200)
            )
            
            # Gestionnaire de clavier pour Enter
            with dpg.handler_registry():
                dpg.add_key_press_handler(dpg.mvKey_Return, callback=self._on_enter_pressed)

    def _create_authenticated_interface(self):
        """
        Crée l'interface pour un utilisateur connecté.
        """
        with dpg.group(tag="authenticated_interface", parent="remote_content"):
            dpg.add_text("✓ Connexion réussie!", color=(0, 255, 0))
            dpg.add_spacer(height=10)
            
            if self.current_user:
                dpg.add_text(f"Bienvenue, {self.current_user.get('username', 'Utilisateur')}")
                dpg.add_text(f"Email: {self.current_user.get('email', 'Non spécifié')}")
                dpg.add_text(f"ID: {self.current_user.get('id', 'Non spécifié')}")
            
            dpg.add_spacer(height=20)
            
            # Message de succès
            dpg.add_text("OK", color=(0, 255, 0), tag="success_message")
            
            dpg.add_spacer(height=20)
            
            # Bouton de déconnexion
            dpg.add_button(
                label="Se déconnecter",
                width=120,
                height=30,
                callback=self._logout
            )

    def _on_enter_pressed(self, sender, app_data):
        """
        Gestionnaire appelé quand la touche Enter est pressée.
        """
        # Vérifier si on est dans l'interface de connexion
        if not self.is_authenticated:
            # Vérifier si l'un des champs de saisie est actif
            if dpg.does_item_exist("username_input") or dpg.does_item_exist("password_input"):
                self._attempt_login()

    def _on_username_change(self, sender, app_data):
        """
        Callback appelé quand le nom d'utilisateur change.
        """
        self.username_value = app_data

    def _on_password_change(self, sender, app_data):
        """
        Callback appelé quand le mot de passe change.
        """
        self.password_value = app_data

    def _attempt_login(self, sender=None, app_data=None):
        """
        Tente de se connecter avec les identifiants saisis.
        """
        # Récupérer les valeurs actuelles des champs
        username = dpg.get_value("username_input") if dpg.does_item_exist("username_input") else ""
        password = dpg.get_value("password_input") if dpg.does_item_exist("password_input") else ""
        
        if not username or not password:
            self._update_status("Veuillez saisir un nom d'utilisateur et un mot de passe", error=True)
            return
        
        # Mettre à jour le statut
        self._update_status("Connexion en cours...", color=(255, 255, 0))
        
        try:
            # Tentative de connexion
            result = self.remote_db.login(username, password)
            
            if result['success']:
                # Connexion réussie
                print("Connexion réussie, mise à jour de l'état...")
                self.is_authenticated = True
                self.current_user = result['data']['user']
                print(f"État mis à jour: is_authenticated = {self.is_authenticated}")
                print(f"Utilisateur actuel: {self.current_user}")
                
                # Recréer l'interface
                self._refresh_interface()
                
            else:
                # Connexion échouée
                error_message = result.get('error', 'Erreur de connexion')
                self._update_status(f"Erreur: {error_message}", error=True)
                
        except Exception as e:
            self._update_status(f"Erreur inattendue: {str(e)}", error=True)

    def _logout(self, sender=None, app_data=None):
        """
        Déconnecte l'utilisateur en utilisant la méthode remote_db.
        """
        print("Début de la déconnexion...")
        
        # Utiliser la méthode logout de remote_db
        self.remote_db.logout()
        
        # Mettre à jour l'état local
        self.is_authenticated = False
        self.current_user = None
        self.status_message = "Déconnecté avec succès"
        
        print(f"État après déconnexion: is_authenticated = {self.is_authenticated}")
        
        # Effacer les champs
        self._clear_fields()
        
        # Recréer l'interface
        self._refresh_interface()

    def _clear_fields(self, sender=None, app_data=None):
        """
        Vide les champs de saisie.
        """
        if dpg.does_item_exist("username_input"):
            dpg.set_value("username_input", "")
        if dpg.does_item_exist("password_input"):
            dpg.set_value("password_input", "")
        
        self.username_value = ""
        self.password_value = ""

    def _update_status(self, message: str, error: bool = False, color: tuple = None):
        """
        Met à jour le message de statut.
        
        Args:
            message (str): Message à afficher
            error (bool): Si True, affiche en rouge
            color (tuple): Couleur personnalisée (R, G, B)
        """
        self.status_message = message
        
        if dpg.does_item_exist("status_message"):
            if error:
                dpg.configure_item("status_message", default_value=message, color=(255, 100, 100))
            elif color:
                dpg.configure_item("status_message", default_value=message, color=color)
            else:
                dpg.configure_item("status_message", default_value=message, color=(200, 200, 200))

    def _refresh_interface(self):
        """
        Rafraîchit l'interface en fonction de l'état de connexion.
        """
        print(f"Rafraîchissement de l'interface, is_authenticated = {self.is_authenticated}")
        
        # Supprimer tout le contenu existant
        if dpg.does_item_exist("remote_content"):
            # Supprimer tous les enfants du conteneur
            children = dpg.get_item_children("remote_content", slot=1)  # slot=1 pour les enfants directs
            if children:
                for child in children:
                    if dpg.does_item_exist(child):
                        dpg.delete_item(child)
        
        # Recréer l'interface appropriée
        if not self.is_authenticated:
            print("Création de l'interface de connexion...")
            self._create_login_interface()
        else:
            print("Création de l'interface utilisateur connecté...")
            self._create_authenticated_interface()
        
        print("Rafraîchissement terminé.")

    def get_remote_db(self):
        """
        Retourne l'instance de RemoteDb.
        
        Returns:
            RemoteDb: Instance de la base de données distante
        """
        return self.remote_db

    def is_user_authenticated(self):
        """
        Vérifie si l'utilisateur est authentifié.
        
        Returns:
            bool: True si authentifié, False sinon
        """
        return self.is_authenticated

    def get_current_user(self):
        """
        Retourne les données de l'utilisateur connecté.
        
        Returns:
            dict: Données utilisateur ou None si non connecté
        """
        return self.current_user

# Installation

## Prérequis :

- Python
- Npm

### Configuration variables d'environnement :
- **Pour le `back` :**  
Copier et compléter le fichier `.env.example` en `.env`
    - **Avoir une base de données PostgreSQL :**  
    Configurer dans le `.env` la base de données PostgreSQL.

- **Pour le `front` :**  
Copier et compléter le fichier `.env.example` en `.env`

## Installer les dépendances :
Lancer la commande `make install` pour installer les dépendances.  

## Lancer le projet :
**Pour le `back` :**  
- Lancer via le launch.json `Start back`

**ou**

- ligne de commande :
```bash
cd back
.venv/Scripts/python -m uvicorn src.app:app --reload --host 127.0.0.1 --port 8000
```

**Pour le `front` :**

En ligne de commande :
```bash
cd front
npm run dev
```
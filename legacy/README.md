# MusicApp

## Description

C'est une simple application de gestion de musiques permettant de lire de scanner dans un dossier donner tous les sous-dossiers et fichiers audio compatibles avec pygames.

Une base de donnée SQLite est crée à la racine du dossier qui est donné à scanner.

L'application à les fonctions d'un lecteur de musique de base.

On peut également créer des tags et lier les musiques à ces derniers

## Setup

En plus de l'installation des librairies python, il faut ajouter un '.env' à la racine du projet.

Ce .env contient une seule ligne:

SONG_FOLDER_PATH=VOTRE_CHEMIN_DACCESS_AU_DOSSIER

Ou VOTRE_CHEMIN_DACCESS_AU_DOSSIER est le chemin jusqu'au dossier jusqu'à vos musiques que l'application va utiliser.

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Downloader - Application de téléchargement YouTube
==========================================================

Une application graphique moderne pour télécharger des vidéos et audios YouTube.

Fonctionnalités:
- Téléchargement audio (MP3, AAC, WAV, FLAC, OGG, M4A, OPUS, WMA)
- Téléchargement vidéo (MP4, MKV, WEBM, AVI, MOV, FLV)
- Détection automatique des qualités disponibles
- Barre de progression en temps réel
- Historique des téléchargements
- Mode sombre/clair

Auteur: YouTube Downloader Team
Version: 1.0.0
"""

import sys
import os

# Ajouter le dossier racine au path pour les imports
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


def check_dependencies():
    """
    Vérifie que toutes les dépendances sont installées.
    Affiche un message d'erreur explicite si une dépendance manque.
    """
    missing = []
    
    try:
        import customtkinter
    except ImportError:
        missing.append("customtkinter")
    
    try:
        import yt_dlp
    except ImportError:
        missing.append("yt-dlp")
    
    try:
        from PIL import Image
    except ImportError:
        missing.append("Pillow")
    
    try:
        import requests
    except ImportError:
        missing.append("requests")
    
    if missing:
        print("=" * 60)
        print("ERREUR : Dépendances manquantes")
        print("=" * 60)
        print(f"\nLes modules suivants ne sont pas installés : {', '.join(missing)}")
        print("\nPour installer les dépendances, exécutez :")
        print("  pip install -r requirements.txt")
        print("\nOu installez-les individuellement :")
        for dep in missing:
            print(f"  pip install {dep}")
        print()
        return False
    
    return True


def create_directories():
    """Crée les dossiers nécessaires pour l'application."""
    directories = [
        os.path.join(ROOT_DIR, 'config'),
        os.path.join(ROOT_DIR, 'data'),
        os.path.join(ROOT_DIR, 'assets')
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except Exception as e:
                print(f"Avertissement : Impossible de créer {directory}: {e}")


def main():
    """Point d'entrée principal de l'application."""
    # Vérifier les dépendances
    if not check_dependencies():
        sys.exit(1)
    
    # Créer les dossiers nécessaires
    create_directories()
    
    # Importer et lancer l'application
    try:
        from gui.app import YouTubeDownloaderApp
        
        # Créer et lancer l'application
        app = YouTubeDownloaderApp()
        app.mainloop()
        
    except Exception as e:
        import traceback
        print("=" * 60)
        print("ERREUR : L'application a rencontré une erreur")
        print("=" * 60)
        print(f"\nDétails : {str(e)}")
        print("\nTrace complète :")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


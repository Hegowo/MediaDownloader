# ⬇️ Media Downloader

Une application graphique moderne et universelle pour télécharger des vidéos et audios depuis **YouTube, TikTok, Instagram, Twitter/X, et +1000 autres sites**.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## ✨ Fonctionnalités

- **+1000 sites supportés** grâce à yt-dlp
- **Interface graphique moderne** avec CustomTkinter
- **Mode sombre/clair** avec sauvegarde de la préférence
- **Détection automatique** de la plateforme et des formats disponibles
- **Formats audio** : MP3, AAC, WAV, FLAC, OGG, M4A, OPUS, WMA
- **Formats vidéo** : MP4, MKV, WEBM, AVI, MOV, FLV
- **Qualités vidéo** : 144p à 8K (selon disponibilité)
- **Barre de progression** avec vitesse et temps restant
- **Historique des téléchargements**
- **Renommage du fichier** avant téléchargement

## 🌐 Plateformes Supportées

| Plateforme | Support |
|------------|---------|
| 🎬 YouTube | ✅ Vidéos, Shorts, Music, Playlists |
| 🎵 TikTok | ✅ Vidéos |
| 📸 Instagram | ✅ Reels, Posts, Stories |
| 🐦 Twitter/X | ✅ Vidéos, GIFs |
| 📘 Facebook | ✅ Vidéos, Reels |
| 🎮 Twitch | ✅ Clips, VODs |
| 📺 Dailymotion | ✅ Vidéos |
| 🎥 Vimeo | ✅ Vidéos |
| 🤖 Reddit | ✅ Vidéos |
| 🌐 Et +1000 autres... | ✅ Sites de streaming, etc. |

## 📋 Prérequis

- **Python 3.8** ou supérieur
- **FFmpeg** (requis pour la conversion audio/vidéo)
- Connexion Internet

### Installation de FFmpeg

#### Windows
```bash
winget install FFmpeg
```
Ou via Chocolatey : `choco install ffmpeg`

#### macOS
```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

## 🚀 Installation

### 1. Cloner ou télécharger le projet

```bash
git clone https://github.com/votre-repo/media-downloader.git
cd media-downloader
```

### 2. Créer un environnement virtuel (recommandé)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

## 🎮 Utilisation

### Lancer l'application

```bash
python main.py
```

### Workflow de téléchargement

1. **Coller l'URL** de n'importe quelle plateforme supportée
2. **La plateforme est détectée automatiquement** (badge affiché)
3. **Cliquer sur "Analyser"** pour récupérer les informations
4. **Choisir le type** : Audio ou Vidéo
5. **Sélectionner le format** et la qualité souhaitée
6. **Modifier le nom du fichier** si nécessaire
7. **Choisir le dossier** de destination
8. **Cliquer sur "Télécharger"**

### URLs supportées (exemples)

```
# YouTube
https://www.youtube.com/watch?v=VIDEO_ID
https://youtu.be/VIDEO_ID
https://www.youtube.com/shorts/VIDEO_ID

# TikTok
https://www.tiktok.com/@user/video/123456789

# Instagram
https://www.instagram.com/reel/ABC123/
https://www.instagram.com/p/ABC123/

# Twitter/X
https://twitter.com/user/status/123456789
https://x.com/user/status/123456789

# Et bien plus...
```

## 📁 Structure du projet

```
MediaDownloader/
├── main.py                 # Point d'entrée de l'application
├── requirements.txt        # Dépendances Python
├── README.md               # Ce fichier
│
├── gui/                    # Interface graphique
│   ├── __init__.py
│   ├── app.py              # Fenêtre principale
│   ├── widgets.py          # Composants personnalisés
│   └── themes.py           # Gestion des thèmes
│
├── core/                   # Logique métier
│   ├── __init__.py
│   ├── downloader.py       # Téléchargement avec yt-dlp
│   ├── validator.py        # Validation des URLs multi-plateformes
│   └── formats.py          # Définition des formats
│
├── utils/                  # Utilitaires
│   ├── __init__.py
│   └── history.py          # Gestion de l'historique
│
├── config/                 # Configuration
│   └── theme.json          # Préférence de thème
│
└── data/                   # Données
    └── history.json        # Historique des téléchargements
```

## 🔧 Dépannage

### "FFmpeg not found"
Assurez-vous que FFmpeg est installé et accessible. Après installation avec winget, **redémarrez votre terminal**.

### Vidéo privée ou indisponible
Certains contenus ne sont pas accessibles (privés, restrictions géographiques, etc.).

### Site non supporté
Vérifiez si le site est dans la [liste des sites supportés par yt-dlp](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).

### Erreur de connexion
Vérifiez votre connexion Internet et réessayez.

## 📄 Licence

Ce projet est sous licence MIT.

## ⚠️ Avertissement légal

Cet outil est fourni à des fins éducatives. Respectez les conditions d'utilisation des plateformes et les droits d'auteur. Ne téléchargez que du contenu pour lequel vous avez les droits ou l'autorisation.

---

Développé avec ❤️ en Python | Propulsé par [yt-dlp](https://github.com/yt-dlp/yt-dlp)

# -*- coding: utf-8 -*-
"""
Module de validation des URLs pour plusieurs plateformes.
Supporte YouTube, TikTok, Instagram, Twitter/X, Facebook, et bien d'autres.
"""

import re
from typing import Optional, Tuple, Dict
from urllib.parse import urlparse


class Platform:
    """Représente une plateforme de vidéos supportée."""
    
    def __init__(self, name: str, icon: str, domains: list, color: str = "#ffffff"):
        self.name = name
        self.icon = icon
        self.domains = domains
        self.color = color


# Plateformes supportées avec leurs domaines
SUPPORTED_PLATFORMS: Dict[str, Platform] = {
    'youtube': Platform(
        name='YouTube',
        icon='🎬',
        domains=['youtube.com', 'youtu.be', 'youtube-nocookie.com', 'music.youtube.com'],
        color='#FF0000'
    ),
    'tiktok': Platform(
        name='TikTok',
        icon='🎵',
        domains=['tiktok.com', 'vm.tiktok.com'],
        color='#000000'
    ),
    'instagram': Platform(
        name='Instagram',
        icon='📸',
        domains=['instagram.com', 'instagr.am'],
        color='#E4405F'
    ),
    'twitter': Platform(
        name='Twitter/X',
        icon='🐦',
        domains=['twitter.com', 'x.com', 't.co'],
        color='#1DA1F2'
    ),
    'facebook': Platform(
        name='Facebook',
        icon='📘',
        domains=['facebook.com', 'fb.watch', 'fb.com'],
        color='#1877F2'
    ),
    'twitch': Platform(
        name='Twitch',
        icon='🎮',
        domains=['twitch.tv', 'clips.twitch.tv'],
        color='#9146FF'
    ),
    'vimeo': Platform(
        name='Vimeo',
        icon='🎥',
        domains=['vimeo.com', 'player.vimeo.com'],
        color='#1AB7EA'
    ),
    'dailymotion': Platform(
        name='Dailymotion',
        icon='📺',
        domains=['dailymotion.com', 'dai.ly'],
        color='#0066DC'
    ),
    'reddit': Platform(
        name='Reddit',
        icon='🤖',
        domains=['reddit.com', 'redd.it', 'v.redd.it'],
        color='#FF4500'
    ),
    'soundcloud': Platform(
        name='SoundCloud',
        icon='🎧',
        domains=['soundcloud.com'],
        color='#FF5500'
    ),
    'pinterest': Platform(
        name='Pinterest',
        icon='📌',
        domains=['pinterest.com', 'pin.it'],
        color='#E60023'
    ),
    'bilibili': Platform(
        name='Bilibili',
        icon='📺',
        domains=['bilibili.com', 'b23.tv'],
        color='#00A1D6'
    ),
    'generic': Platform(
        name='Site Web',
        icon='🌐',
        domains=[],
        color='#666666'
    )
}


class URLValidator:
    """
    Classe pour valider les URLs de vidéos de multiples plateformes.
    Utilise yt-dlp qui supporte plus de 1000 sites.
    """
    
    @classmethod
    def detect_platform(cls, url: str) -> Platform:
        """
        Détecte la plateforme à partir de l'URL.
        
        Args:
            url: L'URL à analyser
            
        Returns:
            Platform correspondante ou 'generic' si non reconnue
        """
        if not url:
            return SUPPORTED_PLATFORMS['generic']
        
        try:
            parsed = urlparse(url.lower().strip())
            domain = parsed.netloc.replace('www.', '')
            
            for platform_id, platform in SUPPORTED_PLATFORMS.items():
                if platform_id == 'generic':
                    continue
                for platform_domain in platform.domains:
                    if platform_domain in domain:
                        return platform
            
            return SUPPORTED_PLATFORMS['generic']
        except Exception:
            return SUPPORTED_PLATFORMS['generic']
    
    @classmethod
    def is_valid_url(cls, url: str) -> bool:
        """
        Vérifie si l'URL est une URL valide (format basique).
        
        Args:
            url: L'URL à vérifier
            
        Returns:
            True si l'URL a un format valide
        """
        if not url or not isinstance(url, str):
            return False
        
        url = url.strip()
        
        # Vérifier le format basique d'une URL
        url_pattern = re.compile(
            r'^https?://'  # http:// ou https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domaine
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ou IP
            r'(?::\d+)?'  # port optionnel
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return url_pattern.match(url) is not None
    
    @classmethod
    def validate_url(cls, url: str) -> Tuple[bool, str, Optional[Platform]]:
        """
        Valide une URL et retourne un tuple avec le résultat.
        
        Args:
            url: L'URL à valider
            
        Returns:
            Tuple (is_valid, message, platform)
        """
        if not url:
            return False, "Veuillez entrer une URL", None
        
        url = url.strip()
        
        # Ajouter https:// si manquant
        if not url.startswith(('http://', 'https://')):
            if url.startswith('www.') or '.' in url.split('/')[0]:
                url = 'https://' + url
        
        if not cls.is_valid_url(url):
            return False, "Format d'URL invalide", None
        
        platform = cls.detect_platform(url)
        
        return True, f"URL {platform.name} détectée", platform
    
    @classmethod
    def normalize_url(cls, url: str) -> str:
        """
        Normalise une URL (ajoute https:// si nécessaire).
        
        Args:
            url: L'URL à normaliser
            
        Returns:
            L'URL normalisée
        """
        url = url.strip()
        
        if not url.startswith(('http://', 'https://')):
            if url.startswith('www.') or '.' in url.split('/')[0]:
                url = 'https://' + url
        
        return url


class URLValidationError(Exception):
    """Exception levée lors d'une erreur de validation d'URL."""
    pass

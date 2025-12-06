# Module core - Logique métier du téléchargeur de médias
# Ce module contient les classes et fonctions pour interagir avec yt-dlp

from .downloader import MediaDownloader, YouTubeDownloader  # YouTubeDownloader = alias
from .validator import URLValidator, SUPPORTED_PLATFORMS
from .formats import AUDIO_FORMATS, VIDEO_FORMATS, AUDIO_BITRATES, VIDEO_QUALITIES

__all__ = [
    'MediaDownloader',
    'YouTubeDownloader',  # Alias pour rétrocompatibilité
    'URLValidator',
    'SUPPORTED_PLATFORMS',
    'AUDIO_FORMATS',
    'VIDEO_FORMATS',
    'AUDIO_BITRATES',
    'VIDEO_QUALITIES'
]


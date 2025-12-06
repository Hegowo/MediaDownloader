# -*- coding: utf-8 -*-
"""
Constantes des formats audio et vidéo supportés par l'application.
Définit les formats disponibles, les bitrates audio et les qualités vidéo.
"""

# ============================================================================
# FORMATS AUDIO SUPPORTÉS
# ============================================================================
AUDIO_FORMATS = {
    'mp3': {
        'name': 'MP3',
        'extension': 'mp3',
        'codec': 'libmp3lame',
        'description': 'Format audio universel, compatible partout',
        'supports_bitrate': True
    },
    'aac': {
        'name': 'AAC',
        'extension': 'm4a',
        'codec': 'aac',
        'description': 'Format Apple, haute qualité',
        'supports_bitrate': True
    },
    'wav': {
        'name': 'WAV',
        'extension': 'wav',
        'codec': 'pcm_s16le',
        'description': 'Audio non compressé, qualité maximale',
        'supports_bitrate': False
    },
    'flac': {
        'name': 'FLAC',
        'extension': 'flac',
        'codec': 'flac',
        'description': 'Compression sans perte, audiophile',
        'supports_bitrate': False
    },
    'ogg': {
        'name': 'OGG Vorbis',
        'extension': 'ogg',
        'codec': 'libvorbis',
        'description': 'Format libre, bonne qualité',
        'supports_bitrate': True
    },
    'm4a': {
        'name': 'M4A',
        'extension': 'm4a',
        'codec': 'aac',
        'description': 'Format Apple Music',
        'supports_bitrate': True
    },
    'opus': {
        'name': 'OPUS',
        'extension': 'opus',
        'codec': 'libopus',
        'description': 'Format moderne, excellent à bas débit',
        'supports_bitrate': True
    },
    'wma': {
        'name': 'WMA',
        'extension': 'wma',
        'codec': 'wmav2',
        'description': 'Format Windows Media',
        'supports_bitrate': True
    }
}

# ============================================================================
# BITRATES AUDIO DISPONIBLES (en kbps)
# ============================================================================
AUDIO_BITRATES = {
    '128': {
        'value': 128,
        'label': '128 kbps',
        'description': 'Qualité standard'
    },
    '192': {
        'value': 192,
        'label': '192 kbps',
        'description': 'Bonne qualité'
    },
    '256': {
        'value': 256,
        'label': '256 kbps',
        'description': 'Haute qualité'
    },
    '320': {
        'value': 320,
        'label': '320 kbps',
        'description': 'Qualité maximale MP3'
    }
}

# ============================================================================
# FORMATS VIDÉO SUPPORTÉS
# ============================================================================
VIDEO_FORMATS = {
    'mp4': {
        'name': 'MP4',
        'extension': 'mp4',
        'codec': 'h264',
        'description': 'Format universel, compatible partout'
    },
    'mkv': {
        'name': 'MKV',
        'extension': 'mkv',
        'codec': 'h264',
        'description': 'Format conteneur flexible'
    },
    'webm': {
        'name': 'WEBM',
        'extension': 'webm',
        'codec': 'vp9',
        'description': 'Format web optimisé'
    },
    'avi': {
        'name': 'AVI',
        'extension': 'avi',
        'codec': 'h264',
        'description': 'Format classique Windows'
    },
    'mov': {
        'name': 'MOV',
        'extension': 'mov',
        'codec': 'h264',
        'description': 'Format Apple QuickTime'
    },
    'flv': {
        'name': 'FLV',
        'extension': 'flv',
        'codec': 'h264',
        'description': 'Format Flash Video'
    }
}

# ============================================================================
# QUALITÉS VIDÉO POSSIBLES
# ============================================================================
VIDEO_QUALITIES = {
    '144': {
        'height': 144,
        'label': '144p',
        'description': 'Très basse qualité'
    },
    '240': {
        'height': 240,
        'label': '240p',
        'description': 'Basse qualité'
    },
    '360': {
        'height': 360,
        'label': '360p',
        'description': 'Qualité standard'
    },
    '480': {
        'height': 480,
        'label': '480p (SD)',
        'description': 'Définition standard'
    },
    '720': {
        'height': 720,
        'label': '720p (HD)',
        'description': 'Haute définition'
    },
    '1080': {
        'height': 1080,
        'label': '1080p (Full HD)',
        'description': 'Full HD'
    },
    '1440': {
        'height': 1440,
        'label': '1440p (2K)',
        'description': 'Quad HD / 2K'
    },
    '2160': {
        'height': 2160,
        'label': '2160p (4K)',
        'description': 'Ultra HD / 4K'
    },
    '4320': {
        'height': 4320,
        'label': '4320p (8K)',
        'description': 'Ultra HD / 8K'
    }
}

def get_audio_format_list():
    """Retourne la liste des formats audio pour l'affichage."""
    return [(key, info['name']) for key, info in AUDIO_FORMATS.items()]

def get_video_format_list():
    """Retourne la liste des formats vidéo pour l'affichage."""
    return [(key, info['name']) for key, info in VIDEO_FORMATS.items()]

def get_bitrate_list():
    """Retourne la liste des bitrates pour l'affichage."""
    return [(key, info['label']) for key, info in AUDIO_BITRATES.items()]

def get_quality_label(height):
    """Retourne le label de qualité pour une hauteur donnée."""
    height_str = str(height)
    if height_str in VIDEO_QUALITIES:
        return VIDEO_QUALITIES[height_str]['label']
    return f"{height}p"


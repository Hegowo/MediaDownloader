# -*- coding: utf-8 -*-
"""
Module principal de téléchargement utilisant yt-dlp.
Supporte plus de 1000 sites : YouTube, TikTok, Instagram, Twitter, sites de streaming, etc.
"""

import os
import threading
import shutil
import subprocess
import re
from typing import Optional, Dict, List, Callable, Any
import yt_dlp

from .formats import AUDIO_FORMATS, VIDEO_FORMATS, VIDEO_QUALITIES, get_quality_label


def find_ffmpeg() -> Optional[str]:
    """
    Recherche le chemin de FFmpeg sur le système.
    
    Returns:
        Chemin vers le dossier contenant ffmpeg.exe ou None si non trouvé
    """
    # 1. Vérifier si ffmpeg est dans le PATH
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return os.path.dirname(ffmpeg_path)
    
    # 2. Chercher dans les emplacements Windows courants
    possible_paths = [
        # WinGet installation
        os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\WinGet\Packages'),
        # Chocolatey
        r'C:\ProgramData\chocolatey\bin',
        # Scoop
        os.path.expandvars(r'%USERPROFILE%\scoop\shims'),
        # Installation manuelle courante
        r'C:\ffmpeg\bin',
        r'C:\Program Files\ffmpeg\bin',
        r'C:\Program Files (x86)\ffmpeg\bin',
    ]
    
    for base_path in possible_paths:
        if os.path.exists(base_path):
            # Chercher ffmpeg.exe récursivement
            for root, dirs, files in os.walk(base_path):
                if 'ffmpeg.exe' in files:
                    return root
    
    # 3. Essayer de trouver via where.exe (Windows)
    try:
        result = subprocess.run(
            ['where.exe', 'ffmpeg'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            ffmpeg_exe = result.stdout.strip().split('\n')[0]
            return os.path.dirname(ffmpeg_exe)
    except Exception:
        pass
    
    return None


# Chemin FFmpeg détecté au chargement du module
FFMPEG_LOCATION = find_ffmpeg()


class DownloadError(Exception):
    """Exception levée lors d'une erreur de téléchargement."""
    pass


class VideoInfo:
    """Classe contenant les informations d'une vidéo/média."""
    
    def __init__(self, data: Dict):
        self.id = data.get('id', '')
        self.title = data.get('title', 'Titre inconnu')
        self.author = data.get('uploader', data.get('channel', data.get('creator', 'Auteur inconnu')))
        self.duration = data.get('duration', 0)
        self.thumbnail = self._get_best_thumbnail(data)
        self.description = data.get('description', '')
        self.view_count = data.get('view_count', 0)
        self.upload_date = data.get('upload_date', '')
        self.extractor = data.get('extractor', 'generic')
        self.webpage_url = data.get('webpage_url', data.get('url', ''))
        self.available_qualities = []
        self.formats = data.get('formats', [])
        self.is_live = data.get('is_live', False)
        
        # Extraire les qualités disponibles
        self._extract_available_qualities()
    
    def _get_best_thumbnail(self, data: Dict) -> str:
        """Récupère la meilleure miniature disponible."""
        # Essayer d'abord le thumbnail principal
        if data.get('thumbnail'):
            return data['thumbnail']
        
        # Sinon chercher dans la liste des thumbnails
        thumbnails = data.get('thumbnails', [])
        if thumbnails:
            # Trier par préférence (resolution si disponible)
            sorted_thumbs = sorted(
                thumbnails,
                key=lambda x: x.get('preference', 0) or x.get('width', 0) or 0,
                reverse=True
            )
            if sorted_thumbs:
                return sorted_thumbs[0].get('url', '')
        
        return ''
    
    def _extract_available_qualities(self):
        """Extrait les qualités vidéo disponibles depuis les formats."""
        heights = set()
        
        for fmt in self.formats:
            # On ne garde que les formats vidéo (avec une hauteur)
            height = fmt.get('height')
            vcodec = fmt.get('vcodec', '')
            
            # Ignorer les formats audio-only
            if height and vcodec and vcodec != 'none':
                heights.add(height)
        
        # Inclure aussi les qualités non-standard pour certains sites
        all_heights = sorted(heights) if heights else []
        
        # Filtrer vers les qualités standard si possible
        standard_heights = [144, 240, 360, 480, 720, 1080, 1440, 2160, 4320]
        standard_available = [h for h in all_heights if h in standard_heights]
        
        # Si on a des qualités standard, les utiliser, sinon garder tout
        if standard_available:
            self.available_qualities = standard_available
        elif all_heights:
            # Garder les qualités disponibles même non-standard
            self.available_qualities = all_heights
        else:
            # Par défaut, proposer les qualités courantes
            self.available_qualities = [720, 1080]
    
    def get_duration_formatted(self) -> str:
        """Retourne la durée formatée (HH:MM:SS ou MM:SS)."""
        if not self.duration:
            return "00:00"
        
        try:
            duration = int(self.duration)
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            seconds = duration % 60
            
            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes:02d}:{seconds:02d}"
        except (ValueError, TypeError):
            return "00:00"
    
    def get_quality_options(self) -> List[tuple]:
        """Retourne les options de qualité pour l'interface."""
        options = []
        for height in self.available_qualities:
            label = get_quality_label(height)
            options.append((height, label))
        
        # S'assurer qu'il y a au moins une option
        if not options:
            options = [(720, "720p (HD)"), (1080, "1080p (Full HD)")]
        
        return options


class MediaDownloader:
    """
    Classe principale pour télécharger des médias depuis n'importe quel site.
    Utilise yt-dlp qui supporte plus de 1000 sites.
    """
    
    # User-Agent pour simuler un navigateur moderne
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    def __init__(self):
        self.current_download = None
        self.is_downloading = False
        self.should_cancel = False
        self._progress_callback: Optional[Callable] = None
        self._complete_callback: Optional[Callable] = None
        self._error_callback: Optional[Callable] = None
    
    def set_callbacks(self, 
                      progress: Optional[Callable] = None,
                      complete: Optional[Callable] = None,
                      error: Optional[Callable] = None):
        """
        Définit les callbacks pour le suivi du téléchargement.
        
        Args:
            progress: Callback(percent, speed, eta) appelé pendant le téléchargement
            complete: Callback(filepath) appelé à la fin du téléchargement
            error: Callback(error_message) appelé en cas d'erreur
        """
        self._progress_callback = progress
        self._complete_callback = complete
        self._error_callback = error
    
    def _get_base_options(self) -> Dict:
        """Retourne les options de base pour yt-dlp."""
        opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'no_color': True,
            # Headers pour contourner certaines protections
            'http_headers': {
                'User-Agent': self.USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            },
            # Options pour les sites difficiles
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                },
            },
            # Socket timeout
            'socket_timeout': 30,
        }
        
        # Ajouter le chemin FFmpeg si détecté
        if FFMPEG_LOCATION:
            opts['ffmpeg_location'] = FFMPEG_LOCATION
        
        return opts
    
    def get_video_info(self, url: str) -> VideoInfo:
        """
        Récupère les informations d'une vidéo depuis n'importe quel site supporté.
        
        Args:
            url: L'URL de la vidéo
            
        Returns:
            VideoInfo contenant les métadonnées
            
        Raises:
            DownloadError: Si la vidéo est inaccessible
        """
        ydl_opts = self._get_base_options()
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info is None:
                    raise DownloadError("Impossible d'extraire les informations de cette URL")
                
                return VideoInfo(info)
                
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e).lower()
            
            # Messages d'erreur personnalisés selon le type d'erreur
            if 'private' in error_msg:
                raise DownloadError("Ce contenu est privé et ne peut pas être téléchargé.")
            elif 'unavailable' in error_msg or 'not available' in error_msg:
                raise DownloadError("Ce contenu n'est pas disponible.")
            elif 'removed' in error_msg or 'deleted' in error_msg:
                raise DownloadError("Ce contenu a été supprimé.")
            elif 'age' in error_msg or 'login' in error_msg:
                raise DownloadError("Ce contenu nécessite une connexion ou une vérification d'âge.")
            elif 'copyright' in error_msg:
                raise DownloadError("Ce contenu n'est pas disponible pour des raisons de droits d'auteur.")
            elif 'geo' in error_msg or 'country' in error_msg:
                raise DownloadError("Ce contenu n'est pas disponible dans votre région.")
            elif 'unsupported' in error_msg or 'no suitable' in error_msg:
                raise DownloadError("Ce site n'est pas supporté ou le format n'est pas reconnu.")
            elif 'unable to extract' in error_msg:
                raise DownloadError("Impossible d'extraire la vidéo. Le site a peut-être changé ou n'est pas supporté.")
            else:
                raise DownloadError(f"Erreur: {str(e)}")
                
        except Exception as e:
            error_str = str(e).lower()
            if 'getaddrinfo' in error_str or 'connection' in error_str:
                raise DownloadError("Pas de connexion Internet. Vérifiez votre connexion.")
            elif 'timeout' in error_str:
                raise DownloadError("Le serveur met trop de temps à répondre. Réessayez plus tard.")
            raise DownloadError(f"Erreur inattendue: {str(e)}")
    
    def _progress_hook(self, d: Dict):
        """Hook interne pour suivre la progression du téléchargement."""
        if self.should_cancel:
            raise yt_dlp.utils.DownloadError("Téléchargement annulé par l'utilisateur")
        
        if d['status'] == 'downloading':
            # Calculer le pourcentage
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            
            if total > 0:
                percent = (downloaded / total) * 100
            else:
                # Pas de taille totale connue, utiliser les fragments si disponibles
                fragment_index = d.get('fragment_index', 0)
                fragment_count = d.get('fragment_count', 0)
                if fragment_count > 0:
                    percent = (fragment_index / fragment_count) * 100
                else:
                    percent = 0
            
            # Vitesse de téléchargement
            speed = d.get('speed', 0)
            if speed:
                if speed > 1024 * 1024:
                    speed_str = f"{speed / (1024 * 1024):.1f} MB/s"
                elif speed > 1024:
                    speed_str = f"{speed / 1024:.1f} KB/s"
                else:
                    speed_str = f"{speed:.0f} B/s"
            else:
                speed_str = "..."
            
            # Temps restant estimé
            eta = d.get('eta', 0)
            if eta:
                if eta > 3600:
                    eta_str = f"{eta // 3600}h {(eta % 3600) // 60}min"
                elif eta > 60:
                    eta_str = f"{eta // 60}min {eta % 60}s"
                else:
                    eta_str = f"{eta}s"
            else:
                eta_str = "..."
            
            if self._progress_callback:
                self._progress_callback(percent, speed_str, eta_str)
        
        elif d['status'] == 'finished':
            if self._progress_callback:
                self._progress_callback(100, "Terminé", "0s")
    
    def download_audio(self, url: str, output_dir: str, filename: str,
                       audio_format: str = 'mp3', bitrate: int = 192) -> str:
        """
        Télécharge l'audio d'une vidéo.
        
        Args:
            url: URL de la vidéo
            output_dir: Dossier de destination
            filename: Nom du fichier (sans extension)
            audio_format: Format audio (mp3, aac, wav, flac, etc.)
            bitrate: Bitrate en kbps (pour les formats compressés)
            
        Returns:
            Chemin complet du fichier téléchargé
        """
        format_info = AUDIO_FORMATS.get(audio_format, AUDIO_FORMATS['mp3'])
        extension = format_info['extension']
        
        # Nettoyer le nom de fichier
        safe_filename = self._sanitize_filename(filename)
        output_template = os.path.join(output_dir, f"{safe_filename}.%(ext)s")
        final_path = os.path.join(output_dir, f"{safe_filename}.{extension}")
        
        # Options yt-dlp pour l'audio
        ydl_opts = self._get_base_options()
        ydl_opts.update({
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'progress_hooks': [self._progress_hook],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_format if audio_format != 'm4a' else 'aac',
                'preferredquality': str(bitrate) if format_info['supports_bitrate'] else '0',
            }],
        })
        
        # Pour WAV et FLAC, on ne spécifie pas de qualité
        if not format_info['supports_bitrate']:
            ydl_opts['postprocessors'][0]['preferredquality'] = '0'
        
        return self._execute_download(url, ydl_opts, final_path)
    
    def download_video(self, url: str, output_dir: str, filename: str,
                       video_format: str = 'mp4', quality: int = 1080,
                       include_audio: bool = True) -> str:
        """
        Télécharge une vidéo.
        
        Args:
            url: URL de la vidéo
            output_dir: Dossier de destination
            filename: Nom du fichier (sans extension)
            video_format: Format vidéo (mp4, mkv, webm, etc.)
            quality: Hauteur de la vidéo (720, 1080, etc.)
            include_audio: Inclure l'audio ou non
            
        Returns:
            Chemin complet du fichier téléchargé
        """
        format_info = VIDEO_FORMATS.get(video_format, VIDEO_FORMATS['mp4'])
        extension = format_info['extension']
        
        # Nettoyer le nom de fichier
        safe_filename = self._sanitize_filename(filename)
        output_template = os.path.join(output_dir, f"{safe_filename}.%(ext)s")
        final_path = os.path.join(output_dir, f"{safe_filename}.{extension}")
        
        # Construire le sélecteur de format
        # Format plus flexible pour supporter plus de sites
        if include_audio:
            format_selector = (
                f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/'
                f'bestvideo+bestaudio/best'
            )
        else:
            format_selector = f'bestvideo[height<={quality}]/bestvideo/best'
        
        # Options yt-dlp pour la vidéo
        ydl_opts = self._get_base_options()
        ydl_opts.update({
            'format': format_selector,
            'outtmpl': output_template,
            'progress_hooks': [self._progress_hook],
            'merge_output_format': extension,
        })
        
        # Ajouter le postprocesseur pour la conversion si nécessaire
        if extension not in ['mp4', 'webm', 'mkv']:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': extension,
            }]
        
        return self._execute_download(url, ydl_opts, final_path)
    
    def _execute_download(self, url: str, ydl_opts: Dict, final_path: str) -> str:
        """Exécute le téléchargement avec les options spécifiées."""
        self.is_downloading = True
        self.should_cancel = False
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            if self._complete_callback:
                self._complete_callback(final_path)
            
            return final_path
            
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if "annulé" in error_msg.lower() or "cancelled" in error_msg.lower():
                raise DownloadError("Téléchargement annulé")
            raise DownloadError(f"Erreur de téléchargement: {error_msg}")
        except Exception as e:
            error_msg = str(e)
            if self._error_callback:
                self._error_callback(error_msg)
            raise DownloadError(f"Erreur: {error_msg}")
        finally:
            self.is_downloading = False
    
    def download_async(self, download_func: Callable, *args, **kwargs):
        """
        Lance un téléchargement dans un thread séparé.
        
        Args:
            download_func: La fonction de téléchargement à appeler
            *args, **kwargs: Arguments à passer à la fonction
        """
        def _download_thread():
            try:
                download_func(*args, **kwargs)
            except DownloadError as e:
                if self._error_callback:
                    self._error_callback(str(e))
            except Exception as e:
                if self._error_callback:
                    self._error_callback(f"Erreur inattendue: {str(e)}")
        
        thread = threading.Thread(target=_download_thread, daemon=True)
        thread.start()
        return thread
    
    def cancel_download(self):
        """Annule le téléchargement en cours."""
        self.should_cancel = True
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        Nettoie un nom de fichier en supprimant les caractères invalides.
        
        Args:
            filename: Nom de fichier à nettoyer
            
        Returns:
            Nom de fichier nettoyé
        """
        # Caractères interdits dans les noms de fichiers Windows
        invalid_chars = '<>:"/\\|?*'
        
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Supprimer les emojis et caractères spéciaux problématiques
        filename = re.sub(r'[^\w\s\-_\.\(\)\[\]]', '_', filename, flags=re.UNICODE)
        
        # Supprimer les espaces/underscores multiples
        filename = re.sub(r'[_\s]+', ' ', filename)
        
        # Limiter la longueur
        if len(filename) > 200:
            filename = filename[:200]
        
        return filename.strip()


# Alias pour la rétrocompatibilité
YouTubeDownloader = MediaDownloader

# -*- coding: utf-8 -*-
"""
Application principale - Téléchargeur de Médias Universel.
Supporte YouTube, TikTok, Instagram, Twitter, et +1000 autres sites.
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
import os
from typing import Optional

from .widgets import (
    VideoInfoFrame, 
    FormatSelector, 
    ProgressFrame,
    FilenameEntry,
    DestinationSelector
)
from .themes import ThemeManager, ThemeToggleButton
from core.downloader import MediaDownloader, VideoInfo, DownloadError
from core.validator import URLValidator, SUPPORTED_PLATFORMS
from utils.history import HistoryManager, HistoryWindow


class YouTubeDownloaderApp(ctk.CTk):
    """
    Application principale de téléchargement de médias.
    Supporte YouTube, TikTok, Instagram, Twitter, et bien plus.
    """
    
    APP_NAME = "Media Downloader"
    APP_VERSION = "2.0.0"
    WINDOW_SIZE = (850, 750)
    
    def __init__(self):
        super().__init__()
        
        # Initialiser les gestionnaires
        self.theme_manager = ThemeManager()
        self.downloader = MediaDownloader()
        self.history_manager = HistoryManager()
        
        # État de l'application
        self.current_video_info: Optional[VideoInfo] = None
        self.current_platform = None
        self.is_analyzing = False
        
        # Configuration de la fenêtre
        self._setup_window()
        
        # Configuration des callbacks du downloader
        self._setup_downloader_callbacks()
        
        # Création de l'interface
        self._create_ui()
    
    def _setup_window(self):
        """Configure la fenêtre principale."""
        self.title(f"{self.APP_NAME} v{self.APP_VERSION}")
        self.geometry(f"{self.WINDOW_SIZE[0]}x{self.WINDOW_SIZE[1]}")
        self.minsize(750, 650)
        
        # Centrer la fenêtre
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.WINDOW_SIZE[0]) // 2
        y = (self.winfo_screenheight() - self.WINDOW_SIZE[1]) // 2
        self.geometry(f"+{x}+{y}")
        
        # Configuration du grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
    
    def _setup_downloader_callbacks(self):
        """Configure les callbacks du downloader."""
        self.downloader.set_callbacks(
            progress=self._on_download_progress,
            complete=self._on_download_complete,
            error=self._on_download_error
        )
    
    def _create_ui(self):
        """Crée l'interface utilisateur complète."""
        # Container principal avec scroll
        self.main_frame = ctk.CTkScrollableFrame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        row = 0
        
        # ========== En-tête ==========
        self._create_header(row)
        row += 1
        
        # ========== Plateformes supportées ==========
        self._create_platforms_info(row)
        row += 1
        
        # ========== Zone URL ==========
        self._create_url_section(row)
        row += 1
        
        # ========== Info vidéo ==========
        self.video_info_frame = VideoInfoFrame(self.main_frame)
        self.video_info_frame.grid(row=row, column=0, sticky="ew", pady=(15, 0))
        row += 1
        
        # ========== Sélecteur de format ==========
        self.format_selector = FormatSelector(
            self.main_frame,
            on_type_change=self._on_format_type_change
        )
        self.format_selector.grid(row=row, column=0, sticky="ew", pady=(15, 0))
        row += 1
        
        # ========== Nom du fichier ==========
        self.filename_entry = FilenameEntry(self.main_frame)
        self.filename_entry.grid(row=row, column=0, sticky="ew", pady=(15, 0))
        row += 1
        
        # ========== Dossier de destination ==========
        self.destination_selector = DestinationSelector(self.main_frame)
        self.destination_selector.grid(row=row, column=0, sticky="ew", pady=(15, 0))
        row += 1
        
        # ========== Bouton de téléchargement ==========
        self._create_download_button(row)
        row += 1
        
        # ========== Barre de progression ==========
        self.progress_frame = ProgressFrame(self.main_frame)
        self.progress_frame.grid(row=row, column=0, sticky="ew", pady=(15, 0))
        row += 1
        
        # ========== Message de statut ==========
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(size=13),
            text_color=("gray40", "gray60")
        )
        self.status_label.grid(row=row, column=0, sticky="ew", pady=(10, 0))
        row += 1
        
        # ========== Footer / Crédits ==========
        self._create_footer(row)
    
    def _create_header(self, row: int):
        """Crée l'en-tête de l'application."""
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.grid(row=row, column=0, sticky="ew", pady=(0, 5))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Logo / Titre
        title_label = ctk.CTkLabel(
            header_frame,
            text="⬇️ Media Downloader",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Sous-titre
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="YouTube • TikTok • Instagram • Twitter • +1000 sites",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        )
        subtitle_label.grid(row=1, column=0, sticky="w", pady=(2, 0))
        
        # Boutons à droite
        buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        buttons_frame.grid(row=0, column=2, rowspan=2, sticky="e")
        
        # Bouton historique
        self.history_button = ctk.CTkButton(
            buttons_frame,
            text="📋",
            width=40,
            height=40,
            font=ctk.CTkFont(size=18),
            fg_color="transparent",
            hover_color=("gray75", "gray25"),
            command=self._show_history
        )
        self.history_button.grid(row=0, column=0, padx=(0, 5))
        
        # Bouton thème
        self.theme_toggle = ThemeToggleButton(buttons_frame, self.theme_manager)
        self.theme_toggle.grid(row=0, column=1)
    
    def _create_platforms_info(self, row: int):
        """Crée la barre des plateformes supportées."""
        platforms_frame = ctk.CTkFrame(self.main_frame, fg_color=("gray90", "gray17"))
        platforms_frame.grid(row=row, column=0, sticky="ew", pady=(5, 10))
        
        # Afficher les icônes des principales plateformes
        icons_label = ctk.CTkLabel(
            platforms_frame,
            text="🎬 YouTube   🎵 TikTok   📸 Instagram   🐦 Twitter/X   📘 Facebook   🎮 Twitch   🌐 Et plus...",
            font=ctk.CTkFont(size=12),
            text_color=("gray30", "gray70")
        )
        icons_label.pack(pady=8, padx=15)
    
    def _create_url_section(self, row: int):
        """Crée la section de saisie d'URL."""
        url_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        url_frame.grid(row=row, column=0, sticky="ew")
        url_frame.grid_columnconfigure(0, weight=1)
        
        # Label avec indicateur de plateforme
        self.url_label_frame = ctk.CTkFrame(url_frame, fg_color="transparent")
        self.url_label_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        
        self.url_label = ctk.CTkLabel(
            self.url_label_frame,
            text="URL de la vidéo :",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.url_label.pack(side="left")
        
        # Badge de plateforme détectée
        self.platform_badge = ctk.CTkLabel(
            self.url_label_frame,
            text="",
            font=ctk.CTkFont(size=12),
            fg_color=("gray80", "gray30"),
            corner_radius=10,
            padx=10,
            pady=2
        )
        
        # Frame pour l'entrée et le bouton
        input_frame = ctk.CTkFrame(url_frame, fg_color="transparent")
        input_frame.grid(row=1, column=0, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Champ de saisie URL
        self.url_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Collez le lien ici (YouTube, TikTok, Instagram, Twitter...)",
            height=45,
            font=ctk.CTkFont(size=13)
        )
        self.url_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.url_entry.bind("<Return>", lambda e: self._analyze_url())
        self.url_entry.bind("<KeyRelease>", self._on_url_changed)
        
        # Bouton Analyser
        self.analyze_button = ctk.CTkButton(
            input_frame,
            text="🔍 Analyser",
            width=130,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._analyze_url
        )
        self.analyze_button.grid(row=0, column=1)
    
    def _create_download_button(self, row: int):
        """Crée le bouton de téléchargement."""
        self.download_button = ctk.CTkButton(
            self.main_frame,
            text="⬇️ Télécharger",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._start_download,
            state="disabled"
        )
        self.download_button.grid(row=row, column=0, sticky="ew", pady=(20, 0))
    
    def _create_footer(self, row: int):
        """Crée le footer avec les crédits."""
        import webbrowser
        
        footer_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        footer_frame.grid(row=row, column=0, sticky="ew", pady=(30, 10))
        
        # Texte "Créé par"
        created_label = ctk.CTkLabel(
            footer_frame,
            text="Créé par ",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray50")
        )
        created_label.pack(side="left", expand=True, anchor="e")
        
        # Lien cliquable vers GitHub
        self.author_link = ctk.CTkLabel(
            footer_frame,
            text="Arthur KETCHEIAN",
            font=ctk.CTkFont(size=12, underline=True),
            text_color=("#1f6aa5", "#5fa8d3"),
            cursor="hand2"
        )
        self.author_link.pack(side="left", anchor="w")
        self.author_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Hegowo/MediaDownloader"))
        
        # Effet hover sur le lien
        self.author_link.bind("<Enter>", lambda e: self.author_link.configure(text_color=("#14375e", "#8bc4ea")))
        self.author_link.bind("<Leave>", lambda e: self.author_link.configure(text_color=("#1f6aa5", "#5fa8d3")))
    
    # ========== Actions ==========
    
    def _on_url_changed(self, event=None):
        """Callback quand l'URL change (détection en temps réel)."""
        url = self.url_entry.get().strip()
        
        if url:
            # Détecter la plateforme
            is_valid, message, platform = URLValidator.validate_url(url)
            
            if platform:
                self.current_platform = platform
                self.platform_badge.configure(text=f"{platform.icon} {platform.name}")
                self.platform_badge.pack(side="left", padx=(10, 0))
            else:
                self.platform_badge.pack_forget()
        else:
            self.platform_badge.pack_forget()
            self.current_platform = None
    
    def _analyze_url(self):
        """Analyse l'URL saisie."""
        url = self.url_entry.get().strip()
        
        if not url:
            self._show_error("Veuillez entrer une URL")
            return
        
        # Normaliser l'URL
        url = URLValidator.normalize_url(url)
        self.url_entry.delete(0, 'end')
        self.url_entry.insert(0, url)
        
        # Valider l'URL
        is_valid, message, platform = URLValidator.validate_url(url)
        
        if not is_valid:
            self._show_error(message)
            return
        
        self.current_platform = platform
        
        # Désactiver le bouton pendant l'analyse
        self.is_analyzing = True
        self.analyze_button.configure(state="disabled", text="⏳ Analyse...")
        platform_name = platform.name if platform else "du site"
        self._set_status(f"Récupération des informations {platform_name}...")
        
        # Lancer l'analyse dans un thread
        thread = threading.Thread(target=self._fetch_video_info, args=(url,), daemon=True)
        thread.start()
    
    def _fetch_video_info(self, url: str):
        """Récupère les informations de la vidéo (dans un thread)."""
        try:
            info = self.downloader.get_video_info(url)
            # Mettre à jour l'interface dans le thread principal
            self.after(0, self._on_video_info_received, info)
        except DownloadError as e:
            self.after(0, self._on_video_info_error, str(e))
        except Exception as e:
            self.after(0, self._on_video_info_error, f"Erreur: {str(e)}")
    
    def _on_video_info_received(self, info: VideoInfo):
        """Callback quand les infos vidéo sont reçues."""
        self.current_video_info = info
        self.is_analyzing = False
        
        # Réactiver le bouton
        self.analyze_button.configure(state="normal", text="🔍 Analyser")
        
        # Afficher les informations
        self.video_info_frame.update_info(
            title=info.title,
            author=info.author,
            duration=info.get_duration_formatted(),
            thumbnail_url=info.thumbnail
        )
        
        # Configurer le sélecteur de format
        self.format_selector.set_available_qualities(info.get_quality_options())
        self.format_selector.show()
        
        # Pré-remplir le nom de fichier
        self.filename_entry.set_filename(info.title)
        self.filename_entry.show()
        
        # Afficher le sélecteur de destination
        self.destination_selector.show()
        
        # Activer le bouton de téléchargement
        self.download_button.configure(state="normal")
        
        platform_icon = self.current_platform.icon if self.current_platform else "✅"
        self._set_status(f"{platform_icon} Contenu analysé avec succès")
    
    def _on_video_info_error(self, error_message: str):
        """Callback en cas d'erreur d'analyse."""
        self.is_analyzing = False
        self.analyze_button.configure(state="normal", text="🔍 Analyser")
        self._show_error(error_message)
        self._set_status("")
    
    def _on_format_type_change(self, format_type: str):
        """Callback quand le type de format change."""
        pass
    
    def _start_download(self):
        """Démarre le téléchargement."""
        if not self.current_video_info:
            self._show_error("Veuillez d'abord analyser une vidéo")
            return
        
        # Vérifier le nom de fichier
        filename = self.filename_entry.get_filename()
        if not filename:
            self._show_error("Veuillez entrer un nom de fichier")
            return
        
        # Vérifier le dossier de destination
        output_dir = self.destination_selector.get_path()
        if not output_dir:
            self._show_error("Veuillez sélectionner un dossier de destination")
            return
        
        if not os.path.isdir(output_dir):
            self._show_error("Le dossier de destination n'existe pas")
            return
        
        # Récupérer la sélection
        selection = self.format_selector.get_selection()
        
        # Désactiver les contrôles
        self._set_controls_enabled(False)
        
        # Afficher la progression
        self.progress_frame.reset()
        self.progress_frame.show()
        
        # Lancer le téléchargement
        url = self.url_entry.get().strip()
        
        if selection['type'] == 'audio':
            self.progress_frame.set_status(f"Téléchargement audio ({selection['format'].upper()})...")
            self.downloader.download_async(
                self.downloader.download_audio,
                url=url,
                output_dir=output_dir,
                filename=filename,
                audio_format=selection['format'],
                bitrate=selection['bitrate']
            )
        else:
            quality_label = f"{selection['quality']}p"
            audio_text = "avec audio" if selection['include_audio'] else "sans audio"
            self.progress_frame.set_status(f"Téléchargement vidéo ({quality_label}, {audio_text})...")
            self.downloader.download_async(
                self.downloader.download_video,
                url=url,
                output_dir=output_dir,
                filename=filename,
                video_format=selection['format'],
                quality=selection['quality'],
                include_audio=selection['include_audio']
            )
    
    def _on_download_progress(self, percent: float, speed: str, eta: str):
        """Callback de progression du téléchargement."""
        self.after(0, self.progress_frame.update_progress, percent, speed, eta)
    
    def _on_download_complete(self, filepath: str):
        """Callback de fin de téléchargement."""
        def _complete():
            self._set_controls_enabled(True)
            self.progress_frame.update_progress(100, "Terminé", "0s")
            self._set_status(f"✅ Téléchargement terminé : {os.path.basename(filepath)}")
            
            # Ajouter à l'historique
            if self.current_video_info:
                selection = self.format_selector.get_selection()
                platform_name = self.current_platform.name if self.current_platform else "Web"
                self.history_manager.add_entry(
                    title=f"[{platform_name}] {self.current_video_info.title}",
                    url=self.url_entry.get().strip(),
                    format_type=selection['type'],
                    format_name=selection.get('format', ''),
                    quality=selection.get('quality') or selection.get('bitrate', ''),
                    filepath=filepath
                )
            
            # Notification
            messagebox.showinfo(
                "Téléchargement terminé",
                f"Le fichier a été téléchargé avec succès :\n{filepath}"
            )
        
        self.after(0, _complete)
    
    def _on_download_error(self, error_message: str):
        """Callback en cas d'erreur de téléchargement."""
        def _error():
            self._set_controls_enabled(True)
            self.progress_frame.hide()
            self._show_error(f"Erreur de téléchargement :\n{error_message}")
            self._set_status("❌ Téléchargement échoué")
        
        self.after(0, _error)
    
    def _show_history(self):
        """Affiche la fenêtre d'historique."""
        HistoryWindow(self, self.history_manager)
    
    # ========== Utilitaires ==========
    
    def _set_controls_enabled(self, enabled: bool):
        """Active ou désactive les contrôles de l'interface."""
        state = "normal" if enabled else "disabled"
        
        self.url_entry.configure(state=state)
        self.analyze_button.configure(state=state)
        self.download_button.configure(state=state)
    
    def _set_status(self, message: str):
        """Définit le message de statut."""
        self.status_label.configure(text=message)
    
    def _show_error(self, message: str):
        """Affiche une boîte de dialogue d'erreur."""
        messagebox.showerror("Erreur", message)
    
    def _show_info(self, message: str):
        """Affiche une boîte de dialogue d'information."""
        messagebox.showinfo("Information", message)

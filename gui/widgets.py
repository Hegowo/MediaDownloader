# -*- coding: utf-8 -*-
"""
Widgets personnalisés pour l'application YouTube Downloader.
Contient les composants réutilisables de l'interface.
"""

import customtkinter as ctk
from PIL import Image, ImageTk
import requests
from io import BytesIO
from typing import Optional, Callable, List, Tuple
import threading


class VideoInfoFrame(ctk.CTkFrame):
    """
    Frame affichant les informations de la vidéo (miniature, titre, durée, auteur).
    """
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.thumbnail_size = (320, 180)
        self._setup_ui()
        self.hide()
    
    def _setup_ui(self):
        """Configure l'interface du frame."""
        # Container principal avec padding
        self.grid_columnconfigure(0, weight=0)  # Miniature
        self.grid_columnconfigure(1, weight=1)  # Infos
        
        # Miniature
        self.thumbnail_label = ctk.CTkLabel(
            self, 
            text="",
            width=self.thumbnail_size[0],
            height=self.thumbnail_size[1]
        )
        self.thumbnail_label.grid(row=0, column=0, padx=(10, 15), pady=10, sticky="nw")
        
        # Frame pour les informations textuelles
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        self.info_frame.grid_columnconfigure(0, weight=1)
        
        # Titre de la vidéo
        self.title_label = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
            wraplength=400
        )
        self.title_label.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        
        # Auteur
        self.author_label = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=ctk.CTkFont(size=13),
            anchor="w",
            text_color=("gray40", "gray60")
        )
        self.author_label.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        
        # Durée
        self.duration_label = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=ctk.CTkFont(size=13),
            anchor="w",
            text_color=("gray40", "gray60")
        )
        self.duration_label.grid(row=2, column=0, sticky="ew", pady=(0, 5))
        
        # Placeholder pour la miniature
        self._set_placeholder_thumbnail()
    
    def _set_placeholder_thumbnail(self):
        """Définit une miniature placeholder."""
        # Créer une image placeholder grise
        placeholder = Image.new('RGB', self.thumbnail_size, color=(60, 60, 60))
        self._current_image = ctk.CTkImage(
            light_image=placeholder,
            dark_image=placeholder,
            size=self.thumbnail_size
        )
        self.thumbnail_label.configure(image=self._current_image)
    
    def update_info(self, title: str, author: str, duration: str, thumbnail_url: str = ""):
        """
        Met à jour les informations affichées.
        
        Args:
            title: Titre de la vidéo
            author: Nom de l'auteur/chaîne
            duration: Durée formatée
            thumbnail_url: URL de la miniature
        """
        self.title_label.configure(text=title)
        self.author_label.configure(text=f"👤 {author}")
        self.duration_label.configure(text=f"⏱️ {duration}")
        
        # Charger la miniature dans un thread séparé
        if thumbnail_url:
            thread = threading.Thread(
                target=self._load_thumbnail,
                args=(thumbnail_url,),
                daemon=True
            )
            thread.start()
        
        self.show()
    
    def _load_thumbnail(self, url: str):
        """Charge la miniature depuis une URL (dans un thread)."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            image_data = BytesIO(response.content)
            image = Image.open(image_data)
            image = image.resize(self.thumbnail_size, Image.Resampling.LANCZOS)
            
            # Mettre à jour dans le thread principal
            self._current_image = ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=self.thumbnail_size
            )
            self.thumbnail_label.configure(image=self._current_image)
            
        except Exception as e:
            print(f"Erreur chargement miniature: {e}")
            self._set_placeholder_thumbnail()
    
    def show(self):
        """Affiche le frame."""
        self.grid()
    
    def hide(self):
        """Cache le frame."""
        self.grid_remove()
    
    def clear(self):
        """Réinitialise le frame."""
        self.title_label.configure(text="")
        self.author_label.configure(text="")
        self.duration_label.configure(text="")
        self._set_placeholder_thumbnail()
        self.hide()


class FormatSelector(ctk.CTkFrame):
    """
    Widget de sélection du format et de la qualité.
    Gère la logique Audio/Vidéo avec les options correspondantes.
    """
    
    def __init__(self, master, on_type_change: Optional[Callable] = None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.on_type_change = on_type_change
        self.current_type = "audio"
        self._setup_ui()
        self.hide()
    
    def _setup_ui(self):
        """Configure l'interface du sélecteur."""
        self.grid_columnconfigure(0, weight=1)
        
        # ========== Sélecteur Audio/Vidéo ==========
        self.type_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.type_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.type_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.type_label = ctk.CTkLabel(
            self.type_frame,
            text="Type d'export :",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.type_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        
        self.type_segmented = ctk.CTkSegmentedButton(
            self.type_frame,
            values=["🎵 Audio", "🎬 Vidéo"],
            command=self._on_type_selected,
            font=ctk.CTkFont(size=13)
        )
        self.type_segmented.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.type_segmented.set("🎵 Audio")
        
        # ========== Options Audio ==========
        self.audio_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.audio_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.audio_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Format audio
        self.audio_format_label = ctk.CTkLabel(
            self.audio_frame,
            text="Format audio :",
            font=ctk.CTkFont(size=13)
        )
        self.audio_format_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.audio_format_combo = ctk.CTkComboBox(
            self.audio_frame,
            values=["MP3", "AAC", "WAV", "FLAC", "OGG", "M4A", "OPUS", "WMA"],
            state="readonly",
            command=self._on_audio_format_changed
        )
        self.audio_format_combo.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        self.audio_format_combo.set("MP3")
        
        # Bitrate
        self.bitrate_label = ctk.CTkLabel(
            self.audio_frame,
            text="Qualité (bitrate) :",
            font=ctk.CTkFont(size=13)
        )
        self.bitrate_label.grid(row=0, column=1, sticky="w", pady=(0, 5))
        
        self.bitrate_combo = ctk.CTkComboBox(
            self.audio_frame,
            values=["128 kbps", "192 kbps", "256 kbps", "320 kbps"],
            state="readonly"
        )
        self.bitrate_combo.grid(row=1, column=1, sticky="ew")
        self.bitrate_combo.set("192 kbps")
        
        # ========== Options Vidéo ==========
        self.video_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.video_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Format vidéo
        self.video_format_label = ctk.CTkLabel(
            self.video_frame,
            text="Format vidéo :",
            font=ctk.CTkFont(size=13)
        )
        self.video_format_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.video_format_combo = ctk.CTkComboBox(
            self.video_frame,
            values=["MP4", "MKV", "WEBM", "AVI", "MOV", "FLV"],
            state="readonly"
        )
        self.video_format_combo.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        self.video_format_combo.set("MP4")
        
        # Qualité vidéo
        self.quality_label = ctk.CTkLabel(
            self.video_frame,
            text="Qualité :",
            font=ctk.CTkFont(size=13)
        )
        self.quality_label.grid(row=0, column=1, sticky="w", pady=(0, 5))
        
        self.quality_combo = ctk.CTkComboBox(
            self.video_frame,
            values=["1080p (Full HD)"],
            state="readonly"
        )
        self.quality_combo.grid(row=1, column=1, sticky="ew")
        
        # Option audio inclus
        self.include_audio_var = ctk.BooleanVar(value=True)
        self.include_audio_check = ctk.CTkCheckBox(
            self.video_frame,
            text="Inclure l'audio",
            variable=self.include_audio_var,
            font=ctk.CTkFont(size=13)
        )
        self.include_audio_check.grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))
        
        # Cacher le frame vidéo par défaut
        self.video_frame.grid_remove()
    
    def _on_type_selected(self, value: str):
        """Callback quand le type (Audio/Vidéo) change."""
        if "Audio" in value:
            self.current_type = "audio"
            self.video_frame.grid_remove()
            self.audio_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        else:
            self.current_type = "video"
            self.audio_frame.grid_remove()
            self.video_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        if self.on_type_change:
            self.on_type_change(self.current_type)
    
    def _on_audio_format_changed(self, value: str):
        """Callback quand le format audio change."""
        # Certains formats ne supportent pas le bitrate
        no_bitrate_formats = ["WAV", "FLAC"]
        if value in no_bitrate_formats:
            self.bitrate_combo.configure(state="disabled")
            self.bitrate_label.configure(text_color=("gray60", "gray40"))
        else:
            self.bitrate_combo.configure(state="readonly")
            self.bitrate_label.configure(text_color=("gray10", "gray90"))
    
    def set_available_qualities(self, qualities: List[Tuple[int, str]]):
        """
        Définit les qualités vidéo disponibles.
        
        Args:
            qualities: Liste de tuples (hauteur, label)
        """
        if qualities:
            labels = [q[1] for q in qualities]
            self.quality_combo.configure(values=labels)
            # Sélectionner la meilleure qualité par défaut
            self.quality_combo.set(labels[-1])
        else:
            self.quality_combo.configure(values=["Non disponible"])
            self.quality_combo.set("Non disponible")
    
    def get_selection(self) -> dict:
        """
        Retourne la sélection actuelle.
        
        Returns:
            Dict avec les paramètres sélectionnés
        """
        if self.current_type == "audio":
            # Extraire le bitrate du texte "192 kbps"
            bitrate_text = self.bitrate_combo.get()
            bitrate = int(bitrate_text.split()[0]) if bitrate_text else 192
            
            return {
                'type': 'audio',
                'format': self.audio_format_combo.get().lower(),
                'bitrate': bitrate
            }
        else:
            # Extraire la qualité du texte "1080p (Full HD)"
            quality_text = self.quality_combo.get()
            quality = int(quality_text.split('p')[0]) if quality_text and quality_text != "Non disponible" else 1080
            
            return {
                'type': 'video',
                'format': self.video_format_combo.get().lower(),
                'quality': quality,
                'include_audio': self.include_audio_var.get()
            }
    
    def show(self):
        """Affiche le sélecteur."""
        self.grid()
    
    def hide(self):
        """Cache le sélecteur."""
        self.grid_remove()
    
    def reset(self):
        """Réinitialise le sélecteur."""
        self.type_segmented.set("🎵 Audio")
        self._on_type_selected("🎵 Audio")
        self.audio_format_combo.set("MP3")
        self.bitrate_combo.set("192 kbps")
        self.video_format_combo.set("MP4")
        self.include_audio_var.set(True)


class ProgressFrame(ctk.CTkFrame):
    """
    Frame affichant la progression du téléchargement.
    """
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self._setup_ui()
        self.hide()
    
    def _setup_ui(self):
        """Configure l'interface du frame."""
        self.grid_columnconfigure(0, weight=1)
        
        # Label de statut
        self.status_label = ctk.CTkLabel(
            self,
            text="Préparation du téléchargement...",
            font=ctk.CTkFont(size=13)
        )
        self.status_label.grid(row=0, column=0, sticky="w", pady=(0, 8))
        
        # Barre de progression
        self.progress_bar = ctk.CTkProgressBar(self, height=20)
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        self.progress_bar.set(0)
        
        # Frame pour les détails
        self.details_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.details_frame.grid(row=2, column=0, sticky="ew")
        self.details_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Pourcentage
        self.percent_label = ctk.CTkLabel(
            self.details_frame,
            text="0%",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        )
        self.percent_label.grid(row=0, column=0, sticky="w")
        
        # Vitesse
        self.speed_label = ctk.CTkLabel(
            self.details_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        )
        self.speed_label.grid(row=0, column=1)
        
        # Temps restant
        self.eta_label = ctk.CTkLabel(
            self.details_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        )
        self.eta_label.grid(row=0, column=2, sticky="e")
    
    def update_progress(self, percent: float, speed: str = "", eta: str = ""):
        """
        Met à jour la progression.
        
        Args:
            percent: Pourcentage (0-100)
            speed: Vitesse de téléchargement
            eta: Temps restant estimé
        """
        self.progress_bar.set(percent / 100)
        self.percent_label.configure(text=f"{percent:.1f}%")
        
        if speed:
            self.speed_label.configure(text=f"⚡ {speed}")
        
        if eta:
            self.eta_label.configure(text=f"⏳ {eta}")
        
        if percent >= 100:
            self.status_label.configure(text="Téléchargement terminé !")
    
    def set_status(self, status: str):
        """Définit le message de statut."""
        self.status_label.configure(text=status)
    
    def show(self):
        """Affiche le frame."""
        self.grid()
    
    def hide(self):
        """Cache le frame."""
        self.grid_remove()
    
    def reset(self):
        """Réinitialise le frame."""
        self.progress_bar.set(0)
        self.percent_label.configure(text="0%")
        self.speed_label.configure(text="")
        self.eta_label.configure(text="")
        self.status_label.configure(text="Préparation du téléchargement...")


class FilenameEntry(ctk.CTkFrame):
    """
    Widget pour saisir le nom du fichier de destination.
    """
    
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self._setup_ui()
        self.hide()
    
    def _setup_ui(self):
        """Configure l'interface."""
        self.grid_columnconfigure(0, weight=1)
        
        self.label = ctk.CTkLabel(
            self,
            text="Nom du fichier :",
            font=ctk.CTkFont(size=13)
        )
        self.label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text="Entrez le nom du fichier...",
            height=35
        )
        self.entry.grid(row=1, column=0, sticky="ew")
    
    def get_filename(self) -> str:
        """Retourne le nom de fichier saisi."""
        return self.entry.get().strip()
    
    def set_filename(self, filename: str):
        """Définit le nom de fichier."""
        self.entry.delete(0, 'end')
        self.entry.insert(0, filename)
    
    def show(self):
        """Affiche le widget."""
        self.grid()
    
    def hide(self):
        """Cache le widget."""
        self.grid_remove()
    
    def reset(self):
        """Réinitialise le widget."""
        self.entry.delete(0, 'end')


class DestinationSelector(ctk.CTkFrame):
    """
    Widget pour sélectionner le dossier de destination.
    """
    
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.selected_path = ""
        self._setup_ui()
        self.hide()
    
    def _setup_ui(self):
        """Configure l'interface."""
        self.grid_columnconfigure(0, weight=1)
        
        self.label = ctk.CTkLabel(
            self,
            text="Dossier de destination :",
            font=ctk.CTkFont(size=13)
        )
        self.label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Frame pour le chemin et le bouton
        self.path_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.path_frame.grid(row=1, column=0, sticky="ew")
        self.path_frame.grid_columnconfigure(0, weight=1)
        
        self.path_label = ctk.CTkLabel(
            self.path_frame,
            text="Aucun dossier sélectionné",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60"),
            anchor="w"
        )
        self.path_label.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.browse_button = ctk.CTkButton(
            self.path_frame,
            text="📁 Parcourir",
            width=120,
            command=self._browse_folder
        )
        self.browse_button.grid(row=0, column=1)
    
    def _browse_folder(self):
        """Ouvre le dialogue de sélection de dossier."""
        from tkinter import filedialog
        import os
        
        # Dossier initial : Téléchargements ou Documents
        initial_dir = os.path.expanduser("~/Downloads")
        if not os.path.exists(initial_dir):
            initial_dir = os.path.expanduser("~/Documents")
        
        folder = filedialog.askdirectory(
            title="Sélectionner le dossier de destination",
            initialdir=initial_dir
        )
        
        if folder:
            self.selected_path = folder
            # Afficher un chemin tronqué si trop long
            display_path = folder
            if len(display_path) > 50:
                display_path = "..." + display_path[-47:]
            self.path_label.configure(text=display_path, text_color=("gray10", "gray90"))
    
    def get_path(self) -> str:
        """Retourne le chemin sélectionné."""
        return self.selected_path
    
    def set_path(self, path: str):
        """Définit le chemin."""
        self.selected_path = path
        display_path = path
        if len(display_path) > 50:
            display_path = "..." + display_path[-47:]
        self.path_label.configure(text=display_path, text_color=("gray10", "gray90"))
    
    def show(self):
        """Affiche le widget."""
        self.grid()
    
    def hide(self):
        """Cache le widget."""
        self.grid_remove()
    
    def reset(self):
        """Réinitialise le widget."""
        self.selected_path = ""
        self.path_label.configure(
            text="Aucun dossier sélectionné",
            text_color=("gray40", "gray60")
        )


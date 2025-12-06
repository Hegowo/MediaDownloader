# -*- coding: utf-8 -*-
"""
Gestionnaire d'historique des téléchargements.
Stocke et récupère l'historique dans un fichier JSON.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import customtkinter as ctk
from tkinter import messagebox


class HistoryEntry:
    """Représente une entrée dans l'historique."""
    
    def __init__(self, data: Dict):
        self.id = data.get('id', '')
        self.title = data.get('title', '')
        self.url = data.get('url', '')
        self.format_type = data.get('format_type', '')  # 'audio' ou 'video'
        self.format_name = data.get('format_name', '')  # 'mp3', 'mp4', etc.
        self.quality = data.get('quality', '')  # '1080' ou '320'
        self.filepath = data.get('filepath', '')
        self.timestamp = data.get('timestamp', '')
        self.date = data.get('date', '')
    
    def to_dict(self) -> Dict:
        """Convertit l'entrée en dictionnaire."""
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'format_type': self.format_type,
            'format_name': self.format_name,
            'quality': self.quality,
            'filepath': self.filepath,
            'timestamp': self.timestamp,
            'date': self.date
        }
    
    def get_format_display(self) -> str:
        """Retourne une représentation lisible du format."""
        if self.format_type == 'audio':
            return f"🎵 {self.format_name.upper()} ({self.quality} kbps)"
        else:
            return f"🎬 {self.format_name.upper()} ({self.quality}p)"


class HistoryManager:
    """
    Gestionnaire de l'historique des téléchargements.
    """
    
    MAX_ENTRIES = 100  # Nombre maximum d'entrées dans l'historique
    
    def __init__(self, history_path: Optional[str] = None):
        """
        Initialise le gestionnaire d'historique.
        
        Args:
            history_path: Chemin vers le fichier d'historique
        """
        self.history_path = history_path or self._get_default_path()
        self.entries: List[HistoryEntry] = []
        
        # Charger l'historique existant
        self._load()
    
    def _get_default_path(self) -> str:
        """Retourne le chemin par défaut du fichier d'historique."""
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(app_dir, 'data', 'history.json')
    
    def _load(self):
        """Charge l'historique depuis le fichier."""
        try:
            if os.path.exists(self.history_path):
                with open(self.history_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.entries = [HistoryEntry(entry) for entry in data.get('history', [])]
        except Exception as e:
            print(f"Erreur chargement historique: {e}")
            self.entries = []
    
    def _save(self):
        """Sauvegarde l'historique dans le fichier."""
        try:
            # Créer le dossier si nécessaire
            history_dir = os.path.dirname(self.history_path)
            if history_dir and not os.path.exists(history_dir):
                os.makedirs(history_dir)
            
            data = {
                'version': '1.0',
                'history': [entry.to_dict() for entry in self.entries]
            }
            
            with open(self.history_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur sauvegarde historique: {e}")
    
    def add_entry(self, title: str, url: str, format_type: str, 
                  format_name: str, quality, filepath: str):
        """
        Ajoute une nouvelle entrée à l'historique.
        
        Args:
            title: Titre de la vidéo
            url: URL YouTube
            format_type: 'audio' ou 'video'
            format_name: Nom du format (mp3, mp4, etc.)
            quality: Qualité (bitrate ou résolution)
            filepath: Chemin du fichier téléchargé
        """
        now = datetime.now()
        
        entry = HistoryEntry({
            'id': now.strftime('%Y%m%d%H%M%S%f'),
            'title': title,
            'url': url,
            'format_type': format_type,
            'format_name': format_name,
            'quality': str(quality),
            'filepath': filepath,
            'timestamp': now.isoformat(),
            'date': now.strftime('%d/%m/%Y %H:%M')
        })
        
        # Ajouter au début de la liste
        self.entries.insert(0, entry)
        
        # Limiter le nombre d'entrées
        if len(self.entries) > self.MAX_ENTRIES:
            self.entries = self.entries[:self.MAX_ENTRIES]
        
        # Sauvegarder
        self._save()
    
    def get_entries(self, limit: Optional[int] = None) -> List[HistoryEntry]:
        """
        Retourne les entrées de l'historique.
        
        Args:
            limit: Nombre maximum d'entrées à retourner
            
        Returns:
            Liste des entrées
        """
        if limit:
            return self.entries[:limit]
        return self.entries
    
    def get_entry_count(self) -> int:
        """Retourne le nombre d'entrées dans l'historique."""
        return len(self.entries)
    
    def clear(self):
        """Efface tout l'historique."""
        self.entries = []
        self._save()
    
    def delete_entry(self, entry_id: str):
        """
        Supprime une entrée de l'historique.
        
        Args:
            entry_id: ID de l'entrée à supprimer
        """
        self.entries = [e for e in self.entries if e.id != entry_id]
        self._save()


class HistoryWindow(ctk.CTkToplevel):
    """
    Fenêtre modale affichant l'historique des téléchargements.
    """
    
    def __init__(self, parent, history_manager: HistoryManager):
        super().__init__(parent)
        
        self.history_manager = history_manager
        
        # Configuration de la fenêtre
        self.title("📋 Historique des téléchargements")
        self.geometry("700x500")
        self.minsize(600, 400)
        
        # Rendre la fenêtre modale
        self.transient(parent)
        self.grab_set()
        
        # Centrer sur la fenêtre parente
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 700) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 500) // 2
        self.geometry(f"+{x}+{y}")
        
        # Créer l'interface
        self._create_ui()
        
        # Charger l'historique
        self._load_history()
    
    def _create_ui(self):
        """Crée l'interface de la fenêtre."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # En-tête
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"Historique ({self.history_manager.get_entry_count()} téléchargements)",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Bouton effacer tout
        clear_button = ctk.CTkButton(
            header_frame,
            text="🗑️ Tout effacer",
            width=120,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            hover_color=("#ffebee", "#4a1515"),
            command=self._clear_history
        )
        clear_button.grid(row=0, column=1)
        
        # Liste scrollable
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Message si vide
        self.empty_label = ctk.CTkLabel(
            self.scroll_frame,
            text="Aucun téléchargement dans l'historique",
            font=ctk.CTkFont(size=14),
            text_color=("gray40", "gray60")
        )
    
    def _load_history(self):
        """Charge et affiche l'historique."""
        # Effacer le contenu actuel
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        entries = self.history_manager.get_entries()
        
        if not entries:
            self.empty_label = ctk.CTkLabel(
                self.scroll_frame,
                text="Aucun téléchargement dans l'historique",
                font=ctk.CTkFont(size=14),
                text_color=("gray40", "gray60")
            )
            self.empty_label.grid(row=0, column=0, pady=50)
            return
        
        # Afficher les entrées
        for i, entry in enumerate(entries):
            self._create_entry_widget(i, entry)
    
    def _create_entry_widget(self, row: int, entry: HistoryEntry):
        """Crée un widget pour une entrée de l'historique."""
        frame = ctk.CTkFrame(self.scroll_frame)
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 8))
        frame.grid_columnconfigure(0, weight=1)
        
        # Infos frame
        info_frame = ctk.CTkFrame(frame, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=8)
        info_frame.grid_columnconfigure(0, weight=1)
        
        # Titre
        title_label = ctk.CTkLabel(
            info_frame,
            text=entry.title[:60] + "..." if len(entry.title) > 60 else entry.title,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Détails
        details_text = f"{entry.get_format_display()} • {entry.date}"
        details_label = ctk.CTkLabel(
            info_frame,
            text=details_text,
            font=ctk.CTkFont(size=11),
            text_color=("gray40", "gray60"),
            anchor="w"
        )
        details_label.grid(row=1, column=0, sticky="w", pady=(2, 0))
        
        # Boutons
        buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
        buttons_frame.grid(row=0, column=1, padx=10, pady=8)
        
        # Bouton ouvrir dossier
        open_button = ctk.CTkButton(
            buttons_frame,
            text="📂",
            width=35,
            height=35,
            fg_color="transparent",
            hover_color=("gray75", "gray25"),
            command=lambda e=entry: self._open_folder(e)
        )
        open_button.grid(row=0, column=0, padx=(0, 5))
        
        # Bouton supprimer
        delete_button = ctk.CTkButton(
            buttons_frame,
            text="🗑️",
            width=35,
            height=35,
            fg_color="transparent",
            hover_color=("#ffebee", "#4a1515"),
            command=lambda e=entry: self._delete_entry(e)
        )
        delete_button.grid(row=0, column=1)
    
    def _open_folder(self, entry: HistoryEntry):
        """Ouvre le dossier contenant le fichier."""
        import subprocess
        import platform
        
        filepath = entry.filepath
        
        if not os.path.exists(filepath):
            messagebox.showwarning(
                "Fichier introuvable",
                f"Le fichier n'existe plus :\n{filepath}"
            )
            return
        
        folder = os.path.dirname(filepath)
        
        try:
            if platform.system() == 'Windows':
                subprocess.run(['explorer', '/select,', filepath])
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', '-R', filepath])
            else:  # Linux
                subprocess.run(['xdg-open', folder])
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le dossier :\n{e}")
    
    def _delete_entry(self, entry: HistoryEntry):
        """Supprime une entrée de l'historique."""
        self.history_manager.delete_entry(entry.id)
        self._load_history()
    
    def _clear_history(self):
        """Efface tout l'historique."""
        if messagebox.askyesno(
            "Confirmation",
            "Êtes-vous sûr de vouloir effacer tout l'historique ?"
        ):
            self.history_manager.clear()
            self._load_history()


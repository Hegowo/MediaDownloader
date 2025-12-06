# -*- coding: utf-8 -*-
"""
Gestionnaire de thèmes pour l'application.
Permet de basculer entre le mode sombre et clair.
"""

import customtkinter as ctk
from typing import Callable, Optional
import json
import os


class ThemeManager:
    """
    Gestionnaire des thèmes de l'application.
    Sauvegarde la préférence utilisateur.
    """
    
    # Couleurs personnalisées pour chaque thème
    COLORS = {
        'dark': {
            'primary': '#1f538d',
            'primary_hover': '#14375e',
            'success': '#2d7d46',
            'error': '#c0392b',
            'warning': '#f39c12',
            'surface': '#2b2b2b',
            'surface_hover': '#3d3d3d',
            'text': '#ffffff',
            'text_secondary': '#b0b0b0',
            'border': '#404040'
        },
        'light': {
            'primary': '#3498db',
            'primary_hover': '#2980b9',
            'success': '#27ae60',
            'error': '#e74c3c',
            'warning': '#f1c40f',
            'surface': '#ffffff',
            'surface_hover': '#f0f0f0',
            'text': '#2c3e50',
            'text_secondary': '#7f8c8d',
            'border': '#bdc3c7'
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise le gestionnaire de thèmes.
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config_path = config_path or self._get_default_config_path()
        self.current_theme = 'dark'
        self._on_theme_change_callback: Optional[Callable] = None
        
        # Charger la préférence sauvegardée
        self._load_preference()
        
        # Appliquer le thème
        self._apply_theme()
    
    def _get_default_config_path(self) -> str:
        """Retourne le chemin par défaut du fichier de configuration."""
        # Utiliser le dossier de l'application
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(app_dir, 'config', 'theme.json')
    
    def _load_preference(self):
        """Charge la préférence de thème depuis le fichier."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_theme = data.get('theme', 'dark')
        except Exception:
            # En cas d'erreur, garder le thème par défaut
            self.current_theme = 'dark'
    
    def _save_preference(self):
        """Sauvegarde la préférence de thème."""
        try:
            # Créer le dossier si nécessaire
            config_dir = os.path.dirname(self.config_path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump({'theme': self.current_theme}, f)
        except Exception as e:
            print(f"Erreur sauvegarde thème: {e}")
    
    def _apply_theme(self):
        """Applique le thème actuel à CustomTkinter."""
        ctk.set_appearance_mode(self.current_theme)
    
    def set_theme(self, theme: str):
        """
        Définit le thème de l'application.
        
        Args:
            theme: 'dark' ou 'light'
        """
        if theme not in ['dark', 'light']:
            return
        
        self.current_theme = theme
        self._apply_theme()
        self._save_preference()
        
        if self._on_theme_change_callback:
            self._on_theme_change_callback(theme)
    
    def toggle_theme(self):
        """Bascule entre le mode sombre et clair."""
        new_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.set_theme(new_theme)
    
    def get_theme(self) -> str:
        """Retourne le thème actuel."""
        return self.current_theme
    
    def is_dark(self) -> bool:
        """Retourne True si le thème actuel est sombre."""
        return self.current_theme == 'dark'
    
    def get_colors(self) -> dict:
        """Retourne les couleurs du thème actuel."""
        return self.COLORS.get(self.current_theme, self.COLORS['dark'])
    
    def get_color(self, color_name: str) -> str:
        """
        Retourne une couleur spécifique du thème actuel.
        
        Args:
            color_name: Nom de la couleur (primary, success, error, etc.)
        """
        colors = self.get_colors()
        return colors.get(color_name, '#ffffff')
    
    def set_on_theme_change(self, callback: Callable):
        """
        Définit le callback à appeler lors du changement de thème.
        
        Args:
            callback: Fonction(theme: str) à appeler
        """
        self._on_theme_change_callback = callback


class ThemeToggleButton(ctk.CTkButton):
    """
    Bouton pour basculer entre les thèmes.
    Affiche une icône différente selon le thème actuel.
    """
    
    def __init__(self, master, theme_manager: ThemeManager, **kwargs):
        self.theme_manager = theme_manager
        
        # Configuration par défaut
        default_kwargs = {
            'text': self._get_icon(),
            'width': 40,
            'height': 40,
            'font': ctk.CTkFont(size=18),
            'fg_color': 'transparent',
            'hover_color': ('gray75', 'gray25'),
            'command': self._toggle
        }
        default_kwargs.update(kwargs)
        
        super().__init__(master, **default_kwargs)
        
        # S'abonner aux changements de thème
        self.theme_manager.set_on_theme_change(self._on_theme_changed)
    
    def _get_icon(self) -> str:
        """Retourne l'icône selon le thème actuel."""
        return "🌙" if self.theme_manager.is_dark() else "☀️"
    
    def _toggle(self):
        """Bascule le thème."""
        self.theme_manager.toggle_theme()
    
    def _on_theme_changed(self, theme: str):
        """Callback appelé quand le thème change."""
        self.configure(text=self._get_icon())


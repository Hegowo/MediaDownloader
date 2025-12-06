# -*- coding: utf-8 -*-
"""
Crée une icône ICO à partir du logo SVG.
Utilise une approche de rendu basique sans dépendances Cairo.
"""

import os
import sys
from PIL import Image, ImageDraw

def create_icon_from_svg():
    """Crée une icône représentative du logo Media Downloader."""
    
    ico_path = os.path.join("utils", "media", "logo.ico")
    
    print("[*] Creation de l'icone...")
    
    # Créer une image de base 256x256 avec fond transparent
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Dessiner un cercle de fond (style moderne)
    padding = 20
    draw.ellipse(
        [padding, padding, size - padding, size - padding],
        fill=(41, 128, 185, 255)  # Bleu moderne
    )
    
    # Dessiner une flèche de téléchargement stylisée
    center_x = size // 2
    arrow_color = (255, 255, 255, 255)  # Blanc
    
    # Corps de la flèche (rectangle vertical)
    rect_width = 40
    rect_height = 80
    rect_top = 60
    draw.rectangle(
        [center_x - rect_width//2, rect_top, 
         center_x + rect_width//2, rect_top + rect_height],
        fill=arrow_color
    )
    
    # Pointe de la flèche (triangle)
    triangle_width = 100
    triangle_top = rect_top + rect_height - 10
    triangle_bottom = triangle_top + 60
    draw.polygon(
        [
            (center_x - triangle_width//2, triangle_top),
            (center_x + triangle_width//2, triangle_top),
            (center_x, triangle_bottom)
        ],
        fill=arrow_color
    )
    
    # Barre horizontale en bas (représentant le "sol" / destination)
    bar_width = 120
    bar_height = 15
    bar_top = size - padding - 50
    draw.rectangle(
        [center_x - bar_width//2, bar_top,
         center_x + bar_width//2, bar_top + bar_height],
        fill=arrow_color
    )
    
    # Sauvegarder avec plusieurs tailles pour ICO
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    img.save(
        ico_path,
        format='ICO',
        sizes=sizes
    )
    
    # Sauvegarder aussi un PNG
    png_path = os.path.join("utils", "media", "logo.png")
    img.save(png_path, format='PNG')
    
    print(f"[OK] Icone creee : {ico_path}")
    print(f"[OK] PNG cree : {png_path}")
    
    return ico_path

if __name__ == "__main__":
    create_icon_from_svg()


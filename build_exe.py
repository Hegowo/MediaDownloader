# -*- coding: utf-8 -*-
"""
Script de compilation de l'application en executable Windows.
Convertit le logo SVG en ICO et compile avec PyInstaller.
"""

import os
import subprocess
import sys

# Fixer l'encodage pour la console Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def convert_svg_to_ico():
    """Convertit le logo SVG en ICO pour Windows."""
    from PIL import Image
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
    
    svg_path = os.path.join("utils", "media", "logo.svg")
    ico_path = os.path.join("utils", "media", "logo.ico")
    png_path = os.path.join("utils", "media", "logo.png")
    
    print("[*] Conversion du logo SVG en ICO...")
    
    # Convertir SVG en PNG via svglib/reportlab
    drawing = svg2rlg(svg_path)
    if drawing is None:
        raise Exception("Impossible de lire le fichier SVG")
    
    # Redimensionner pour avoir une bonne resolution
    scale = 256 / max(drawing.width, drawing.height)
    drawing.width = drawing.width * scale
    drawing.height = drawing.height * scale
    drawing.scale(scale, scale)
    
    # Rendre en PNG
    renderPM.drawToFile(drawing, png_path, fmt="PNG")
    
    # Ouvrir le PNG et creer l'ICO avec plusieurs tailles
    img = Image.open(png_path)
    
    # Creer un fond transparent si necessaire
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Centrer l'image dans un carre
    size = max(img.size)
    new_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    offset = ((size - img.width) // 2, (size - img.height) // 2)
    new_img.paste(img, offset)
    
    # Creer l'ICO avec plusieurs tailles pour Windows
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    new_img.save(
        ico_path,
        format='ICO',
        sizes=sizes
    )
    
    print(f"[OK] Logo converti : {ico_path}")
    return ico_path


def build_exe(ico_path):
    """Compile l'application avec PyInstaller."""
    print("\n[*] Compilation de l'executable...")
    
    # Chemin PyInstaller
    pyinstaller_cmd = [sys.executable, "-m", "PyInstaller"]
    
    # Options PyInstaller
    cmd = pyinstaller_cmd + [
        "--name=MediaDownloader",
        "--onefile",              # Un seul fichier .exe
        "--windowed",             # Pas de console
        f"--icon={ico_path}",     # Icone de l'application
        "--clean",                # Nettoyer avant compilation
        "--noconfirm",            # Pas de confirmation
        # Inclure les donnees necessaires
        "--add-data=utils/media;utils/media",
        "--add-data=config;config",
        "--add-data=data;data",
        "--add-data=assets;assets",
        # Imports caches
        "--hidden-import=customtkinter",
        "--hidden-import=PIL",
        "--hidden-import=PIL._tkinter_finder",
        "--hidden-import=yt_dlp",
        "--hidden-import=requests",
        # Collecter les packages complets
        "--collect-all=customtkinter",
        "--collect-all=yt_dlp",
        # Point d'entree
        "main.py"
    ]
    
    print(f"Commande: {' '.join(cmd[:5])}...")
    print("\n[...] Compilation en cours... (cela peut prendre quelques minutes)")
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        exe_path = os.path.join("dist", "MediaDownloader.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n[OK] Compilation reussie !")
            print(f"[>] Fichier : {os.path.abspath(exe_path)}")
            print(f"[>] Taille : {size_mb:.1f} MB")
        return True
    else:
        print(f"\n[ERREUR] Erreur de compilation (code: {result.returncode})")
        return False


def main():
    print("=" * 60)
    print("  Media Downloader - Compilation en executable Windows")
    print("=" * 60)
    print()
    
    # Verifier qu'on est dans le bon dossier
    if not os.path.exists("main.py"):
        print("[ERREUR] Executez ce script depuis le dossier racine du projet")
        sys.exit(1)
    
    # Convertir le logo
    ico_path = None
    try:
        ico_path = convert_svg_to_ico()
    except Exception as e:
        print(f"[AVERTISSEMENT] Erreur conversion logo: {e}")
        print("[*] Compilation sans icone personnalisee...")
    
    # Compiler
    if ico_path and os.path.exists(ico_path):
        success = build_exe(ico_path)
    else:
        # Compiler sans icone personnalisee - modifier la commande
        print("[*] Compilation sans icone...")
        success = build_exe_no_icon()
    
    if success:
        print("\n" + "=" * 60)
        print("  [OK] Termine ! L'executable est dans le dossier 'dist'")
        print("=" * 60)
    
    return 0 if success else 1


def build_exe_no_icon():
    """Compile sans icone personnalisee."""
    pyinstaller_cmd = [sys.executable, "-m", "PyInstaller"]
    
    cmd = pyinstaller_cmd + [
        "--name=MediaDownloader",
        "--onefile",
        "--windowed",
        "--clean",
        "--noconfirm",
        "--add-data=utils/media;utils/media",
        "--add-data=config;config", 
        "--add-data=data;data",
        "--add-data=assets;assets",
        "--hidden-import=customtkinter",
        "--hidden-import=PIL",
        "--hidden-import=PIL._tkinter_finder",
        "--hidden-import=yt_dlp",
        "--hidden-import=requests",
        "--collect-all=customtkinter",
        "--collect-all=yt_dlp",
        "main.py"
    ]
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        exe_path = os.path.join("dist", "MediaDownloader.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n[OK] Compilation reussie !")
            print(f"[>] Fichier : {os.path.abspath(exe_path)}")
            print(f"[>] Taille : {size_mb:.1f} MB")
        return True
    return False


if __name__ == "__main__":
    sys.exit(main())

from PySide6.QtCore import QFile, QTextStream
from PySide6.QtWidgets import QApplication
import os

class StyleManager:
    """Gestor de estilos para la aplicación"""
    
    def __init__(self):
        self.current_theme = "dark"
        self.themes_path = os.path.join(os.path.dirname(__file__), "styles")
        
    def apply_style(self, widget):
        """Aplicar el estilo actual al widget y sus hijos"""
        # Primero aplicar el estilo base
        base_file = os.path.join(self.themes_path, "base.qss")
        base_style = ""
        
        if os.path.exists(base_file):
            with open(base_file, "r", encoding='utf-8') as f:
                base_style = f.read()
        
        # Luego aplicar el tema específico
        theme_file = os.path.join(self.themes_path, "themes", f"{self.current_theme}.qss")
        theme_style = ""
        
        if os.path.exists(theme_file):
            with open(theme_file, "r", encoding='utf-8') as f:
                theme_style = f.read()
        
        # Combinar estilos y aplicar
        combined_style = base_style + "\n" + theme_style
        widget.setStyleSheet(combined_style)
    
    def toggle_theme(self):
        """Cambiar entre temas claro y oscuro"""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        # Aplicar a toda la aplicación
        self.apply_style(QApplication.instance())
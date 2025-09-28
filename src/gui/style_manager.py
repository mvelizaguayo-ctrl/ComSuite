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
        theme_file = os.path.join(self.themes_path, "themes", f"{self.current_theme}.qss")
        
        if os.path.exists(theme_file):
            with open(theme_file, "r") as f:
                widget.setStyleSheet(f.read())
        else:
            # Si no existe el archivo de tema, aplicar estilo base
            base_file = os.path.join(self.themes_path, "base.qss")
            if os.path.exists(base_file):
                with open(base_file, "r") as f:
                    widget.setStyleSheet(f.read())
    
    def toggle_theme(self):
        """Cambiar entre temas claro y oscuro"""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        # Aplicar a toda la aplicación
        self.apply_style(QApplication.instance())
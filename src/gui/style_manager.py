# src/gui/style_manager.py
from PySide6.QtCore import QFile, QTextStream
from PySide6.QtWidgets import QApplication

class StyleManager:
    """Gestor central de estilos QSS para toda la aplicación"""
    
    @staticmethod
    def apply_base_style(app: QApplication):
        """Aplica el estilo base a toda la aplicación"""
        StyleManager._load_style(app, "src/gui/styles/base.qss")
    
    @staticmethod
    def apply_theme(app: QApplication, theme_name: str):
        """Aplica un tema específico (dark, light, etc.)"""
        theme_path = f"src/gui/styles/themes/{theme_name}.qss"
        StyleManager._load_style(app, theme_path)
    
    @staticmethod
    def _load_style(app: QApplication, path: str):
        """Carga y aplica un archivo QSS"""
        style_file = QFile(path)
        if style_file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(style_file)
            stylesheet = stream.readAll()
            app.setStyleSheet(stylesheet)
            style_file.close()
        else:
            print(f"No se pudo cargar el estilo: {path}")
            
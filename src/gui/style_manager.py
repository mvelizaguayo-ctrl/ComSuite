from PySide6.QtCore import QFile, QTextStream
from PySide6.QtWidgets import QApplication
import os
import sys

class StyleManager:
    """Gestor de estilos para la aplicación - CON DIAGNÓSTICO COMPLETO"""
    
    @staticmethod
    def get_resource_path(relative_path):
        """Obtener la ruta absoluta a un recurso, funcionando para dev y en ejecutable"""
        try:
            # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)
    
    @staticmethod
    def apply_theme(widget, theme_name="dark"):
        """Aplicar SOLO el tema especificado, con diagnóstico completo"""
        print("=== INICIANDO APLICACIÓN DE TEMAS ===")
        
        # Construir la ruta al archivo de tema
        theme_path = os.path.join("src", "gui", "styles", "themes", f"{theme_name}.qss")
        
        print(f"1. Ruta del tema: {theme_path}")
        print(f"2. ¿Existe el archivo? {os.path.exists(theme_path)}")
        
        # Verificar si el archivo existe
        if not os.path.exists(theme_path):
            print(f"❌ ERROR: El archivo de tema no existe: {theme_path}")
            return False
        
        # Intentar cargar el archivo QSS del tema
        qss_file = QFile(theme_path)
        if qss_file.exists():
            qss_file.open(QFile.ReadOnly | QFile.Text)
            theme_styles = QTextStream(qss_file).readAll()
            qss_file.close()
            
            print(f"3. Archivo QSS cargado: {len(theme_styles)} caracteres")
            print(f"4. Primeros 200 caracteres del QSS:")
            print(theme_styles[:200])
            
            # Verificar si contiene estilos oscuros
            if "background-color: #1e1e1e" in theme_styles or "background-color: #2d2d2d" in theme_styles:
                print("✅ Se detectaron estilos oscuros en el QSS")
            else:
                print("❌ NO se detectaron estilos oscuros en el QSS")
                print("❌ El archivo QSS puede contener estilos para tema claro")
            
            # Aplicar SOLO los estilos del tema (sin base.qss)
            widget.setStyleSheet(theme_styles)
            
            print("5. Estilos aplicados al widget")
            print("=== APLICACIÓN DE TEMAS COMPLETADA ===")
            return True
        else:
            print(f"❌ ERROR: No se pudo abrir el archivo QSS: {theme_path}")
            return False
    
    @staticmethod
    def get_current_theme_path(theme_name="dark"):
        """Obtener la ruta al archivo de tema actual"""
        return os.path.join("src", "gui", "styles", "themes", f"{theme_name}.qss")
    
    @staticmethod
    def debug_widget_styles(widget):
        """Método de depuración para ver estilos aplicados a un widget"""
        print("=== DEPURACIÓN DE ESTILOS DEL WIDGET ===")
        print(f"Clase del widget: {widget.__class__.__name__}")
        print(f"Estilos aplicados: {widget.styleSheet()[:200] if widget.styleSheet() else 'SIN ESTILOS'}")
        
        # Verificar estilos específicos
        style = widget.styleSheet()
        if style:
            if "background-color: #1e1e1e" in style:
                print("✅ Widget tiene fondo oscuro")
            else:
                print("❌ Widget NO tiene fondo oscuro")
            
            if "background-color: #f0f0f0" in style or "background: #ffffff" in style:
                print("❌ Widget tiene estilos de tema CLARO")
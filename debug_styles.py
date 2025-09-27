# debug_styles.py
# Ruta completa: C:\Users\manue\ComSuite\debug_styles.py

import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import QFile

def debug_qss():
    app = QApplication([])
    
    # Obtener la ruta absoluta del directorio actual (donde está este script)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Directorio actual: {current_dir}")
    
    # Construir la ruta absoluta al archivo QSS
    qss_path = os.path.join(current_dir, "src", "gui", "styles", "base.qss")
    print(f"Ruta al archivo QSS: {qss_path}")
    print(f"¿Existe el archivo?: {os.path.exists(qss_path)}")
    
    if os.path.exists(qss_path):
        print("\n=== Contenido del archivo QSS ===")
        with open(qss_path, 'r') as f:
            content = f.read()
            print(content)
        
        print("\n=== Intentando cargar con QFile ===")
        file = QFile(qss_path)
        if file.open(QFile.ReadOnly):
            qss_content = bytes(file.readAll()).decode('utf-8')
            print(f"✅ QFile leyó {len(qss_content)} caracteres")
            print("Primeros 200 caracteres del QSS:")
            print(qss_content[:200] + "..." if len(qss_content) > 200 else qss_content)
            
            # Aplicar estilos
            app.setStyleSheet(qss_content)
            file.close()
            print("✅ Estilos aplicados a la aplicación")
        else:
            print("❌ Error: QFile no pudo abrir el archivo")
            print(f"Error de QFile: {file.errorString()}")
    else:
        print("❌ Error: El archivo QSS no existe en la ruta especificada")
    
    # Crear ventana de prueba simple
    print("\n=== Creando ventana de prueba ===")
    window = QWidget()
    window.setWindowTitle("Debug de Estilos - ComSuite")
    window.setMinimumSize(400, 200)
    
    layout = QVBoxLayout()
    
    # Etiqueta para verificar estilos
    test_label = QLabel("ESTILOS DE PRUEBA")
    test_label.setStyleSheet("font-size: 16px; font-weight: bold;")
    
    # Etiqueta adicional
    info_label = QLabel("Si los estilos cargan, el fondo debe ser gris claro")
    info_label.setObjectName("infoLabel")
    
    layout.addWidget(test_label)
    layout.addWidget(info_label)
    window.setLayout(layout)
    
    print("Mostrando ventana...")
    window.show()
    
    # Información adicional
    print("\n=== Información de depuración ===")
    print(f"Python ejecutable: {sys.executable}")
    print(f"Versión de Python: {sys.version}")
    
    try:
        from PySide6 import QtCore
        print(f"PySide6 versión: {QtCore.__version__}")
    except ImportError:
        print("❌ Error: No se pudo importar PySide6")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    debug_qss()
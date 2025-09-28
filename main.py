import sys
import os

# Agregar el directorio raíz del proyecto al PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Agregar el directorio src al PYTHONPATH
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from PySide6.QtWidgets import QApplication
from src.core.communication_engine import CommunicationEngine
from src.gui.main_window import MainWindow

def main():
    # Crear aplicación
    app = QApplication(sys.argv)
    app.setApplicationName("ComSuite Professional Communication Suite")
    app.setApplicationVersion("1.0.0")
    
    # Inicializar el motor de comunicaciones
    try:
        comm_engine = CommunicationEngine()
        print("Motor de comunicaciones inicializado correctamente")
    except Exception as e:
        print(f"Error inicializando el motor de comunicaciones: {e}")
        sys.exit(1)
    
    # Crear la ventana principal
    try:
        main_window = MainWindow(comm_engine)
        print("Ventana principal creada correctamente")
    except Exception as e:
        print(f"Error creando la ventana principal: {e}")
        sys.exit(1)
    
    # Conectar señales del core a la GUI
    comm_engine.protocol_loaded.connect(main_window.on_protocol_loaded)
    comm_engine.device_connected.connect(main_window.on_device_connected)
    comm_engine.device_disconnected.connect(main_window.on_device_disconnected)
    
    # Configurar tamaño inicial y comportamiento de la ventana
    main_window.resize(1400, 900)  # Tamaño inicial más grande
    main_window.setMinimumSize(1000, 700)  # Tamaño mínimo para evitar recortes
    
    # Mostrar ventana
    main_window.show()
    
    # Ejecutar aplicación
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
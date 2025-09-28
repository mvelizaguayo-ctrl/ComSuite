import sys
import os

# Agregar el directorio raíz del proyecto al PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication
from src.core.communication_engine import CommunicationEngine
from src.gui.main_window import MainWindow

def main():
    # Crear aplicación
    app = QApplication(sys.argv)
    app.setApplicationName("ComSuite Professional Communication Suite")
    app.setApplicationVersion("1.0.0")
    
    # Inicializar el motor de comunicaciones
    comm_engine = CommunicationEngine()
    
    # Crear la ventana principal
    main_window = MainWindow(comm_engine)
    
    # Conectar señales del core a la GUI
    comm_engine.protocol_loaded.connect(main_window.on_protocol_loaded)
    comm_engine.device_connected.connect(main_window.on_device_connected)
    comm_engine.device_disconnected.connect(main_window.on_device_disconnected)
    
    # Mostrar ventana
    main_window.show()
    
    # Ejecutar aplicación
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
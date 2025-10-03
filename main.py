import sys
from PySide6.QtWidgets import QApplication

# Prefer executing as package (python -m src). Try to import package entry points
try:
    from src.gui.main_window import MainWindow
    from src.core.communication_engine import CommunicationEngine
    from src.gui.style_manager import StyleManager
except Exception:
    # Fallback: if run as script from project root, try relative imports
    from src.gui.main_window import MainWindow
    from src.core.communication_engine import CommunicationEngine
    from src.gui.style_manager import StyleManager


def main():
    """Función principal de la aplicación"""
    # Crear la aplicación
    app = QApplication(sys.argv)
    
    # Establecer información de la aplicación
    app.setApplicationName("ComSuite Professional Suite")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("ComSuite")
    
    try:
        # Inicializar el motor de comunicaciones
        communication_engine = CommunicationEngine()
        print("Motor de comunicaciones inicializado correctamente")
        
        # Crear la ventana principal
        window = MainWindow(communication_engine)
        print("Ventana principal creada correctamente")
        
        # Conectar señales del motor de comunicaciones con la ventana principal
        communication_engine.protocol_loaded.connect(window.on_protocol_loaded)
        print("Señales conectadas correctamente")
        
        # Aplicar estilos - ANTES de mostrar la ventana
        StyleManager.apply_theme(window, "dark")
        print("Estilos aplicados correctamente")
        
        # Mostrar la ventana - DESPUÉS de aplicar estilos
        window.show()
        print("Ventana mostrada correctamente")
        
        # Ejecutar la aplicación
        return app.exec()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print("Nota: es preferible ejecutar la aplicación como paquete: python -m src")
    sys.exit(main())
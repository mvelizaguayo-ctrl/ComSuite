import sys
from PySide6.QtWidgets import QApplication

from .gui.main_window import MainWindow
from .core.communication_engine import CommunicationEngine
from .gui.style_manager import StyleManager


def main():
    """Función principal de la aplicación (paquete)."""
    app = QApplication(sys.argv)

    app.setApplicationName("ComSuite Professional Suite")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("ComSuite")

    try:
        communication_engine = CommunicationEngine()
        print("Motor de comunicaciones inicializado correctamente")

        window = MainWindow(communication_engine)
        print("Ventana principal creada correctamente")

        communication_engine.protocol_loaded.connect(window.on_protocol_loaded)
        print("Señales conectadas correctamente")

        StyleManager.apply_theme(window, "dark")
        print("Estilos aplicados correctamente")

        window.show()
        print("Ventana mostrada correctamente")

        return app.exec()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

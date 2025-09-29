import sys
import os
from PySide6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.core.communication_engine import CommunicationEngine
from src.gui.style_manager import StyleManager

def main():
    """Función principal de la aplicación - CON DIAGNÓSTICO"""
    print("=== INICIANDO APLICACIÓN ===")
    print(f"Directorio actual: {os.getcwd()}")
    
    # Listar archivos de estilos disponibles
    styles_dir = "src/gui/styles/themes"
    print(f"=== ARCHIVOS EN {styles_dir} ===")
    if os.path.exists(styles_dir):
        for file in os.listdir(styles_dir):
            print(f"  - {file}")
    else:
        print(f"❌ Directorio no existe: {styles_dir}")
    
    try:
        # Crear la aplicación
        app = QApplication(sys.argv)
        
        # Inicializar el motor de comunicaciones
        communication_engine = CommunicationEngine()
        print("✅ Motor de comunicaciones inicializado")
        
        # Crear la ventana principal
        main_window = MainWindow(communication_engine)
        print("✅ Ventana principal creada")
        
        # Conectar señales
        communication_engine.protocol_loaded.connect(main_window.on_protocol_loaded)
        print("✅ Señales conectadas")
        
        # Aplicar estilos con diagnóstico
        print("=== APLICANDO ESTILOS ===")
        success = StyleManager.apply_theme(main_window, "dark")
        
        if success:
            print("✅ Estilos aplicados exitosamente")
            # Depurar estilos del widget principal
            StyleManager.debug_widget_styles(main_window)
        else:
            print("❌ ERROR al aplicar estilos")
        
        main_window.show()
        print("✅ Ventana mostrada")
        
        # Ejecutar la aplicación
        return app.exec()
        
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
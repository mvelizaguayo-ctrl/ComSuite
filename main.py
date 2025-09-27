# main.py
import sys
from PySide6.QtWidgets import QApplication
from src.gui.style_manager import StyleManager

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ComSuite")
    app.setOrganizationName("ComSuiteTeam")
    
    # Aplicar estilos base
    StyleManager.apply_base_style(app)
    
    # Aquí crearemos la ventana principal después
    # main_window = MainWindow()
    # main_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
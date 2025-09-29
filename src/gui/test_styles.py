# src/gui/test_styles.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, 
    QLabel, QLineEdit, QApplication
)
from PySide6.QtCore import QFile, QTextStream

class StyleTestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prueba de Estilos")
        self.setMinimumSize(400, 300)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Elementos de prueba
        title = QLabel("ComSuite - Prueba de Estilos")
        title.setObjectName("infoLabel")
        
        input_field = QLineEdit("Ejemplo de texto")
        
        button = QPushButton("Botón de prueba")
        
        # Añadir al layout
        layout.addWidget(title)
        layout.addWidget(input_field)
        layout.addWidget(button)
        
        self.setLayout(layout)

def test_styles():
    app = QApplication([])
    
    # Cargar estilos directamente para prueba
    # style_file = QFile("src/gui/styles/base.qss")
    # if style_file.open(QFile.ReadOnly | QFile.Text):
    #     stream = QTextStream(style_file)
    #     app.setStyleSheet(stream.readAll())
    #     style_file.close()
    
    window = StyleTestWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    test_styles()
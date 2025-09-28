from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QListWidget, QListWidgetItem, QFrame,
    QMessageBox, QSizePolicy  # <-- MOVER AQUÍ
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon, QFont

from ..wizards.device_wizard import DeviceWizard
from ..panels.device_panel import SimpleDevicePanel
from ..panels.data_monitor import SimpleDataMonitor


class NoviceMode(QWidget):
    """Interfaz simplificada para usuarios novatos"""
    
    device_added = Signal(str)  # Señal cuando se agrega un dispositivo
    
    def __init__(self, communication_engine):
        super().__init__()
        self.communication_engine = communication_engine
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Frame para borde
        self.frame = QFrame()
        self.frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        
        # Layout dentro del frame
        layout = QVBoxLayout(self.frame)
        
        # Título descriptivo
        title_label = QLabel("ComSuite - Modo Novato")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        
        # Descripción del modo
        desc_label = QLabel(
            "Este modo simplificado le permite agregar y monitorear dispositivos "
            "sin necesidad de conocimientos técnicos avanzados."
        )
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        
        # Panel de dispositivos simplificado
        self.device_panel = SimpleDevicePanel(self.communication_engine)
        self.device_panel.setMinimumHeight(150)  # Altura mínima
        
        # Botón grande para agregar dispositivos
        self.add_device_btn = QPushButton("Agregar Nuevo Dispositivo")
        self.add_device_btn.setIcon(QIcon("icons/add_device.png"))
        self.add_device_btn.setFixedHeight(60)
        self.add_device_btn.setMinimumWidth(200)  # Ancho mínimo
        self.add_device_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_device_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        # Monitor de datos simplificado
        self.data_monitor = SimpleDataMonitor()
        
        # Agregar widgets al layout
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(self.device_panel)
        layout.addWidget(self.add_device_btn)
        layout.addWidget(self.data_monitor)
        
        # Configurar espaciado
        layout.setSpacing(20)  # Espacio entre widgets
        layout.setContentsMargins(25, 25, 25, 25)  # Márgenes del contenedor
        
        # Agregar el frame al layout principal
        main_layout.addWidget(self.frame)
        
        # Configurar políticas de tamaño
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
    def setup_connections(self):
        self.add_device_btn.clicked.connect(self.show_device_wizard)
        self.device_panel.device_selected.connect(self.on_device_selected)
        
    def show_device_wizard(self):
        """Mostrar asistente simplificado para agregar dispositivos"""
        wizard = DeviceWizard(self.communication_engine, simplified=True)
        wizard.device_created.connect(self.on_device_created)
        wizard.exec_()
        
    def on_device_created(self, device_info):
        """Manejar creación de nuevo dispositivo"""
        self.device_panel.add_device(device_info)
        self.device_added.emit(device_info['device_id'])
        QMessageBox.information(
            self, 
            "Dispositivo Agregado", 
            f"El dispositivo {device_info['device_id']} ha sido agregado correctamente."
        )
        
    def on_device_selected(self, device_id):
        """Manejar selección de dispositivo"""
        self.data_monitor.set_device(device_id)
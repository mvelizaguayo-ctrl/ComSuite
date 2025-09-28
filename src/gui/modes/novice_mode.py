from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QListWidget, QListWidgetItem, QFrame,
    QMessageBox
)
from PySide6.QtCore import Qt, Signal
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
        
        # Botón grande para agregar dispositivos
        self.add_device_btn = QPushButton("Agregar Nuevo Dispositivo")
        self.add_device_btn.setIcon(QIcon("icons/add_device.png"))
        self.add_device_btn.setFixedHeight(60)
        self.add_device_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        # Monitor de datos simplificado
        self.data_monitor = SimpleDataMonitor()
        
        # Agregar widgets al layout
        main_layout.addWidget(title_label)
        main_layout.addWidget(desc_label)
        main_layout.addWidget(self.device_panel)
        main_layout.addWidget(self.add_device_btn)
        main_layout.addWidget(self.data_monitor)
        
        # Espaciado
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
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
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ..panels.device_panel import DevicePanel
from ..panels.connection_panel import ConnectionPanel
from ..panels.data_monitor import DataMonitor
from ..panels.log_viewer import LogViewer


class ExpertMode(QWidget):
    """Interfaz completa para usuarios expertos"""
    
    def __init__(self, communication_engine):
        super().__init__()
        self.communication_engine = communication_engine
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        # Layout principal con splitter para flexibilidad
        main_layout = QHBoxLayout(self)
        
        # Panel izquierdo: Dispositivos y conexión
        left_panel = QVBoxLayout()
        
        # Título del panel izquierdo
        left_title = QLabel("Dispositivos y Conexión")
        left_title.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.device_panel = DevicePanel(self.communication_engine)
        self.connection_panel = ConnectionPanel(self.communication_engine)
        
        left_panel.addWidget(left_title)
        left_panel.addWidget(self.device_panel)
        left_panel.addWidget(self.connection_panel)
        
        # Panel derecho: Monitor de datos y logs
        right_panel = QVBoxLayout()
        
        # Título del panel derecho
        right_title = QLabel("Monitoreo y Diagnóstico")
        right_title.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.data_monitor = DataMonitor()
        self.log_viewer = LogViewer()
        
        right_panel.addWidget(right_title)
        right_panel.addWidget(self.data_monitor)
        right_panel.addWidget(self.log_viewer)
        
        # Crear widgets para el splitter
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        
        # Configurar splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)  # Panel izquierdo
        splitter.setStretchFactor(1, 2)  # Panel derecho (más grande)
        
        # Agregar splitter al layout principal
        main_layout.addWidget(splitter)
        
        # Configurar márgenes y espaciado
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
    def setup_connections(self):
        # Conectar señales entre componentes
        self.device_panel.device_selected.connect(self.data_monitor.set_device)
        self.device_panel.device_selected.connect(self.log_viewer.set_device)
        self.connection_panel.connection_status_changed.connect(self.log_viewer.log_connection)
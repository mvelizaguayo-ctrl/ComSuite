from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QProgressBar, QGroupBox
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon, QFont


class DeviceWidget(QFrame):
    """Widget para representar un dispositivo individual"""
    
    connect_clicked = Signal(str)  # device_id
    disconnect_clicked = Signal(str)  # device_id
    configure_clicked = Signal(str)  # device_id
    
    def __init__(self, device_info, parent=None):
        super().__init__(parent)
        self.device_info = device_info
        self.setup_ui()
        
        # Establecer estilo de frame
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Título del dispositivo
        title = QLabel(self.device_info['device_id'])
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        
        # Información del dispositivo
        info_group = QGroupBox("Información")
        info_layout = QVBoxLayout()
        
        protocol_label = QLabel(f"Protocolo: {self.device_info.get('protocol', 'Desconocido')}")
        type_label = QLabel(f"Tipo: {self.device_info.get('device_type', 'Genérico')}")
        
        info_layout.addWidget(protocol_label)
        info_layout.addWidget(type_label)
        
        info_group.setLayout(info_layout)
        
        # Estado de conexión
        self.status_label = QLabel("Desconectado")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        
        # Barra de progreso de comunicación
        self.comm_progress = QProgressBar()
        self.comm_progress.setRange(0, 100)
        self.comm_progress.setValue(0)
        self.comm_progress.setTextVisible(False)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        
        self.connect_btn = QPushButton("Conectar")
        self.connect_btn.setIcon(QIcon("icons/connect.png"))
        self.connect_btn.clicked.connect(self.on_connect)
        
        self.disconnect_btn = QPushButton("Desconectar")
        self.disconnect_btn.setIcon(QIcon("icons/disconnect.png"))
        self.disconnect_btn.clicked.connect(self.on_disconnect)
        self.disconnect_btn.setEnabled(False)
        
        self.configure_btn = QPushButton("Configurar")
        self.configure_btn.setIcon(QIcon("icons/settings.png"))
        self.configure_btn.clicked.connect(self.on_configure)
        
        button_layout.addWidget(self.connect_btn)
        button_layout.addWidget(self.disconnect_btn)
        button_layout.addWidget(self.configure_btn)
        
        # Agregar widgets al layout
        layout.addWidget(title)
        layout.addWidget(info_group)
        layout.addWidget(self.status_label)
        layout.addWidget(self.comm_progress)
        layout.addLayout(button_layout)
        
        # Establecer tamaño fijo
        self.setFixedSize(250, 300)
        
    def on_connect(self):
        """Manejar clic en conectar"""
        self.connect_clicked.emit(self.device_info['device_id'])
        
    def on_disconnect(self):
        """Manejar clic en desconectar"""
        self.disconnect_clicked.emit(self.device_info['device_id'])
        
    def on_configure(self):
        """Manejar clic en configurar"""
        self.configure_clicked.emit(self.device_info['device_id'])
        
    def set_connected(self, connected):
        """Actualizar estado de conexión"""
        if connected:
            self.status_label.setText("Conectado")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.comm_progress.setValue(100)
        else:
            self.status_label.setText("Desconectado")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)
            self.comm_progress.setValue(0)
            
    def update_progress(self, value):
        """Actualizar barra de progreso"""
        self.comm_progress.setValue(value)
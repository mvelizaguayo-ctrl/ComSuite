from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QGroupBox, QProgressBar,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QIcon


class ConnectionPanel(QWidget):
    """Panel de estado de conexiones para modo experto"""
    
    connection_status_changed = Signal(str, bool)  # device_id, connected
    
    def __init__(self, communication_engine):
        super().__init__()
        self.communication_engine = communication_engine
        self.setup_ui()
        self.setup_connections()
        
        # Timer para actualizar estado
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_connections_status)
        self.update_timer.start(1000)  # Actualizar cada segundo
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Estado de Conexiones")
        title.setStyleSheet("font-weight: bold; font-size: 12px;")
        
        # Tabla de conexiones
        self.connection_table = QTableWidget()
        self.connection_table.setColumnCount(4)
        self.connection_table.setHorizontalHeaderLabels(["Dispositivo", "Protocolo", "Estado", "Acciones"])
        self.connection_table.horizontalHeader().setStretchLastSection(True)
        self.connection_table.verticalHeader().setVisible(False)
        self.connection_table.setAlternatingRowColors(True)
        
        # Grupo de estadísticas
        stats_group = QGroupBox("Estadísticas de Conexión")
        stats_layout = QHBoxLayout()
        
        self.total_label = QLabel("Total: 0")
        self.connected_label = QLabel("Conectados: 0")
        self.disconnected_label = QLabel("Desconectados: 0")
        
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.connected_label)
        stats_layout.addWidget(self.disconnected_label)
        stats_layout.addStretch()
        
        stats_group.setLayout(stats_layout)
        
        # Agregar widgets al layout
        layout.addWidget(title)
        layout.addWidget(self.connection_table)
        layout.addWidget(stats_group)
        
        # Frame para borde
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        
    def setup_connections(self):
        # Conectar señales del motor de comunicación
        self.communication_engine.device_connected.connect(self.on_device_connected)
        self.communication_engine.device_disconnected.connect(self.on_device_disconnected)
        
    def update_connections_status(self):
        """Actualizar el estado de todas las conexiones"""
        devices = self.communication_engine.device_manager.get_all_devices()
        
        self.connection_table.setRowCount(len(devices))
        
        total = len(devices)
        connected = 0
        
        for i, (device_id, device) in enumerate(devices.items()):
            # Dispositivo
            device_item = QTableWidgetItem(device_id)
            self.connection_table.setItem(i, 0, device_item)
            
            # Protocolo
            protocol_item = QTableWidgetItem(device.protocol_name)
            self.connection_table.setItem(i, 1, protocol_item)
            
            # Estado
            status = "Conectado" if device.is_connected() else "Desconectado"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(Qt.green if device.is_connected() else Qt.red)
            self.connection_table.setItem(i, 2, status_item)
            
            # Acciones
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            if device.is_connected():
                disconnect_btn = QPushButton("Desconectar")
                disconnect_btn.setIcon(QIcon("icons/disconnect.png"))
                disconnect_btn.clicked.connect(lambda checked, did=device_id: self.disconnect_device(did))
                actions_layout.addWidget(disconnect_btn)
            else:
                connect_btn = QPushButton("Conectar")
                connect_btn.setIcon(QIcon("icons/connect.png"))
                connect_btn.clicked.connect(lambda checked, did=device_id: self.connect_device(did))
                actions_layout.addWidget(connect_btn)
            
            self.connection_table.setCellWidget(i, 3, actions_widget)
            
            if device.is_connected():
                connected += 1
        
        # Actualizar estadísticas
        self.total_label.setText(f"Total: {total}")
        self.connected_label.setText(f"Conectados: {connected}")
        self.disconnected_label.setText(f"Desconectados: {total - connected}")
        
    def connect_device(self, device_id):
        """Conectar un dispositivo"""
        self.communication_engine.device_manager.connect_device(device_id)
        
    def disconnect_device(self, device_id):
        """Desconectar un dispositivo"""
        self.communication_engine.device_manager.disconnect_device(device_id)
        
    def on_device_connected(self, device_id):
        """Manejar conexión de dispositivo"""
        self.connection_status_changed.emit(device_id, True)
        self.update_connections_status()
        
    def on_device_disconnected(self, device_id):
        """Manejar desconexión de dispositivo"""
        self.connection_status_changed.emit(device_id, False)
        self.update_connections_status()
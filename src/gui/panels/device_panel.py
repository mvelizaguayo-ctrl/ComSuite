from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
    QListWidgetItem, QLabel, QPushButton, QFrame,
    QMenu, QMessageBox, QInputDialog, QSizePolicy
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon


class DevicePanel(QFrame):  # <-- CAMBIAR DE QWidget A QFrame
    """Panel de dispositivos para modo experto"""
    
    device_selected = Signal(str)  # Emite ID del dispositivo seleccionado
    device_removed = Signal(str)   # Emite ID del dispositivo eliminado
    
    def __init__(self, communication_engine):
        super().__init__()
        self.communication_engine = communication_engine
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Dispositivos Configurados")
        title.setStyleSheet("font-weight: bold; font-size: 12px;")
        
        # Lista de dispositivos
        self.device_list = QListWidget()
        self.device_list.setAlternatingRowColors(True)
        self.device_list.setMinimumHeight(150)  # Altura mínima
        
        # Botones
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Agregar")
        self.add_btn.setIcon(QIcon("icons/add.png"))
        self.add_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.remove_btn = QPushButton("Eliminar")
        self.remove_btn.setIcon(QIcon("icons/remove.png"))
        self.remove_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.connect_btn = QPushButton("Conectar")
        self.connect_btn.setIcon(QIcon("icons/connect.png"))
        self.connect_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.disconnect_btn = QPushButton("Desconectar")
        self.disconnect_btn.setIcon(QIcon("icons/disconnect.png"))
        self.disconnect_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.remove_btn)
        button_layout.addWidget(self.connect_btn)
        button_layout.addWidget(self.disconnect_btn)
        
        # Agregar widgets al layout
        layout.addWidget(title)
        layout.addWidget(self.device_list)
        layout.addLayout(button_layout)
        
        # Frame para borde - AHORA ES CORRECTO porque heredamos de QFrame
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        
        # Configurar políticas de tamaño
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
    def setup_connections(self):
        self.device_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.device_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        self.add_btn.clicked.connect(self.add_device)
        self.remove_btn.clicked.connect(self.remove_device)
        self.connect_btn.clicked.connect(self.connect_device)
        self.disconnect_btn.clicked.connect(self.disconnect_device)
        
        # Conectar señales del motor de comunicación
        self.communication_engine.device_connected.connect(self.on_device_connected)
        self.communication_engine.device_disconnected.connect(self.on_device_disconnected)
        
    def add_device(self):
        """Agregar nuevo dispositivo usando el wizard completo"""
        from ..wizards.device_wizard import DeviceWizard
        wizard = DeviceWizard(self.communication_engine, simplified=False)
        wizard.exec_()
        
    def remove_device(self):
        """Eliminar dispositivo seleccionado"""
        current_item = self.device_list.currentItem()
        if current_item:
            device_id = current_item.data(Qt.UserRole)
            
            reply = QMessageBox.question(
                self, 
                "Confirmar Eliminación",
                f"¿Está seguro de eliminar el dispositivo {device_id}?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.communication_engine.device_manager.remove_device(device_id)
                self.device_list.takeItem(self.device_list.row(current_item))
                self.device_removed.emit(device_id)
                
    def connect_device(self):
        """Conectar dispositivo seleccionado"""
        current_item = self.device_list.currentItem()
        if current_item:
            device_id = current_item.data(Qt.UserRole)
            self.communication_engine.device_manager.connect_device(device_id)
            
    def disconnect_device(self):
        """Desconectar dispositivo seleccionado"""
        current_item = self.device_list.currentItem()
        if current_item:
            device_id = current_item.data(Qt.UserRole)
            self.communication_engine.device_manager.disconnect_device(device_id)
            
    def on_selection_changed(self):
        """Manejar cambio de selección"""
        current_item = self.device_list.currentItem()
        if current_item:
            device_id = current_item.data(Qt.UserRole)
            self.device_selected.emit(device_id)
            
    def on_item_double_clicked(self, item):
        """Manejar doble clic para conectar/desconectar"""
        device_id = item.data(Qt.UserRole)
        device = self.communication_engine.device_manager.get_device(device_id)
        
        if device and device.is_connected():
            self.communication_engine.device_manager.disconnect_device(device_id)
        else:
            self.communication_engine.device_manager.connect_device(device_id)
            
    def on_device_connected(self, device_id):
        """Actualizar UI cuando se conecta un dispositivo"""
        for i in range(self.device_list.count()):
            item = self.device_list.item(i)
            if item.data(Qt.UserRole) == device_id:
                item.setIcon(QIcon("icons/device_connected.png"))
                break
                
    def on_device_disconnected(self, device_id):
        """Actualizar UI cuando se desconecta un dispositivo"""
        for i in range(self.device_list.count()):
            item = self.device_list.item(i)
            if item.data(Qt.UserRole) == device_id:
                item.setIcon(QIcon("icons/device_disconnected.png"))
                break
                
    def add_device_item(self, device_info):
        """Agregar un dispositivo a la lista"""
        device_id = device_info['device_id']
        protocol = device_info.get('protocol', 'Desconocido')
        
        item = QListWidgetItem(f"{device_id} ({protocol})")
        item.setData(Qt.UserRole, device_id)
        item.setIcon(QIcon("icons/device_disconnected.png"))
        
        self.device_list.addItem(item)


class SimpleDevicePanel(QFrame):  # <-- CAMBIAR DE QWidget A QFrame
    """Panel simplificado para modo novato"""
    
    device_selected = Signal(str)  # Emite ID del dispositivo seleccionado
    
    def __init__(self, communication_engine):
        super().__init__()
        self.communication_engine = communication_engine
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Mis Dispositivos")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        title.setAlignment(Qt.AlignCenter)
        
        # Lista de dispositivos
        self.device_list = QListWidget()
        self.device_list.setAlternatingRowColors(True)
        self.device_list.setMaximumHeight(200)
        self.device_list.setMinimumHeight(150)  # Altura mínima
        
        # Descripción
        desc = QLabel("Haga clic en un dispositivo para ver sus datos")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        
        # Agregar widgets
        layout.addWidget(title)
        layout.addWidget(self.device_list)
        layout.addWidget(desc)
        
        # Frame para borde - AHORA ES CORRECTO porque heredamos de QFrame
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        
        # Configurar políticas de tamaño
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
    def setup_connections(self):
        self.device_list.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Conectar señales del motor de comunicación
        self.communication_engine.device_connected.connect(self.on_device_connected)
        self.communication_engine.device_disconnected.connect(self.on_device_disconnected)
        
    def on_selection_changed(self):
        """Manejar cambio de selección"""
        current_item = self.device_list.currentItem()
        if current_item:
            device_id = current_item.data(Qt.UserRole)
            self.device_selected.emit(device_id)
            
    def on_device_connected(self, device_id):
        """Actualizar UI cuando se conecta un dispositivo"""
        for i in range(self.device_list.count()):
            item = self.device_list.item(i)
            if item.data(Qt.UserRole) == device_id:
                item.setIcon(QIcon("icons/device_connected.png"))
                break
                
    def on_device_disconnected(self, device_id):
        """Actualizar UI cuando se desconecta un dispositivo"""
        for i in range(self.device_list.count()):
            item = self.device_list.item(i)
            if item.data(Qt.UserRole) == device_id:
                item.setIcon(QIcon("icons/device_disconnected.png"))
                break
                
    def add_device(self, device_info):
        """Agregar un dispositivo a la lista"""
        device_id = device_info['device_id']
        protocol = device_info.get('protocol', 'Desconocido')
        
        item = QListWidgetItem(f"{device_id}")
        item.setData(Qt.UserRole, device_id)
        item.setIcon(QIcon("icons/device_disconnected.png"))
        
        self.device_list.addItem(item)
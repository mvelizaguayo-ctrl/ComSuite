from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QProgressBar, QComboBox,
    QSpinBox, QLineEdit, QFormLayout
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon


class ConnectionWidget(QWidget):
    """Widget para configuración de conexión"""
    
    connect_clicked = Signal(dict)  # config
    disconnect_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Frame principal
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        frame_layout = QVBoxLayout(frame)
        
        # Título
        title = QLabel("Configuración de Conexión")
        title.setStyleSheet("font-weight: bold; font-size: 12px;")
        
        # Formulario de configuración
        form_layout = QFormLayout()
        
        # Protocolo
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["Modbus TCP", "Modbus RTU", "Profinet", "Profibus-DP", "Ethernet/IP"])
        form_layout.addRow("Protocolo:", self.protocol_combo)
        
        # Configuración TCP
        self.ip_edit = QLineEdit()
        self.ip_edit.setPlaceholderText("192.168.1.100")
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(502)
        
        form_layout.addRow("Dirección IP:", self.ip_edit)
        form_layout.addRow("Puerto:", self.port_spin)
        
        # Configuración RTU
        self.combo_port = QComboBox()
        self.combo_port.addItems(["COM1", "COM2", "COM3", "COM4"])
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        
        form_layout.addRow("Puerto COM:", self.combo_port)
        form_layout.addRow("Baud Rate:", self.baudrate_combo)
        
        # Botones
        button_layout = QHBoxLayout()
        
        self.connect_btn = QPushButton("Conectar")
        self.connect_btn.setIcon(QIcon("icons/connect.png"))
        self.connect_btn.clicked.connect(self.on_connect)
        
        self.disconnect_btn = QPushButton("Desconectar")
        self.disconnect_btn.setIcon(QIcon("icons/disconnect.png"))
        self.disconnect_btn.clicked.connect(self.on_disconnect)
        
        button_layout.addWidget(self.connect_btn)
        button_layout.addWidget(self.disconnect_btn)
        
        # Agregar widgets al frame
        frame_layout.addWidget(title)
        frame_layout.addLayout(form_layout)
        frame_layout.addLayout(button_layout)
        
        # Agregar frame al layout principal
        layout.addWidget(frame)
        
        # Conectar cambios de protocolo
        self.protocol_combo.currentTextChanged.connect(self.on_protocol_changed)
        
        # Inicializar visibilidad
        self.on_protocol_changed(self.protocol_combo.currentText())
        
    def on_protocol_changed(self, protocol):
        """Actualizar campos según el protocolo seleccionado"""
        is_tcp = "TCP" in protocol or "Ethernet" in protocol or "Profinet" in protocol
        is_rtu = "RTU" in protocol or "Profibus" in protocol
        
        # Mostrar/ocultar campos según protocolo
        self.ip_edit.setVisible(is_tcp)
        self.port_spin.setVisible(is_tcp)
        self.combo_port.setVisible(is_rtu)
        self.baudrate_combo.setVisible(is_rtu)
        
        # Actualizar etiquetas
        form_layout = self.layout().itemAt(0).widget().layout()
        for i in range(form_layout.rowCount()):
            label = form_layout.itemAt(i, QFormLayout.LabelRole)
            field = form_layout.itemAt(i, QFormLayout.FieldRole)
            
            if label and field:
                widget = field.widget()
                if widget == self.ip_edit:
                    label.widget().setVisible(is_tcp)
                elif widget == self.port_spin:
                    label.widget().setVisible(is_tcp)
                elif widget == self.combo_port:
                    label.widget().setVisible(is_rtu)
                elif widget == self.baudrate_combo:
                    label.widget().setVisible(is_rtu)
    
    def on_connect(self):
        """Manejar clic en conectar"""
        config = {
            'protocol': self.protocol_combo.currentText(),
            'device_id': 'temp_device'  # Debería ser configurable
        }
        
        protocol = self.protocol_combo.currentText()
        if "TCP" in protocol or "Ethernet" in protocol or "Profinet" in protocol:
            config.update({
                'ip': self.ip_edit.text(),
                'port': self.port_spin.value()
            })
        else:
            config.update({
                'com_port': self.combo_port.currentText(),
                'baudrate': self.baudrate_combo.currentText()
            })
        
        self.connect_clicked.emit(config)
        
    def on_disconnect(self):
        """Manejar clic en desconectar"""
        self.disconnect_clicked.emit()
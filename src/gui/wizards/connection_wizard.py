from PySide6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QPushButton,
    QFormLayout, QGroupBox, QMessageBox, QSpinBox
)
from PySide6.QtCore import Qt, Signal  # <-- AGREGAR ESTA IMPORTACIÓN
from PySide6.QtGui import QIcon


class ConnectionTypePage(QWizardPage):
    """Página de selección de tipo de conexión"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Paso 1: Tipo de Conexión")
        self.setSubTitle("Seleccione el tipo de conexión que desea establecer")
        
        layout = QVBoxLayout()
        
        # Opciones de conexión
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems([
            "Modbus TCP",
            "Modbus RTU", 
            "Profinet",
            "Profibus-DP",
            "Ethernet/IP"
        ])
        
        # Descripción
        desc_label = QLabel(
            "Seleccione el protocolo de comunicación que utilizará para conectarse "
            "al dispositivo. Cada protocolo tiene parámetros de configuración específicos."
        )
        desc_label.setWordWrap(True)
        
        layout.addWidget(desc_label)
        layout.addWidget(QLabel("Protocolo:"))
        layout.addWidget(self.protocol_combo)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Registrar campo obligatorio
        self.registerField("protocol*", self.protocol_combo, "currentText")
        
    def nextId(self):
        return 1  # Siguiente página: Configuración


class ConnectionConfigPage(QWizardPage):
    """Página de configuración de la conexión"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Paso 2: Configuración de Conexión")
        self.setSubTitle("Configure los parámetros de comunicación")
        
        layout = QFormLayout()
        
        # Configuración TCP
        self.ip_edit = QLineEdit()
        self.ip_edit.setPlaceholderText("192.168.1.100")
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(502)
        
        # Configuración RTU
        self.combo_port = QComboBox()
        self.combo_port.addItems(["COM1", "COM2", "COM3", "COM4"])
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        
        # Agregar campos al formulario
        layout.addRow("Dirección IP:", self.ip_edit)
        layout.addRow("Puerto:", self.port_spin)
        layout.addRow("Puerto COM:", self.combo_port)
        layout.addRow("Baud Rate:", self.baudrate_combo)
        
        self.setLayout(layout)
        
        # Registrar campos
        self.registerField("ip*", self.ip_edit)
        self.registerField("port*", self.port_spin)
        self.registerField("com_port*", self.combo_port)
        self.registerField("baudrate*", self.baudrate_combo)
        
    def initializePage(self):
        """Mostrar/ocultar campos según el protocolo"""
        protocol = self.field("protocol")
        is_tcp = "TCP" in protocol or "Ethernet" in protocol or "Profinet" in protocol
        is_rtu = "RTU" in protocol or "Profibus" in protocol
        
        # Mostrar/ocultar campos según protocolo
        self.ip_edit.setVisible(is_tcp)
        self.port_spin.setVisible(is_tcp)
        self.combo_port.setVisible(is_rtu)
        self.baudrate_combo.setVisible(is_rtu)
        
        # Actualizar etiquetas
        form_layout = self.layout()
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
    
    def nextId(self):
        return -1  # Finalizar wizard


class ConnectionWizard(QWizard):
    """Asistente para configurar conexiones"""
    
    connection_configured = Signal(dict)  # Señal cuando se configura una conexión
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_wizard()
        
    def setup_wizard(self):
        self.setWindowTitle("Asistente de Conexión")
        self.setWizardStyle(QWizard.ModernStyle)
        
        # Tamaño mínimo
        self.setMinimumSize(500, 350)
        
        # Páginas del asistente
        self.addPage(ConnectionTypePage(self))
        self.addPage(ConnectionConfigPage(self))
        
    def accept(self):
        """Recopilar configuración cuando se completa el asistente"""
        config = {
            'protocol': self.field("protocol"),
            'ip': self.field("ip"),
            'port': self.field("port"),
            'com_port': self.field("com_port"),
            'baudrate': self.field("baudrate")
        }
        
        # Emitir señal con la configuración
        self.connection_configured.emit(config)
        
        super().accept()
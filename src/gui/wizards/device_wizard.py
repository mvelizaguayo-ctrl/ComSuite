from PySide6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QPushButton,
    QFormLayout, QGroupBox, QMessageBox, QSpinBox,
    QCheckBox, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont


class DeviceTypePage(QWizardPage):
    """Página de selección de tipo de dispositivo"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Paso 1: Tipo de Dispositivo")
        self.setSubTitle("Seleccione el tipo de dispositivo que desea configurar")
        
        layout = QVBoxLayout()
        
        # Grupo de tipos de dispositivo
        device_group = QGroupBox("Tipos de Dispositivo Comunes")
        device_layout = QVBoxLayout()
        
        # Opciones predefinidas
        self.sensor_radio = QRadioButton("Sensor (Temperatura, Presión, etc.)")
        self.vfd_radio = QRadioButton("Variador de Frecuencia (VFD)")
        self.plc_radio = QRadioButton("PLC (Controlador Lógico Programable)")
        self.other_radio = QRadioButton("Otro (Configuración personalizada)")
        
        # Configurar grupo de botones
        self.device_group = QButtonGroup(self)
        self.device_group.addButton(self.sensor_radio)
        self.device_group.addButton(self.vfd_radio)
        self.device_group.addButton(self.plc_radio)
        self.device_group.addButton(self.other_radio)
        
        # Seleccionar por defecto
        self.sensor_radio.setChecked(True)
        
        device_layout.addWidget(self.sensor_radio)
        device_layout.addWidget(self.vfd_radio)
        device_layout.addWidget(self.plc_radio)
        device_layout.addWidget(self.other_radio)
        
        device_group.setLayout(device_layout)
        
        # Descripción
        desc_label = QLabel(
            "Seleccione el tipo de dispositivo más cercano a su necesidad. "
            "Esto ayudará a configurar los parámetros automáticamente."
        )
        desc_label.setWordWrap(True)
        
        layout.addWidget(desc_label)
        layout.addWidget(device_group)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def nextId(self):
        return 1  # Siguiente página: Protocolo


class ProtocolConfigPage(QWizardPage):
    """Página de configuración del protocolo"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Paso 2: Configuración del Protocolo")
        self.setSubTitle("Configure los parámetros de comunicación")
        
        layout = QFormLayout()
        
        # Selección de protocolo
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["Modbus TCP", "Modbus RTU", "Profinet", "Profibus-DP", "Ethernet/IP"])
        
        # Configuración básica
        self.device_id_edit = QLineEdit()
        self.device_id_edit.setPlaceholderText("Ej: sensor_temp_01")
        
        # Parámetros según protocolo
        self.ip_edit = QLineEdit()
        self.ip_edit.setPlaceholderText("192.168.1.100")
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(502)
        
        self.combo_port = QComboBox()
        self.combo_port.addItems(["COM1", "COM2", "COM3", "COM4"])
        
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        
        # Agregar campos al formulario
        layout.addRow("Protocolo:", self.protocol_combo)
        layout.addRow("ID del Dispositivo:", self.device_id_edit)
        layout.addRow("Dirección IP:", self.ip_edit)
        layout.addRow("Puerto:", self.port_spin)
        layout.addRow("Puerto COM:", self.combo_port)
        layout.addRow("Baud Rate:", self.baudrate_combo)
        
        # Conectar cambios de protocolo
        self.protocol_combo.currentTextChanged.connect(self.on_protocol_changed)
        
        self.setLayout(layout)
        
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
        return 2  # Siguiente página: Configuración avanzada


class AdvancedConfigPage(QWizardPage):
    """Página de configuración avanzada"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Paso 3: Configuración Avanzada")
        self.setSubTitle("Configure parámetros avanzados del dispositivo")
        
        layout = QVBoxLayout()
        
        # Grupo de direcciones
        address_group = QGroupBox("Direcciones de Registro")
        address_layout = QFormLayout()
        
        self.start_address = QSpinBox()
        self.start_address.setRange(0, 65535)
        self.start_address.setValue(0)
        
        self.register_count = QSpinBox()
        self.register_count.setRange(1, 125)
        self.register_count.setValue(10)
        
        address_layout.addRow("Dirección Inicial:", self.start_address)
        address_layout.addRow("Cantidad de Registros:", self.register_count)
        
        address_group.setLayout(address_layout)
        
        # Grupo de opciones
        options_group = QGroupBox("Opciones Adicionales")
        options_layout = QVBoxLayout()
        
        self.polling_check = QCheckBox("Habilitar monitoreo continuo")
        self.polling_check.setChecked(True)
        
        self.polling_interval = QSpinBox()
        self.polling_interval.setRange(100, 10000)
        self.polling_interval.setValue(1000)
        self.polling_interval.setSuffix(" ms")
        
        options_layout.addWidget(self.polling_check)
        options_layout.addWidget(QLabel("Intervalo de monitoreo:"))
        options_layout.addWidget(self.polling_interval)
        
        options_group.setLayout(options_layout)
        
        layout.addWidget(address_group)
        layout.addWidget(options_group)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def nextId(self):
        return 3  # Siguiente página: Resumen


class SummaryPage(QWizardPage):
    """Página de resumen y confirmación"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Paso 4: Resumen de Configuración")
        self.setSubTitle("Verifique la configuración antes de crear el dispositivo")
        
        layout = QVBoxLayout()
        
        # Resumen de configuración
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 10px; border-radius: 5px; }")
        
        layout.addWidget(QLabel("Resumen de la configuración:"))
        layout.addWidget(self.summary_label)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def initializePage(self):
        """Generar resumen cuando se muestra la página"""
        wizard = self.wizard()
        
        # Recopilar información de todas las páginas
        device_type = ""
        if wizard.page(1).sensor_radio.isChecked():
            device_type = "Sensor"
        elif wizard.page(1).vfd_radio.isChecked():
            device_type = "Variador de Frecuencia (VFD)"
        elif wizard.page(1).plc_radio.isChecked():
            device_type = "PLC"
        else:
            device_type = "Personalizado"
        
        protocol = wizard.page(2).protocol_combo.currentText()
        device_id = wizard.page(2).device_id_edit.text()
        
        # Generar resumen
        summary_text = f"""
        <b>Tipo de Dispositivo:</b> {device_type}<br>
        <b>Protocolo:</b> {protocol}<br>
        <b>ID del Dispositivo:</b> {device_id}<br>
        """
        
        if "TCP" in protocol:
            ip = wizard.page(2).ip_edit.text()
            port = wizard.page(2).port_spin.value()
            summary_text += f"<b>Dirección IP:</b> {ip}<br><b>Puerto:</b> {port}<br>"
        else:
            com_port = wizard.page(2).combo_port.currentText()
            baudrate = wizard.page(2).baudrate_combo.currentText()
            summary_text += f"<b>Puerto COM:</b> {com_port}<br><b>Baud Rate:</b> {baudrate}<br>"
        
        start_addr = wizard.page(3).start_address.value()
        reg_count = wizard.page(3).register_count.value()
        summary_text += f"<b>Dirección Inicial:</b> {start_addr}<br><b>Registros:</b> {reg_count}<br>"
        
        if wizard.page(3).polling_check.isChecked():
            interval = wizard.page(3).polling_interval.value()
            summary_text += f"<b>Monitoreo Continuo:</b> Sí ({interval} ms)"
        else:
            summary_text += "<b>Monitoreo Continuo:</b> No"
        
        self.summary_label.setText(summary_text)
    
    def nextId(self):
        return -1  # Última página


class DeviceWizard(QWizard):
    """Asistente paso a paso para agregar dispositivos"""
    
    device_created = Signal(dict)  # Señal cuando se crea un dispositivo
    
    def __init__(self, communication_engine, simplified=False):
        super().__init__()
        self.communication_engine = communication_engine
        self.simplified = simplified
        self.device_config = {}
        
        self.setup_wizard()
        
    def setup_wizard(self):
        self.setWindowTitle("Asistente de Configuración de Dispositivos")
        self.setWizardStyle(QWizard.ModernStyle)
        
        # Tamaño mínimo
        self.setMinimumSize(600, 400)
        
        # Páginas del asistente
        self.addPage(DeviceTypePage(self))
        
        if not self.simplified:
            self.addPage(ProtocolConfigPage(self))
            self.addPage(AdvancedConfigPage(self))
            self.addPage(SummaryPage(self))
        else:
            # Modo simplificado: combinar páginas
            self.addPage(SimplifiedConfigPage(self))
    
    def accept(self):
        """Crear dispositivo cuando se completa el asistente"""
        # Recopilar configuración
        if self.simplified:
            self.device_config = self.collect_simplified_config()
        else:
            self.device_config = self.collect_advanced_config()
        
        # Crear dispositivo usando el DeviceManager
        try:
            device = self.communication_engine.device_manager.create_device_from_template(
                template_name=self.device_config['device_type'],
                device_id=self.device_config['device_id'],
                config=self.device_config
            )
            
            # Emitir señal
            self.device_created.emit(self.device_config)
            
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"No se pudo crear el dispositivo: {str(e)}"
            )
    
    def collect_simplified_config(self):
        """Recopilar configuración en modo simplificado"""
        page = self.page(1)  # SimplifiedConfigPage
        
        return {
            'device_type': 'sensor',  # Por defecto en modo simplificado
            'device_id': page.device_id_edit.text(),
            'protocol': 'Modbus TCP',
            'config': {
                'ip': page.ip_edit.text(),
                'port': page.port_spin.value(),
                'start_address': 0,
                'register_count': 10,
                'polling_enabled': True,
                'polling_interval': 1000
            }
        }
    
    def collect_advanced_config(self):
        """Recopilar configuración en modo avanzado"""
        # Recopilar de todas las páginas
        device_type_page = self.page(1)
        protocol_page = self.page(2)
        advanced_page = self.page(3)
        
        # Determinar tipo de dispositivo
        if device_type_page.sensor_radio.isChecked():
            device_type = 'sensor'
        elif device_type_page.vfd_radio.isChecked():
            device_type = 'vfd'
        elif device_type_page.plc_radio.isChecked():
            device_type = 'plc'
        else:
            device_type = 'custom'
        
        # Configuración base
        config = {
            'device_type': device_type,
            'device_id': protocol_page.device_id_edit.text(),
            'protocol': protocol_page.protocol_combo.currentText(),
            'config': {
                'start_address': advanced_page.start_address.value(),
                'register_count': advanced_page.register_count.value(),
                'polling_enabled': advanced_page.polling_check.isChecked(),
                'polling_interval': advanced_page.polling_interval.value()
            }
        }
        
        # Configuración específica del protocolo
        protocol = protocol_page.protocol_combo.currentText()
        if "TCP" in protocol or "Ethernet" in protocol:
            config['config'].update({
                'ip': protocol_page.ip_edit.text(),
                'port': protocol_page.port_spin.value()
            })
        else:
            config['config'].update({
                'com_port': protocol_page.combo_port.currentText(),
                'baudrate': protocol_page.baudrate_combo.currentText()
            })
        
        return config


class SimplifiedConfigPage(QWizardPage):
    """Página simplificada para modo novato"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Configuración del Dispositivo")
        self.setSubTitle("Ingrese los datos básicos para su dispositivo")
        
        layout = QFormLayout()
        
        # Campos básicos
        self.device_id_edit = QLineEdit()
        self.device_id_edit.setPlaceholderText("Ej: sensor_temperatura_01")
        
        self.ip_edit = QLineEdit()
        self.ip_edit.setPlaceholderText("192.168.1.100")
        
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(502)
        
        # Agregar campos
        layout.addRow("Nombre del Dispositivo:", self.device_id_edit)
        layout.addRow("Dirección IP:", self.ip_edit)
        layout.addRow("Puerto:", self.port_spin)
        
        self.setLayout(layout)
    
    def nextId(self):
        return -1  # Finalizar wizard
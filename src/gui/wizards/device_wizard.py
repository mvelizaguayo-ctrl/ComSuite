# src/gui/wizards/device_wizard.py
import sys
from pathlib import Path

# Obtener el directorio raíz del proyecto
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QPushButton,
    QFormLayout, QGroupBox, QMessageBox, QSpinBox,
    QCheckBox, QRadioButton, QButtonGroup, QScrollArea,
    QWidget
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont

# Importación con manejo de errores
try:
    from ...config.template_manager import template_manager
    print("✅ template_manager importado correctamente en device_wizard")
except ImportError as e:
    print(f"❌ Error importando template_manager en device_wizard: {e}")
    # Crear un mock para evitar que la aplicación falle
    class MockTemplateManager:
        def get_fabricantes(self):
            return ["Error al cargar fabricantes"]
        def get_modelos_by_fabricante(self, fabricante):
            return ["Error al cargar modelos"]
        def get_template_summary(self, fabricante, modelo):
            return {"categorias": {"Control": []}}
    
    template_manager = MockTemplateManager()


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
        # Si es VFD, ir a páginas de VFD, sino a protocolo
        if self.vfd_radio.isChecked():
            return 1  # Página de fabricante VFD
        else:
            return 5  # Página de protocolo (para otros dispositivos)


class VFDFabricantePage(QWizardPage):
    """Página de selección de fabricante VFD"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Paso 2: Selección de Fabricante VFD")
        self.setSubTitle("Seleccione el fabricante del VFD")
        
        layout = QVBoxLayout()
        
        # ComboBox de fabricantes
        self.fabricante_combo = QComboBox()
        
        # Conectar señal para validar cuando cambie la selección
        self.fabricante_combo.currentTextChanged.connect(self.on_fabricante_changed)
        
        layout.addWidget(QLabel("Fabricante:"))
        layout.addWidget(self.fabricante_combo)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Registrar campo como obligatorio
        self.registerField("fabricante*", self.fabricante_combo, "currentText")
        
        print("🔧 VFDFabricantePage inicializada")
        
    def on_fabricante_changed(self, text):
        """Validar cuando se selecciona un fabricante"""
        print(f"🔄 Fabricante cambiado a: '{text}'")
        self.completeChanged.emit()
    
    def initializePage(self):
        """Cargar fabricantes cuando se muestra la página"""
        print("📖 initializePage() llamado en VFDFabricantePage")
        
        try:
            fabricantes = template_manager.get_fabricantes()
            self.fabricante_combo.clear()
            
            if fabricantes and len(fabricantes) > 0:
                self.fabricante_combo.addItems(fabricantes)
                print(f"✅ Fabricantes cargados: {len(fabricantes)}")
                print(f"📋 Lista de fabricantes: {fabricantes}")
                
                # Seleccionar el primer fabricante por defecto
                self.fabricante_combo.setCurrentIndex(0)
                primer_fabricante = self.fabricante_combo.currentText()
                print(f"🎯 Primer fabricante seleccionado: '{primer_fabricante}'")
            else:
                self.fabricante_combo.addItem("No hay fabricantes disponibles")
                print("⚠️ No hay fabricantes disponibles")
                
        except Exception as e:
            print(f"❌ Error cargando fabricantes: {e}")
            self.fabricante_combo.clear()
            self.fabricante_combo.addItem("Error: " + str(e))
    
    def isComplete(self):
        """Determinar si la página está completa"""
        current_text = self.fabricante_combo.currentText()
        is_valid = (current_text != "" and 
                   current_text != "No hay fabricantes disponibles" and 
                   current_text != "Error: " and
                   not current_text.startswith("Error:"))
        
        print(f"🔍 isComplete() llamado - Texto actual: '{current_text}', Válido: {is_valid}")
        return is_valid
    
    def nextId(self):
        print("📖 nextId() llamado en VFDFabricantePage")
        return 2  # Página de selección de modelo


class VFDModeloPage(QWizardPage):
    """Página de selección de modelo VFD"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Paso 3: Selección de Modelo VFD")
        self.setSubTitle("Seleccione el modelo del VFD")
        
        layout = QVBoxLayout()
        
        # ComboBox de modelos
        self.modelo_combo = QComboBox()
        
        # Añadir un elemento por defecto
        self.modelo_combo.addItem("Seleccione un modelo...")
        
        layout.addWidget(QLabel("Modelo:"))
        layout.addWidget(self.modelo_combo)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Registrar campo como obligatorio
        self.registerField("modelo*", self.modelo_combo, "currentText")
        
        # Conectar señal para validar cuando cambie la selección
        self.modelo_combo.currentTextChanged.connect(self.on_modelo_changed)
        
        print("🔧 VFDModeloPage inicializada")
        
    def on_modelo_changed(self, text):
        """Validar cuando se selecciona un modelo"""
        print(f"🔄 Modelo cambiado a: '{text}'")
        # Habilitar el botón Siguiente solo si no es el texto por defecto
        self.completeChanged.emit()
    
    def initializePage(self):
        """Actualizar modelos según el fabricante seleccionado"""
        fabricante = self.field("fabricante")
        print(f"🔍 Buscando modelos para fabricante: '{fabricante}'")
        
        # Guardar la selección actual si existe
        current_selection = self.modelo_combo.currentText()
        
        try:
            modelos = template_manager.get_modelos_by_fabricante(fabricante)
            self.modelo_combo.clear()
            
            # Añadir elemento por defecto
            self.modelo_combo.addItem("Seleccione un modelo...")
            
            # Añadir modelos reales
            if modelos:
                self.modelo_combo.addItems(modelos)
                print(f"✅ Modelos cargados: {len(modelos)}")
                print(f"📋 Lista de modelos: {modelos}")
                
                # Intentar restaurar la selección anterior
                index = self.modelo_combo.findText(current_selection)
                if index >= 1:  # Ignorar el elemento por defecto (índice 0)
                    self.modelo_combo.setCurrentIndex(index)
                    print(f"🎯 Selección restaurada: {current_selection}")
            else:
                self.modelo_combo.addItem("No hay modelos disponibles")
                print("⚠️ No hay modelos disponibles para este fabricante")
                
        except Exception as e:
            print(f"❌ Error cargando modelos: {e}")
            self.modelo_combo.clear()
            self.modelo_combo.addItem("Error: " + str(e))
    
    def isComplete(self):
        """Determinar si la página está completa"""
        current_text = self.modelo_combo.currentText()
        is_valid = current_text != "Seleccione un modelo..." and current_text != ""
        print(f"🔍 isComplete() llamado - Texto actual: '{current_text}', Válido: {is_valid}")
        return is_valid
    
    def nextId(self):
        print("📖 nextId() llamado")
        return 3  # Página de selección de parámetros


class VFDParametrosPage(QWizardPage):
    """Página de selección de parámetros VFD"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Paso 4: Selección de Parámetros VFD")
        self.setSubTitle("Seleccione los parámetros que desea monitorear")
        
        layout = QVBoxLayout()
        
        # Scroll area para parámetros
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # Widget contenedor
        container = QWidget()
        self.params_layout = QVBoxLayout()
        
        # Grupos de parámetros por categoría
        self.param_groups = {}
        self.param_checkboxes = {}
        
        container.setLayout(self.params_layout)
        scroll.setWidget(container)
        
        layout.addWidget(scroll)
        self.setLayout(layout)
        
        print("🔧 VFDParametrosPage inicializada")
        
    def initializePage(self):
        """Cargar parámetros según el modelo seleccionado"""
        fabricante = self.field("fabricante")
        modelo = self.field("modelo")
        print(f"🔍 Buscando parámetros para {fabricante} {modelo}")
        
        # Limpiar grupos anteriores
        for group in self.param_groups.values():
            group.setParent(None)
        self.param_groups.clear()
        self.param_checkboxes.clear()
        
        # Limpiar layout
        while self.params_layout.count():
            item = self.params_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        try:
            resumen = template_manager.get_template_summary(fabricante, modelo)
            print(f"✅ Categorías encontradas: {list(resumen['categorias'].keys())}")
            
            # Crear grupos por categoría
            for categoria, params in resumen['categorias'].items():
                print(f"📁 Procesando categoría '{categoria}' con {len(params)} parámetros")
                
                group = QGroupBox(categoria)
                group_layout = QVBoxLayout()
                
                # Añadir checkbox para "Seleccionar todos"
                select_all_checkbox = QCheckBox(f"Seleccionar todos los parámetros de {categoria}")
                select_all_checkbox.setStyleSheet("font-weight: bold;")
                group_layout.addWidget(select_all_checkbox)
                
                # Conectar señal para seleccionar/deseleccionar todos
                def make_select_all_handler(categoria_param, group_layout_param):
                    def select_all_handler(checked):
                        for i in range(1, group_layout_param.count()):  # Empezar desde 1 para saltar el "Seleccionar todos"
                            widget = group_layout_param.itemAt(i).widget()
                            if isinstance(widget, QCheckBox):
                                widget.setChecked(checked)
                    return select_all_handler
                
                select_all_checkbox.toggled.connect(make_select_all_handler(categoria, group_layout))
                
                # Añadir parámetros individuales
                for param in params:
                    checkbox = QCheckBox(f"{param['nombre']} ({param['unidad'] or 'N/A'})")
                    checkbox.setToolTip(param['descripcion'])
                    self.param_checkboxes[param['nombre']] = checkbox
                    group_layout.addWidget(checkbox)
                
                group.setLayout(group_layout)
                self.param_groups[categoria] = group
                self.params_layout.addWidget(group)
                
                # Seleccionar algunos parámetros por defecto (ej: los primeros 2 de cada categoría)
                if params:
                    for i, param in enumerate(params[:2]):
                        if param['nombre'] in self.param_checkboxes:
                            self.param_checkboxes[param['nombre']].setChecked(True)
                
        except Exception as e:
            print(f"❌ Error cargando parámetros: {e}")
            error_label = QLabel(f"Error al cargar parámetros: {str(e)}")
            self.params_layout.addWidget(error_label)
    
    def get_selected_parameters(self):
        """Obtener parámetros seleccionados"""
        selected = []
        for nombre, checkbox in self.param_checkboxes.items():
            if checkbox.isChecked():
                selected.append(nombre)
        print(f"✅ Parámetros seleccionados: {selected}")
        return selected
    
    def isComplete(self):
        """Determinar si la página está completa"""
        # La página está completa si al menos un parámetro está seleccionado
        selected_count = sum(1 for checkbox in self.param_checkboxes.values() if checkbox.isChecked())
        is_complete = selected_count > 0
        print(f"🔍 Página de parámetros completa: {is_complete} ({selected_count} parámetros seleccionados)")
        return is_complete
    
    def nextId(self):
        print("📖 nextId() llamado en VFDParametrosPage")
        return 4  # Página de configuración de conexión


class VFDConnectionConfigPage(QWizardPage):
    """Página de configuración de conexión para VFD"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Paso 5: Configuración de Conexión VFD")
        self.setSubTitle("Configure los parámetros de comunicación")

        layout = QFormLayout()

        # Selección de modo Modbus (TCP/RTU)
        self.modbus_mode_combo = QComboBox()
        self.modbus_mode_combo.addItems(["Modbus TCP", "Modbus RTU"])
        self.modbus_mode_combo.setCurrentIndex(0)

        # Configuración TCP
        self.ip_edit = QLineEdit()
        self.ip_edit.setPlaceholderText("192.168.1.100")
        self.ip_edit.setText("192.168.1.100")  # Valor por defecto

        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(502)  # Valor por defecto

        # Configuración RTU
        self.combo_port = QComboBox()
        self.combo_port.addItems(["COM1", "COM2", "COM3", "COM4"])

        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200"])

        # Agregar campos al formulario
        layout.addRow("Modo Modbus:", self.modbus_mode_combo)
        layout.addRow("Dirección IP:", self.ip_edit)
        layout.addRow("Puerto:", self.port_spin)
        layout.addRow("Puerto COM:", self.combo_port)
        layout.addRow("Baud Rate:", self.baudrate_combo)

        # Opción: requerir conexión antes de finalizar
        self.require_connection_cb = QCheckBox("Requerir conexión antes de finalizar")
        self.require_connection_cb.setChecked(False)
        layout.addRow(self.require_connection_cb)

        self.setLayout(layout)

        # Registrar campos
        self.registerField("modbus_mode", self.modbus_mode_combo)
        self.registerField("ip*", self.ip_edit)
        self.registerField("port*", self.port_spin)
        self.registerField("com_port*", self.combo_port)
        self.registerField("baudrate*", self.baudrate_combo)

        # Conectar señales para validación y visibilidad dinámica
        self.ip_edit.textChanged.connect(self.validate_fields)
        self.port_spin.valueChanged.connect(self.validate_fields)
        self.modbus_mode_combo.currentTextChanged.connect(self.on_mode_changed)

        print("🔧 VFDConnectionConfigPage inicializada")
        
    def validate_fields(self):
        """Validar campos y actualizar estado de la página"""
        self.completeChanged.emit()
        print("🔄 Validación de campos llamada")

    def on_mode_changed(self, text):
        """Actualizar visibilidad cuando el modo Modbus cambia"""
        is_tcp = 'TCP' in text
        self.ip_edit.setVisible(is_tcp)
        self.port_spin.setVisible(is_tcp)
        self.combo_port.setVisible(not is_tcp)
        self.baudrate_combo.setVisible(not is_tcp)
        # Forzar recalculo del layout/completeChanged
        self.completeChanged.emit()
    
    def initializePage(self):
        """Mostrar/ocultar campos según el protocolo"""
        print("📖 initializePage() llamado en VFDConnectionConfigPage")
        # Determinar visibilidad según selección de modo Modbus
        mode = self.modbus_mode_combo.currentText() if hasattr(self, 'modbus_mode_combo') else 'Modbus TCP'
        is_tcp = 'TCP' in mode
        is_rtu = not is_tcp
        
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
    
    def isComplete(self):
        """Determinar si la página está completa"""
        ip_text = self.ip_edit.text().strip()
        port_value = self.port_spin.value()
        
        # Validar que IP no esté vacía y puerto sea válido
        is_valid = (ip_text != "" and port_value > 0)
        
        print(f"🔍 Página de conexión completa: {is_valid} (IP: '{ip_text}', Puerto: {port_value})")
        return is_valid
    
    def nextId(self):
        print("📖 nextId() llamado en VFDConnectionConfigPage")
        return -1  # Finalizar wizard


# Páginas originales para otros dispositivos
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
        return 6  # Siguiente página: Configuración avanzada


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
        return 7  # Siguiente página: Resumen


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
    
# src/gui/wizards/device_wizard.py
# Reemplazar solo el método initializePage de SummaryPage

# src/gui/wizards/device_wizard.py
# Reemplazar solo el método initializePage de SummaryPage

    def initializePage(self):
        """Generar resumen cuando se muestra la página"""
        wizard = self.wizard()
        
        # Acceder directamente a las páginas por índice conocido
        device_type_page = wizard.page(0)  # DeviceTypePage
        
        # Recopilar información de todas las páginas
        device_type = ""
        if device_type_page.vfd_radio.isChecked():
            device_type = "Variador de Frecuencia (VFD)"
        elif device_type_page.sensor_radio.isChecked():
            device_type = "Sensor"
        elif device_type_page.plc_radio.isChecked():
            device_type = "PLC"
        else:
            device_type = "Personalizado"
        
        # Generar resumen según el tipo de dispositivo
        if device_type_page.vfd_radio.isChecked():
            # Resumen para VFD
            fabricante = wizard.field("fabricante")
            modelo = wizard.field("modelo")
            
            summary_text = f"""
            <b>Tipo de Dispositivo:</b> {device_type}<br>
            <b>Fabricante:</b> {fabricante}<br>
            <b>Modelo:</b> {modelo}<br>
            """
            
            # Obtener parámetros seleccionados - accedemos directamente por índice
            parametros_page = wizard.page(3)  # VFDParametrosPage está en índice 3
            if parametros_page and hasattr(parametros_page, 'get_selected_parameters'):
                selected_params = parametros_page.get_selected_parameters()
                if selected_params:
                    summary_text += f"<b>Parámetros Seleccionados:</b> {', '.join(selected_params[:5])}"
                    if len(selected_params) > 5:
                        summary_text += f" (+{len(selected_params)-5} más)"
                    summary_text += "<br>"
            
            # Configuración de conexión
            ip = wizard.field("ip")
            port = wizard.field("port")
            if ip:
                summary_text += f"<b>Dirección IP:</b> {ip}<br><b>Puerto:</b> {port}<br>"
            
        else:
            # Resumen para otros dispositivos
            protocol_page = wizard.page(5)  # ProtocolConfigPage
            device_id = protocol_page.device_id_edit.text()
            
            summary_text = f"""
            <b>Tipo de Dispositivo:</b> {device_type}<br>
            <b>Protocolo:</b> {protocol_page.protocol_combo.currentText()}<br>
            <b>ID del Dispositivo:</b> {device_id}<br>
            """
            
            if "TCP" in protocol_page.protocol_combo.currentText():
                ip = protocol_page.ip_edit.text()
                port = protocol_page.port_spin.value()
                summary_text += f"<b>Dirección IP:</b> {ip}<br><b>Puerto:</b> {port}<br>"
            else:
                com_port = protocol_page.combo_port.currentText()
                baudrate = protocol_page.baudrate_combo.currentText()
                summary_text += f"<b>Puerto COM:</b> {com_port}<br><b>Baud Rate:</b> {baudrate}<br>"
            
            advanced_page = wizard.page(6)  # AdvancedConfigPage
            start_addr = advanced_page.start_address.value()
            reg_count = advanced_page.register_count.value()
            summary_text += f"<b>Dirección Inicial:</b> {start_addr}<br><b>Registros:</b> {reg_count}<br>"
            
            if advanced_page.polling_check.isChecked():
                interval = advanced_page.polling_interval.value()
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
        if self.simplified:
            # Modo simplificado: solo mostrar la página simplificada
            self.addPage(SimplifiedConfigPage(self))
            return

        # Flujo completo para modo avanzado
        self.addPage(DeviceTypePage(self))      # 0

        # Páginas para VFD
        self.addPage(VFDFabricantePage(self))   # 1
        self.addPage(VFDModeloPage(self))       # 2
        self.addPage(VFDParametrosPage(self))    # 3
        self.addPage(VFDConnectionConfigPage(self))  # 4

        # Páginas para otros dispositivos
        self.addPage(ProtocolConfigPage(self))   # 5
        self.addPage(AdvancedConfigPage(self))   # 6
        self.addPage(SummaryPage(self))          # 7
    
    def accept(self):
        """Crear dispositivo cuando se completa el asistente"""
        # Recopilar configuración
        if self.simplified:
            self.device_config = self.collect_simplified_config()
        else:
            self.device_config = self.collect_advanced_config()
        # Si se pidió requerir conexión, validar conectividad antes de emitir
        try:
            require_conn = False
            # comprobar en páginas VFD o avanzadas
            page_conn = None
            try:
                page_conn = self.page(4)  # VFDConnectionConfigPage está en índice 4
            except Exception:
                page_conn = None

            if page_conn and hasattr(page_conn, 'require_connection_cb'):
                require_conn = page_conn.require_connection_cb.isChecked()

            if require_conn:
                # Intentar conectar usando ModbusProtocol (forma mínima)
                try:
                    from ...protocols.modbus.modbus_protocol import ModbusProtocol

                    # Construir config simple (asumir master TCP)
                    cfg = self.device_config
                    protocol_cfg = {
                        'mode': 'master',
                        'protocol_type': 'TCP',
                    }
                    if 'config' in cfg and isinstance(cfg['config'], dict):
                        c = cfg['config']
                        if 'ip' in c and 'port' in c:
                            protocol_cfg.update({'ip': c['ip'], 'port': c['port']})

                    proto = ModbusProtocol()
                    ok = proto.connect(protocol_cfg)
                    if not ok:
                        QMessageBox.critical(self, "Conexión fallida", "No se pudo establecer conexión Modbus con la configuración proporcionada. Revise IP/PUERTO y vuelva a intentarlo.")
                        return
                    else:
                        # desconectar rápido (validación pasada)
                        try:
                            proto.disconnect()
                        except Exception:
                            pass
                except Exception as e:
                    QMessageBox.critical(self, "Error de validación", f"Error al validar la conexión: {e}")
                    return

        except Exception:
            # Si algo sale mal al leer la checkbox, no bloquear la creación
            pass

        # Emitir señal
        self.device_created.emit(self.device_config)

        super().accept()
    
    def collect_advanced_config(self):
        """Recopilar configuración en modo avanzado"""
        # Recopilar de todas las páginas
        device_type_page = self.page(0)
        
        # Determinar tipo de dispositivo
        if device_type_page.vfd_radio.isChecked():
            device_type = 'vfd'
            return self.collect_vfd_config()
        elif device_type_page.sensor_radio.isChecked():
            device_type = 'sensor'
        elif device_type_page.plc_radio.isChecked():
            device_type = 'plc'
        else:
            device_type = 'custom'
        
        # Configuración para dispositivos no VFD
        protocol_page = self.page(5)
        advanced_page = self.page(6)
        
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
    
# src/gui/wizards/device_wizard.py
# Reemplazar solo el método collect_vfd_config

    def collect_vfd_config(self):
        """Recopilar configuración para VFD"""
        fabricante = self.field("fabricante")
        modelo = self.field("modelo")
        
        # Obtener parámetros seleccionados - accedemos directamente por índice
        selected_params = []
        parametros_page = self.page(3)  # Sabemos que VFDParametrosPage está en índice 3
        if parametros_page and hasattr(parametros_page, 'get_selected_parameters'):
            selected_params = parametros_page.get_selected_parameters()
        
        config = {
            'device_type': 'vfd',
            'fabricante': fabricante,
            'modelo': modelo,
            'parametros': selected_params,
            'protocol': 'Modbus TCP',  # Por defecto, será actualizado según selección
            'config': {
                'ip': self.field("ip"),
                'port': self.field("port"),
                'polling_enabled': True,
                'polling_interval': 1000
            }
        }
        # Intentar leer el modo Modbus desde la página de conexión si está presente
        try:
            conn_page = self.page(4)
            if hasattr(conn_page, 'modbus_mode_combo'):
                mode = conn_page.modbus_mode_combo.currentText()
                config['protocol'] = mode
                # Si RTU, tomar puerto COM/baud
                if 'RTU' in mode:
                    config['config'].pop('ip', None)
                    config['config'].pop('port', None)
                    config['config'].update({
                        'com_port': conn_page.combo_port.currentText(),
                        'baudrate': conn_page.baudrate_combo.currentText()
                    })
        except Exception:
            pass
        return config
    
    
    def collect_simplified_config(self):
        """Recopilar configuración en modo simplificado"""
        # Buscar dinámicamente la página simplificada (no asumimos índice)
        page = None
        # QWizard no expone pageCount(), usar pageIds() para iterar
        try:
            ids = self.pageIds()
        except Exception:
            ids = []

        for pid in ids:
            p = self.page(pid)
            if hasattr(p, 'device_id_edit') and hasattr(p, 'ip_edit'):
                page = p
                break

        if page is None:
            # Fallback: devolver valores por defecto
            return {
                'device_type': 'sensor',
                'device_id': 'sensor_1',
                'protocol': 'Modbus TCP',
                'config': {
                    'ip': '127.0.0.1',
                    'port': 502,
                    'start_address': 0,
                    'register_count': 10,
                    'polling_enabled': True,
                    'polling_interval': 1000
                }
            }

        # Leer selección de modo Modbus desde la página simplificada
        protocol = 'Modbus TCP'
        try:
            if hasattr(page, 'modbus_mode_combo'):
                protocol = page.modbus_mode_combo.currentText()
        except Exception:
            pass

        cfg = {
            'device_type': 'sensor',  # Por defecto en modo simplificado
            'device_id': page.device_id_edit.text(),
            'protocol': protocol,
            'config': {
                'ip': page.ip_edit.text(),
                'port': page.port_spin.value(),
                'start_address': 0,
                'register_count': 10,
                'polling_enabled': True,
                'polling_interval': 1000
            }
        }

        # Si el modo es RTU, ajustar campos
        if 'RTU' in protocol:
            cfg['config'].pop('ip', None)
            cfg['config'].pop('port', None)
            # No tenemos selección de COM en simplificado; dejar campos vacíos o defaults
            cfg['config'].update({'com_port': '', 'baudrate': '9600'})

        return cfg


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
        # Selector modo Modbus (simplificado)
        self.modbus_mode_combo = QComboBox()
        self.modbus_mode_combo.addItems(["Modbus TCP", "Modbus RTU"])
        self.modbus_mode_combo.setCurrentIndex(0)

        layout.addRow("Nombre del Dispositivo:", self.device_id_edit)
        layout.addRow("Modo Modbus:", self.modbus_mode_combo)
        layout.addRow("Dirección IP:", self.ip_edit)
        layout.addRow("Puerto:", self.port_spin)

        # Registrar campos para validación del wizard
        self.registerField("simpl_device_id*", self.device_id_edit, "text")
        self.registerField("simpl_modbus_mode", self.modbus_mode_combo)
        self.registerField("simpl_ip*", self.ip_edit, "text")
        self.registerField("simpl_port", self.port_spin)

        self.setLayout(layout)
    
    def nextId(self):
        return -1  # Finalizar wizard
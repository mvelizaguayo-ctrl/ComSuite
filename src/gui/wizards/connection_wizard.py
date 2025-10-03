# src/gui/wizards/connection_wizard.py
import sys
import os
from pathlib import Path

# Obtener el directorio raíz del proyecto de manera robusta
try:
    # Método 1: Desde el archivo actual
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    
    # Verificar que existe el directorio src
    if not (project_root / "src").exists():
        # Método 2: Buscar hacia arriba hasta encontrar el directorio raíz
        current_dir = current_file.parent
        while current_dir != current_dir.parent and not (current_dir / "src" / "config" / "template_manager.py").exists():
            current_dir = current_dir.parent
        project_root = current_dir
    
    # Añadir al path
    sys.path.insert(0, str(project_root))
    
    # Depuración
    print(f"Directorio raíz del proyecto: {project_root}")
    print(f"sys.path[0]: {sys.path[0]}")
    
except Exception as e:
    print(f"Error al calcular ruta: {e}")
    # Usar ruta relativa como fallback
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from PySide6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QPushButton,
    QFormLayout, QGroupBox, QMessageBox, QSpinBox,
    QListWidget, QListWidgetItem, QCheckBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

# Importación con manejo de errores y depuración
try:
    from ...config.template_manager import template_manager
    print("✅ template_manager importado correctamente")
except ImportError as e:
    print(f"❌ Error importando template_manager: {e}")
    # Crear un mock para evitar que la aplicación falle
    class MockTemplateManager:
        def get_fabricantes(self):
            return ["Error al cargar fabricantes"]
        def get_modelos_by_fabricante(self, fabricante):
            return ["Error al cargar modelos"]
        def get_template_summary(self, fabricante, modelo):
            return {"categorias": {"Control": []}}
    
    template_manager = MockTemplateManager()


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
            "VFD Modbus TCP",
            "VFD Modbus RTU", 
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
        # Si es VFD, ir a selección de fabricante, sino a configuración
        if "VFD" in self.field("protocol"):
            return 1  # Página de selección de fabricante
        else:
            return 4  # Saltar directamente a configuración


class VFDFabricantePage(QWizardPage):
    """Página de selección de fabricante VFD"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Paso 2: Selección de Fabricante")
        self.setSubTitle("Seleccione el fabricante del VFD")
        
        layout = QVBoxLayout()
        
        # ComboBox de fabricantes
        self.fabricante_combo = QComboBox()
        
        # Cargar fabricantes desde template_manager
        try:
            fabricantes = template_manager.get_fabricantes()
            self.fabricante_combo.addItems(fabricantes)
            print(f"✅ Fabricantes cargados: {len(fabricantes)}")
        except Exception as e:
            print(f"❌ Error cargando fabricantes: {e}")
            self.fabricante_combo.addItem("Error: " + str(e))
        
        layout.addWidget(QLabel("Fabricante:"))
        layout.addWidget(self.fabricante_combo)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Registrar campo
        self.registerField("fabricante*", self.fabricante_combo, "currentText")
        
    def nextId(self):
        return 2  # Página de selección de modelo


class VFDModeloPage(QWizardPage):
    """Página de selección de modelo VFD"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Paso 3: Selección de Modelo")
        self.setSubTitle("Seleccione el modelo del VFD")
        
        layout = QVBoxLayout()
        
        # ComboBox de modelos
        self.modelo_combo = QComboBox()
        
        layout.addWidget(QLabel("Modelo:"))
        layout.addWidget(self.modelo_combo)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Registrar campo
        self.registerField("modelo*", self.modelo_combo, "currentText")
        
    def initializePage(self):
        """Actualizar modelos según el fabricante seleccionado"""
        fabricante = self.field("fabricante")
        print(f"🔍 Buscando modelos para fabricante: {fabricante}")
        
        try:
            modelos = template_manager.get_modelos_by_fabricante(fabricante)
            self.modelo_combo.clear()
            self.modelo_combo.addItems(modelos)
            print(f"✅ Modelos cargados: {len(modelos)}")
        except Exception as e:
            print(f"❌ Error cargando modelos: {e}")
            self.modelo_combo.clear()
            self.modelo_combo.addItem("Error: " + str(e))
    
    def nextId(self):
        return 3  # Página de selección de parámetros


class VFDParametrosPage(QWizardPage):
    """Página de selección de parámetros VFD"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Paso 4: Selección de Parámetros")
        self.setSubTitle("Seleccione los parámetros que desea monitorear")
        
        layout = QVBoxLayout()
        
        # Scroll area para parámetros
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # Widget contenedor
        container = QWidget()
        params_layout = QVBoxLayout()
        
        # Grupos de parámetros por categoría
        self.param_groups = {}
        self.param_checkboxes = {}
        
        container.setLayout(params_layout)
        scroll.setWidget(container)
        
        layout.addWidget(scroll)
        self.setLayout(layout)
        
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
        
        try:
            resumen = template_manager.get_template_summary(fabricante, modelo)
            print(f"✅ Categorías encontradas: {list(resumen['categorias'].keys())}")
            
            # Crear grupos por categoría
            for categoria, params in resumen['categorias'].items():
                group = QGroupBox(categoria)
                group_layout = QVBoxLayout()
                
                for param in params:
                    checkbox = QCheckBox(f"{param['nombre']} ({param['unidad'] or 'N/A'})")
                    checkbox.setToolTip(param['descripcion'])
                    self.param_checkboxes[param['nombre']] = checkbox
                    group_layout.addWidget(checkbox)
                
                group.setLayout(group_layout)
                self.param_groups[categoria] = group
                self.layout().addWidget(group)
                
        except Exception as e:
            print(f"❌ Error cargando parámetros: {e}")
            error_label = QLabel(f"Error al cargar parámetros: {str(e)}")
            self.layout().addWidget(error_label)
    
    def get_selected_parameters(self):
        """Obtener parámetros seleccionados"""
        selected = []
        for nombre, checkbox in self.param_checkboxes.items():
            if checkbox.isChecked():
                selected.append(nombre)
        return selected
    
    def nextId(self):
        return 4  # Página de configuración


class ConnectionConfigPage(QWizardPage):
    """Página de configuración de la conexión"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Paso 5: Configuración de Conexión")
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
        is_tcp = "TCP" in protocol
        is_rtu = "RTU" in protocol
        
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
        self.setMinimumSize(600, 400)
        
        # Páginas del asistente en orden correcto
        self.addPage(ConnectionTypePage(self))    # 0
        self.addPage(VFDFabricantePage(self))    # 1
        self.addPage(VFDModeloPage(self))        # 2
        self.addPage(VFDParametrosPage(self))     # 3
        self.addPage(ConnectionConfigPage(self))  # 4
        
    def accept(self):
        """Recopilar configuración cuando se completa el asistente"""
        config = {
            'protocol': self.field("protocol"),
            'ip': self.field("ip"),
            'port': self.field("port"),
            'com_port': self.field("com_port"),
            'baudrate': self.field("baudrate")
        }
        
        # Añadir información de plantilla si es VFD
        if self.field("fabricante") and self.field("modelo"):
            config.update({
                'fabricante': self.field("fabricante"),
                'modelo': self.field("modelo")
            })
            
            # Obtener parámetros seleccionados
            for page in self.pages():
                if isinstance(page, VFDParametrosPage):
                    config['parametros'] = page.get_selected_parameters()
                    break
        
        print(f"📋 Configuración final: {config}")
        
        # Emitir señal con la configuración
        self.connection_configured.emit(config)
        
        super().accept()
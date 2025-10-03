from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QListWidget, QListWidgetItem, QFrame,
    QMessageBox, QSizePolicy  # <-- MOVER AQUÍ
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon, QFont

from ..wizards.device_wizard import DeviceWizard
from ..wizards.other_registers_wizard import OtherRegistersWizard
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
        
        # Frame para borde
        self.frame = QFrame()
        self.frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        
        # Layout dentro del frame
        layout = QVBoxLayout(self.frame)
        
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
        self.device_panel.setMinimumHeight(150)  # Altura mínima
        
        # Botón grande para agregar dispositivos
        self.add_device_btn = QPushButton("Agregar Nuevo Dispositivo")
        self.add_device_btn.setIcon(QIcon("icons/add_device.png"))
        self.add_device_btn.setFixedHeight(60)
        self.add_device_btn.setMinimumWidth(200)  # Ancho mínimo
        self.add_device_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_device_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        # Monitor de datos simplificado
        self.data_monitor = SimpleDataMonitor()

        # Botón para "Otros" registros
        self.other_btn = QPushButton("Otros")
        self.other_btn.setFixedHeight(40)

        # Agregar widgets al layout
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(self.device_panel)
        layout.addWidget(self.add_device_btn)
        layout.addWidget(self.other_btn)
        layout.addWidget(self.data_monitor)
        
        # Configurar espaciado
        layout.setSpacing(20)  # Espacio entre widgets
        layout.setContentsMargins(25, 25, 25, 25)  # Márgenes del contenedor
        
        # Agregar el frame al layout principal
        main_layout.addWidget(self.frame)
        
        # Configurar políticas de tamaño
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
    def setup_connections(self):
        self.add_device_btn.clicked.connect(self.show_device_wizard)
        self.other_btn.clicked.connect(self.show_other_wizard)
        self.device_panel.device_selected.connect(self.on_device_selected)
        
    def show_device_wizard(self):
        """Mostrar asistente simplificado para agregar dispositivos"""
        # Abrir el asistente completo (mismo comportamiento que modo experto)
        wizard = DeviceWizard(self.communication_engine, simplified=False)
        wizard.device_created.connect(self.on_device_created)
        wizard.exec_()
        
    def on_device_created(self, device_info):
        """Manejar creación de nuevo dispositivo"""
        # Crear el dispositivo en el DeviceManager central
        try:
            dm = self.communication_engine.device_manager
            device = dm.create_device_from_template(device_info)

            if device is None:
                # Intentar crear UI igual con la info del wizard si falla la creación
                self.device_panel.add_device(device_info)
                QMessageBox.warning(self, "Atención", "El dispositivo fue agregado a la lista, pero no se pudo crear en el gestor (ver logs).")
                return

            # Añadir al panel la representación mínima requerida
            ui_info = {'device_id': device.device_id, 'protocol': getattr(device, 'protocol_name', 'Desconocido')}
            self.device_panel.add_device(ui_info)
            self.device_added.emit(device.device_id)
            # Intentar conectar automáticamente el dispositivo recién creado
            try:
                connected = self.communication_engine.device_manager.connect_device(device.device_id)
                if connected:
                    # Emitir señal para actualizar UI
                    self.communication_engine.device_connected.emit(device.device_id)
                else:
                    self.communication_engine.device_disconnected.emit(device.device_id)
            except Exception:
                pass

            QMessageBox.information(self, "Dispositivo Agregado", f"El dispositivo {device.device_id} ha sido agregado correctamente.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo agregar el dispositivo: {e}")
            raise
        
    def on_device_selected(self, device_id):
        """Manejar selección de dispositivo"""
        # Si el device existe en el DeviceManager, pasar el objeto junto al id
        try:
            dm = self.communication_engine.device_manager
            device_obj = dm.get_device(device_id)
            if device_obj is not None:
                # Pasamos una tupla (id, objeto) para que el monitor muestre registros
                self.data_monitor.set_device((device_id, device_obj))
                return
        except Exception:
            pass

        # Fallback: pasar solo el id
        self.data_monitor.set_device(device_id)

    def show_other_wizard(self):
        wiz = OtherRegistersWizard(self)
        wiz.registers_created.connect(self._on_registers_created)
        wiz.exec_()

    def _on_registers_created(self, regs, cfg):
        # Añadir cada registro como un ítem en el panel simplificado
            # Persistir cada registro como un dispositivo/entrada en el DeviceManager
            dm = None
            try:
                dm = self.communication_engine.device_manager
            except Exception:
                dm = None

            # Crear un único dispositivo que agrupe todos los registros
            device_name = cfg.get('device_name') or f"regs_{len(dm.get_all_devices())+1 if dm else '1'}"
            device_id = device_name

            template = {
                'device_type': 'register_group',
                'device_id': device_id,
                'protocol': cfg.get('protocol', 'Modbus TCP'),
                'config': {
                    'ip': cfg.get('ip'),
                    'port': cfg.get('port'),
                    'com_port': cfg.get('com_port'),
                    'baudrate': cfg.get('baudrate')
                },
                # Lista de registros
                'registers': regs
            }

            created = None
            try:
                if dm is not None:
                    created = dm.create_device_from_template(template)
            except Exception:
                created = None

            if created is None:
                # Fallback: añadir cada registro como UI básico
                for r in regs:
                    ui_info = {'device_id': f"reg_{r['function']}_{r['address']}", 'protocol': cfg.get('protocol')}
                    self.device_panel.add_device(ui_info)
            else:
                # Guardar la lista de registros en el objeto creado
                try:
                    if not hasattr(created, 'registers'):
                        created.registers = []
                    # regs ya es una lista de dicts
                    created.registers.extend(regs)
                except Exception:
                    pass

                # Añadir al panel
                try:
                    self.add_device_to_panel(created)
                except Exception:
                    ui_info = {'device_id': device_id, 'protocol': cfg.get('protocol')}
                    self.device_panel.add_device(ui_info)

    def add_device_to_panel(self, device):
        """Compatibilidad: recibir un DeviceInterface y añadirlo al panel UI."""
        try:
            ui_info = {'device_id': device.device_id, 'protocol': getattr(device, 'protocol_name', 'Desconocido')}
            self.device_panel.add_device(ui_info)
        except Exception:
            pass
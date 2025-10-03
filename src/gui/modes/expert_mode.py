from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QFrame, QSizePolicy  # <-- MOVER AQUÍ
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ..panels.device_panel import DevicePanel
from ..panels.connection_panel import ConnectionPanel
from ..panels.data_monitor import DataMonitor
from ..panels.log_viewer import LogViewer
from ..wizards.other_registers_wizard import OtherRegistersWizard
from PySide6.QtWidgets import QPushButton


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
        # Botón rápido para 'Otros' (registros)
        self.other_btn = QPushButton("Otros")
        self.other_btn.setFixedHeight(30)
        left_panel.addWidget(self.other_btn)
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
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        right_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
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
        
        # Configurar políticas de tamaño
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
    def setup_connections(self):
        # Conectar señales entre componentes
        self.device_panel.device_selected.connect(self.data_monitor.set_device)
        self.device_panel.device_selected.connect(self.log_viewer.set_device)
        self.connection_panel.connection_status_changed.connect(self.log_viewer.log_connection)
        # Conectar boton 'Otros'
        try:
            self.other_btn.clicked.connect(self._open_other_wizard)
        except Exception:
            pass

    def _open_other_wizard(self):
        wiz = OtherRegistersWizard(self)
        wiz.registers_created.connect(self._on_registers_created)
        wiz.exec_()

    def _on_registers_created(self, regs, cfg):
        # Reusar la lógica que crea un solo dispositivo agrupando registros
        dm = None
        try:
            dm = self.communication_engine.device_manager
        except Exception:
            dm = None

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
            'registers': regs
        }

        created = None
        try:
            if dm is not None:
                created = dm.create_device_from_template(template)
        except Exception:
            created = None

        if created is None:
            # Fallback UI: añadir cada registro como item básico
            for r in regs:
                ui_info = {'device_id': f"reg_{r['function']}_{r['address']}", 'protocol': cfg.get('protocol')}
                try:
                    self.device_panel.add_device_item(ui_info)
                except Exception:
                    pass
        else:
            try:
                if not hasattr(created, 'registers'):
                    created.registers = []
                created.registers.extend(regs)
            except Exception:
                pass

            try:
                self.add_device_to_panel(created)
            except Exception:
                ui_info = {'device_id': device_id, 'protocol': cfg.get('protocol')}
                try:
                    self.device_panel.add_device_item(ui_info)
                except Exception:
                    pass

    def add_device_to_panel(self, device):
        """Compatibilidad: añadir dispositivo al panel experto."""
        try:
            ui_info = {'device_id': device.device_id, 'protocol': getattr(device, 'protocol_name', 'Desconocido')}
            self.device_panel.add_device_item(ui_info)
        except Exception:
            pass
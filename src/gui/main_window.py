from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QStatusBar, QMenuBar, QMenu, 
    QMessageBox, QLabel, QComboBox, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QAction

from .modes.expert_mode import ExpertMode
from .style_manager import StyleManager


class MainWindow(QMainWindow):
    
    mode_changed = Signal(str)
    
    def __init__(self, communication_engine):
        super().__init__()
        self.communication_engine = communication_engine
        self.current_mode = None
        self.style_manager = StyleManager()
        
        self.setup_ui()
        self.setup_connections()
        self.setup_menu()
        self.apply_styles()
        
    def setup_ui(self):
        self.setWindowTitle("ComSuite Professional Communication Suite")
        self.setMinimumSize(1200, 800)

        # Widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)

        # Selector de modo (únicamente Experto por ahora)
        mode_selector_layout = QHBoxLayout()
        mode_label = QLabel("Modo de operación:")

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Modo Experto")
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)

        mode_selector_layout.addWidget(mode_label)
        mode_selector_layout.addWidget(self.mode_combo)
        mode_selector_layout.addStretch()

        # Stacked widget
        self.stacked_widget = QStackedWidget()

        # Crear y añadir modo experto (único modo activo)
        self.expert_mode = ExpertMode(self.communication_engine)
        self.stacked_widget.addWidget(self.expert_mode)

        # Layout principal
        main_layout.addLayout(mode_selector_layout)
        main_layout.addWidget(self.stacked_widget)

        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Establecer estado inicial (Modo Experto)
        self.mode_combo.setCurrentText("Modo Experto")
        self.stacked_widget.setCurrentWidget(self.expert_mode)
        self.current_mode = "expert"
        self.status_bar.showMessage("Modo Experto activado")
        
    def setup_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Archivo")
        file_menu.addAction("Nuevo Proyecto", self.new_project, "Ctrl+N")
        file_menu.addAction("Abrir Proyecto", self.open_project, "Ctrl+O")
        file_menu.addAction("Guardar Proyecto", self.save_project, "Ctrl+S")
        file_menu.addSeparator()
        file_menu.addAction("Salir", self.close, "Ctrl+Q")
        
        devices_menu = menubar.addMenu("Dispositivos")
        devices_menu.addAction("Agregar Dispositivo", self.add_device, "Ctrl+D")
        devices_menu.addAction("Otros (Registros)", self.open_other_registers_wizard)
        
        view_menu = menubar.addMenu("Vista")
        view_menu.addAction("Cambiar Tema", self.change_theme)
        
        help_menu = menubar.addMenu("Ayuda")
        help_menu.addAction("Acerca de", self.show_about)
        
    def setup_connections(self):
        self.communication_engine.protocol_loaded.connect(self.on_protocol_loaded)
        self.communication_engine.device_connected.connect(self.on_device_connected)
        self.communication_engine.device_disconnected.connect(self.on_device_disconnected)
        
    def apply_styles(self):
        """Aplicar estilos CSS"""
        try:
            print("Aplicando estilos CSS...")
            self.style_manager.apply_style(self)
            print("Estilos CSS aplicados")
        except Exception as e:
            print(f"Error aplicando estilos CSS: {e}")
        
    def on_mode_changed(self, mode_text):
        print(f"Cambio de modo detectado: {mode_text}")
        # Solo Modo Experto disponible actualmente
        if mode_text == "Modo Experto":
            self.stacked_widget.setCurrentWidget(self.expert_mode)
            self.current_mode = "expert"
            self.status_bar.showMessage("Modo Experto activado")
            print("Activado Modo Experto")
        
        self.mode_changed.emit(self.current_mode)
        
    def on_protocol_loaded(self, protocol_name):
        self.status_bar.showMessage(f"Protocolo {protocol_name} cargado correctamente", 3000)
        
    def on_device_connected(self, device_id):
        self.status_bar.showMessage(f"Dispositivo {device_id} conectado", 3000)
        
    def on_device_disconnected(self, device_id):
        self.status_bar.showMessage(f"Dispositivo {device_id} desconectado", 3000)

    def open_other_registers_wizard(self):
        from .wizards.other_registers_wizard import OtherRegistersWizard
        wiz = OtherRegistersWizard(self)
        # Reusar lógica similar a la de ExpertMode
        def _on_regs(regs, cfg):
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

            try:
                if dm is not None:
                    created = dm.create_device_from_template(template)
                    if created is not None:
                        try:
                            if not hasattr(created, 'registers'):
                                created.registers = []
                            created.registers.extend(regs)
                        except Exception:
                            pass
                        try:
                            self.expert_mode.add_device_to_panel(created)
                        except Exception:
                            pass
                        return
            except Exception:
                pass

            # fallback: add simple UI items
            for r in regs:
                ui_info = {'device_id': f"reg_{r['function']}_{r['address']}", 'protocol': cfg.get('protocol')}
                try:
                    self.expert_mode.device_panel.add_device_item(ui_info)
                except Exception:
                    pass

        wiz.registers_created.connect(_on_regs)
        wiz.exec_()
        
    def new_project(self):
        QMessageBox.information(self, "Nuevo Proyecto", "Funcionalidad de nuevo proyecto en desarrollo")
        
    def open_project(self):
        QMessageBox.information(self, "Abrir Proyecto", "Funcionalidad de abrir proyecto en desarrollo")
        
    def save_project(self):
        QMessageBox.information(self, "Guardar Proyecto", "Funcionalidad de guardar proyecto en desarrollo")
        
    def add_device(self):
        from .wizards.device_wizard import DeviceWizard

        # Siempre abrir el wizard en modo completo (experto)
        wizard = DeviceWizard(self.communication_engine, simplified=False)

        # Conectar la señal para manejar la creación del dispositivo
        wizard.device_created.connect(self.on_device_created)

        print("🧪 Abriendo wizard para agregar dispositivo...")
        result = wizard.exec()
        print(f"📊 Wizard ejecutado con resultado: {result}")

# src/gui/main_window.py
# Reemplazar el método on_device_created

# src/gui/main_window.py
# Reemplazar el método on_device_created

# src/gui/main_window.py
# Reemplazar temporalmente el método on_device_created para diagnóstico

# src/gui/main_window.py - Método on_device_created simplificado
    def on_device_created(self, device_config):
        """Manejar la creación de un nuevo dispositivo"""
        print(f"🎯 on_device_created llamado con config: {device_config}")
        
        try:
            # Crear dispositivo usando el DeviceManager
            dm = self.communication_engine.device_manager
            
            # Usar el nuevo método create_vfd_device
            device = dm.create_vfd_device(
                device_id=device_config.get('device_id', f"vfd_{len(dm.devices)+1}"),
                fabricante=device_config.get('fabricante', 'Unknown'),
                modelo=device_config.get('modelo', 'Unknown'),
                parametros=device_config.get('parametros', []),
                config=device_config
            )
            
            if device is None:
                error_msg = "El dispositivo se creó pero es None"
                print(f"❌ {error_msg}")
                raise ValueError(error_msg)
            
            print(f"✅ Dispositivo creado: {device}")
            print(f"📱 Tipo: {type(device)}")
            print(f"🔌 ID: {getattr(device, 'device_id', 'Sin ID')}")
            
            # Añadir dispositivo al modo experto (único modo activo)
            print("🔧 Añadiendo dispositivo a modo experto...")
            self.expert_mode.add_device_to_panel(device)
            
            self.status_bar.showMessage(f"Dispositivo {device.device_id} agregado correctamente", 3000)
            print(f"🎉 Dispositivo {device.device_id} agregado exitosamente")
            
        except Exception as e:
            print(f"❌ Error en on_device_created: {e}")
            print(f"🔍 Tipo de error: {type(e).__name__}")
            import traceback
            print(f"📊 Traceback completo:")
            traceback.print_exc()
            
            QMessageBox.critical(
                self, 
                "Error", 
                f"No se pudo crear el dispositivo:\n\nTipo: {type(e).__name__}\nMensaje: {str(e)}"
            )
        
    def change_theme(self):
        self.style_manager.toggle_theme()
        self.apply_styles()
        
    def show_about(self):
        QMessageBox.about(
            self, 
            "Acerca de ComSuite",
            "ComSuite Professional Communication Suite\n\n"
            "Versión: 1.0.0\n"
            "Arquitectura modular para comunicación industrial\n\n"
            "© 2023 ComSuite Team"
        )
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QStatusBar, QMenuBar, QMenu, 
    QMessageBox, QLabel, QComboBox, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QAction

from .modes.novice_mode import NoviceMode
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
        
        # Selector de modo
        mode_selector_layout = QHBoxLayout()
        mode_label = QLabel("Modo de operación:")
        
        # Crear combo box con estilos aplicados directamente
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Modo Novato")
        self.mode_combo.addItem("Modo Experto")
        
        # APLICAR ESTILOS DIRECTAMENTE AL COMBO BOX
        
        
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        
        mode_selector_layout.addWidget(mode_label)
        mode_selector_layout.addWidget(self.mode_combo)
        mode_selector_layout.addStretch()
        
        # Stacked widget
        self.stacked_widget = QStackedWidget()
        
        # Crear y añadir modos
        self.novice_mode = NoviceMode(self.communication_engine)
        self.expert_mode = ExpertMode(self.communication_engine)
        
        self.stacked_widget.addWidget(self.novice_mode)
        self.stacked_widget.addWidget(self.expert_mode)
        
        # Layout principal
        main_layout.addLayout(mode_selector_layout)
        main_layout.addWidget(self.stacked_widget)
        
        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Establecer estado inicial
        self.mode_combo.setCurrentText("Modo Novato")
        self.stacked_widget.setCurrentWidget(self.novice_mode)
        self.current_mode = "novice"
        self.status_bar.showMessage("Modo Novato activado")
        
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
        
        if mode_text == "Modo Novato":
            self.stacked_widget.setCurrentWidget(self.novice_mode)
            self.current_mode = "novice"
            self.status_bar.showMessage("Modo Novato activado")
            print("Activado Modo Novato")
        elif mode_text == "Modo Experto":
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
        
    def new_project(self):
        QMessageBox.information(self, "Nuevo Proyecto", "Funcionalidad de nuevo proyecto en desarrollo")
        
    def open_project(self):
        QMessageBox.information(self, "Abrir Proyecto", "Funcionalidad de abrir proyecto en desarrollo")
        
    def save_project(self):
        QMessageBox.information(self, "Guardar Proyecto", "Funcionalidad de guardar proyecto en desarrollo")
        
    def add_device(self):
        from .wizards.device_wizard import DeviceWizard
        wizard = DeviceWizard(self.communication_engine, simplified=self.current_mode == "novato")
        wizard.exec()
        
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
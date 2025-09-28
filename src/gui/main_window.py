from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QStatusBar, QMenuBar, QMenu, 
    QMessageBox, QLabel, QComboBox, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QAction

# Importaciones corregidas
from .modes.novice_mode import NoviceMode
from .modes.expert_mode import ExpertMode
from .style_manager import StyleManager


class MainWindow(QMainWindow):
    """Ventana principal con selector de modo Novato/Experto"""
    
    # Señales para comunicación con otros componentes
    mode_changed = Signal(str)  # Emite el modo actual ("novice" o "expert")
    
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
        
        # Widget central con stacked layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(self.central_widget)
        
        # Selector de modo en la parte superior
        mode_selector_layout = QHBoxLayout()
        
        mode_label = QLabel("Modo de operación:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Modo Novato", "Modo Experto"])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        
        mode_selector_layout.addWidget(mode_label)
        mode_selector_layout.addWidget(self.mode_combo)
        mode_selector_layout.addStretch()
        
        # Stacked widget para los modos
        self.stacked_widget = QStackedWidget()
        
        # Inicialmente en modo novato
        self.novice_mode = NoviceMode(self.communication_engine)
        self.expert_mode = ExpertMode(self.communication_engine)
        
        # Añadir ambos modos al stacked widget
        self.stacked_widget.addWidget(self.novice_mode)  # Índice 0
        self.stacked_widget.addWidget(self.expert_mode)  # Índice 1
        
        # Layout principal
        main_layout.addLayout(mode_selector_layout)
        main_layout.addWidget(self.stacked_widget)
        
        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo - Modo Novato activado")
        
        # Establecer modo inicial
        self.stacked_widget.setCurrentWidget(self.novice_mode)
        self.current_mode = "novice"
        
        # Establecer el valor inicial del combo box
        self.mode_combo.setCurrentText("Modo Novato")
        
        # Agrega este código temporalmente al final del método setup_ui() en main_window.py
        print("=== DIAGNÓSTICO ===")
        print(f"Combo box items: {[self.mode_combo.itemText(i) for i in range(self.mode_combo.count())]}")
        print(f"Stacked widget count: {self.stacked_widget.count()}")
        print(f"Current combo text: '{self.mode_combo.currentText()}'")
        print(f"Current stacked widget index: {self.stacked_widget.currentIndex()}")
        print("==================")
                
    def setup_menu(self):
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu("Archivo")
        
        new_action = QAction("Nuevo Proyecto", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("Abrir Proyecto", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        save_action = QAction("Guardar Proyecto", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Salir", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menú Dispositivos
        devices_menu = menubar.addMenu("Dispositivos")
        
        add_device_action = QAction("Agregar Dispositivo", self)
        add_device_action.setShortcut("Ctrl+D")
        add_device_action.triggered.connect(self.add_device)
        devices_menu.addAction(add_device_action)
        
        # Menú Vista
        view_menu = menubar.addMenu("Vista")
        
        theme_action = QAction("Cambiar Tema", self)
        theme_action.triggered.connect(self.change_theme)
        view_menu.addAction(theme_action)
        
        # Menú Ayuda
        help_menu = menubar.addMenu("Ayuda")
        
        about_action = QAction("Acerca de", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_connections(self):
        # Conectar señales del motor de comunicación
        self.communication_engine.protocol_loaded.connect(self.on_protocol_loaded)
        self.communication_engine.device_connected.connect(self.on_device_connected)
        self.communication_engine.device_disconnected.connect(self.on_device_disconnected)
        
    def apply_styles(self):
        self.style_manager.apply_style(self)
        
    def on_mode_changed(self, mode_text):
        """Manejar cambio de modo"""
        print(f"Modo seleccionado: {mode_text}")  # Debug
        
        if "Novato" in mode_text:
            self.stacked_widget.setCurrentWidget(self.novice_mode)
            self.current_mode = "novice"
            self.status_bar.showMessage("Modo Novato activado")
            print("Cambiado a Modo Novato")  # Debug
        else:
            self.stacked_widget.setCurrentWidget(self.expert_mode)
            self.current_mode = "expert"
            self.status_bar.showMessage("Modo Experto activado")
            print("Cambiado a Modo Experto")  # Debug
            
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
        """Agregar dispositivo usando el asistente apropiado según el modo"""
        from .wizards.device_wizard import DeviceWizard
        
        if self.current_mode == "novice":
            wizard = DeviceWizard(self.communication_engine, simplified=True)
        else:
            wizard = DeviceWizard(self.communication_engine, simplified=False)
            
        wizard.exec_()
        
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
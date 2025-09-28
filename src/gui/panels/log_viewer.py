from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QTextEdit, QComboBox,
    QGroupBox, QCheckBox
)
from PySide6.QtCore import Signal, Qt, QDateTime
from PySide6.QtGui import QTextCursor, QFont, QColor


class LogViewer(QFrame):
    """Visor de logs para modo experto - Ahora hereda de QFrame"""
    
    def __init__(self):
        super().__init__()
        self.current_device_id = None
        self.setup_ui()
        
        # Establecer estilo de frame
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Visor de Logs")
        title.setStyleSheet("font-weight: bold; font-size: 12px;")
        
        # Controles
        controls_layout = QHBoxLayout()
        
        self.device_label = QLabel("Dispositivo: Todos")
        self.device_label.setFont(QFont("Arial", 10, QFont.Bold))
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["Todos", "INFO", "WARNING", "ERROR"])
        
        self.auto_scroll_check = QCheckBox("Auto-scroll")
        self.auto_scroll_check.setChecked(True)
        
        self.clear_btn = QPushButton("Limpiar")
        self.clear_btn.clicked.connect(self.clear_logs)
        
        controls_layout.addWidget(self.device_label)
        controls_layout.addStretch()
        controls_layout.addWidget(QLabel("Nivel:"))
        controls_layout.addWidget(self.log_level_combo)
        controls_layout.addWidget(self.auto_scroll_check)
        controls_layout.addWidget(self.clear_btn)
        
        # Área de logs
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        font = QFont("Courier New", 9)
        self.log_text.setFont(font)
        
        # Agregar widgets al layout
        layout.addWidget(title)
        layout.addLayout(controls_layout)
        layout.addWidget(self.log_text)
        
        # Logs iniciales
        self.add_log("INFO", "Sistema iniciado", "system")
        self.add_log("INFO", "Visor de logs listo", "log_viewer")
        
    def set_device(self, device_id):
        """Establecer el dispositivo a monitorear"""
        self.current_device_id = device_id
        if device_id:
            self.device_label.setText(f"Dispositivo: {device_id}")
            self.add_log("INFO", f"Monitoreando dispositivo: {device_id}", "log_viewer")
        else:
            self.device_label.setText("Dispositivo: Todos")
            
    def add_log(self, level, message, source="system"):
        """Agregar un mensaje al log"""
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        
        # Formato: [timestamp] [LEVEL] [source] message
        log_entry = f"[{timestamp}] [{level}] [{source}] {message}\n"
        
        # Colorear según nivel
        color_map = {
            "INFO": Qt.GlobalColor.black,
            "WARNING": QColor(255, 165, 0),  # Naranja
            "ERROR": Qt.GlobalColor.red
        }
        color = color_map.get(level, Qt.GlobalColor.black)
        
        self.log_text.moveCursor(QTextCursor.End)
        self.log_text.setTextColor(color)
        self.log_text.insertPlainText(log_entry)
        
        # Auto-scroll si está habilitado
        if self.auto_scroll_check.isChecked():
            self.log_text.moveCursor(QTextCursor.End)
            
    def clear_logs(self):
        """Limpiar el visor de logs"""
        self.log_text.clear()
        self.add_log("INFO", "Logs limpiados", "log_viewer")
        
    def log_connection(self, device_id, connected):
        """Registrar evento de conexión/desconexión"""
        status = "conectado" if connected else "desconectado"
        self.add_log("INFO", f"Dispositivo {device_id} {status}", "connection")
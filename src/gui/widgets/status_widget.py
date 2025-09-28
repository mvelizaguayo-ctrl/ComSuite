from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QProgressBar, QGroupBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont


class StatusWidget(QWidget):
    """Widget para mostrar estado del sistema"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        # Timer para actualizar estado
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(1000)  # Actualizar cada segundo
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Frame principal
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        frame_layout = QVBoxLayout(frame)
        
        # Título
        title = QLabel("Estado del Sistema")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        
        # Grupo de estado del sistema
        system_group = QGroupBox("Sistema")
        system_layout = QVBoxLayout()
        
        self.system_status = QLabel("Operativo")
        self.system_status.setAlignment(Qt.AlignCenter)
        self.system_status.setStyleSheet("color: green; font-weight: bold;")
        
        self.uptime_label = QLabel("Tiempo activo: 00:00:00")
        self.uptime_label.setAlignment(Qt.AlignCenter)
        
        system_layout.addWidget(self.system_status)
        system_layout.addWidget(self.uptime_label)
        
        system_group.setLayout(system_layout)
        
        # Grupo de recursos
        resources_group = QGroupBox("Recursos")
        resources_layout = QVBoxLayout()
        
        # CPU
        cpu_layout = QHBoxLayout()
        cpu_label = QLabel("CPU:")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        self.cpu_bar.setValue(25)
        self.cpu_bar.setTextVisible(True)
        
        cpu_layout.addWidget(cpu_label)
        cpu_layout.addWidget(self.cpu_bar)
        
        # Memoria
        mem_layout = QHBoxLayout()
        mem_label = QLabel("Memoria:")
        self.mem_bar = QProgressBar()
        self.mem_bar.setRange(0, 100)
        self.mem_bar.setValue(40)
        self.mem_bar.setTextVisible(True)
        
        mem_layout.addWidget(mem_label)
        mem_layout.addWidget(self.mem_bar)
        
        # Red
        net_layout = QHBoxLayout()
        net_label = QLabel("Red:")
        self.net_bar = QProgressBar()
        self.net_bar.setRange(0, 100)
        self.net_bar.setValue(15)
        self.net_bar.setTextVisible(True)
        
        net_layout.addWidget(net_label)
        net_layout.addWidget(self.net_bar)
        
        resources_layout.addLayout(cpu_layout)
        resources_layout.addLayout(mem_layout)
        resources_layout.addLayout(net_layout)
        
        resources_group.setLayout(resources_layout)
        
        # Agregar widgets al frame
        frame_layout.addWidget(title)
        frame_layout.addWidget(system_group)
        frame_layout.addWidget(resources_group)
        
        # Agregar frame al layout principal
        layout.addWidget(frame)
        
        # Establecer tamaño fijo
        self.setFixedSize(300, 250)
        
        # Inicializar tiempo de actividad
        self.start_time = Qt.DateTime.currentDateTime()
        
    def update_status(self):
        """Actualizar estado del sistema"""
        # Actualizar tiempo de actividad
        uptime = Qt.DateTime.currentDateTime().toSecsSinceEpoch() - self.start_time.toSecsSinceEpoch()
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60
        self.uptime_label.setText(f"Tiempo activo: {hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # Simular uso de recursos (en implementación real se obtendrían del sistema)
        import random
        self.cpu_bar.setValue(random.randint(10, 50))
        self.mem_bar.setValue(random.randint(30, 70))
        self.net_bar.setValue(random.randint(5, 30))
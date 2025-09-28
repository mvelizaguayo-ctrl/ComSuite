from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QSpinBox, QGroupBox, QSizePolicy
)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QIcon, QFont
import random


class DataMonitor(QFrame):  # Cambiado a QFrame para evitar layouts anidados
    """Monitor de datos para modo experto"""
    
    def __init__(self):
        super().__init__()
        self.current_device_id = None
        self.setup_ui()
        
        # Timer para actualizar datos
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(1000)
        
    def setup_ui(self):
        # Layout principal directamente en el QFrame
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Monitor de Datos")
        title.setStyleSheet("font-weight: bold; font-size: 12px;")
        
        # Controles de monitoreo
        controls_layout = QHBoxLayout()
        
        self.device_label = QLabel("Dispositivo: Ninguno seleccionado")
        self.device_label.setFont(QFont("Arial", 10, QFont.Bold))
        
        controls_layout.addWidget(self.device_label)
        controls_layout.addStretch()
        
        # Tabla de datos
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(3)
        self.data_table.setHorizontalHeaderLabels(["Dirección", "Valor", "Estado"])
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.verticalHeader().setVisible(False)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setMinimumHeight(200)
        
        # Grupo de opciones
        options_group = QGroupBox("Opciones de Monitoreo")
        options_layout = QHBoxLayout()
        
        self.polling_check = QLabel("Monitoreo continuo: Activo")
        self.polling_check.setStyleSheet("color: green;")
        
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(100, 10000)
        self.interval_spin.setValue(1000)
        self.interval_spin.setSuffix(" ms")
        self.interval_spin.valueChanged.connect(self.update_interval)
        
        options_layout.addWidget(self.polling_check)
        options_layout.addWidget(QLabel("Intervalo:"))
        options_layout.addWidget(self.interval_spin)
        options_layout.addStretch()
        
        options_group.setLayout(options_layout)
        
        # Agregar widgets al layout principal
        layout.addWidget(title)
        layout.addLayout(controls_layout)
        layout.addWidget(self.data_table)
        layout.addWidget(options_group)
        
        # Configurar políticas de tamaño
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Establecer el estilo del frame
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        
    def set_device(self, device_id):
        """Establecer el dispositivo a monitorear"""
        self.current_device_id = device_id
        self.device_label.setText(f"Dispositivo: {device_id}")
        self.update_data()
        
    def update_data(self):
        """Actualizar los datos del dispositivo actual"""
        if not self.current_device_id:
            return
            
        # Simular datos
        self.data_table.setRowCount(10)
        
        for i in range(10):
            # Dirección
            addr_item = QTableWidgetItem(f"{i:04d}")
            self.data_table.setItem(i, 0, addr_item)
            
            # Valor
            value = random.randint(1000, 5000)
            value_item = QTableWidgetItem(str(value))
            self.data_table.setItem(i, 1, value_item)
            
            # Estado
            status = "OK" if i % 5 != 0 else "ALARM"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(Qt.GlobalColor.green if status == "OK" else Qt.GlobalColor.red)
            self.data_table.setItem(i, 2, status_item)
            
    def update_interval(self, interval):
        """Actualizar intervalo de monitoreo"""
        self.update_timer.setInterval(interval)


class SimpleDataMonitor(QFrame):  # Cambiado a QFrame
    """Monitor de datos simplificado para modo novato"""
    
    def __init__(self):
        super().__init__()
        self.current_device_id = None
        self.setup_ui()
        
        # Timer para actualizar datos
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(2000)
        
    def setup_ui(self):
        # Layout principal directamente en el QFrame
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Datos del Dispositivo")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        title.setAlignment(Qt.AlignCenter)
        
        # Dispositivo actual
        self.device_label = QLabel("Ningún dispositivo seleccionado")
        self.device_label.setAlignment(Qt.AlignCenter)
        self.device_label.setStyleSheet("font-size: 12px; color: gray;")
        
        # Panel de datos principales
        self.data_panel = QGroupBox("Lecturas Actuales")
        self.data_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.data_panel.setMinimumHeight(200)
        
        data_layout = QVBoxLayout()
        data_layout.setSpacing(15)
        data_layout.setContentsMargins(20, 30, 20, 20)
        
        self.temp_label = QLabel("Temperatura: --°C")
        self.temp_label.setStyleSheet("font-size: 16px; margin: 8px;")
        self.temp_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.pressure_label = QLabel("Presión: -- PSI")
        self.pressure_label.setStyleSheet("font-size: 16px; margin: 8px;")
        self.pressure_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.flow_label = QLabel("Flujo: -- L/min")
        self.flow_label.setStyleSheet("font-size: 16px; margin: 8px;")
        self.flow_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        data_layout.addWidget(self.temp_label)
        data_layout.addWidget(self.pressure_label)
        data_layout.addWidget(self.flow_label)
        
        self.data_panel.setLayout(data_layout)
        
        # Estado - CON COLOR AZUL
        self.status_label = QLabel("Estado: Esperando dispositivo...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 12px; color: blue; margin-top: 15px;")
        
        # Agregar widgets al layout
        layout.addWidget(title)
        layout.addWidget(self.device_label)
        layout.addWidget(self.data_panel)
        layout.addWidget(self.status_label)
        
        # Configurar espaciado
        layout.setSpacing(25)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Configurar políticas de tamaño
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(300)
        
        # Establecer el estilo del frame
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        
    def set_device(self, device_id):
        """Establecer el dispositivo a monitorear"""
        self.current_device_id = device_id
        self.device_label.setText(f"Monitoreando: {device_id}")
        self.status_label.setText("Estado: Monitoreando...")
        self.update_data()
        
    def update_data(self):
        """Actualizar los datos del dispositivo actual"""
        if not self.current_device_id:
            return
            
        # Simular datos
        import random
        
        temp = random.uniform(20.0, 80.0)
        pressure = random.uniform(10.0, 100.0)
        flow = random.uniform(0.0, 50.0)
        
        self.temp_label.setText(f"Temperatura: {temp:.1f}°C")
        self.pressure_label.setText(f"Presión: {pressure:.1f} PSI")
        self.flow_label.setText(f"Flujo: {flow:.1f} L/min")
        
        # Actualizar estado
        status = "OK" if temp < 70 else "ALTA TEMPERATURA"
        self.status_label.setText(f"Estado: {status}")
        self.status_label.setStyleSheet(
            "font-size: 12px; color: green; margin-top: 15px;" if status == "OK" else "font-size: 12px; color: red; margin-top: 15px;"
        )
from PySide6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QComboBox,
    QSpinBox, QPushButton, QListWidget, QListWidgetItem, QMessageBox, QWidget, QHBoxLayout
)
from PySide6.QtCore import Signal

class OtherRegister:
    def __init__(self, func, address):
        self.func = func
        self.address = address

    def to_dict(self):
        return {'function': self.func, 'address': self.address}


class OtherRegistersWizard(QWizard):
    registers_created = Signal(list, dict)  # (list of registers, config)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Crear registros - Otros")
        self.setWizardStyle(QWizard.ModernStyle)
        self.registers = []
        self.setup_pages()
        # actualizar resumen cuando se navega a la página de resumen (id 2)
        try:
            self.currentIdChanged.connect(self._on_page_changed)
        except Exception:
            pass

    def setup_pages(self):
        self.addPage(self._make_config_page())
        self.addPage(self._make_register_entry_page())
        self.addPage(self._make_summary_page())

    def _make_config_page(self):
        page = QWizardPage()
        page.setTitle("Configuración de comunicación")
        layout = QFormLayout(page)

        page.modbus_mode = QComboBox()
        page.modbus_mode.addItems(["Modbus TCP", "Modbus RTU"])
        page.device_name = QLineEdit()
        page.device_name.setPlaceholderText("Nombre del grupo de registros (opcional)")

        page.ip_edit = QLineEdit()
        page.port_spin = QSpinBox()
        page.port_spin.setRange(1, 65535)
        page.port_spin.setValue(502)

        page.com_port = QComboBox()
        page.com_port.addItems(["COM1", "COM2", "COM3"])
        page.baudrate = QComboBox()
        page.baudrate.addItems(["9600", "19200", "38400", "57600", "115200"]) 

        layout.addRow("Modo Modbus:", page.modbus_mode)
        layout.addRow("Nombre del dispositivo:", page.device_name)
        layout.addRow("IP:", page.ip_edit)
        layout.addRow("Puerto:", page.port_spin)
        layout.addRow("Puerto COM:", page.com_port)
        layout.addRow("Baudrate:", page.baudrate)

        return page

    def _make_register_entry_page(self):
        page = QWizardPage()
        page.setTitle("Agregar registros Modbus")
        vbox = QVBoxLayout(page)

        form = QFormLayout()
        page.func_combo = QComboBox()
        page.func_combo.addItems(["0x", "1x", "3x", "4x", "5x", "6x", "10x", "16x"])
        page.address_spin = QSpinBox()
        page.address_spin.setRange(0, 65535)
        page.address_spin.setValue(0)

        form.addRow("Función Modbus:", page.func_combo)
        form.addRow("Dirección:", page.address_spin)

        vbox.addLayout(form)

        # Lista de registros añadidos
        page.registers_list = QListWidget()
        vbox.addWidget(page.registers_list)

        # Botones para agregar y terminar
        btns = QWidget()
        h = QHBoxLayout(btns)
        page.add_btn = QPushButton("Agregar registro")
        page.finish_btn = QPushButton("Finalizar creación de registros")
        h.addWidget(page.add_btn)
        h.addWidget(page.finish_btn)
        vbox.addWidget(btns)

        # Connects
        page.add_btn.clicked.connect(lambda: self._add_register(page))
        page.finish_btn.clicked.connect(lambda: self.next())

        return page

    def _make_summary_page(self):
        page = QWizardPage()
        page.setTitle("Resumen de registros")
        vbox = QVBoxLayout(page)
        page.summary_list = QListWidget()
        vbox.addWidget(QLabel("Registros creados:"))
        vbox.addWidget(page.summary_list)

        # Botones: volver al inicio o finalizar
        page.back_to_start = QPushButton("Volver al inicio")
        page.finish_process = QPushButton("Finalizar proceso")
        btns = QWidget()
        h = QHBoxLayout(btns)
        h.addWidget(page.back_to_start)
        h.addWidget(page.finish_process)
        vbox.addWidget(btns)

        page.back_to_start.clicked.connect(self._back_to_start)
        page.finish_process.clicked.connect(self._emit_and_close)

        return page

    def _on_page_changed(self, page_id: int):
        """Handler para refrescar el contenido de las páginas al navegar.

        En particular, cuando se muestra la página de resumen (id 2), llenamos
        la lista con los registros actualmente añadidos.
        """
        try:
            # id 2 es la página de resumen según el orden en setup_pages
            if page_id == 2:
                summary = self.page(2)
                if summary is not None and hasattr(summary, 'summary_list'):
                    summary.summary_list.clear()
                    for r in self.registers:
                        summary.summary_list.addItem(f"{r.func} @ {r.address}")
        except Exception:
            pass

    def _back_to_start(self):
        """Intentar volver a la primera página del asistente."""
        try:
            # Intentamos reiniciar el asistente al inicio
            self.setStartId(0)
            # QWizard tiene restart() en algunas versiones; intentando usarla
            if hasattr(self, 'restart'):
                try:
                    self.restart()
                    return
                except Exception:
                    pass
            # Si no hay restart(), movemos la página actual manualmente
            # usando el histórico (retroceder hasta el inicio)
            while self.currentId() != 0:
                try:
                    self.back()
                except Exception:
                    break
        except Exception:
            pass

    def _add_register(self, page):
        func = page.func_combo.currentText()
        addr = page.address_spin.value()
        reg = OtherRegister(func, addr)
        self.registers.append(reg)
        page.registers_list.addItem(f"{func} @ {addr}")

    def _emit_and_close(self):
        # Emitir la lista de registros y configuración
        config_page = self.page(0)
        cfg = {
            'protocol': config_page.modbus_mode.currentText(),
            'device_name': config_page.device_name.text(),
            'ip': config_page.ip_edit.text(),
            'port': config_page.port_spin.value(),
            'com_port': config_page.com_port.currentText(),
            'baudrate': config_page.baudrate.currentText()
        }
        regs = [r.to_dict() for r in self.registers]
        self.registers_created.emit(regs, cfg)
        self.accept()

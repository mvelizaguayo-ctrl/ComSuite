#!/usr/bin/env python3
"""
Slave Modbus Unificado - Implementación limpia para ComSuite
Wrapper unificado para Modbus TCP y RTU Slave.
"""

class ModbusSlave:
    """Clase unificada para Modbus TCP y RTU Slave"""

    def __init__(self, protocol='TCP', **kwargs):
        self.protocol = protocol.upper()
        self._slave = None

        if self.protocol == 'TCP':
            from .slave_tcp import ModbusSlaveTCP
            self._slave = ModbusSlaveTCP(**kwargs)
        elif self.protocol == 'RTU':
            from .slave_rtu import ModbusSlaveRTU
            self._slave = ModbusSlaveRTU(**kwargs)
        else:
            raise ValueError("Protocolo debe ser 'TCP' o 'RTU'")

    def set_log_callback(self, callback):
        """Establecer callback para logging"""
        self._slave.set_log_callback(callback)

    def set_frame_callback(self, callback):
        """Establecer callback para tramas"""
        self._slave.set_frame_callback(callback)

    def start(self):
        """Iniciar el slave"""
        return self._slave.start()

    def stop(self):
        """Detener el slave"""
        self._slave.stop()
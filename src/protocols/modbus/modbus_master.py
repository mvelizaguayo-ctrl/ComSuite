#!/usr/bin/env python3
"""
Master Modbus Unificado - Implementación limpia para ComSuite
Wrapper unificado para Modbus TCP y RTU Master.
"""

class ModbusMaster:
    """Clase unificada para Modbus TCP y RTU"""

    def __init__(self, protocol='TCP', **kwargs):
        self.protocol = protocol.upper()
        self._master = None

        if self.protocol == 'TCP':
            from .master_tcp import ModbusMasterTCP
            self._master = ModbusMasterTCP(**kwargs)
        elif self.protocol == 'RTU':
            from .master_rtu import ModbusMasterRTU
            self._master = ModbusMasterRTU(**kwargs)
        else:
            raise ValueError("Protocolo debe ser 'TCP' o 'RTU'")

    def set_log_callback(self, callback):
        """Establecer callback para logging"""
        self._master.set_log_callback(callback)

    def set_frame_callback(self, callback):
        """Establecer callback para tramas"""
        self._master.set_frame_callback(callback)

    def connect(self):
        """Conectar al dispositivo Modbus"""
        return self._master.connect()

    def disconnect(self):
        """Desconectar del dispositivo Modbus"""
        self._master.disconnect()

    # Funciones de lectura
    def read_coils(self, start_address, count):
        """Leer coils (FC 01)"""
        return self._master.read_coils(start_address, count)

    def read_discrete_inputs(self, start_address, count):
        """Leer discrete inputs (FC 02)"""
        return self._master.read_discrete_inputs(start_address, count)

    def read_holding_registers(self, start_address, count):
        """Leer holding registers (FC 03)"""
        return self._master.read_holding_registers(start_address, count)

    def read_input_registers(self, start_address, count):
        """Leer input registers (FC 04)"""
        return self._master.read_input_registers(start_address, count)

    # Funciones de escritura
    def write_single_coil(self, address, value):
        """Escribir single coil (FC 05)"""
        return self._master.write_single_coil(address, value)

    def write_single_register(self, address, value):
        """Escribir single register (FC 06)"""
        return self._master.write_single_register(address, value)

    def write_multiple_coils(self, address, values):
        """Escribir multiple coils (FC 15)"""
        return self._master.write_multiple_coils(address, values)

    def write_multiple_registers(self, address, values):
        """Escribir multiple registers (FC 16)"""
        return self._master.write_multiple_registers(address, values)

    def stop(self):
        """Detener el master"""
        if hasattr(self._master, 'stop'):
            self._master.stop()
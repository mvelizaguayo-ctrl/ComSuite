#!/usr/bin/env python3
"""
Master Modbus TCP - Implementación limpia para ComSuite
Clase pura de comunicación sin rutinas de prueba.
"""

import socket
import struct
import logging

class ModbusMasterTCP:
    """Master Modbus TCP completo con todas las funciones Modbus"""

    def __init__(self, ip='127.0.0.1', port=502, slave_id=1):
        self.ip = ip
        self.port = port
        self.slave_id = slave_id
        self.socket = None
        self.connected = False
        self.transaction_id = 0
        self.timeout = 3.0

        # Callbacks para logging y diagnóstico
        self.log_callback = None
        self.frame_callback = None

    def set_log_callback(self, callback):
        """Establecer callback para logging"""
        self.log_callback = callback

    def set_frame_callback(self, callback):
        """Establecer callback para tramas"""
        self.frame_callback = callback

    def _log(self, message):
        """Logging interno"""
        if self.log_callback:
            self.log_callback(f"Master: {message}")
        else:
            print(f"Master: {message}")

    def _get_next_transaction_id(self):
        """Obtener siguiente ID de transacción"""
        self.transaction_id = (self.transaction_id + 1) % 65536
        return self.transaction_id

    def connect(self):
        """Conectar al slave"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.ip, self.port))
            self.connected = True
            self._log(f"Conectado a {self.ip}:{self.port}")
            return True
        except Exception as e:
            self._log(f"Error al conectar a {self.ip}:{self.port}: {e}")
            return False

    def disconnect(self):
        """Desconectar del slave"""
        if self.socket:
            self.socket.close()
            self.socket = None
        self.connected = False
        self._log("Desconectado")

    def send_request(self, request):
        """Enviar petición y recibir respuesta"""
        if not self.connected and not self.connect():
            return None

        try:
            if self.frame_callback:
                self.frame_callback("ENVIADO", request)

            self.socket.send(request)

            # Esperar respuesta con timeout
            self.socket.settimeout(self.timeout)
            response = self.socket.recv(1024)

            if self.frame_callback:
                self.frame_callback("RECIBIDO", response)

            return response
        except socket.timeout:
            self._log("Timeout esperando respuesta")
            return None
        except Exception as e:
            self._log(f"Error en comunicación: {e}")
            self.connected = False
            return None

    # === FUNCIONES DE LECTURA ===

    def read_coils(self, start_address, count):
        """Leer coils (FC 01)"""
        transaction_id = self._get_next_transaction_id()

        request = struct.pack('>HHHBBHH',
            transaction_id,
            0,  # Protocol ID
            6,  # Length
            self.slave_id,
            1,  # Function code
            start_address,
            count
        )

        response = self.send_request(request)
        if not response:
            return [False] * count

        # Verificar respuesta
        if len(response) < 9:
            self._log("Respuesta demasiado corta")
            return [False] * count

        # Verificar transaction ID
        resp_transaction_id = int.from_bytes(response[0:2], byteorder='big')
        if resp_transaction_id != transaction_id:
            self._log(f"ID de transacción incorrecto: esperado {transaction_id}, recibido {resp_transaction_id}")
            return [False] * count

        if response[7] & 0x80:  # Excepción
            exception_code = response[8]
            self._log(f"Excepción recibida: código {exception_code}")
            return [False] * count

        if response[6] != self.slave_id:
            self._log(f"Unit ID incorrecto: esperado {self.slave_id}, recibido {response[6]}")
            return [False] * count

        # Extraer valores
        byte_count = response[8]
        values = []
        for i in range(count):
            byte_index = i // 8
            bit_index = i % 8
            if byte_index < byte_count:
                byte_value = response[9 + byte_index]
                values.append(bool(byte_value & (1 << bit_index)))
            else:
                values.append(False)

        return values

    def read_discrete_inputs(self, start_address, count):
        """Leer discrete inputs (FC 02)"""
        transaction_id = self._get_next_transaction_id()

        request = struct.pack('>HHHBBHH',
            transaction_id,
            0,  # Protocol ID
            6,  # Length
            self.slave_id,
            2,  # Function code
            start_address,
            count
        )

        response = self.send_request(request)
        if not response:
            return [False] * count

        # Verificar respuesta
        if len(response) < 9:
            self._log("Respuesta demasiado corta")
            return [False] * count

        # Verificar transaction ID
        resp_transaction_id = int.from_bytes(response[0:2], byteorder='big')
        if resp_transaction_id != transaction_id:
            self._log(f"ID de transacción incorrecto: esperado {transaction_id}, recibido {resp_transaction_id}")
            return [False] * count

        if response[7] & 0x80:  # Excepción
            exception_code = response[8]
            self._log(f"Excepción recibida: código {exception_code}")
            return [False] * count

        if response[6] != self.slave_id:
            self._log(f"Unit ID incorrecto: esperado {self.slave_id}, recibido {response[6]}")
            return [False] * count

        # Extraer valores
        byte_count = response[8]
        values = []
        for i in range(count):
            byte_index = i // 8
            bit_index = i % 8
            if byte_index < byte_count:
                byte_value = response[9 + byte_index]
                values.append(bool(byte_value & (1 << bit_index)))
            else:
                values.append(False)

        return values

    def read_holding_registers(self, start_address, count):
        """Leer holding registers (FC 03)"""
        transaction_id = self._get_next_transaction_id()

        request = struct.pack('>HHHBBHH',
            transaction_id,
            0,  # Protocol ID
            6,  # Length
            self.slave_id,
            3,  # Function code
            start_address,
            count
        )

        response = self.send_request(request)
        if not response:
            return [0] * count

        # Verificar respuesta
        if len(response) < 9:
            self._log("Respuesta demasiado corta")
            return [0] * count

        # Verificar transaction ID
        resp_transaction_id = int.from_bytes(response[0:2], byteorder='big')
        if resp_transaction_id != transaction_id:
            self._log(f"ID de transacción incorrecto: esperado {transaction_id}, recibido {resp_transaction_id}")
            return [0] * count

        if response[7] & 0x80:  # Excepción
            exception_code = response[8]
            self._log(f"Excepción recibida: código {exception_code}")
            return [0] * count

        if response[6] != self.slave_id:
            self._log(f"Unit ID incorrecto: esperado {self.slave_id}, recibido {response[6]}")
            return [0] * count

        # Extraer valores
        byte_count = response[8]
        values = []
        for i in range(byte_count // 2):
            value = struct.unpack('>H', response[9 + i*2:11 + i*2])[0]
            values.append(value)

        return values

    def read_input_registers(self, start_address, count):
        """Leer input registers (FC 04)"""
        transaction_id = self._get_next_transaction_id()

        request = struct.pack('>HHHBBHH',
            transaction_id,
            0,  # Protocol ID
            6,  # Length
            self.slave_id,
            4,  # Function code
            start_address,
            count
        )

        response = self.send_request(request)
        if not response:
            return [0] * count

        # Verificar respuesta
        if len(response) < 9:
            self._log("Respuesta demasiado corta")
            return [0] * count

        # Verificar transaction ID
        resp_transaction_id = int.from_bytes(response[0:2], byteorder='big')
        if resp_transaction_id != transaction_id:
            self._log(f"ID de transacción incorrecto: esperado {transaction_id}, recibido {resp_transaction_id}")
            return [0] * count

        if response[7] & 0x80:  # Excepción
            exception_code = response[8]
            self._log(f"Excepción recibida: código {exception_code}")
            return [0] * count

        if response[6] != self.slave_id:
            self._log(f"Unit ID incorrecto: esperado {self.slave_id}, recibido {response[6]}")
            return [0] * count

        # Extraer valores
        byte_count = response[8]
        values = []
        for i in range(byte_count // 2):
            value = struct.unpack('>H', response[9 + i*2:11 + i*2])[0]
            values.append(value)

        return values

    # === FUNCIONES DE ESCRITURA ===

    def write_single_coil(self, address, value):
        """Escribir single coil (FC 05)"""
        transaction_id = self._get_next_transaction_id()

        coil_value = 0xFF00 if value else 0x0000

        request = struct.pack('>HHHBBHH',
            transaction_id,
            0,  # Protocol ID
            6,  # Length
            self.slave_id,
            5,  # Function code
            address,
            coil_value
        )

        response = self.send_request(request)
        if not response:
            return False

        # Verificar respuesta
        if len(response) < 12:
            self._log("Respuesta demasiado corta")
            return False

        # Verificar transaction ID
        resp_transaction_id = int.from_bytes(response[0:2], byteorder='big')
        if resp_transaction_id != transaction_id:
            self._log(f"ID de transacción incorrecto: esperado {transaction_id}, recibido {resp_transaction_id}")
            return False

        if response[7] & 0x80:  # Excepción
            exception_code = response[8]
            self._log(f"Excepción recibida: código {exception_code}")
            return False

        return True

    def write_single_register(self, address, value):
        """Escribir single register (FC 06)"""
        transaction_id = self._get_next_transaction_id()

        request = struct.pack('>HHHBBHH',
            transaction_id,
            0,  # Protocol ID
            6,  # Length
            self.slave_id,
            6,  # Function code
            address,
            value
        )

        response = self.send_request(request)
        if not response:
            return False

        # Verificar respuesta
        if len(response) < 12:
            self._log("Respuesta demasiado corta")
            return False

        # Verificar transaction ID
        resp_transaction_id = int.from_bytes(response[0:2], byteorder='big')
        if resp_transaction_id != transaction_id:
            self._log(f"ID de transacción incorrecto: esperado {transaction_id}, recibido {resp_transaction_id}")
            return False

        if response[7] & 0x80:  # Excepción
            exception_code = response[8]
            self._log(f"Excepción recibida: código {exception_code}")
            return False

        return True

    def write_multiple_coils(self, address, values):
        """Escribir multiple coils (FC 15)"""
        transaction_id = self._get_next_transaction_id()

        coil_count = len(values)
        byte_count = (coil_count + 7) // 8

        # Empaquetar valores en bytes
        coils_bytes = bytearray(byte_count)
        for i, value in enumerate(values):
            if value:
                byte_index = i // 8
                bit_index = i % 8
                coils_bytes[byte_index] |= (1 << bit_index)

        length = 7 + byte_count

        request = bytearray()
        request.extend(struct.pack('>HHHBBH',
            transaction_id,
            0,  # Protocol ID
            length,
            self.slave_id,
            15,  # Function code
            address,
            coil_count
        ))
        request.append(byte_count)
        request.extend(coils_bytes)

        response = self.send_request(request)
        if not response:
            return False

        # Verificar respuesta
        if len(response) < 12:
            self._log("Respuesta demasiado corta")
            return False

        # Verificar transaction ID
        resp_transaction_id = int.from_bytes(response[0:2], byteorder='big')
        if resp_transaction_id != transaction_id:
            self._log(f"ID de transacción incorrecto: esperado {transaction_id}, recibido {resp_transaction_id}")
            return False

        if response[7] & 0x80:  # Excepción
            exception_code = response[8]
            self._log(f"Excepción recibida: código {exception_code}")
            return False

        return True

    def write_multiple_registers(self, address, values):
        """Escribir multiple registers (FC 16)"""
        transaction_id = self._get_next_transaction_id()

        register_count = len(values)
        byte_count = register_count * 2
        length = 7 + byte_count

        request = bytearray()
        request.extend(struct.pack('>HHHBBH',
            transaction_id,
            0,  # Protocol ID
            length,
            self.slave_id,
            16,  # Function code
            address,
            register_count
        ))
        request.append(byte_count)

        for value in values:
            request.extend(struct.pack('>H', value))

        response = self.send_request(request)
        if not response:
            return False

        # Verificar respuesta
        if len(response) < 12:
            self._log("Respuesta demasiado corta")
            return False

        # Verificar transaction ID
        resp_transaction_id = int.from_bytes(response[0:2], byteorder='big')
        if resp_transaction_id != transaction_id:
            self._log(f"ID de transacción incorrecto: esperado {transaction_id}, recibido {resp_transaction_id}")
            return False

        if response[7] & 0x80:  # Excepción
            exception_code = response[8]
            self._log(f"Excepción recibida: código {exception_code}")
            return False

        return True
#!/usr/bin/env python3
"""
Master Modbus RTU - Implementación limpia para ComSuite
Clase pura de comunicación sin rutinas de prueba.
"""

import serial
import struct
import time

class ModbusMasterRTU:
    """Master Modbus RTU completo con todas las funciones Modbus"""

    def __init__(self, port, baudrate=9600, parity='N', stopbits=1, bytesize=8, slave_id=1):
        self.port = port
        self.baudrate = baudrate
        self.parity = parity
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.slave_id = slave_id
        self.serial_port = None
        self.connected = False
        self.timeout = 3.0
        self.should_stop = False

        # Mapeo de paridad
        self.parity_map = {
            'N': serial.PARITY_NONE,
            'E': serial.PARITY_EVEN,
            'O': serial.PARITY_ODD
        }

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
            self.log_callback(f"Master RTU: {message}")
        else:
            print(f"Master RTU: {message}")

    def connect(self):
        """Conectar al puerto serie"""
        try:
            self.serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                parity=self.parity_map[self.parity],
                stopbits=self.stopbits,
                bytesize=self.bytesize,
                timeout=self.timeout,
                rtscts=False,
                dsrdtr=False,
                xonxoff=False
            )
            self.connected = True
            self._log(f"Conectado a {self.port} @ {self.baudrate} baud")
            return True
        except Exception as e:
            self._log(f"Error al conectar: {e}")
            return False

    def disconnect(self):
        """Desconectar del puerto serie"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.connected = False
        self._log("Desconectado")

    def calculate_crc(self, data):
        """Calcular CRC16 Modbus"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc = crc >> 1
        return crc & 0xFFFF

    def send_request(self, function_code, data):
        """Enviar petición RTU y recibir respuesta"""
        if not self.connected and not self.connect():
            return None

        try:
            # Construir trama
            request = bytearray([self.slave_id, function_code])
            request.extend(data)

            # Calcular y agregar CRC
            crc = self.calculate_crc(request)
            # Convertir CRC a little-endian para transmisión
            crc_bytes = bytes([crc & 0xFF, (crc >> 8) & 0xFF])
            request.extend(crc_bytes)

            self._log(f"Enviando trama: {request.hex()}")

            # Limpiar buffer antes de enviar
            if self.serial_port:
                self.serial_port.reset_input_buffer()

            # Enviar petición
            bytes_written = self.serial_port.write(request)
            self.serial_port.flush()
            self._log(f"Bytes escritos: {bytes_written}")

            # Esperar respuesta
            time.sleep(0.5)  # Espera conservadora

            response = bytearray()
            timeout = time.time() + self.timeout

            while time.time() < timeout and not self.should_stop:
                if self.serial_port and self.serial_port.in_waiting > 0:
                    data_read = self.serial_port.read(self.serial_port.in_waiting)
                    response.extend(data_read)
                    self._log(f"Recibidos {len(data_read)} bytes: {data_read.hex()}")

                    # Verificar si tenemos respuesta completa
                    if len(response) >= 5:  # Mínimo: ID + FC + CRC (2 bytes)
                        # Verificar CRC
                        response_data = response[:-2]
                        response_crc_bytes = response[-2:]

                        # Reconstruir el CRC desde little-endian
                        response_crc = response_crc_bytes[0] | (response_crc_bytes[1] << 8)
                        calculated_response_crc = self.calculate_crc(response_data)

                        self._log(f"CRC recibido: 0x{response_crc:04X}, CRC calculado: 0x{calculated_response_crc:04X}")

                        if response_crc == calculated_response_crc:
                            self._log("CRC válido - Respuesta completa")
                            return response_data
                        else:
                            self._log("CRC inválido")
                            # Limpiar buffer y reiniciar
                            if self.serial_port:
                                self.serial_port.reset_input_buffer()
                            response = bytearray()

                time.sleep(0.01)

            if self.should_stop:
                self._log("Deteniendo por petición del usuario")
                return None

            self._log("Timeout esperando respuesta")
            return None

        except Exception as e:
            self._log(f"Error en comunicación: {e}")
            return None

    def stop(self):
        """Detener el master"""
        self.should_stop = True
        self._log("Solicitando detención...")
        time.sleep(0.1)  # Dar tiempo para que se procese la detención
        self.disconnect()

    # === FUNCIONES DE LECTURA ===

    def read_coils(self, start_address, count):
        """Leer coils (FC 01)"""
        self._log(f"Leyendo coils desde dirección {start_address}, cantidad {count}")

        if start_address > 65535 or count < 1 or count > 2000:
            self._log(f"Parámetros inválidos: dirección={start_address}, conteo={count}")
            return [False] * count

        data = struct.pack('>HH', start_address, count)
        response = self.send_request(1, data)

        if not response or len(response) < 2:
            self._log("Respuesta inválida o vacía")
            return [False] * count

        if response[1] & 0x80:  # Excepción
            exception_code = response[2]
            self._log(f"Excepción recibida: código {exception_code}")
            return [False] * count

        byte_count = response[2]
        values = []
        for i in range(count):
            byte_index = i // 8
            bit_index = i % 8
            if byte_index < byte_count:
                byte_value = response[3 + byte_index]
                values.append(bool(byte_value & (1 << bit_index)))
            else:
                values.append(False)

        self._log(f"Valores leídos: {values[:10]}{'...' if len(values) > 10 else ''}")
        return values

    def read_discrete_inputs(self, start_address, count):
        """Leer discrete inputs (FC 02)"""
        self._log(f"Leyendo discrete inputs desde dirección {start_address}, cantidad {count}")

        if start_address > 65535 or count < 1 or count > 2000:
            self._log(f"Parámetros inválidos: dirección={start_address}, conteo={count}")
            return [False] * count

        data = struct.pack('>HH', start_address, count)
        response = self.send_request(2, data)

        if not response or len(response) < 2:
            self._log("Respuesta inválida o vacía")
            return [False] * count

        if response[1] & 0x80:  # Excepción
            exception_code = response[2]
            self._log(f"Excepción recibida: código {exception_code}")
            return [False] * count

        byte_count = response[2]
        values = []
        for i in range(count):
            byte_index = i // 8
            bit_index = i % 8
            if byte_index < byte_count:
                byte_value = response[3 + byte_index]
                values.append(bool(byte_value & (1 << bit_index)))
            else:
                values.append(False)

        self._log(f"Valores leídos: {values[:10]}{'...' if len(values) > 10 else ''}")
        return values

    def read_holding_registers(self, start_address, count):
        """Leer holding registers (FC 03)"""
        self._log(f"Leyendo holding registers desde dirección {start_address}, cantidad {count}")

        if start_address > 65535 or count < 1 or count > 125:
            self._log(f"Parámetros inválidos: dirección={start_address}, conteo={count}")
            return [0] * count

        # Empaquetar datos en big-endian
        data = struct.pack('>HH', start_address, count)
        self._log(f"Datos empaquetados: {data.hex()}")

        response = self.send_request(3, data)

        if not response or len(response) < 2:
            self._log("Respuesta inválida o vacía")
            return [0] * count

        if response[1] & 0x80:  # Excepción
            exception_code = response[2]
            self._log(f"Excepción recibida: código {exception_code}")
            return [0] * count

        byte_count = response[2]
        values = []
        for i in range(byte_count // 2):
            # Desempaquetar en big-endian
            value = struct.unpack('>H', response[3 + i*2:5 + i*2])[0]
            values.append(value)

        self._log(f"Valores leídos: {values}")
        return values

    def read_input_registers(self, start_address, count):
        """Leer input registers (FC 04)"""
        self._log(f"Leyendo input registers desde dirección {start_address}, cantidad {count}")

        if start_address > 65535 or count < 1 or count > 125:
            self._log(f"Parámetros inválidos: dirección={start_address}, conteo={count}")
            return [0] * count

        data = struct.pack('>HH', start_address, count)
        response = self.send_request(4, data)

        if not response or len(response) < 2:
            self._log("Respuesta inválida o vacía")
            return [0] * count

        if response[1] & 0x80:  # Excepción
            exception_code = response[2]
            self._log(f"Excepción recibida: código {exception_code}")
            return [0] * count

        byte_count = response[2]
        values = []
        for i in range(byte_count // 2):
            # Desempaquetar en big-endian
            value = struct.unpack('>H', response[3 + i*2:5 + i*2])[0]
            values.append(value)

        self._log(f"Valores leídos: {values}")
        return values

    # === FUNCIONES DE ESCRITURA ===

    def write_single_coil(self, address, value):
        """Escribir single coil (FC 05)"""
        self._log(f"Escribiendo coil en dirección {address}, valor {value}")

        if address > 65535:
            self._log(f"Dirección inválida: {address}")
            return False

        coil_value = 0xFF00 if value else 0x0000
        data = struct.pack('>HH', address, coil_value)
        response = self.send_request(5, data)

        return response is not None

    def write_single_register(self, address, value):
        """Escribir single register (FC 06)"""
        self._log(f"Escribiendo registro en dirección {address}, valor {value}")

        if address > 65535:
            self._log(f"Dirección inválida: {address}")
            return False

        data = struct.pack('>HH', address, value)
        response = self.send_request(6, data)

        return response is not None

    def write_multiple_coils(self, address, values):
        """Escribir multiple coils (FC 15)"""
        self._log(f"Escribiendo múltiples coils en dirección {address}, cantidad {len(values)}")

        if address > 65535 or len(values) < 1 or len(values) > 1968:
            self._log(f"Parámetros inválidos: dirección={address}, cantidad={len(values)}")
            return False

        coil_count = len(values)
        byte_count = (coil_count + 7) // 8

        # Empaquetar valores en bytes
        coils_bytes = bytearray(byte_count)
        for i, value in enumerate(values):
            if value:
                byte_index = i // 8
                bit_index = i % 8
                coils_bytes[byte_index] |= (1 << bit_index)

        data = bytearray()
        data.extend(struct.pack('>HH', address, coil_count))
        data.append(byte_count)
        data.extend(coils_bytes)

        response = self.send_request(15, data)
        return response is not None

    def write_multiple_registers(self, address, values):
        """Escribir multiple registers (FC 16)"""
        self._log(f"Escribiendo múltiples registros en dirección {address}, cantidad {len(values)}")

        if address > 65535 or len(values) < 1 or len(values) > 123:
            self._log(f"Parámetros inválidos: dirección={address}, cantidad={len(values)}")
            return False

        register_count = len(values)
        byte_count = register_count * 2

        data = bytearray()
        data.extend(struct.pack('>HH', address, register_count))
        data.append(byte_count)
        for value in values:
            data.extend(struct.pack('>H', value))

        response = self.send_request(16, data)
        return response is not None
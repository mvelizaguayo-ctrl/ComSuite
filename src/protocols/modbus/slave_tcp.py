#!/usr/bin/env python3
"""
Slave Modbus TCP - Implementación limpia para ComSuite
Clase pura de comunicación sin rutinas de prueba.
"""

import socket
import threading
import time
import struct
import logging

class ModbusSlaveTCP:
    """Slave Modbus TCP completo con todas las funciones Modbus"""

    def __init__(self, ip='127.0.0.1', port=502, slave_id=1):
        self.ip = ip
        self.port = port
        self.slave_id = slave_id
        self.server_socket = None
        self.running = False
        self.client_socket = None
        self.timeout = 3.0  # Timeout más generoso

        # Registros - CORRECTAMENTE SEPARADOS
        self.coils = [False] * 10000  # 0x - Coils
        self.discrete_inputs = [False] * 10000  # 1x - Discrete Inputs
        self.input_registers = [0] * 10000  # 3x - Input Registers (solo lectura)
        self.holding_registers = [0] * 10000  # 4x - Holding Registers (lectura/escritura)

        # Callbacks para logging y diagnóstico
        self.log_callback = None
        self.frame_callback = None

        # Inicializar con valores de prueba
        self._initialize_test_values()

    def _initialize_test_values(self):
        """Inicializar con valores de prueba para todas las funciones"""
        # Coils (0x) - valores alternados
        for i in range(20):
            self.coils[i] = (i % 2 == 0)

        # Discrete Inputs (1x) - valores alternados
        for i in range(20):
            self.discrete_inputs[i] = (i % 3 == 0)

        # Input Registers (3x) - valores secuenciales
        for i in range(20):
            self.input_registers[i] = 100 + i * 10

        # Holding Registers (4x) - valores secuenciales
        for i in range(20):
            self.holding_registers[i] = 1000 + i * 100

    def set_log_callback(self, callback):
        """Establecer callback para logging"""
        self.log_callback = callback

    def set_frame_callback(self, callback):
        """Establecer callback para tramas"""
        self.frame_callback = callback

    def _log(self, message):
        """Logging interno"""
        if self.log_callback:
            self.log_callback(f"Slave: {message}")
        else:
            print(f"Slave: {message}")

    def start(self):
        """Iniciar servidor TCP"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.ip, self.port))
            self.server_socket.listen(1)
            self.running = True

            self._log(f"Servidor iniciado en {self.ip}:{self.port}")

            while self.running:
                try:
                    self.server_socket.settimeout(1.0)
                    self.client_socket, addr = self.server_socket.accept()
                    self._log(f"Conexión aceptada desde {addr}")

                    while self.running:
                        try:
                            self.client_socket.settimeout(self.timeout)
                            data = self.client_socket.recv(1024)
                            if not data:
                                break

                            if self.frame_callback:
                                self.frame_callback("RECIBIDO", data)

                            response = self.process_request(data)

                            if response:
                                if self.frame_callback:
                                    self.frame_callback("ENVIADO", response)
                                self.client_socket.send(response)

                        except socket.timeout:
                            continue
                        except Exception as e:
                            self._log(f"Error en comunicación: {e}")
                            break

                    self.client_socket.close()
                    self._log(f"Conexión cerrada con {addr}")

                except socket.timeout:
                    continue
                except Exception as e:
                    self._log(f"Error al aceptar conexión: {e}")

        except Exception as e:
            self._log(f"Error al iniciar servidor: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def process_request(self, data):
        """Procesar petición Modbus - IMPLEMENTACIÓN COMPLETA"""
        try:
            if len(data) < 8:
                self._log(f"Trama demasiado corta: {len(data)} bytes")
                return b""

            # Extraer campos de la trama Modbus TCP
            transaction_id = int.from_bytes(data[0:2], byteorder='big')
            protocol_id = int.from_bytes(data[2:4], byteorder='big')
            length = int.from_bytes(data[4:6], byteorder='big')
            unit_id = data[6]
            function_code = data[7]

            self._log(f"Función: {function_code} (0x{function_code:02x}), Unit ID: {unit_id}")

            # Verificar protocol ID (debe ser 0 para Modbus)
            if protocol_id != 0:
                self._log(f"Protocol ID incorrecto: {protocol_id}")
                return b""

            # Verificar longitud
            if length != len(data) - 6:
                self._log(f"Longitud incorrecta: indicado {length}, real {len(data) - 6}")
                return b""

            if unit_id != self.slave_id:
                self._log(f"Unit ID incorrecto: esperado {self.slave_id}, recibido {unit_id}")
                return b""

            # Manejar TODAS las funciones Modbus
            if function_code == 1:  # Read Coils (FC 01)
                return self.handle_read_coils(data, transaction_id, unit_id)
            elif function_code == 2:  # Read Discrete Inputs (FC 02)
                return self.handle_read_discrete_inputs(data, transaction_id, unit_id)
            elif function_code == 3:  # Read Holding Registers (FC 03)
                return self.handle_read_holding_registers(data, transaction_id, unit_id)
            elif function_code == 4:  # Read Input Registers (FC 04)
                return self.handle_read_input_registers(data, transaction_id, unit_id)
            elif function_code == 5:  # Write Single Coil (FC 05)
                return self.handle_write_single_coil(data, transaction_id, unit_id)
            elif function_code == 6:  # Write Single Register (FC 06)
                return self.handle_write_single_register(data, transaction_id, unit_id)
            elif function_code == 15:  # Write Multiple Coils (FC 15)
                return self.handle_write_multiple_coils(data, transaction_id, unit_id)
            elif function_code == 16:  # Write Multiple Registers (FC 16)
                return self.handle_write_multiple_registers(data, transaction_id, unit_id)
            else:
                self._log(f"Función no soportada: {function_code}")
                return self.create_exception_response(transaction_id, unit_id, function_code, 1)

        except Exception as e:
            self._log(f"Error al procesar petición: {e}")
            return b""

    # === IMPLEMENTACIÓN DE TODAS LAS FUNCIONES MODBUS ===

    def handle_read_coils(self, data, transaction_id, unit_id):
        """Manejar lectura de Coils (FC 01)"""
        if len(data) < 12:
            self._log("Trama demasiado corta para Read Coils")
            return self.create_exception_response(transaction_id, unit_id, 1, 3)

        start_address = int.from_bytes(data[8:10], byteorder='big')
        coil_count = int.from_bytes(data[10:12], byteorder='big')

        self._log(f"Read Coils: addr={start_address}, count={coil_count}")

        # Verificar límites
        if start_address < 0 or start_address >= len(self.coils):
            self._log(f"Dirección de coil fuera de rango: {start_address}")
            return self.create_exception_response(transaction_id, unit_id, 1, 2)

        if start_address + coil_count > len(self.coils):
            self._log(f"Conteo de coils excede el rango: {start_address} + {coil_count}")
            return self.create_exception_response(transaction_id, unit_id, 1, 2)

        # Construir respuesta
        byte_count = (coil_count + 7) // 8
        response = bytearray()
        response.extend(transaction_id.to_bytes(2, byteorder='big'))
        response.extend((0).to_bytes(2, byteorder='big'))  # Protocol ID
        response.extend((byte_count + 3).to_bytes(2, byteorder='big'))  # Length
        response.append(unit_id)
        response.append(1)  # Código de función
        response.append(byte_count)

        # Empaquetar coils en bytes
        coils_bytes = bytearray(byte_count)
        for i in range(coil_count):
            if self.coils[start_address + i]:
                byte_index = i // 8
                bit_index = i % 8
                coils_bytes[byte_index] |= (1 << bit_index)

        response.extend(coils_bytes)
        return bytes(response)

    def handle_read_discrete_inputs(self, data, transaction_id, unit_id):
        """Manejar lectura de Discrete Inputs (FC 02)"""
        if len(data) < 12:
            self._log("Trama demasiado corta para Read Discrete Inputs")
            return self.create_exception_response(transaction_id, unit_id, 2, 3)

        start_address = int.from_bytes(data[8:10], byteorder='big')
        input_count = int.from_bytes(data[10:12], byteorder='big')

        self._log(f"Read Discrete Inputs: addr={start_address}, count={input_count}")

        # Verificar límites
        if start_address < 0 or start_address >= len(self.discrete_inputs):
            self._log(f"Dirección de discrete input fuera de rango: {start_address}")
            return self.create_exception_response(transaction_id, unit_id, 2, 2)

        if start_address + input_count > len(self.discrete_inputs):
            self._log(f"Conteo de discrete inputs excede el rango: {start_address} + {input_count}")
            return self.create_exception_response(transaction_id, unit_id, 2, 2)

        # Construir respuesta
        byte_count = (input_count + 7) // 8
        response = bytearray()
        response.extend(transaction_id.to_bytes(2, byteorder='big'))
        response.extend((0).to_bytes(2, byteorder='big'))  # Protocol ID
        response.extend((byte_count + 3).to_bytes(2, byteorder='big'))  # Length
        response.append(unit_id)
        response.append(2)  # Código de función
        response.append(byte_count)

        # Empaquetar inputs en bytes
        inputs_bytes = bytearray(byte_count)
        for i in range(input_count):
            if self.discrete_inputs[start_address + i]:
                byte_index = i // 8
                bit_index = i % 8
                inputs_bytes[byte_index] |= (1 << bit_index)

        response.extend(inputs_bytes)
        return bytes(response)

    def handle_read_holding_registers(self, data, transaction_id, unit_id):
        """Manejar lectura de Holding Registers (FC 03)"""
        if len(data) < 12:
            self._log("Trama demasiado corta para Read Holding Registers")
            return self.create_exception_response(transaction_id, unit_id, 3, 3)

        start_address = int.from_bytes(data[8:10], byteorder='big')
        register_count = int.from_bytes(data[10:12], byteorder='big')

        self._log(f"Read Holding Registers: addr={start_address}, count={register_count}")

        # Verificar límites
        if start_address < 0 or start_address >= len(self.holding_registers):
            self._log(f"Dirección de holding register fuera de rango: {start_address}")
            return self.create_exception_response(transaction_id, unit_id, 3, 2)

        if start_address + register_count > len(self.holding_registers):
            self._log(f"Conteo de holding registers excede el rango: {start_address} + {register_count}")
            return self.create_exception_response(transaction_id, unit_id, 3, 2)

        # Construir respuesta
        byte_count = register_count * 2
        response = bytearray()
        response.extend(transaction_id.to_bytes(2, byteorder='big'))
        response.extend((0).to_bytes(2, byteorder='big'))  # Protocol ID
        response.extend((byte_count + 3).to_bytes(2, byteorder='big'))  # Length
        response.append(unit_id)
        response.append(3)  # Código de función
        response.append(byte_count)

        # Agregar valores de los registros
        values = []
        for i in range(register_count):
            value = self.holding_registers[start_address + i]
            values.append(value)
            response.extend(value.to_bytes(2, byteorder='big'))

        self._log(f"Valores enviados: {values}")
        return bytes(response)

    def handle_read_input_registers(self, data, transaction_id, unit_id):
        """Manejar lectura de Input Registers (FC 04)"""
        if len(data) < 12:
            self._log("Trama demasiado corta para Read Input Registers")
            return self.create_exception_response(transaction_id, unit_id, 4, 3)

        start_address = int.from_bytes(data[8:10], byteorder='big')
        register_count = int.from_bytes(data[10:12], byteorder='big')

        self._log(f"Read Input Registers: addr={start_address}, count={register_count}")

        # Verificar límites
        if start_address < 0 or start_address >= len(self.input_registers):
            self._log(f"Dirección de input register fuera de rango: {start_address}")
            return self.create_exception_response(transaction_id, unit_id, 4, 2)

        if start_address + register_count > len(self.input_registers):
            self._log(f"Conteo de input registers excede el rango: {start_address} + {register_count}")
            return self.create_exception_response(transaction_id, unit_id, 4, 2)

        # Construir respuesta
        byte_count = register_count * 2
        response = bytearray()
        response.extend(transaction_id.to_bytes(2, byteorder='big'))
        response.extend((0).to_bytes(2, byteorder='big'))  # Protocol ID
        response.extend((byte_count + 3).to_bytes(2, byteorder='big'))  # Length
        response.append(unit_id)
        response.append(4)  # Código de función
        response.append(byte_count)

        # Agregar valores de los registros
        values = []
        for i in range(register_count):
            value = self.input_registers[start_address + i]
            values.append(value)
            response.extend(value.to_bytes(2, byteorder='big'))

        self._log(f"Valores enviados: {values}")
        return bytes(response)

    def handle_write_single_coil(self, data, transaction_id, unit_id):
        """Manejar escritura de Single Coil (FC 05)"""
        if len(data) < 12:
            self._log("Trama demasiado corta para Write Single Coil")
            return self.create_exception_response(transaction_id, unit_id, 5, 3)

        address = int.from_bytes(data[8:10], byteorder='big')
        value = int.from_bytes(data[10:12], byteorder='big')

        coil_state = (value == 0xFF00)
        self._log(f"Write Single Coil: addr={address}, value={coil_state}")

        # Verificar límites
        if address < 0 or address >= len(self.coils):
            self._log(f"Dirección de coil fuera de rango: {address}")
            return self.create_exception_response(transaction_id, unit_id, 5, 2)

        # Escribir valor
        self.coils[address] = coil_state
        self._log(f"Coil en dirección {address} establecido a {coil_state}")

        # Construir respuesta (eco de la petición)
        response = bytearray(data)
        return bytes(response)

    def handle_write_single_register(self, data, transaction_id, unit_id):
        """Manejar escritura de Single Register (FC 06)"""
        if len(data) < 12:
            self._log("Trama demasiado corta para Write Single Register")
            return self.create_exception_response(transaction_id, unit_id, 6, 3)

        address = int.from_bytes(data[8:10], byteorder='big')
        value = int.from_bytes(data[10:12], byteorder='big')

        self._log(f"Write Single Register: addr={address}, value={value}")

        # Verificar límites
        if address < 0 or address >= len(self.holding_registers):
            self._log(f"Dirección de holding register fuera de rango: {address}")
            return self.create_exception_response(transaction_id, unit_id, 6, 2)

        # Escribir valor
        self.holding_registers[address] = value
        self._log(f"Holding register en dirección {address} establecido a {value}")

        # Construir respuesta (eco de la petición)
        response = bytearray(data)
        return bytes(response)

    def handle_write_multiple_coils(self, data, transaction_id, unit_id):
        """Manejar escritura de Multiple Coils (FC 15)"""
        if len(data) < 13:
            self._log("Trama demasiado corta para Write Multiple Coils")
            return self.create_exception_response(transaction_id, unit_id, 15, 3)

        address = int.from_bytes(data[8:10], byteorder='big')
        coil_count = int.from_bytes(data[10:12], byteorder='big')
        byte_count = data[12]

        # Verificar que la trama tenga suficientes datos
        if len(data) < 13 + byte_count:
            self._log("Trama incompleta para Write Multiple Coils")
            return self.create_exception_response(transaction_id, unit_id, 15, 3)

        self._log(f"Write Multiple Coils: addr={address}, count={coil_count}")

        # Verificar límites
        if address < 0 or address >= len(self.coils):
            self._log(f"Dirección de coil fuera de rango: {address}")
            return self.create_exception_response(transaction_id, unit_id, 15, 2)

        if address + coil_count > len(self.coils):
            self._log(f"Conteo de coils excede el rango: {address} + {coil_count}")
            return self.create_exception_response(transaction_id, unit_id, 15, 2)

        # Extraer y escribir valores de coils
        for i in range(coil_count):
            byte_index = i // 8
            bit_index = i % 8
            byte_value = data[13 + byte_index]
            coil_state = bool(byte_value & (1 << bit_index))
            self.coils[address + i] = coil_state

        self._log(f"{coil_count} coils escritos desde dirección {address}")

        # Construir respuesta
        response = bytearray()
        response.extend(transaction_id.to_bytes(2, byteorder='big'))
        response.extend((0).to_bytes(2, byteorder='big'))  # Protocol ID
        response.extend((6).to_bytes(2, byteorder='big'))  # Length
        response.append(unit_id)
        response.append(15)  # Código de función
        response.extend(address.to_bytes(2, byteorder='big'))
        response.extend(coil_count.to_bytes(2, byteorder='big'))

        return bytes(response)

    def handle_write_multiple_registers(self, data, transaction_id, unit_id):
        """Manejar escritura de Multiple Registers (FC 16)"""
        if len(data) < 13:
            self._log("Trama demasiado corta para Write Multiple Registers")
            return self.create_exception_response(transaction_id, unit_id, 16, 3)

        address = int.from_bytes(data[8:10], byteorder='big')
        register_count = int.from_bytes(data[10:12], byteorder='big')
        byte_count = data[12]

        # Verificar que la trama tenga suficientes datos
        if len(data) < 13 + byte_count:
            self._log("Trama incompleta para Write Multiple Registers")
            return self.create_exception_response(transaction_id, unit_id, 16, 3)

        self._log(f"Write Multiple Registers: addr={address}, count={register_count}")

        # Verificar límites
        if address < 0 or address >= len(self.holding_registers):
            self._log(f"Dirección de holding register fuera de rango: {address}")
            return self.create_exception_response(transaction_id, unit_id, 16, 2)

        if address + register_count > len(self.holding_registers):
            self._log(f"Conteo de holding registers excede el rango: {address} + {register_count}")
            return self.create_exception_response(transaction_id, unit_id, 16, 2)

        # Extraer y escribir valores de registros
        values = []
        for i in range(register_count):
            value = int.from_bytes(data[13 + i*2:15 + i*2], byteorder='big')
            self.holding_registers[address + i] = value
            values.append(value)

        self._log(f"{register_count} holding registers escritos desde dirección {address}: {values}")

        # Construir respuesta
        response = bytearray()
        response.extend(transaction_id.to_bytes(2, byteorder='big'))
        response.extend((0).to_bytes(2, byteorder='big'))  # Protocol ID
        response.extend((6).to_bytes(2, byteorder='big'))  # Length
        response.append(unit_id)
        response.append(16)  # Código de función
        response.extend(address.to_bytes(2, byteorder='big'))
        response.extend(register_count.to_bytes(2, byteorder='big'))

        return bytes(response)

    def create_exception_response(self, transaction_id, unit_id, function_code, exception_code):
        """Crear respuesta de excepción"""
        response = bytearray()
        response.extend(transaction_id.to_bytes(2, byteorder='big'))
        response.extend((0).to_bytes(2, byteorder='big'))  # Protocol ID
        response.extend((2).to_bytes(2, byteorder='big'))  # Length
        response.append(unit_id)
        response.append(function_code | 0x80)  # Function code con bit de excepción
        response.append(exception_code)

        self._log(f"Excepción: función={function_code}, código={exception_code}")
        return bytes(response)

    def stop(self):
        """Detener servidor"""
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
        self._log("Servidor detenido")
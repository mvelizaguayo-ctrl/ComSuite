#!/usr/bin/env python3
"""
Slave Modbus RTU - Implementación limpia para ComSuite
Clase pura de comunicación sin rutinas de prueba.
"""

import serial
import threading
import time
import struct

class ModbusSlaveRTU:
    """Slave Modbus RTU completo con todas las funciones Modbus"""

    def __init__(self, port, baudrate=9600, parity='N', stopbits=1, bytesize=8, slave_id=1):
        self.port = port
        self.baudrate = baudrate
        self.parity = parity
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.slave_id = slave_id
        self.serial_port = None
        self.connected = False
        self.running = False

        # Mapeo de paridad
        self.parity_map = {
            'N': serial.PARITY_NONE,
            'E': serial.PARITY_EVEN,
            'O': serial.PARITY_ODD
        }

        # Registros
        self.coils = [False] * 10000
        self.discrete_inputs = [False] * 10000
        self.input_registers = [0] * 10000
        self.holding_registers = [0] * 10000

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
            self.log_callback(f"Slave RTU: {message}")
        else:
            print(f"Slave RTU: {message}")

    def connect(self):
        """Conectar al puerto serie"""
        try:
            self.serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                parity=self.parity_map[self.parity],
                stopbits=self.stopbits,
                bytesize=self.bytesize,
                timeout=1.0
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
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc

    def start(self):
        """Iniciar servidor RTU"""
        if not self.connected and not self.connect():
            return False

        self.running = True
        self._log(f"Iniciando servidor RTU slave ID={self.slave_id}")

        def server_loop():
            buffer = bytearray()

            while self.running:
                try:
                    if self.serial_port.in_waiting > 0:
                        data = self.serial_port.read(self.serial_port.in_waiting)
                        buffer.extend(data)

                        # Procesar tramas completas
                        while len(buffer) >= 4:  # Mínimo: uid + fc + data(1) + crc
                            # Verificar CRC
                            if len(buffer) >= 4:
                                received_crc = int.from_bytes(buffer[-2:], byteorder='little')
                                calculated_crc = self.calculate_crc(buffer[:-2])

                                if received_crc == calculated_crc:
                                    # Trama completa, procesar
                                    frame = buffer[:-2]  # Quitar CRC
                                    buffer = buffer[len(frame) + 2:]  # Remover de buffer

                                    if self.frame_callback:
                                        self.frame_callback("RECIBIDO", frame + received_crc.to_bytes(2, byteorder='little'))

                                    # Procesar petición
                                    response = self.process_request(frame)

                                    if response:
                                        # Agregar CRC y enviar
                                        crc = self.calculate_crc(response)
                                        response_with_crc = response + crc.to_bytes(2, byteorder='little')

                                        if self.frame_callback:
                                            self.frame_callback("ENVIADO", response_with_crc)

                                        self.serial_port.write(response_with_crc)
                                        self.serial_port.flush()
                                    else:
                                        # CRC inválido, remover primer byte y continuar
                                        buffer.pop(0)
                                else:
                                    break

                except Exception as e:
                    self._log(f"Error en servidor: {e}")
                    time.sleep(0.1)

        # Iniciar servidor en hilo separado
        server_thread = threading.Thread(target=server_loop, daemon=True)
        server_thread.start()

        return True

    def process_request(self, frame):
        """Procesar petición como slave"""
        if len(frame) < 2:
            return None

        request_unit_id = frame[0]
        function_code = frame[1]

        if request_unit_id != self.slave_id:
            return None

        # Manejar funciones Modbus
        if function_code == 1:  # Read Coils (FC 01)
            return self.handle_read_coils(frame)
        elif function_code == 2:  # Read Discrete Inputs (FC 02)
            return self.handle_read_discrete_inputs(frame)
        elif function_code == 3:  # Read Holding Registers (FC 03)
            return self.handle_read_holding_registers(frame)
        elif function_code == 4:  # Read Input Registers (FC 04)
            return self.handle_read_input_registers(frame)
        elif function_code == 5:  # Write Single Coil (FC 05)
            return self.handle_write_single_coils(frame)
        elif function_code == 6:  # Write Single Register (FC 06)
            return self.handle_write_single_register(frame)
        elif function_code == 15:  # Write Multiple Coils (FC 15)
            return self.handle_write_multiple_coils(frame)
        elif function_code == 16:  # Write Multiple Registers (FC 16)
            return self.handle_write_multiple_registers(frame)
        else:
            self._log(f"Función no soportada: {function_code}")
            return bytearray([self.slave_id, function_code | 0x80, 1])  # Excepción

    # === IMPLEMENTACIÓN DE FUNCIONES MODBUS ===

    def handle_read_holding_registers(self, frame):
        """Manejar lectura de Holding Registers (FC 03)"""
        if len(frame) < 6:
            return None

        start_address = struct.unpack('>H', frame[2:4])[0]
        register_count = struct.unpack('>H', frame[4:6])[0]

        self._log(f"Read Holding Registers: addr={start_address}, count={register_count}")

        # Verificar límites
        if start_address < 0 or start_address >= len(self.holding_registers):
            return bytearray([self.slave_id, 3 | 0x80, 2])  # Excepción

        if start_address + register_count > len(self.holding_registers):
            return bytearray([self.slave_id, 3 | 0x80, 2])  # Excepción

        # Construir respuesta
        byte_count = register_count * 2
        response = bytearray([self.slave_id, 3, byte_count])

        # Agregar valores de los registros
        values = []
        for i in range(register_count):
            value = self.holding_registers[start_address + i]
            values.append(value)
            response.extend(value.to_bytes(2, byteorder='big'))

        self._log(f"Valores enviados: {values}")
        return response

    def handle_write_single_register(self, frame):
        """Manejar escritura de Single Register (FC 06)"""
        if len(frame) < 6:
            return None

        address = struct.unpack('>H', frame[2:4])[0]
        value = struct.unpack('>H', frame[4:6])[0]

        self._log(f"Write Single Register: addr={address}, value={value}")

        # Verificar límites
        if address < 0 or address >= len(self.holding_registers):
            return bytearray([self.slave_id, 6 | 0x80, 2])  # Excepción

        # Escribir valor
        self.holding_registers[address] = value

        # Responder con eco
        return frame

    def handle_read_coils(self, frame):
        """Manejar lectura de Coils (FC 01)"""
        if len(frame) < 6:
            return None

        start_address = struct.unpack('>H', frame[2:4])[0]
        coil_count = struct.unpack('>H', frame[4:6])[0]

        self._log(f"Read Coils: addr={start_address}, count={coil_count}")

        # Verificar límites
        if start_address < 0 or start_address >= len(self.coils):
            return bytearray([self.slave_id, 1 | 0x80, 2])  # Excepción

        if start_address + coil_count > len(self.coils):
            return bytearray([self.slave_id, 1 | 0x80, 2])  # Excepción

        # Construir respuesta
        byte_count = (coil_count + 7) // 8
        response = bytearray([self.slave_id, 1, byte_count])

        # Empaquetar coils en bytes
        coils_bytes = bytearray(byte_count)
        for i in range(coil_count):
            if self.coils[start_address + i]:
                byte_index = i // 8
                bit_index = i % 8
                coils_bytes[byte_index] |= (1 << bit_index)

        response.extend(coils_bytes)
        return response

    def handle_read_discrete_inputs(self, frame):
        """Manejar lectura de Discrete Inputs (FC 02)"""
        if len(frame) < 6:
            return None

        start_address = struct.unpack('>H', frame[2:4])[0]
        input_count = struct.unpack('>H', frame[4:6])[0]

        self._log(f"Read Discrete Inputs: addr={start_address}, count={input_count}")

        # Verificar límites
        if start_address < 0 or start_address >= len(self.discrete_inputs):
            return bytearray([self.slave_id, 2 | 0x80, 2])  # Excepción

        if start_address + input_count > len(self.discrete_inputs):
            return bytearray([self.slave_id, 2 | 0x80, 2])  # Excepción

        # Construir respuesta
        byte_count = (input_count + 7) // 8
        response = bytearray([self.slave_id, 2, byte_count])

        # Empaquetar inputs en bytes
        inputs_bytes = bytearray(byte_count)
        for i in range(input_count):
            if self.discrete_inputs[start_address + i]:
                byte_index = i // 8
                bit_index = i % 8
                inputs_bytes[byte_index] |= (1 << bit_index)

        response.extend(inputs_bytes)
        return response

    def handle_read_input_registers(self, frame):
        """Manejar lectura de Input Registers (FC 04)"""
        if len(frame) < 6:
            return None

        start_address = struct.unpack('>H', frame[2:4])[0]
        register_count = struct.unpack('>H', frame[4:6])[0]

        self._log(f"Read Input Registers: addr={start_address}, count={register_count}")

        # Verificar límites
        if start_address < 0 or start_address >= len(self.input_registers):
            return bytearray([self.slave_id, 4 | 0x80, 2])  # Excepción

        if start_address + register_count > len(self.input_registers):
            return bytearray([self.slave_id, 4 | 0x80, 2])  # Excepción

        # Construir respuesta
        byte_count = register_count * 2
        response = bytearray([self.slave_id, 4, byte_count])

        # Agregar valores de los registros
        values = []
        for i in range(register_count):
            value = self.input_registers[start_address + i]
            values.append(value)
            response.extend(value.to_bytes(2, byteorder='big'))

        self._log(f"Valores enviados: {values}")
        return response

    def handle_write_single_coils(self, frame):
        """Manejar escritura de Single Coil (FC 05)"""
        if len(frame) < 6:
            return None

        address = struct.unpack('>H', frame[2:4])[0]
        value = struct.unpack('>H', frame[4:6])[0]

        coil_state = (value == 0xFF00)
        self._log(f"Write Single Coil: addr={address}, value={coil_state}")

        # Verificar límites
        if address < 0 or address >= len(self.coils):
            return bytearray([self.slave_id, 5 | 0x80, 2])  # Excepción

        # Escribir valor
        self.coils[address] = coil_state

        # Responder con eco
        return frame

    def handle_write_multiple_coils(self, frame):
        """Manejar escritura de Multiple Coils (FC 15)"""
        if len(frame) < 7:
            return None

        address = struct.unpack('>H', frame[2:4])[0]
        coil_count = struct.unpack('>H', frame[4:6])[0]
        byte_count = frame[6]

        self._log(f"Write Multiple Coils: addr={address}, count={coil_count}")

        # Verificar límites
        if address < 0 or address >= len(self.coils):
            return bytearray([self.slave_id, 15 | 0x80, 2])  # Excepción

        if address + coil_count > len(self.coils):
            return bytearray([self.slave_id, 15 | 0x80, 2])  # Excepción

        # Extraer y escribir valores de coils
        for i in range(coil_count):
            byte_index = i // 8
            bit_index = i % 8
            byte_value = frame[7 + byte_index]
            coil_state = bool(byte_value & (1 << bit_index))
            self.coils[address + i] = coil_state

        # Construir respuesta
        response = bytearray([self.slave_id, 15])
        response.extend(struct.pack('>HH', address, coil_count))

        return response

    def handle_write_multiple_registers(self, frame):
        """Manejar escritura de Multiple Registers (FC 16)"""
        if len(frame) < 7:
            return None

        address = struct.unpack('>H', frame[2:4])[0]
        register_count = struct.unpack('>H', frame[4:6])[0]
        byte_count = frame[6]

        self._log(f"Write Multiple Registers: addr={address}, count={register_count}")

        # Verificar límites
        if address < 0 or address >= len(self.holding_registers):
            return bytearray([self.slave_id, 16 | 0x80, 2])  # Excepción

        if address + register_count > len(self.holding_registers):
            return bytearray([self.slave_id, 16 | 0x80, 2])  # Excepción

        # Extraer y escribir valores de registros
        values = []
        for i in range(register_count):
            value = struct.unpack('>H', frame[7 + i*2:9 + i*2])[0]
            self.holding_registers[address + i] = value
            values.append(value)

        self._log(f"Valores escritos: {values}")

        # Construir respuesta
        response = bytearray([self.slave_id, 16])
        response.extend(struct.pack('>HH', address, register_count))

        return response

    def stop(self):
        """Detener servidor"""
        self.running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self._log("Servidor detenido")
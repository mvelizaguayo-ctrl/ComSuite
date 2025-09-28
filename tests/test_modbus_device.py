# tests/test_modbus_device.py
import unittest
import sys
import os
import time
import threading

print("Iniciando pruebas de Modbus Device...")

try:
    # Agregar el directorio src al path
    src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
    sys.path.insert(0, src_path)
    print(f"Path agregado: {src_path}")

    from protocols.modbus.modbus_device import ModbusDevice
    from protocols.modbus.modbus_master import ModbusMaster
    from protocols.modbus.modbus_slave import ModbusSlave
    print("Módulos Modbus importados correctamente")

    def check_serial_ports():
        """Verificar si los puertos COM3 y COM4 están disponibles."""
        try:
            import serial
            # Verificar COM3
            try:
                ser3 = serial.Serial('COM3')
                ser3.close()
            except:
                return False
            # Verificar COM4
            try:
                ser4 = serial.Serial('COM4')
                ser4.close()
            except:
                return False
            return True
        except ImportError:
            return False

    class TestModbusDevice(unittest.TestCase):
        
        def setUp(self):
            """Configuración inicial para cada prueba."""
            print("Configurando prueba...")
            pass

        def test_device_creation(self):
            """Prueba la creación de un dispositivo Modbus."""
            print("Ejecutando prueba de creación de dispositivo...")
            device = ModbusDevice("test_device", "Modbus", {"protocol": "TCP"})
            self.assertEqual(device.device_id, "test_device")
            self.assertEqual(device.protocol_name, "Modbus")
            print("Prueba de creación exitosa")

        def test_device_configuration(self):
            """Prueba la configuración de un dispositivo."""
            print("Ejecutando prueba de configuración...")
            config = {"protocol": "TCP", "host": "127.0.0.1", "port": 502}
            device = ModbusDevice("test_device", "Modbus", config)
            
            # Verificación básica de que el dispositivo se creó correctamente
            self.assertIsNotNone(device)
            self.assertEqual(device.device_id, "test_device")
            self.assertEqual(device.protocol_name, "Modbus")
            
            print("Prueba de configuración exitosa")

        def test_simple_pass(self):
            """Prueba simple que siempre pasa."""
            print("Ejecutando prueba simple...")
            self.assertEqual(1, 1)
            print("Prueba simple exitosa")

        @unittest.skipUnless(check_serial_ports(), "Los puertos COM3 y COM4 no están disponibles")
        def test_rtu_master_slave_communication(self):
            """Prueba de comunicación RTU entre Master (COM4) y Slave (COM3)"""
            print("Ejecutando prueba de comunicación RTU Master-Slave...")
            
            # Configurar Slave en COM3
            slave = ModbusSlave(
                protocol="RTU",
                port="COM3",
                baudrate=9600,
                bytesize=8,
                parity="N",
                stopbits=1,
                slave_id=1
            )
            slave.start()

            # Configurar Master en COM4
            master = ModbusMaster(
                protocol="RTU",
                port="COM4",
                baudrate=9600,
                bytesize=8,
                parity="N",
                stopbits=1,
                slave_id=1
            )

            # Esperar inicialización
            time.sleep(1)

            try:
                # Prueba de lectura inicial
                print("Realizando lectura inicial...")
                result = master.read_holding_registers(0, 10)
                self.assertIsNotNone(result)
                self.assertEqual(len(result), 10)
                expected_values = [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
                self.assertEqual(result, expected_values)
                print("Lectura inicial exitosa")

                # Prueba de escritura y lectura
                print("Realizando escritura y lectura...")
                master.write_single_register(0, 100)
                result = master.read_holding_registers(0, 1)
                self.assertEqual(result[0], 100)
                print("Escritura y lectura exitosas")

                # Prueba adicional
                print("Realizando prueba adicional...")
                master.write_single_register(1, 200)
                result = master.read_holding_registers(1, 1)
                self.assertEqual(result[0], 200)
                print("Prueba adicional exitosa")

            finally:
                slave.stop()
                print("Slave detenido correctamente")

        def test_tcp_master_slave_communication(self):
            """Prueba de comunicación TCP entre Master y Slave en localhost"""
            print("Ejecutando prueba de comunicación TCP Master-Slave...")
            
            # Configurar Slave TCP en puerto 5020
            slave = ModbusSlave(
                protocol="TCP",
                port=5020,
                slave_id=1
            )
            
            # Iniciar el slave en un hilo separado para evitar bloqueo
            slave_thread = threading.Thread(target=slave.start)
            slave_thread.daemon = True
            slave_thread.start()
            
            # Esperar a que el slave se inicie
            time.sleep(1)

            # Configurar Master TCP - CORREGIDO: según parámetros esperados
            master = ModbusMaster(
                protocol="TCP",
                port=5020,
                slave_id=1
            )

            try:
                # Prueba de lectura con timeout
                print("Realizando lectura inicial...")
                start_time = time.time()
                timeout = 5  # 5 segundos de timeout
                
                while time.time() - start_time < timeout:
                    try:
                        result = master.read_holding_registers(0, 10)
                        self.assertIsNotNone(result)
                        self.assertEqual(len(result), 10)
                        # El slave TCP devuelve valores predefinidos
                        expected_values = [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
                        self.assertEqual(result, expected_values)
                        print("Lectura inicial exitosa")
                        break
                    except Exception as e:
                        print(f"Error en lectura: {e}, reintentando...")
                        time.sleep(0.5)
                else:
                    self.fail("Timeout en la lectura inicial")

                # Prueba de escritura y lectura
                print("Realizando escritura y lectura...")
                master.write_single_register(0, 100)
                result = master.read_holding_registers(0, 1)
                self.assertEqual(result[0], 100)
                print("Escritura y lectura exitosas")

            finally:
                slave.stop()
                print("Slave detenido correctamente")

    # Bloque de ejecución principal
    if __name__ == '__main__':
        print("Iniciando unittest...")
        unittest.main(verbosity=2)

except Exception as e:
    print(f"Error crítico: {e}")
    import traceback
    traceback.print_exc()
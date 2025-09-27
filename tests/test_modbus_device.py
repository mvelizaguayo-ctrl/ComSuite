# tests/test_modbus_device.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from protocols.modbus.modbus_device import ModbusDevice
from protocols.modbus.master_rtu import ModbusMasterRTU

def test_modbus_device():
    """Prueba todos los métodos del ModbusDevice"""
    print("=== Prueba de ModbusDevice ===")
    
    # Crear master RTU
    master = ModbusMasterRTU(port='COM3')
    master.set_log_callback(lambda msg: print(f'[Master] {msg}'))
    
    if not master.connect():
        print("❌ No se pudo conectar al master")
        return False
    
    # Crear dispositivo
    device = ModbusDevice(
        device_id="test_device",
        protocol_name="Modbus",
        master_instance=master
    )
    
    print(f"✅ Dispositivo creado: {device.device_id}")
    print(f"✅ Protocolo: {device.protocol_name}")
    print(f"✅ Estado: {device.status}")
    
    # Probar todos los métodos
    print("\n1. Probando read_registers...")
    data = device.read_registers(0, 5)
    print(f"   Registros leídos: {data}")
    
    print("\n2. Probando write_registers...")
    success = device.write_registers(0, [999, 888, 777])
    print(f"   Escritura exitosa: {success}")
    
    print("\n3. Probando read_coils...")
    coils = device.read_coils(0, 5)
    print(f"   Coils leídos: {coils}")
    
    print("\n4. Probando write_coils...")
    success = device.write_coils(0, [True, False, True])
    print(f"   Escritura de coils exitosa: {success}")
    
    print("\n5. Probando read_discrete_inputs...")
    inputs = device.read_discrete_inputs(0, 5)
    print(f"   Discrete inputs leídos: {inputs}")
    
    print("\n6. Probando read_input_registers...")
    input_regs = device.read_input_registers(0, 5)
    print(f"   Input registers leídos: {input_regs}")
    
    print("\n7. Probando get_info...")
    info = device.get_info()
    print(f"   Info: {info}")
    
    print("\n8. Probando get_last_error...")
    error = device.get_last_error()
    print(f"   Último error: {error}")
    
    # Desconectar
    master.disconnect()
    print("✅ Prueba completada")
    return True

if __name__ == "__main__":
    test_modbus_device()
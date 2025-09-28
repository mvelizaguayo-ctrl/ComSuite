# test_simple.py
print("¡El archivo se está ejecutando!")

import sys
import os

print(f"Directorio actual: {os.getcwd()}")
print(f"Python path: {sys.path}")

try:
    # Agregar el directorio src al path
    src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
    sys.path.insert(0, src_path)
    print(f"Path agregado: {src_path}")
    
    # Intentar importar un módulo básico
    from protocols.modbus.modbus_device import ModbusDevice
    print("ModbusDevice importado correctamente")
    
except Exception as e:
    print(f"Error en importación: {e}")
    import traceback
    traceback.print_exc()
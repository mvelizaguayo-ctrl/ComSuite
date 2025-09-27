# tests/test_interfaces.py
# Ruta completa: C:\Users\manue\ComSuite\tests\test_interfaces.py

import sys
import os

# Agregar la ruta src al path para importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from protocols.base_protocol.protocol_interface import ProtocolInterface
from protocols.base_protocol.device_interface import DeviceInterface, DeviceStatus

def test_protocol_interface():
    """Prueba que la interfaz ProtocolInterface esté correctamente definida"""
    print("=== Probando ProtocolInterface ===")
    
    # Verificar que es una clase abstracta
    try:
        # Esto debería fallar porque es abstracta
        protocol = ProtocolInterface()
        print("❌ ERROR: Se pudo instanciar ProtocolInterface directamente")
        return False
    except TypeError:
        print("✅ ProtocolInterface es correctamente abstracta")
    
    # Verificar métodos abstractos
    abstract_methods = ProtocolInterface.__abstractmethods__
    expected_methods = {
        'name', 'version', 'connect', 'disconnect', 'is_connected',
        'read_data', 'write_data', 'get_devices', 'get_device_info', 'validate_config'
    }
    
    if abstract_methods == expected_methods:
        print("✅ ProtocolInterface tiene todos los métodos abstractos requeridos")
        return True
    else:
        print(f"❌ Faltan métodos abstractos. Esperados: {expected_methods}, Encontrados: {abstract_methods}")
        return False

def test_device_interface():
    """Prueba que la interfaz DeviceInterface esté correctamente definida"""
    print("\n=== Probando DeviceInterface ===")
    
    # Verificar que es una clase abstracta
    try:
        device = DeviceInterface()
        print("❌ ERROR: Se pudo instanciar DeviceInterface directamente")
        return False
    except TypeError:
        print("✅ DeviceInterface es correctamente abstracta")
    
    # Verificar métodos abstractos
    abstract_methods = DeviceInterface.__abstractmethods__
    expected_methods = {
        'device_id', 'protocol_name', 'status', 'get_info',
        'read_registers', 'write_registers', 'read_coils', 'write_coils',
        'get_last_error', 'is_available', 'get_config', 'update_config'
    }
    
    if abstract_methods == expected_methods:
        print("✅ DeviceInterface tiene todos los métodos abstractos requeridos")
        
        # Verificar DeviceStatus enum
        if hasattr(DeviceStatus, 'DISCONNECTED') and hasattr(DeviceStatus, 'CONNECTED'):
            print("✅ DeviceStatus enum está correctamente definido")
            return True
        else:
            print("❌ DeviceStatus enum no está correctamente definido")
            return False
    else:
        print(f"❌ Faltan métodos abstractos. Esperados: {expected_methods}, Encontrados: {abstract_methods}")
        return False

def test_imports():
    """Prueba que las importaciones funcionen correctamente"""
    print("\n=== Probando Importaciones ===")
    
    try:
        from protocols.base_protocol import ProtocolInterface, DeviceInterface, DeviceStatus
        print("✅ Importación desde protocols.base_protocol exitosa")
        
        # Verificar tipos
        if hasattr(ProtocolInterface, '__abstractmethods__'):
            print("✅ ProtocolInterface importada correctamente")
        
        if hasattr(DeviceInterface, '__abstractmethods__'):
            print("✅ DeviceInterface importada correctamente")
            
        if hasattr(DeviceStatus, 'DISCONNECTED'):
            print("✅ DeviceStatus importada correctamente")
            
        return True
    except ImportError as e:
        print(f"❌ Error en importación: {e}")
        return False

def main():
    """Ejecuta todas las pruebas de interfaces"""
    print("ComSuite - Pruebas de Interfaces Comunes")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_protocol_interface,
        test_device_interface
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"RESULTADO: {passed}/{total} pruebas pasadas")
    
    if passed == total:
        print("🎉 ¡Todas las interfaces están correctamente implementadas!")
        return True
    else:
        print("❌ Hay problemas en las interfaces que deben corregirse")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
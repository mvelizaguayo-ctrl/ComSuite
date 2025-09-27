# tests/test_modbus_plugin.py
# Ruta completa: C:\Users\manue\ComSuite\tests\test_modbus_plugin.py

import sys
import os

# Agregar la ruta src al path para importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.plugin_loader import PluginLoader

def test_modbus_plugin():
    """Prueba el plugin Modbus"""
    print("=== Probando Plugin Modbus ===")
    
    # Crear plugin loader
    loader = PluginLoader()
    
    # Descubrir y cargar plugins
    print("1. Descubriendo y cargando plugins...")
    if loader.discover_and_load_plugins():
        print("✅ Plugins descubiertos y cargados")
    else:
        print("❌ No se pudieron cargar los plugins")
        return False
    
    # Verificar que ModbusPlugin fue cargado
    loaded_plugins = loader.get_loaded_plugins()
    print(f"Plugins cargados: {loaded_plugins}")
    
    if "ModbusPlugin" not in loaded_plugins:
        print("❌ ModbusPlugin no fue cargado")
        return False
    
    print("✅ ModbusPlugin cargado correctamente")
    
    # Obtener información del plugin
    plugin_info = loader.get_plugin_info("ModbusPlugin")
    print(f"Información del plugin: {plugin_info}")
    
    # Obtener protocolos cargados
    loaded_protocols = loader.get_loaded_protocols()
    print(f"Protocolos cargados: {list(loaded_protocols.keys())}")
    
    if "ModbusPlugin" not in loaded_protocols:
        print("❌ Protocolo Modbus no está disponible")
        return False
    
    print("✅ Protocolo Modbus disponible")
    
    # Probar creación de instancia del protocolo
    print("\n2. Probando creación de instancia del protocolo...")
    protocol_instance = loader.create_protocol("ModbusPlugin")
    
    if protocol_instance:
        print("✅ Instancia del protocolo Modbus creada")
        print(f"   Nombre: {protocol_instance.name}")
        print(f"   Versión: {protocol_instance.version}")
    else:
        print("❌ No se pudo crear la instancia del protocolo")
        return False
    
    # Probar validación de configuración
    print("\n3. Probando validación de configuración...")
    
    # Configuración TCP válida
    tcp_config = {
        'mode': 'master',
        'protocol_type': 'TCP',
        'ip': '127.0.0.1',
        'port': 502,
        'slave_id': 1
    }
    
    if protocol_instance.validate_config(tcp_config):
        print("✅ Configuración TCP válida")
    else:
        print("❌ Configuración TCP inválida")
        return False
    
    # Configuración RTU válida
    rtu_config = {
        'mode': 'master',
        'protocol_type': 'RTU',
        'port': 'COM3',
        'baudrate': 9600,
        'slave_id': 1
    }
    
    if protocol_instance.validate_config(rtu_config):
        print("✅ Configuración RTU válida")
    else:
        print("❌ Configuración RTU inválida")
        return False
    
    # Configuración inválida
    invalid_config = {
        'mode': 'invalid_mode',
        'protocol_type': 'TCP'
    }
    
    if not protocol_instance.validate_config(invalid_config):
        print("✅ Configuración inválida correctamente rechazada")
    else:
        print("❌ Configuración inválida fue aceptada")
        return False
    
    print("\n✅ Todas las pruebas del ModbusPlugin pasaron")
    return True

def main():
    """Ejecuta las pruebas del ModbusPlugin"""
    print("ComSuite - Pruebas del ModbusPlugin")
    print("=" * 50)
    
    if test_modbus_plugin():
        print("\n🎉 ¡ModbusPlugin funciona correctamente!")
        print("📋 El plugin Modbus está listo para integrarse con el CommunicationEngine")
        return True
    else:
        print("\n❌ Hay problemas en el ModbusPlugin")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
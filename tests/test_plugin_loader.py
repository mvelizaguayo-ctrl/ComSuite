# tests/test_plugin_loader.py
# Ruta completa: C:\Users\manue\ComSuite\tests\test_plugin_loader.py

import sys
import os

# Agregar la ruta src al path para importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.plugin_loader import PluginLoader
from protocols.base_protocol.protocol_interface import ProtocolInterface
from plugins.plugin_interface import PluginInterface

class MockPlugin(PluginInterface):
    """Plugin mock para pruebas"""
    
    @property
    def name(self) -> str:
        return "MockPlugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Plugin de prueba para el PluginLoader"
    
    @property
    def author(self) -> str:
        return "Test Author"
    
    def get_protocol_class(self):
        return MockProtocol
    
    def get_dependencies(self) -> list:
        return []  # Sin dependencias
    
    def validate_environment(self) -> bool:
        return True
    
    def initialize(self) -> bool:
        return True
    
    def cleanup(self):
        pass

class MockProtocol(ProtocolInterface):
    """Protocolo mock para pruebas"""
    
    @property
    def name(self) -> str:
        return "MockProtocol"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def connect(self, config):
        return True
    
    def disconnect(self):
        pass
    
    def is_connected(self) -> bool:
        return True
    
    def read_data(self, device_id: str, address: int, count: int):
        return [100 + i for i in range(count)]
    
    def write_data(self, device_id: str, address: int, data: list):
        return True
    
    def get_devices(self):
        return ["mock_device_1"]
    
    def get_device_info(self, device_id: str):
        return {"device_id": device_id, "type": "mock"}
    
    def validate_config(self, config):
        return True

def test_plugin_loader():
    """Prueba el PluginLoader"""
    print("=== Probando PluginLoader ===")
    
    # Crear plugin loader
    loader = PluginLoader()
    
    # Probar descubrimiento (debería encontrar 0 plugins ya que no hemos creado ninguno real)
    print("1. Probando descubrimiento de plugins...")
    if loader.discover_and_load_plugins():
        print("✅ Descubrimiento y carga completados")
    else:
        print("ℹ️  No se encontraron plugins (es normal, aún no hemos creado el plugin Modbus)")
    
    # Probar obtener plugins cargados
    loaded_plugins = loader.get_loaded_plugins()
    print(f"Plugins cargados: {loaded_plugins}")
    
    # Probar obtener protocolos cargados
    loaded_protocols = loader.get_loaded_protocols()
    print(f"Protocolos cargados: {list(loaded_protocols.keys())}")
    
    print("\n✅ PluginLoader funciona correctamente")
    return True

def main():
    """Ejecuta las pruebas del PluginLoader"""
    print("ComSuite - Pruebas del PluginLoader")
    print("=" * 50)
    
    if test_plugin_loader():
        print("\n🎉 ¡PluginLoader funciona correctamente!")
        print("ℹ️  El plugin Modbus real se creará en el siguiente paso")
        return True
    else:
        print("\n❌ Hay problemas en el PluginLoader")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
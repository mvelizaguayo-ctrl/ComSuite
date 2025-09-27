# tests/test_communication_engine.py
# Ruta completa: C:\Users\manue\ComSuite\tests\test_communication_engine.py

import sys
import os

# Agregar la ruta src al path para importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.communication_engine import CommunicationEngine
from protocols.base_protocol.protocol_interface import ProtocolInterface
from protocols.base_protocol.device_interface import DeviceInterface, DeviceStatus

class MockProtocol(ProtocolInterface):
    """Protocolo mock para pruebas"""
    
    def __init__(self, name="MockProtocol"):
        self._name = name
        self._version = "1.0.0"
        self._connected = False
        self._devices = ["device1", "device2"]
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def version(self) -> str:
        return self._version
    
    def connect(self, config):
        self._connected = True
        return True
    
    def disconnect(self):
        self._connected = False
    
    def is_connected(self) -> bool:
        return self._connected
    
    def read_data(self, device_id: str, address: int, count: int):
        return [100 + i for i in range(count)]
    
    def write_data(self, device_id: str, address: int, data: list):
        return True
    
    def get_devices(self):
        return self._devices
    
    def get_device_info(self, device_id: str):
        return {
            "device_id": device_id,
            "type": "mock_device",
            "status": "online"
        }
    
    def validate_config(self, config):
        return True

def test_communication_engine():
    """Prueba el CommunicationEngine con un protocolo mock"""
    print("=== Probando CommunicationEngine ===")
    
    # Crear motor de comunicaciones
    engine = CommunicationEngine()
    
    # Crear protocolo mock
    mock_protocol = MockProtocol()
    
    # Probar registro de protocolo
    print("1. Registrando protocolo...")
    if engine.register_protocol(mock_protocol):
        print("✅ Protocolo registrado correctamente")
    else:
        print("❌ Error al registrar protocolo")
        return False
    
    # Probar lista de protocolos
    protocols = engine.get_protocols()
    if mock_protocol.name in protocols:
        print("✅ Protocolo aparece en la lista de protocolos")
    else:
        print("❌ Protocolo no aparece en la lista")
        return False
    
    # Probar conexión de protocolo
    print("\n2. Conectando protocolo...")
    config = {"test": "config"}
    if engine.connect_protocol(mock_protocol.name, config):
        print("✅ Protocolo conectado correctamente")
    else:
        print("❌ Error al conectar protocolo")
        return False
    
    # Probar lista de dispositivos
    devices = engine.get_devices()
    if len(devices) > 0:
        print(f"✅ Se descubrieron {len(devices)} dispositivos")
    else:
        print("❌ No se descubrieron dispositivos")
        return False
    
    # Probar lectura de datos
    print("\n3. Leyendo datos del dispositivo...")
    device_id = devices[0]
    data = engine.read_device_data(device_id, 0, 5)
    if data and len(data) == 5:
        print(f"✅ Datos leídos correctamente: {data}")
    else:
        print("❌ Error al leer datos")
        return False
    
    # Probar escritura de datos
    print("\n4. Escribiendo datos en el dispositivo...")
    if engine.write_device_data(device_id, 0, [1, 2, 3]):
        print("✅ Datos escritos correctamente")
    else:
        print("❌ Error al escribir datos")
        return False
    
    # Probar desconexión
    print("\n5. Desconectando protocolo...")
    if engine.disconnect_protocol(mock_protocol.name):
        print("✅ Protocolo desconectado correctamente")
    else:
        print("❌ Error al desconectar protocolo")
        return False
    
    # Probar eliminación de protocolo
    print("\n6. Eliminando protocolo...")
    if engine.unregister_protocol(mock_protocol.name):
        print("✅ Protocolo eliminado correctamente")
    else:
        print("❌ Error al eliminar protocolo")
        return False
    
    print("\n✅ Todas las pruebas del CommunicationEngine pasaron")
    return True

def main():
    """Ejecuta las pruebas del CommunicationEngine"""
    print("ComSuite - Pruebas del CommunicationEngine")
    print("=" * 50)
    
    if test_communication_engine():
        print("\n🎉 ¡CommunicationEngine funciona correctamente!")
        return True
    else:
        print("\n❌ Hay problemas en el CommunicationEngine")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
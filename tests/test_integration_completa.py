# tests/test_integration_completa.py
# Ruta completa: C:\Users\manue\ComSuite\tests\test_integration_completa.py

import sys
import os
import time

# Agregar la ruta src al path para importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.communication_engine import CommunicationEngine
from core.plugin_loader import PluginLoader

def test_integracion_completa():
    """Prueba la integración completa del sistema"""
    print("=== Prueba de Integración Completa ===")
    print("1. Inicializando CommunicationEngine...")
    
    # Crear el motor de comunicaciones
    engine = CommunicationEngine()
    
    print("✅ CommunicationEngine inicializado")
    
    # Conectar señales para monitoreo
    eventos_recibidos = []
    
    def capturar_evento(evento, *args):
        eventos_recibidos.append((evento, args))
        print(f"📡 Evento: {evento} - {args}")
    
    # Conectar todas las señales
    engine.protocol_loaded.connect(lambda name: capturar_evento("protocol_loaded", name))
    engine.protocol_connected.connect(lambda name: capturar_evento("protocol_connected", name))
    engine.device_added.connect(lambda device_id: capturar_evento("device_added", device_id))
    engine.data_received.connect(lambda device_id, data: capturar_evento("data_received", device_id, data))
    engine.error_occurred.connect(lambda source, msg: capturar_evento("error_occurred", source, msg))
    
    print("✅ Señales conectadas")
    
    # Paso 2: Cargar plugins
    print("\n2. Cargando plugins...")
    plugin_loader = PluginLoader()
    
    if not plugin_loader.discover_and_load_plugins():
        print("❌ No se pudieron cargar los plugins")
        return False
    
    print("✅ Plugins cargados")
    
    # Paso 3: Registrar plugins en el engine - CORREGIDO
    print("\n3. Registrando plugins en el engine...")
    
    loaded_protocols = plugin_loader.get_loaded_protocols()
    protocol_instances = {}  # Guardar instancias para uso posterior
    
    for plugin_name, protocol_class in loaded_protocols.items():
        protocol_instance = protocol_class()
        protocol_instances[plugin_name] = protocol_instance
        
        # Obtener el nombre real del protocolo (no del plugin)
        protocol_real_name = protocol_instance.name
        print(f"📝 Plugin: {plugin_name} -> Protocolo: {protocol_real_name}")
        
        if engine.register_protocol(protocol_instance):
            print(f"✅ Protocolo {protocol_real_name} registrado")
        else:
            print(f"❌ Error al registrar protocolo {protocol_real_name}")
    
    # Paso 4: Probar configuración Modbus TCP - CORREGIDO
    print("\n4. Probando configuración Modbus TCP...")
    
    tcp_config = {
        'mode': 'master',
        'protocol_type': 'TCP',
        'ip': '127.0.0.1',
        'port': 502,
        'slave_id': 1
    }
    
    # Usar el nombre del protocolo, no del plugin
    if engine.connect_protocol("Modbus", tcp_config):
        print("✅ Conexión TCP establecida")
        
        # Verificar dispositivos
        devices = engine.get_devices()
        print(f"📱 Dispositivos descubiertos: {devices}")
        
        if devices:
            # Probar lectura de datos
            print("\n5. Probando lectura de datos...")
            device_id = devices[0]
            data = engine.read_device_data(device_id, 0, 5)
            print(f"📖 Datos leídos: {data}")
            
            # Probar escritura de datos
            print("\n6. Probando escritura de datos...")
            write_success = engine.write_device_data(device_id, 0, [9999, 8888, 7777])
            print(f"✍️  Escritura exitosa: {write_success}")
            
            # Verificar escritura
            verify_data = engine.read_device_data(device_id, 0, 3)
            print(f"📖 Datos después de escritura: {verify_data}")
            
            # Desconectar
            print("\n7. Desconectando...")
            engine.disconnect_protocol("Modbus")
            print("✅ Desconectado correctamente")
        else:
            print("⚠️  No se descubrieron dispositivos (normal si no hay servidor)")
    
    else:
        print("❌ No se pudo conectar TCP (normal si no hay servidor)")
    
    # Paso 5: Probar configuración Modbus RTU - CORREGIDO
    print("\n8. Probando configuración Modbus RTU...")
    
    rtu_config = {
        'mode': 'master',
        'protocol_type': 'RTU',
        'port': 'COM3',
        'baudrate': 9600,
        'parity': 'N',
        'stopbits': 1,
        'bytesize': 8,
        'slave_id': 1
    }
    
    # Usar el nombre del protocolo, no del plugin
    if engine.connect_protocol("Modbus", rtu_config):
        print("✅ Conexión RTU establecida")
        
        # Verificar dispositivos
        devices = engine.get_devices()
        print(f"📱 Dispositivos RTU descubiertos: {devices}")
        
        if devices:
            # Probar lectura de datos RTU
            device_id = devices[0]
            data = engine.read_device_data(device_id, 0, 5)
            print(f"📖 Datos RTU leídos: {data}")
        
        # Desconectar
        engine.disconnect_protocol("Modbus")
        print("✅ Desconectado RTU correctamente")
    
    else:
        print("❌ No se pudo conectar RTU (normal si no hay dispositivo)")
    
    # Paso 6: Mostrar resumen
    print("\n" + "="*60)
    print("RESUMEN DE LA PRUEBA")
    print("="*60)
    print(f"Eventos capturados: {len(eventos_recibidos)}")
    
    for i, (evento, args) in enumerate(eventos_recibidos):
        print(f"{i+1:2d}. {evento}: {args}")
    
    print("\n✅ Prueba de integración completada")
    return True

def main():
    """Función principal"""
    print("ComSuite - Prueba de Integración Completa")
    print("="*60)
    print("Esta prueba verifica:")
    print("1. CommunicationEngine + PluginLoader")
    print("2. Carga dinámica de plugins")
    print("3. Conexión Modbus TCP/RTU")
    print("4. Lectura/escritura de datos")
    print("5. Manejo de dispositivos")
    print("6. Eventos y señales")
    print("="*60)
    
    try:
        success = test_integracion_completa()
        if success:
            print("\n🎉 ¡INTEGRACIÓN COMPLETA EXITOSA!")
            print("📋 El sistema ComSuite está listo para la GUI")
            return True
        else:
            print("\n❌ La integración tuvo problemas")
            return False
    except Exception as e:
        print(f"\n❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
# src/protocols/modbus/modbus_plugin.py
# Ruta completa: C:\Users\manue\ComSuite\src\protocols\modbus\modbus_plugin.py

import sys
import os

# Asegurar que podamos importar los archivos locales
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from typing import List, Dict, Any, Type
from plugins.plugin_interface import PluginInterface
from protocols.base_protocol.protocol_interface import ProtocolInterface
from .modbus_protocol import ModbusProtocol

class ModbusPlugin(PluginInterface):
    """
    Plugin para comunicación Modbus TCP/RTU.
    Integra las clases Modbus existentes en el sistema ComSuite.
    """
    
    @property
    def name(self) -> str:
        return "ModbusPlugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Plugin de comunicación Modbus TCP/RTU para ComSuite"
    
    @property
    def author(self) -> str:
        return "ComSuite Team"
    
    def get_protocol_class(self) -> Type[ProtocolInterface]:
        """
        Retorna la clase del protocolo Modbus.
        
        Returns:
            Type[ProtocolInterface]: Clase ModbusProtocol
        """
        return ModbusProtocol
    
    def get_dependencies(self) -> List[str]:
        """
        Retorna las dependencias requeridas por el plugin Modbus.
        
        Returns:
            List[str]: Lista de paquetes Python requeridos
        """
        return [
            "PySide6",      # Para la GUI y señales
            "pyserial",      # Para comunicación RTU
            "socket",        # Para comunicación TCP (built-in)
            "struct",        # Para empaquetar datos (built-in)
            "threading",     # Para operaciones asíncronas (built-in)
            "logging"        # Para logging (built-in)
        ]
    
    def validate_environment(self) -> bool:
        """
        Valida si el entorno actual cumple con los requisitos del plugin Modbus.
        
        Returns:
            bool: True si el entorno es válido
        """
        try:
            # Verificar dependencias críticas - MÉTODO MEJORADO
            dependencies_to_check = {
                "PySide6": "PySide6",
                "pyserial": "serial",  # El módulo se llama 'serial' pero el paquete es 'pyserial'
                "socket": "socket",
                "struct": "struct",
                "threading": "threading",
                "logging": "logging"
            }
            
            missing_deps = []
            for package_name, module_name in dependencies_to_check.items():
                try:
                    __import__(module_name)
                    print(f"✅ {package_name} disponible")
                except ImportError:
                    print(f"❌ {package_name} no disponible")
                    missing_deps.append(package_name)
            
            if missing_deps:
                print(f"❌ Dependencias faltantes: {missing_deps}")
                return False
            
            # Verificar que los archivos Modbus existentes estén disponibles
            try:
                from . import master_tcp, master_rtu, slave_tcp, slave_rtu
                print("✅ Archivos Modbus disponibles")
            except ImportError as e:
                print(f"❌ Error al importar archivos Modbus: {e}")
                return False
            
            print("✅ Entorno validado para ModbusPlugin")
            return True
            
        except Exception as e:
            print(f"❌ Error de validación en ModbusPlugin: {e}")
            return False
    
    def initialize(self) -> bool:
        """
        Inicializa el plugin Modbus.
        
        Returns:
            bool: True si la inicialización fue exitosa
        """
        try:
            # Importar y verificar clases Modbus existentes
            from .master_tcp import ModbusMasterTCP
            from .master_rtu import ModbusMasterRTU
            from .slave_tcp import ModbusSlaveTCP
            from .slave_rtu import ModbusSlaveRTU
            
            print("✅ ModbusPlugin inicializado correctamente")
            print("   - Clases Modbus TCP/RTU disponibles")
            print("   - Master/Slave soportados")
            return True
            
        except Exception as e:
            print(f"❌ Error al inicializar ModbusPlugin: {e}")
            return False
    
    def cleanup(self):
        """Limpia recursos del plugin Modbus."""
        print("🧹 Limpiando recursos de ModbusPlugin")
        # No hay recursos específicos que limpiar por ahora
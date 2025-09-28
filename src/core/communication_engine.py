import sys
import os
import importlib
import logging
from typing import Dict, List, Any, Optional
from PySide6.QtCore import QObject, Signal

# Importaciones corregidas
from .plugin_loader import PluginLoader
from ..protocols.base_protocol.protocol_interface import ProtocolInterface
from ..protocols.base_protocol.device_interface import DeviceInterface
from ..config.config_manager import ConfigManager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommunicationEngine(QObject):
    """
    Motor central de comunicaciones.
    Responsabilidad: Cargar plugins y gestionar dispositivos.
    Patrón: Observer (emite señales cuando ocurren eventos).
    """
    
    # Señales para notificación de eventos
    protocol_loaded = Signal(str)  # Señal: nombre del protocolo cargado
    device_connected = Signal(str)  # Señal: ID del dispositivo conectado
    device_disconnected = Signal(str)  # Señal: ID del dispositivo desconectado
    error_occurred = Signal(str, str)  # Señal: (tipo_error, mensaje_error)
    
    def __init__(self):
        super().__init__()
        self.device_manager = DeviceManager()  # Gestor abstracto de dispositivos
        self.plugin_loader = PluginLoader()  # Descubre plugins en /protocols/
        self.config_manager = ConfigManager()  # Gestor de configuración
        self.loaded_protocols: Dict[str, ProtocolInterface] = {}
        
        # Cargar plugins automáticamente al iniciar
        self._load_plugins()
        
    def _load_plugins(self):
        """Cargar dinámicamente todos los plugins disponibles"""
        try:
            plugins = self.plugin_loader.discover_plugins()
            for plugin_name, plugin_module in plugins.items():
                try:
                    plugin_instance = plugin_module.Plugin()
                    self.loaded_protocols[plugin_name] = plugin_instance
                    self.protocol_loaded.emit(plugin_name)
                    logger.info(f"Plugin {plugin_name} cargado correctamente")
                except Exception as e:
                    logger.error(f"Error al cargar plugin {plugin_name}: {e}")
                    self.error_occurred.emit("plugin_error", f"Error cargando {plugin_name}: {e}")
        except Exception as e:
            logger.error(f"Error descubriendo plugins: {e}")
            self.error_occurred.emit("discovery_error", f"Error descubriendo plugins: {e}")
    
    def get_available_protocols(self) -> List[str]:
        """Obtener lista de protocolos disponibles"""
        return list(self.loaded_protocols.keys())
    
    def create_device(self, protocol_name: str, device_config: Dict[str, Any]) -> Optional[DeviceInterface]:
        """Crear un nuevo dispositivo usando el protocolo especificado"""
        if protocol_name not in self.loaded_protocols:
            self.error_occurred.emit("protocol_error", f"Protocolo {protocol_name} no disponible")
            return None
            
        try:
            protocol = self.loaded_protocols[protocol_name]
            device = protocol.create_device(device_config)
            if device:
                self.device_manager.add_device(device)
                logger.info(f"Dispositivo creado con protocolo {protocol_name}")
            return device
        except Exception as e:
            logger.error(f"Error creando dispositivo: {e}")
            self.error_occurred.emit("device_error", f"Error creando dispositivo: {e}")
            return None
    
    def connect_device(self, device_id: str) -> bool:
        """Conectar un dispositivo específico"""
        try:
            success = self.device_manager.connect_device(device_id)
            if success:
                self.device_connected.emit(device_id)
            return success
        except Exception as e:
            logger.error(f"Error conectando dispositivo {device_id}: {e}")
            self.error_occurred.emit("connection_error", f"Error conectando {device_id}: {e}")
            return False
    
    def disconnect_device(self, device_id: str) -> bool:
        """Desconectar un dispositivo específico"""
        try:
            success = self.device_manager.disconnect_device(device_id)
            if success:
                self.device_disconnected.emit(device_id)
            return success
        except Exception as e:
            logger.error(f"Error desconectando dispositivo {device_id}: {e}")
            self.error_occurred.emit("disconnection_error", f"Error desconectando {device_id}: {e}")
            return False


class DeviceManager:
    """Gestor abstracto de dispositivos"""
    
    def __init__(self):
        self.devices: Dict[str, DeviceInterface] = {}
        
    def add_device(self, device: DeviceInterface):
        """Agregar un dispositivo al gestor"""
        self.devices[device.device_id] = device
        
    def remove_device(self, device_id: str):
        """Eliminar un dispositivo del gestor"""
        if device_id in self.devices:
            del self.devices[device_id]
            
    def get_device(self, device_id: str) -> Optional[DeviceInterface]:
        """Obtener un dispositivo por su ID"""
        return self.devices.get(device_id)
    
    def get_all_devices(self) -> Dict[str, DeviceInterface]:
        """Obtener todos los dispositivos"""
        return self.devices.copy()
    
    def connect_device(self, device_id: str) -> bool:
        """Conectar un dispositivo"""
        device = self.get_device(device_id)
        if device:
            return device.connect()
        return False
    
    def disconnect_device(self, device_id: str) -> bool:
        """Desconectar un dispositivo"""
        device = self.get_device(device_id)
        if device:
            return device.disconnect()
        return False
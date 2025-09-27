# src/core/communication_engine.py
# Ruta completa: C:\Users\manue\ComSuite\src\core\communication_engine.py

from typing import Dict, List, Optional, Any
from PySide6.QtCore import QObject, Signal
import logging

from protocols.base_protocol.protocol_interface import ProtocolInterface
from protocols.base_protocol.device_interface import DeviceInterface, DeviceStatus

class CommunicationEngine(QObject):
    """
    Motor central de comunicaciones de ComSuite.
    Gestiona todos los protocolos y dispositivos de manera unificada.
    """
    
    # Señales para notificar eventos a la GUI y otros componentes
    protocol_loaded = Signal(str)                    # Emitido cuando se carga un protocolo
    protocol_connected = Signal(str)                  # Emitido cuando un protocolo se conecta
    protocol_disconnected = Signal(str)              # Emitido cuando un protocolo se desconecta
    device_added = Signal(str)                       # Emitido cuando se añade un dispositivo
    device_removed = Signal(str)                     # Emitido cuando se elimina un dispositivo
    device_status_changed = Signal(str, str)         # Emitido cuando cambia el estado de un dispositivo
    data_received = Signal(str, list)                # Emitido cuando se reciben datos
    error_occurred = Signal(str, str)                # Emitido cuando ocurre un error
    
    def __init__(self):
        super().__init__()
        
        # Gestión de protocolos
        self._protocols: Dict[str, ProtocolInterface] = {}
        self._devices: Dict[str, Dict[str, Any]] = {}  # CORREGIDO: Diccionario de diccionarios
        
        # Configuración de logging
        self._setup_logging()
        
        self._log.info("CommunicationEngine inicializado")
    
    def _setup_logging(self):
        """Configura el sistema de logging"""
        self._log = logging.getLogger("CommunicationEngine")
        self._log.setLevel(logging.INFO)
        
        if not self._log.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self._log.addHandler(handler)
    
    def register_protocol(self, protocol: ProtocolInterface) -> bool:
        """
        Registra un protocolo en el motor de comunicaciones.
        
        Args:
            protocol: Instancia de ProtocolInterface a registrar
        
        Returns:
            bool: True si se registró correctamente, False en caso contrario
        """
        try:
            protocol_name = protocol.name
            
            if protocol_name in self._protocols:
                self._log.warning(f"Protocolo '{protocol_name}' ya está registrado")
                return False
            
            self._protocols[protocol_name] = protocol
            self._log.info(f"Protocolo '{protocol_name}' registrado correctamente")
            
            # Emitir señal (Qt maneja automáticamente si no hay receptores)
            self.protocol_loaded.emit(protocol_name)
            
            return True
            
        except Exception as e:
            error_msg = f"Error al registrar protocolo: {str(e)}"
            self._log.error(error_msg)
            self.error_occurred.emit("register_protocol", error_msg)
            return False
    
    def unregister_protocol(self, protocol_name: str) -> bool:
        """
        Elimina un protocolo del motor de comunicaciones.
        
        Args:
            protocol_name: Nombre del protocolo a eliminar
        
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            if protocol_name not in self._protocols:
                self._log.warning(f"Protocolo '{protocol_name}' no está registrado")
                return False
            
            # Desconectar el protocolo si está conectado
            protocol = self._protocols[protocol_name]
            if protocol.is_connected():
                protocol.disconnect()
            
            # Eliminar dispositivos asociados - CORREGIDO
            devices_to_remove = [
                device_id for device_id, device in self._devices.items()
                if device['protocol_name'] == protocol_name
            ]
            
            for device_id in devices_to_remove:
                self.remove_device(device_id)
            
            # Eliminar el protocolo
            del self._protocols[protocol_name]
            self._log.info(f"Protocolo '{protocol_name}' eliminado correctamente")
            
            return True
            
        except Exception as e:
            error_msg = f"Error al eliminar protocolo '{protocol_name}': {str(e)}"
            self._log.error(error_msg)
            self.error_occurred.emit("unregister_protocol", error_msg)
            return False
    
    def connect_protocol(self, protocol_name: str, config: Dict[str, Any]) -> bool:
        """
        Conecta un protocolo usando la configuración proporcionada.
        
        Args:
            protocol_name: Nombre del protocolo a conectar
            config: Configuración de conexión
        
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario
        """
        try:
            if protocol_name not in self._protocols:
                error_msg = f"Protocolo '{protocol_name}' no está registrado"
                self._log.error(error_msg)
                self.error_occurred.emit("connect_protocol", error_msg)
                return False
            
            protocol = self._protocols[protocol_name]
            
            # Validar configuración
            if not protocol.validate_config(config):
                error_msg = f"Configuración inválida para protocolo '{protocol_name}'"
                self._log.error(error_msg)
                self.error_occurred.emit("connect_protocol", error_msg)
                return False
            
            # Conectar protocolo
            if protocol.connect(config):
                self._log.info(f"Protocolo '{protocol_name}' conectado correctamente")
                self.protocol_connected.emit(protocol_name)
                
                # Descubrir y registrar dispositivos
                self._discover_devices(protocol_name)
                
                return True
            else:
                error_msg = f"No se pudo conectar el protocolo '{protocol_name}'"
                self._log.error(error_msg)
                self.error_occurred.emit("connect_protocol", error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Error al conectar protocolo '{protocol_name}': {str(e)}"
            self._log.error(error_msg)
            self.error_occurred.emit("connect_protocol", error_msg)
            return False
    
    def disconnect_protocol(self, protocol_name: str) -> bool:
        """
        Desconecta un protocolo.
        
        Args:
            protocol_name: Nombre del protocolo a desconectar
        
        Returns:
            bool: True si la desconexión fue exitosa, False en caso contrario
        """
        try:
            if protocol_name not in self._protocols:
                error_msg = f"Protocolo '{protocol_name}' no está registrado"
                self._log.error(error_msg)
                self.error_occurred.emit("disconnect_protocol", error_msg)
                return False
            
            protocol = self._protocols[protocol_name]
            
            if protocol.is_connected():
                protocol.disconnect()
                self._log.info(f"Protocolo '{protocol_name}' desconectado correctamente")
                self.protocol_disconnected.emit(protocol_name)
                
                # Actualizar estado de dispositivos
                self._update_devices_status(protocol_name, DeviceStatus.DISCONNECTED)
                
                return True
            else:
                self._log.warning(f"Protocolo '{protocol_name}' ya está desconectado")
                return True
                
        except Exception as e:
            error_msg = f"Error al desconectar protocolo '{protocol_name}': {str(e)}"
            self._log.error(error_msg)
            self.error_occurred.emit("disconnect_protocol", error_msg)
            return False
    
    def _discover_devices(self, protocol_name: str):
        """Descubre y registra dispositivos para un protocolo conectado"""
        try:
            protocol = self._protocols[protocol_name]
            device_ids = protocol.get_devices()
            
            for device_id in device_ids:
                device_info = protocol.get_device_info(device_id)
                if device_info:
                    self.add_device(protocol_name, device_id, device_info)
                    
        except Exception as e:
            error_msg = f"Error al descubrir dispositivos para '{protocol_name}': {str(e)}"
            self._log.error(error_msg)
            self.error_occurred.emit("discover_devices", error_msg)
    
    def add_device(self, protocol_name: str, device_id: str, device_info: Dict[str, Any]) -> bool:
        """
        Añade un dispositivo al motor de comunicaciones.
        
        Args:
            protocol_name: Nombre del protocolo
            device_id: ID del dispositivo
            device_info: Información del dispositivo
        
        Returns:
            bool: True si se añadió correctamente, False en caso contrario
        """
        try:
            if device_id in self._devices:
                self._log.warning(f"Dispositivo '{device_id}' ya está registrado")
                return False
            
            # Crear entrada de dispositivo como diccionario
            self._devices[device_id] = {
                'protocol_name': protocol_name,
                'info': device_info,
                'status': DeviceStatus.CONNECTED
            }
            
            self._log.info(f"Dispositivo '{device_id}' añadido correctamente")
            self.device_added.emit(device_id)
            
            return True
            
        except Exception as e:
            error_msg = f"Error al añadir dispositivo '{device_id}': {str(e)}"
            self._log.error(error_msg)
            self.error_occurred.emit("add_device", error_msg)
            return False
    
    def remove_device(self, device_id: str) -> bool:
        """
        Elimina un dispositivo del motor de comunicaciones.
        
        Args:
            device_id: ID del dispositivo a eliminar
        
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            if device_id not in self._devices:
                self._log.warning(f"Dispositivo '{device_id}' no está registrado")
                return False
            
            del self._devices[device_id]
            self._log.info(f"Dispositivo '{device_id}' eliminado correctamente")
            self.device_removed.emit(device_id)
            
            return True
            
        except Exception as e:
            error_msg = f"Error al eliminar dispositivo '{device_id}': {str(e)}"
            self._log.error(error_msg)
            self.error_occurred.emit("remove_device", error_msg)
            return False
    
    def _update_devices_status(self, protocol_name: str, status: DeviceStatus):
        """Actualiza el estado de todos los dispositivos de un protocolo"""
        for device_id, device_info in self._devices.items():
            if device_info['protocol_name'] == protocol_name:  # CORREGIDO
                device_info['status'] = status
                self.device_status_changed.emit(device_id, status.value)
    
    def get_protocols(self) -> List[str]:
        """
        Obtiene la lista de protocolos registrados.
        
        Returns:
            List[str]: Lista de nombres de protocolos
        """
        return list(self._protocols.keys())
    
    def get_devices(self) -> List[str]:
        """
        Obtiene la lista de dispositivos registrados.
        
        Returns:
            List[str]: Lista de IDs de dispositivos
        """
        return list(self._devices.keys())
    
    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de un dispositivo específico.
        
        Args:
            device_id: ID del dispositivo
        
        Returns:
            Optional[Dict]: Información del dispositivo o None si no existe
        """
        device = self._devices.get(device_id)
        return device['info'] if device else None
    
    def get_device_status(self, device_id: str) -> Optional[DeviceStatus]:
        """
        Obtiene el estado de un dispositivo específico.
        
        Args:
            device_id: ID del dispositivo
        
        Returns:
            Optional[DeviceStatus]: Estado del dispositivo o None si no existe
        """
        device = self._devices.get(device_id)
        return device['status'] if device else None
    
    def read_device_data(self, device_id: str, address: int, count: int) -> Optional[List[int]]:
        """
        Lee datos de un dispositivo específico.
        
        Args:
            device_id: ID del dispositivo
            address: Dirección de inicio
            count: Cantidad de datos a leer
        
        Returns:
            Optional[List[int]]: Datos leídos o None si hay error
        """
        try:
            device = self._devices.get(device_id)
            if not device:
                error_msg = f"Dispositivo '{device_id}' no encontrado"
                self._log.error(error_msg)
                self.error_occurred.emit("read_device_data", error_msg)
                return None
            
            protocol_name = device['protocol_name']  # CORREGIDO
            protocol = self._protocols.get(protocol_name)
            
            if not protocol:
                error_msg = f"Protocolo '{protocol_name}' no encontrado para dispositivo '{device_id}'"
                self._log.error(error_msg)
                self.error_occurred.emit("read_device_data", error_msg)
                return None
            
            data = protocol.read_data(device_id, address, count)
            
            if data:
                self._log.info(f"Leídos {len(data)} datos del dispositivo '{device_id}'")
                self.data_received.emit(device_id, data)
            
            return data
            
        except Exception as e:
            error_msg = f"Error al leer datos del dispositivo '{device_id}': {str(e)}"
            self._log.error(error_msg)
            self.error_occurred.emit("read_device_data", error_msg)
            return None
    
    def write_device_data(self, device_id: str, address: int, data: List[int]) -> bool:
        """
        Escribe datos en un dispositivo específico.
        
        Args:
            device_id: ID del dispositivo
            address: Dirección de inicio
            data: Datos a escribir
        
        Returns:
            bool: True si la escritura fue exitosa, False en caso contrario
        """
        try:
            device = self._devices.get(device_id)
            if not device:
                error_msg = f"Dispositivo '{device_id}' no encontrado"
                self._log.error(error_msg)
                self.error_occurred.emit("write_device_data", error_msg)
                return False
            
            protocol_name = device['protocol_name']  # CORREGIDO
            protocol = self._protocols.get(protocol_name)
            
            if not protocol:
                error_msg = f"Protocolo '{protocol_name}' no encontrado para dispositivo '{device_id}'"
                self._log.error(error_msg)
                self.error_occurred.emit("write_device_data", error_msg)
                return False
            
            success = protocol.write_data(device_id, address, data)
            
            if success:
                self._log.info(f"Escritos {len(data)} datos en el dispositivo '{device_id}'")
            else:
                error_msg = f"No se pudieron escribir datos en el dispositivo '{device_id}'"
                self._log.error(error_msg)
                self.error_occurred.emit("write_device_data", error_msg)
            
            return success
            
        except Exception as e:
            error_msg = f"Error al escribir datos en el dispositivo '{device_id}': {str(e)}"
            self._log.error(error_msg)
            self.error_occurred.emit("write_device_data", error_msg)
            return False
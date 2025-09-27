# src/protocols/base_protocol/device_interface.py
# Ruta completa: C:\Users\manue\ComSuite\src\protocols\base_protocol\device_interface.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from enum import Enum

class DeviceStatus(Enum):
    """Estados posibles de un dispositivo"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    UNKNOWN = "unknown"

class DeviceInterface(ABC):
    """
    Interfaz abstracta que representa un dispositivo de comunicación.
    Cada dispositivo conectado a través de cualquier protocolo implementará esta interfaz.
    """
    
    @property
    @abstractmethod
    def device_id(self) -> str:
        """Identificador único del dispositivo"""
        pass
    
    @property
    @abstractmethod
    def protocol_name(self) -> str:
        """Nombre del protocolo al que pertenece este dispositivo"""
        pass
    
    @property
    @abstractmethod
    def status(self) -> DeviceStatus:
        """Estado actual del dispositivo"""
        pass
    
    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """
        Obtiene información completa del dispositivo.
        
        Returns:
            Dict[str, Any]: Diccionario con toda la información del dispositivo
        """
        pass
    
    @abstractmethod
    def read_registers(self, start_address: int, count: int) -> List[int]:
        """
        Lee registros del dispositivo.
        
        Args:
            start_address: Dirección de inicio
            count: Cantidad de registros a leer
        
        Returns:
            List[int]: Lista de valores leídos. Vacía si hay error.
        """
        pass
    
    @abstractmethod
    def write_registers(self, start_address: int, values: List[int]) -> bool:
        """
        Escribe registros en el dispositivo.
        
        Args:
            start_address: Dirección de inicio
            values: Lista de valores a escribir
        
        Returns:
            bool: True si la escritura fue exitosa, False en caso contrario
        """
        pass
    
    @abstractmethod
    def read_coils(self, start_address: int, count: int) -> List[bool]:
        """
        Lee coils (bits) del dispositivo.
        
        Args:
            start_address: Dirección de inicio
            count: Cantidad de coils a leer
        
        Returns:
            List[bool]: Lista de valores booleanos leídos. Vacía si hay error.
        """
        pass
    
    @abstractmethod
    def write_coils(self, start_address: int, values: List[bool]) -> bool:
        """
        Escribe coils (bits) en el dispositivo.
        
        Args:
            start_address: Dirección de inicio
            values: Lista de valores booleanos a escribir
        
        Returns:
            bool: True si la escritura fue exitosa, False en caso contrario
        """
        pass
    
    @abstractmethod
    def get_last_error(self) -> Optional[str]:
        """
        Obtiene el último error ocurrido en el dispositivo.
        
        Returns:
            Optional[str]: Mensaje de error o None si no hay errores
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Verifica si el dispositivo está disponible para comunicación.
        
        Returns:
            bool: True si está disponible, False en caso contrario
        """
        pass
    
    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """
        Obtiene la configuración actual del dispositivo.
        
        Returns:
            Dict[str, Any]: Configuración actual del dispositivo
        """
        pass
    
    @abstractmethod
    def update_config(self, config: Dict[str, Any]) -> bool:
        """
        Actualiza la configuración del dispositivo.
        
        Args:
            config: Nueva configuración del dispositivo
        
        Returns:
            bool: True si la actualización fue exitosa, False en caso contrario
        """
        pass
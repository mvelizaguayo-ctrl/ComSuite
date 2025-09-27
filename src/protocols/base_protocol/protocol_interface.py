# src/protocols/base_protocol/protocol_interface.py
# Ruta completa: C:\Users\manue\ComSuite\src\protocols\base_protocol\protocol_interface.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class ProtocolInterface(ABC):
    """
    Interfaz abstracta que todos los protocolos deben implementar.
    Define el contrato para cualquier protocolo de comunicación en ComSuite.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre del protocolo (ej: 'Modbus', 'CAN', 'PROFIBUS')"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Versión del protocolo implementado"""
        pass
    
    @abstractmethod
    def connect(self, config: Dict[str, Any]) -> bool:
        """
        Conecta el protocolo usando la configuración proporcionada.
        
        Args:
            config: Diccionario con parámetros de conexión específicos del protocolo
                  (ej: {'ip': '192.168.1.10', 'port': 502} para Modbus TCP)
        
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Desconecta el protocolo y libera recursos"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        Verifica si el protocolo está actualmente conectado.
        
        Returns:
            bool: True si está conectado, False en caso contrario
        """
        pass
    
    @abstractmethod
    def read_data(self, device_id: str, address: int, count: int) -> List[int]:
        """
        Lee datos de un dispositivo.
        
        Args:
            device_id: Identificador único del dispositivo
            address: Dirección de inicio de lectura
            count: Cantidad de datos a leer
        
        Returns:
            List[int]: Lista con los datos leídos. Vacía si hay error.
        """
        pass
    
    @abstractmethod
    def write_data(self, device_id: str, address: int, data: List[int]) -> bool:
        """
        Escribe datos en un dispositivo.
        
        Args:
            device_id: Identificador único del dispositivo
            address: Dirección de inicio de escritura
            data: Lista de datos a escribir
        
        Returns:
            bool: True si la escritura fue exitosa, False en caso contrario
        """
        pass
    
    @abstractmethod
    def get_devices(self) -> List[str]:
        """
        Obtiene la lista de dispositivos disponibles para este protocolo.
        
        Returns:
            List[str]: Lista de device_id disponibles
        """
        pass
    
    @abstractmethod
    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información detallada de un dispositivo específico.
        
        Args:
            device_id: Identificador del dispositivo
        
        Returns:
            Optional[Dict]: Diccionario con información del dispositivo o None si no existe
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Valida si la configuración proporcionada es correcta para este protocolo.
        
        Args:
            config: Diccionario de configuración a validar
        
        Returns:
            bool: True si la configuración es válida, False en caso contrario
        """
        pass
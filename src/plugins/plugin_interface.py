# src/plugins/plugin_interface.py
# Ruta completa: C:\Users\manue\ComSuite\src\plugins\plugin_interface.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List

class PluginInterface(ABC):
    """
    Interfaz base para todos los plugins de ComSuite.
    Cada protocolo debe implementar esta interfaz para ser reconocido por el sistema.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre del plugin (ej: 'ModbusPlugin', 'CANPlugin')"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Versión del plugin"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Descripción breve del plugin"""
        pass
    
    @property
    @abstractmethod
    def author(self) -> str:
        """Autor del plugin"""
        pass
    
    @abstractmethod
    def get_protocol_class(self):
        """
        Retorna la clase del protocolo que implementa ProtocolInterface.
        
        Returns:
            Clase que implementa ProtocolInterface
        """
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """
        Retorna una lista de dependencias requeridas por el plugin.
        
        Returns:
            List[str]: Lista de nombres de paquetes Python requeridos
        """
        pass
    
    @abstractmethod
    def validate_environment(self) -> bool:
        """
        Valida si el entorno actual cumple con los requisitos del plugin.
        
        Returns:
            bool: True si el entorno es válido, False en caso contrario
        """
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Inicializa el plugin. Se llama después de la validación.
        
        Returns:
            bool: True si la inicialización fue exitosa, False en caso contrario
        """
        pass
    
    @abstractmethod
    def cleanup(self):
        """Limpia recursos del plugin cuando se desactiva."""
        pass
# src/protocols/base_protocol/protocol_interface.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from ..base_protocol.device_interface import DeviceInterface, DeviceStatus

class ProtocolInterface(ABC):
    """Interfaz abstracta para todos los protocolos."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre del protocolo."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Versión del protocolo."""
        pass
    
    @abstractmethod
    def connect(self, config: Dict[str, Any]) -> bool:
        """Conectar al dispositivo usando la configuración proporcionada."""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Desconectar del dispositivo."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Verificar si está conectado."""
        pass
    
    @abstractmethod
    def read_data(self, address: int, count: int) -> List[int]:
        """Leer datos del dispositivo."""
        pass
    
    @abstractmethod
    def write_data(self, address: int, data: List[int]) -> bool:
        """Escribir datos en el dispositivo."""
        pass
    
    @abstractmethod
    def get_device_info(self) -> Dict[str, Any]:
        """Obtener información del dispositivo."""
        pass
    
    @abstractmethod
    def get_status(self) -> DeviceStatus:
        """Obtener estado del dispositivo."""
        pass
    
    # === NUEVOS MÉTODOS PARA SOPORTE DE PLANTILLAS ===
    
    def apply_template(self, template) -> bool:
        """
        Aplicar una plantilla al protocolo.
        
        Args:
            template: Plantilla a aplicar
            
        Returns:
            bool: True si se aplicó correctamente
        """
        try:
            # Implementación base - puede ser sobreescrita por protocolos específicos
            if hasattr(template, 'parameters'):
                self.template_parameters = template.parameters
                self.template_methods = getattr(template, 'automation_methods', {})
                self.template_alarms = getattr(template, 'alarms', {})
                return True
            return False
        except Exception as e:
            # Log error but don't raise to maintain compatibility
            import logging
            logging.getLogger(__name__).error(f"Error applying template: {e}")
            return False
    
    def get_template_parameters(self) -> Dict[str, Any]:
        """
        Obtener parámetros de la plantilla aplicada.
        
        Returns:
            Dict[str, Any]: Parámetros de la plantilla
        """
        return getattr(self, 'template_parameters', {})
    
    def execute_template_method(self, method_name: str, **kwargs) -> Any:
        """
        Ejecutar un método de la plantilla.
        
        Args:
            method_name: Nombre del método a ejecutar
            **kwargs: Parámetros del método
            
        Returns:
            Any: Resultado de la ejecución o None si falla
        """
        try:
            template_methods = getattr(self, 'template_methods', {})
            if method_name in template_methods:
                method_info = template_methods[method_name]
                script = method_info.get('script', '')
                
                # Crear un entorno seguro para ejecutar el script
                env = {
                    'self': self,
                    'kwargs': kwargs,
                    'write_parameter': self._write_template_parameter,
                    'read_parameter': self._read_template_parameter
                }
                
                # Ejecutar el script
                exec(script, env)
                return env.get('result')
            else:
                return None
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error executing template method {method_name}: {e}")
            return None
    
    def _write_template_parameter(self, param_name: str, value: Any) -> bool:
        """
        Método interno para escribir un parámetro de plantilla.
        
        Args:
            param_name: Nombre del parámetro
            value: Valor a escribir
            
        Returns:
            bool: True si se escribió correctamente
        """
        try:
            parameters = self.get_template_parameters()
            if param_name in parameters.get('control', {}):
                param_info = parameters['control'][param_name]
                address = param_info.get('address')
                if address is not None:
                    return self.write_data(address, [value])
            return False
        except Exception:
            return False
    
    def _read_template_parameter(self, param_name: str) -> Any:
        """
        Método interno para leer un parámetro de plantilla.
        
        Args:
            param_name: Nombre del parámetro
            
        Returns:
            Any: Valor leído o None si falla
        """
        try:
            parameters = self.get_template_parameters()
            if param_name in parameters.get('control', {}):
                param_info = parameters['control'][param_name]
                address = param_info.get('address')
                count = 1
                if address is not None:
                    data = self.read_data(address, count)
                    return data[0] if data else None
            return None
        except Exception:
            return None
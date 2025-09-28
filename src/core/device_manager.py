# src/core/device_manager.py
import logging
from typing import Dict, List, Optional, Any
from ..protocols.base_protocol.device_interface import DeviceInterface, DeviceStatus

class DeviceManager:
    """Gestor abstracto de dispositivos."""
    
    def __init__(self):
        self.devices: Dict[str, DeviceInterface] = {}
        self.logger = logging.getLogger(__name__)
        
    def register_device(self, device: DeviceInterface) -> bool:
        """Registrar un nuevo dispositivo."""
        if device.device_id in self.devices:
            self.logger.warning(f"Device {device.device_id} already registered")
            return False
        
        self.devices[device.device_id] = device
        self.logger.info(f"Device {device.device_id} registered successfully")
        return True
    
    def unregister_device(self, device_id: str) -> bool:
        """Eliminar un dispositivo registrado."""
        if device_id not in self.devices:
            self.logger.warning(f"Device {device_id} not found")
            return False
        
        del self.devices[device_id]
        self.logger.info(f"Device {device_id} unregistered successfully")
        return True
    
    def get_device(self, device_id: str) -> Optional[DeviceInterface]:
        """Obtener un dispositivo por su ID."""
        return self.devices.get(device_id)
    
    def get_all_devices(self) -> List[DeviceInterface]:
        """Obtener todos los dispositivos registrados."""
        return list(self.devices.values())
    
    def get_devices_by_protocol(self, protocol_name: str) -> List[DeviceInterface]:
        """Obtener dispositivos por protocolo."""
        return [device for device in self.devices.values() 
                if device.protocol_name == protocol_name]
    
    def get_devices_by_status(self, status: DeviceStatus) -> List[DeviceInterface]:
        """Obtener dispositivos por estado."""
        return [device for device in self.devices.values() 
                if device.status == status]
    
    # === NUEVOS MÉTODOS PARA SOPORTE DE PLANTILLAS ===
    
    def create_device_from_template(self, template_name: str, config: Dict[str, Any]) -> Optional[DeviceInterface]:
        """
        Crear un dispositivo usando una plantilla.
        
        Args:
            template_name: Nombre de la plantilla a usar
            config: Configuración específica del dispositivo
            
        Returns:
            DeviceInterface: El dispositivo creado o None si falla
        """
        try:
            # Importar aquí para evitar dependencia circular
            from ..templates.template_manager import TemplateManager
            
            # Obtener la plantilla
            template = TemplateManager.get_template(template_name)
            if not template:
                self.logger.error(f"Template {template_name} not found")
                return None
            
            # Crear dispositivo base
            device = self._create_base_device(template, config)
            if not device:
                return None
            
            # Aplicar plantilla al dispositivo
            device.apply_template(template)
            
            # Registrar el dispositivo
            if self.register_device(device):
                self.logger.info(f"Device created from template {template_name}: {device.device_id}")
                return device
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating device from template {template_name}: {e}")
            return None
    
    def get_available_templates(self) -> List[str]:
        """
        Obtener lista de plantillas disponibles.
        
        Returns:
            List[str]: Nombres de plantillas disponibles
        """
        try:
            from ..templates.template_manager import TemplateManager
            return TemplateManager.get_available_templates()
        except Exception as e:
            self.logger.error(f"Error getting available templates: {e}")
            return []
    
    def register_template(self, template) -> bool:
        """
        Registrar una nueva plantilla en el sistema.
        
        Args:
            template: Plantilla a registrar
            
        Returns:
            bool: True si se registró correctamente
        """
        try:
            from ..templates.template_manager import TemplateManager
            result = TemplateManager.register_template(template)
            if result:
                self.logger.info(f"Template registered: {template.name}")
            return result
        except Exception as e:
            self.logger.error(f"Error registering template: {e}")
            return False
    
    def _create_base_device(self, template, config: Dict[str, Any]) -> Optional[DeviceInterface]:
        """
        Método interno para crear el dispositivo base según la plantilla.
        
        Args:
            template: Plantilla a usar
            config: Configuración específica
            
        Returns:
            DeviceInterface: Dispositivo creado o None
        """
        # Este método será implementado cuando tengamos el sistema de plantillas
        # Por ahora, retornamos None para evitar errores
        self.logger.warning("_create_base_device not implemented yet")
        return None
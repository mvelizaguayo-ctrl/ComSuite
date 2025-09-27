# src/core/plugin_loader.py
# Ruta completa: C:\Users\manue\ComSuite\src\core\plugin_loader.py

import logging
from typing import List, Dict, Any, Type, Optional
from PySide6.QtCore import QObject, Signal

from protocols.base_protocol.protocol_interface import ProtocolInterface
from plugins.plugin_interface import PluginInterface
from plugins.discovery import PluginDiscovery

class PluginLoader(QObject):
    """
    Cargador de plugins para ComSuite.
    Descubre, valida y carga plugins de protocolos automáticamente.
    """
    
    # Señales para notificar eventos
    plugin_discovered = Signal(str, str, str)  # name, version, description
    plugin_loaded = Signal(str)               # plugin name
    plugin_failed = Signal(str, str)          # plugin name, error message
    loading_completed = Signal()               # Todos los plugins cargados
    
    def __init__(self):
        super().__init__()
        
        self.discovery = PluginDiscovery()
        self.loaded_plugins: Dict[str, PluginInterface] = {}
        self.loaded_protocols: Dict[str, Type[ProtocolInterface]] = {}
        
        # Configuración de logging
        self._setup_logging()
        
        self._log.info("PluginLoader inicializado")
    
    def _setup_logging(self):
        """Configura el sistema de logging"""
        self._log = logging.getLogger("PluginLoader")
        self._log.setLevel(logging.INFO)
        
        if not self._log.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self._log.addHandler(handler)
    
    def discover_and_load_plugins(self) -> bool:
        """
        Descubre y carga todos los plugins disponibles.
        
        Returns:
            bool: True si al menos un plugin se cargó correctamente
        """
        try:
            self._log.info("Iniciando descubrimiento y carga de plugins...")
            
            # Descubrir plugins
            plugin_classes = self.discovery.discover_plugins()
            
            if not plugin_classes:
                self._log.warning("No se descubrieron plugins")
                self.loading_completed.emit()
                return False
            
            # Cargar cada plugin
            success_count = 0
            for plugin_class in plugin_classes:
                if self._load_plugin(plugin_class):
                    success_count += 1
            
            self._log.info(f"Carga de plugins completada: {success_count}/{len(plugin_classes)} exitosos")
            self.loading_completed.emit()
            
            return success_count > 0
            
        except Exception as e:
            error_msg = f"Error durante descubrimiento y carga de plugins: {str(e)}"
            self._log.error(error_msg)
            return False
    
    def _load_plugin(self, plugin_class: Type[PluginInterface]) -> bool:
        """
        Carga un plugin específico.
        
        Args:
            plugin_class: Clase del plugin a cargar
        
        Returns:
            bool: True si se cargó correctamente
        """
        try:
            # Crear instancia del plugin
            plugin_instance = plugin_class()
            plugin_name = plugin_instance.name
            
            self._log.info(f"Cargando plugin: {plugin_name}")
            
            # Emitir señal de descubrimiento
            self.plugin_discovered.emit(
                plugin_name,
                plugin_instance.version,
                plugin_instance.description
            )
            
            # Validar entorno (esto ya incluye la verificación de dependencias)
            if not plugin_instance.validate_environment():
                error_msg = f"Entorno no válido para plugin {plugin_name}"
                self._log.error(error_msg)
                self.plugin_failed.emit(plugin_name, error_msg)
                return False
            
            # Inicializar plugin
            if not plugin_instance.initialize():
                error_msg = f"Fallo en inicialización de plugin {plugin_name}"
                self._log.error(error_msg)
                self.plugin_failed.emit(plugin_name, error_msg)
                return False
            
            # Obtener la clase del protocolo
            protocol_class = plugin_instance.get_protocol_class()
            if not protocol_class or not issubclass(protocol_class, ProtocolInterface):
                error_msg = f"Plugin {plugin_name} no proporciona un protocolo válido"
                self._log.error(error_msg)
                self.plugin_failed.emit(plugin_name, error_msg)
                return False
            
            # Guardar plugin y protocolo
            self.loaded_plugins[plugin_name] = plugin_instance
            self.loaded_protocols[plugin_name] = protocol_class
            
            self._log.info(f"Plugin {plugin_name} cargado correctamente")
            self.plugin_loaded.emit(plugin_name)
            
            return True
            
        except Exception as e:
            error_msg = f"Error al cargar plugin {plugin_class.__name__}: {str(e)}"
            self._log.error(error_msg)
            self.plugin_failed.emit(plugin_class.__name__, error_msg)
            return False
    
    def get_loaded_plugins(self) -> List[str]:
        """
        Obtiene la lista de plugins cargados.
        
        Returns:
            List[str]: Nombres de los plugins cargados
        """
        return list(self.loaded_plugins.keys())
    
    def get_loaded_protocols(self) -> Dict[str, Type[ProtocolInterface]]:
        """
        Obtiene los protocolos cargados.
        
        Returns:
            Dict[str, Type[ProtocolInterface]]: Diccionario de protocolos por nombre
        """
        return self.loaded_protocols.copy()
    
    def create_protocol(self, protocol_name: str) -> Optional[ProtocolInterface]:
        """
        Crea una instancia de un protocolo específico.
        
        Args:
            protocol_name: Nombre del protocolo
            
        Returns:
            Optional[ProtocolInterface]: Instancia del protocolo o None
        """
        try:
            if protocol_name not in self.loaded_protocols:
                self._log.error(f"Protocolo {protocol_name} no está cargado")
                return None
            
            protocol_class = self.loaded_protocols[protocol_name]
            return protocol_class()
            
        except Exception as e:
            self._log.error(f"Error al crear protocolo {protocol_name}: {str(e)}")
            return None
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Descarga un plugin específico.
        
        Args:
            plugin_name: Nombre del plugin a descargar
        
        Returns:
            bool: True si se descargó correctamente
        """
        try:
            if plugin_name not in self.loaded_plugins:
                self._log.warning(f"Plugin {plugin_name} no está cargado")
                return False
            
            # Obtener plugin y limpiar
            plugin = self.loaded_plugins[plugin_name]
            plugin.cleanup()
            
            # Eliminar de los diccionarios
            del self.loaded_plugins[plugin_name]
            del self.loaded_protocols[plugin_name]
            
            self._log.info(f"Plugin {plugin_name} descargado correctamente")
            return True
            
        except Exception as e:
            self._log.error(f"Error al descargar plugin {plugin_name}: {str(e)}")
            return False
    
    def unload_all_plugins(self):
        """Descarga todos los plugins cargados."""
        plugin_names = list(self.loaded_plugins.keys())
        for plugin_name in plugin_names:
            self.unload_plugin(plugin_name)
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, str]]:
        """
        Obtiene información de un plugin.
        
        Args:
            plugin_name: Nombre del plugin
            
        Returns:
            Optional[Dict[str, str]]: Información del plugin o None
        """
        if plugin_name in self.loaded_plugins:
            plugin = self.loaded_plugins[plugin_name]
            return {
                'name': plugin.name,
                'version': plugin.version,
                'description': plugin.description,
                'author': plugin.author,
                'dependencies': ', '.join(plugin.get_dependencies())
            }
        return None
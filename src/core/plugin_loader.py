import os
import importlib
import sys
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class PluginLoader:
    """Cargador dinámico de plugins"""
    
    def __init__(self):
        self.plugins: Dict[str, Any] = {}
        
    def discover_plugins(self) -> Dict[str, Any]:
        """Descubre plugins en el directorio src/protocols/"""
        plugins = {}
        
        # Obtener la ruta al directorio de protocolos
        current_dir = os.path.dirname(os.path.abspath(__file__))
        protocols_dir = os.path.join(current_dir, '..', 'protocols')
        
        # Asegurar que el directorio de protocolos esté en el path
        if protocols_dir not in sys.path:
            sys.path.insert(0, protocols_dir)
        
        try:
            for item in os.listdir(protocols_dir):
                item_path = os.path.join(protocols_dir, item)
                
                # Ignorar archivos ocultos y __pycache__
                if item.startswith('.') or item == '__pycache__':
                    continue
                    
                # Verificar si es un directorio y tiene __init__.py
                if os.path.isdir(item_path):
                    init_file = os.path.join(item_path, '__init__.py')
                    if os.path.isfile(init_file):
                        try:
                            # Importar el módulo del plugin
                            module_name = f"src.protocols.{item}"
                            module = importlib.import_module(module_name)
                            
                            # Verificar si tiene la clase Plugin
                            if hasattr(module, 'Plugin'):
                                plugins[item] = module
                                logger.info(f"Plugin descubierto: {item}")
                        except Exception as e:
                            logger.error(f"Error al cargar plugin {item}: {e}")
                            
        except Exception as e:
            logger.error(f"Error explorando directorio de plugins: {e}")
            
        return plugins
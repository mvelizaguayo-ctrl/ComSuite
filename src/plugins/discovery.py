# src/plugins/discovery.py
# Ruta completa: C:\Users\manue\ComSuite\src\plugins\discovery.py

import os
import sys
import importlib.util
import inspect
from typing import List, Type, Optional, Dict
from .plugin_interface import PluginInterface

class PluginDiscovery:
    """
    Descubre y carga plugins automáticamente desde el directorio de protocolos.
    """
    
    def __init__(self, plugins_dir: str = "src/protocols"):
        self.plugins_dir = plugins_dir
        self.discovered_plugins: List[Type[PluginInterface]] = []
        
        # Asegurar que el directorio raíz del proyecto esté en el path
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
    
    def discover_plugins(self) -> List[Type[PluginInterface]]:
        """
        Descubre todos los plugins disponibles en el directorio de protocolos.
        
        Returns:
            List[Type[PluginInterface]]: Lista de clases de plugin descubiertas
        """
        self.discovered_plugins.clear()
        
        if not os.path.exists(self.plugins_dir):
            print(f"Directorio de plugins no encontrado: {self.plugins_dir}")
            return self.discovered_plugins
        
        print(f"Buscando plugins en: {self.plugins_dir}")
        
        # Recorrer todos los subdirectorios en protocols/
        for item in os.listdir(self.plugins_dir):
            item_path = os.path.join(self.plugins_dir, item)
            
            # Saltar archivos ocultos, __pycache__ y directorios que no son plugins válidos
            if (item.startswith('.') or 
                item == '__pycache__' or 
                item == 'base_protocol' or  # Saltar el directorio base_protocol
                not os.path.isdir(item_path)):
                continue
            
            print(f"Verificando directorio: {item}")
            plugin_class = self._discover_plugin_in_directory(item_path, item)
            if plugin_class:
                self.discovered_plugins.append(plugin_class)
        
        print(f"Descubiertos {len(self.discovered_plugins)} plugins")
        return self.discovered_plugins
    
    def _discover_plugin_in_directory(self, directory_path: str, plugin_name: str) -> Optional[Type[PluginInterface]]:
        """
        Descubre un plugin en un directorio específico.
        
        Args:
            directory_path: Ruta al directorio del plugin
            plugin_name: Nombre del plugin
            
        Returns:
            Optional[Type[PluginInterface]]: Clase del plugin encontrada o None
        """
        try:
            # Buscar el archivo del plugin (plugin_name + '_plugin.py')
            plugin_file = os.path.join(directory_path, f"{plugin_name}_plugin.py")
            
            if not os.path.exists(plugin_file):
                print(f"  Archivo de plugin no encontrado: {plugin_file}")
                return None
            
            print(f"  Encontrado archivo de plugin: {plugin_file}")
            
            # Construir el nombre del módulo - CORREGIDO
            # Usar una ruta relativa desde el directorio raíz del proyecto
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            rel_path = os.path.relpath(directory_path, project_root)
            module_name = f"{rel_path.replace(os.sep, '.')}.{plugin_name}_plugin"
            
            print(f"  Intentando cargar módulo: {module_name}")
            
            # Cargar el módulo usando importlib
            spec = importlib.util.spec_from_file_location(module_name, plugin_file)
            if spec is None:
                print(f"  No se pudo crear el spec para el módulo: {plugin_file}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            if module is None:
                print(f"  No se pudo crear el módulo desde el spec: {module_name}")
                return None
            
            # Ejecutar el módulo
            try:
                spec.loader.exec_module(module)
                print(f"  Módulo cargado exitosamente: {module_name}")
            except Exception as e:
                print(f"  Error al ejecutar módulo {module_name}: {e}")
                return None
            
            # Buscar clases que implementen PluginInterface
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, PluginInterface) and 
                    obj != PluginInterface and 
                    obj.__module__ == module.__name__):
                    print(f"  Plugin descubierto: {name} en {plugin_name}")
                    return obj
            
            print(f"  No se encontraron clases PluginInterface en {plugin_name}")
            return None
            
        except Exception as e:
            print(f"  Error al descubrir plugin en {directory_path}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_plugin_info(self, plugin_class: Type[PluginInterface]) -> Dict[str, str]:
        """
        Obtiene información básica de un plugin.
        
        Args:
            plugin_class: Clase del plugin
            
        Returns:
            Dict[str, str]: Información del plugin
        """
        try:
            # Crear una instancia temporal para obtener información
            temp_instance = plugin_class()
            return {
                'name': temp_instance.name,
                'version': temp_instance.version,
                'description': temp_instance.description,
                'author': temp_instance.author,
                'dependencies': ', '.join(temp_instance.get_dependencies())
            }
        except Exception as e:
            return {
                'name': plugin_class.__name__,
                'version': 'Unknown',
                'description': f'Error: {str(e)}',
                'author': 'Unknown',
                'dependencies': 'Unknown'
            }
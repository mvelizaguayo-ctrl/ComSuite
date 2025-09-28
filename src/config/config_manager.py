# src/config/config_manager.py
import json
import os
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

class ConfigManager:
    """Gestor central de configuración."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Configuración global
        self.global_config = self._load_global_config()
        
        # Configuraciones de protocolos
        self.protocol_configs = {}
        self._load_protocol_configs()
        
        # Configuración de proyectos
        self.project_configs = {}
        self._load_project_configs()
    
    def _load_global_config(self) -> Dict[str, Any]:
        """Cargar configuración global."""
        config_file = self.config_dir / "global_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading global config: {e}")
        
        return {
            "default_language": "es",
            "log_level": "INFO",
            "auto_save": True,
            "backup_enabled": True
        }
    
    def _load_protocol_configs(self):
        """Cargar configuraciones de protocolos."""
        protocol_dir = self.config_dir / "protocol_configs"
        if protocol_dir.exists():
            for config_file in protocol_dir.glob("*.json"):
                try:
                    protocol_name = config_file.stem
                    with open(config_file, 'r') as f:
                        self.protocol_configs[protocol_name] = json.load(f)
                except Exception as e:
                    self.logger.error(f"Error loading protocol config {config_file}: {e}")
    
    def _load_project_configs(self):
        """Cargar configuraciones de proyectos."""
        projects_dir = self.config_dir / "projects"
        if projects_dir.exists():
            for project_file in projects_dir.glob("*.json"):
                try:
                    project_name = project_file.stem
                    with open(project_file, 'r') as f:
                        self.project_configs[project_name] = json.load(f)
                except Exception as e:
                    self.logger.error(f"Error loading project config {project_file}: {e}")
    
    def get_global_config(self) -> Dict[str, Any]:
        """Obtener configuración global."""
        return self.global_config.copy()
    
    def save_global_config(self, config: Dict[str, Any]) -> bool:
        """Guardar configuración global."""
        try:
            config_file = self.config_dir / "global_config.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.global_config = config
            return True
        except Exception as e:
            self.logger.error(f"Error saving global config: {e}")
            return False
    
    def get_protocol_config(self, protocol_name: str) -> Optional[Dict[str, Any]]:
        """Obtener configuración de un protocolo."""
        return self.protocol_configs.get(protocol_name)
    
    def save_protocol_config(self, protocol_name: str, config: Dict[str, Any]) -> bool:
        """Guardar configuración de un protocolo."""
        try:
            protocol_dir = self.config_dir / "protocol_configs"
            protocol_dir.mkdir(exist_ok=True)
            
            config_file = protocol_dir / f"{protocol_name}.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.protocol_configs[protocol_name] = config
            return True
        except Exception as e:
            self.logger.error(f"Error saving protocol config {protocol_name}: {e}")
            return False
    
    def get_project_config(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Obtener configuración de un proyecto."""
        return self.project_configs.get(project_name)
    
    def save_project_config(self, project_name: str, config: Dict[str, Any]) -> bool:
        """Guardar configuración de un proyecto."""
        try:
            projects_dir = self.config_dir / "projects"
            projects_dir.mkdir(exist_ok=True)
            
            config_file = projects_dir / f"{project_name}.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.project_configs[project_name] = config
            return True
        except Exception as e:
            self.logger.error(f"Error saving project config {project_name}: {e}")
            return False
    
    # === NUEVOS MÉTODOS PARA SOPORTE DE PLANTILLAS ===
    
    def save_template_metadata(self, template) -> bool:
        """
        Guardar metadatos de una plantilla.
        
        Args:
            template: Plantilla cuyos metadatos se guardarán
            
        Returns:
            bool: True si se guardó correctamente
        """
        try:
            templates_dir = self.config_dir / "templates"
            templates_dir.mkdir(exist_ok=True)
            
            metadata = {
                "name": getattr(template, 'name', 'Unknown'),
                "description": getattr(template, 'description', ''),
                "type": getattr(template, '__class__.__name__', 'Template'),
                "brand": getattr(template, 'brand', 'Generic'),
                "parameters_count": len(getattr(template, 'parameters', {})),
                "methods_count": len(getattr(template, 'automation_methods', {})),
                "created_at": str(template.__dict__.get('created_at', 'unknown'))
            }
            
            metadata_file = templates_dir / f"{template.name}.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.info(f"Template metadata saved: {template.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving template metadata: {e}")
            return False
    
    def load_template_metadata(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Cargar metadatos de una plantilla.
        
        Args:
            template_name: Nombre de la plantilla
            
        Returns:
            Dict[str, Any]: Metadatos de la plantilla o None si no existe
        """
        try:
            templates_dir = self.config_dir / "templates"
            metadata_file = templates_dir / f"{template_name}.json"
            
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            self.logger.error(f"Error loading template metadata {template_name}: {e}")
            return None
    
    def get_user_templates(self) -> List[Dict[str, Any]]:
        """
        Obtener lista de plantillas de usuario.
        
        Returns:
            List[Dict[str, Any]]: Lista de metadatos de plantillas de usuario
        """
        try:
            templates_dir = self.config_dir / "templates"
            templates = []
            
            if templates_dir.exists():
                for metadata_file in templates_dir.glob("*.json"):
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                            templates.append(metadata)
                    except Exception as e:
                        self.logger.error(f"Error reading template metadata {metadata_file}: {e}")
            
            return templates
        except Exception as e:
            self.logger.error(f"Error getting user templates: {e}")
            return []
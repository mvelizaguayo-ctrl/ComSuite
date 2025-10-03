# src/config/template_manager.py
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class VFDTemplate:
    """Estructura de datos para plantillas VFD"""
    fabricante: str
    modelo: str
    protocolo: str
    direccion_modbus: int
    nombre_parametro: str
    acceso: str
    unidad: Optional[str]
    factor_escala: float
    rango_min: float
    rango_max: float
    descripcion: str
    categoria: str

class TemplateManager:
    """Gestor de plantillas VFD usando SQLite"""
    
    def __init__(self, db_path: str = "config/vfd_templates.db"):
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Verifica que la base de datos existe"""
        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"Base de datos no encontrada: {self.db_path}")
    
    def get_fabricantes(self) -> List[str]:
        """Obtiene lista de fabricantes disponibles"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT fabricante FROM vfd_templates ORDER BY fabricante")
        fabricantes = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return fabricantes
    
    def get_modelos_by_fabricante(self, fabricante: str) -> List[str]:
        """Obtiene modelos por fabricante"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT DISTINCT modelo FROM vfd_templates WHERE fabricante = ? ORDER BY modelo",
            (fabricante,)
        )
        modelos = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return modelos
    
    def get_parametros_by_modelo(self, fabricante: str, modelo: str) -> List[VFDTemplate]:
        """Obtiene parámetros por modelo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT fabricante, modelo, protocolo, direccion_modbus, nombre_parametro,
                   acceso, unidad, factor_escala, rango_min, rango_max, descripcion, categoria
            FROM vfd_templates 
            WHERE fabricante = ? AND modelo = ?
            ORDER BY categoria, nombre_parametro
        ''', (fabricante, modelo))
        
        parametros = []
        for row in cursor.fetchall():
            parametros.append(VFDTemplate(*row))
        
        conn.close()
        return parametros
    
    def get_parametros_by_categoria(self, fabricante: str, modelo: str, categoria: str) -> List[VFDTemplate]:
        """Obtiene parámetros filtrados por categoría"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT fabricante, modelo, protocolo, direccion_modbus, nombre_parametro,
                   acceso, unidad, factor_escala, rango_min, rango_max, descripcion, categoria
            FROM vfd_templates 
            WHERE fabricante = ? AND modelo = ? AND categoria = ?
            ORDER BY nombre_parametro
        ''', (fabricante, modelo, categoria))
        
        parametros = []
        for row in cursor.fetchall():
            parametros.append(VFDTemplate(*row))
        
        conn.close()
        return parametros
    
    def get_template_summary(self, fabricante: str, modelo: str) -> Dict[str, Any]:
        """Obtiene resumen de plantilla para el wizard"""
        parametros = self.get_parametros_by_modelo(fabricante, modelo)
        
        # Agrupar por categoría
        categorias = {}
        for param in parametros:
            if param.categoria not in categorias:
                categorias[param.categoria] = []
            categorias[param.categoria].append({
                'nombre': param.nombre_parametro,
                'direccion': param.direccion_modbus,
                'acceso': param.acceso,
                'unidad': param.unidad,
                'factor_escala': param.factor_escala,
                'rango': [param.rango_min, param.rango_max] if param.rango_max > 0 else None,
                'descripcion': param.descripcion
            })
        
        return {
            'fabricante': fabricante,
            'modelo': modelo,
            'protocolo': 'Modbus',
            'categorias': categorias
        }
    
    def search_templates(self, search_term: str) -> List[Dict[str, str]]:
        """Busca plantillas por fabricante o modelo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT fabricante, modelo 
            FROM vfd_templates 
            WHERE fabricante LIKE ? OR modelo LIKE ?
            ORDER BY fabricante, modelo
        ''', (f"%{search_term}%", f"%{search_term}%"))
        
        resultados = [{'fabricante': row[0], 'modelo': row[1]} for row in cursor.fetchall()]
        conn.close()
        return resultados

# Singleton para acceso global
template_manager = TemplateManager()
# src/utils/csv_to_sqlite.py
import sqlite3
import csv
import os
from pathlib import Path

def normalize_categoria(categoria_str):
    """Normaliza valores de categoría a los permitidos en la base de datos"""
    if not categoria_str:
        return 'Monitoreo'  # Valor por defecto
    
    categoria_lower = categoria_str.lower().strip()
    
    # Mapeo de valores comunes
    categoria_mapping = {
        'control': 'Control',
        'monitoreo': 'Monitoreo',
        'configuración': 'Configuración',
        'configuracion': 'Configuración',
        'diagnóstico': 'Diagnóstico',
        'diagnostico': 'Diagnóstico'
    }
    
    return categoria_mapping.get(categoria_lower, 'Monitoreo')

def migrate_csv_to_sqlite(csv_path, db_path):
    """Migra datos de CSV a SQLite para plantillas VFD"""
    
    # Crear directorio si no existe
    db_dir = Path(db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    
    # Conectar a SQLite (crea la base si no existe)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Crear tabla
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vfd_templates (
        id INTEGER PRIMARY KEY,
        fabricante TEXT NOT NULL,
        modelo TEXT NOT NULL,
        protocolo TEXT DEFAULT 'Modbus',
        direccion_modbus INTEGER NOT NULL,
        nombre_parametro TEXT NOT NULL,
        acceso TEXT CHECK(acceso IN ('R', 'W', 'R/W')),
        unidad TEXT,
        factor_escala REAL,
        rango_min REAL,
        rango_max REAL,
        descripcion TEXT,
        categoria TEXT CHECK(categoria IN ('Control', 'Monitoreo', 'Configuración', 'Diagnóstico')),
        UNIQUE(fabricante, modelo, nombre_parametro)
    )
    ''')
    
    # Leer CSV e insertar datos
    with open(csv_path, 'r', encoding='utf-8') as file:
        # Detectar el delimitador correcto
        sample = file.read(1024)
        file.seek(0)
        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(sample).delimiter
        
        csv_reader = csv.DictReader(file, delimiter=delimiter)
        
        for row in csv_reader:
            # Procesar rango con manejo de valores no numéricos
            rango_str = row.get('Rango', '') or ''
            rango_min = 0.0
            rango_max = 0.0
            
            if rango_str and not any(word in rango_str.lower() for word in ['bit', 'palabra', 'word']):
                try:
                    # Intentar procesar como rango numérico
                    rango = rango_str.split('–') if '–' in rango_str else rango_str.split('-')
                    if len(rango) >= 1:
                        rango_min = float(rango[0]) if rango[0] else 0.0
                    if len(rango) >= 2:
                        rango_max = float(rango[1]) if rango[1] else 0.0
                except (ValueError, IndexError):
                    # Si no se puede convertir, mantener 0.0
                    pass
            
            cursor.execute('''
            INSERT OR REPLACE INTO vfd_templates 
            (fabricante, modelo, protocolo, direccion_modbus, nombre_parametro, 
             acceso, unidad, factor_escala, rango_min, rango_max, descripcion, categoria)
            VALUES (?, ?, 'Modbus', ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row.get('Fabricante', '').strip(),
                row.get('Modelo', '').strip(),
                int(row.get('Dirección Modbus', 0)),
                row.get('Nombre', '').strip(),
                row.get('Acceso', '').strip(),
                row.get('Unidad', '').strip() if row.get('Unidad') else None,
                float(row.get('Factor Escala', 1.0)) if row.get('Factor Escala') else 1.0,
                rango_min,
                rango_max,
                row.get('Descripción', '').strip(),
                normalize_categoria(row.get('Categoría', ''))
            ))
    
    conn.commit()
    conn.close()
    print(f"Migración completada: {csv_path} -> {db_path}")

if __name__ == "__main__":
    # Rutas relativas al proyecto
    csv_path = "variadores_modbus.csv"
    db_path = "config/vfd_templates.db"
    
    migrate_csv_to_sqlite(csv_path, db_path)
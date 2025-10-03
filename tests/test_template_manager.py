# test_template_manager.py
import sys
from pathlib import Path

# Añadir el directorio raíz al path (subir un nivel desde tests/ a ComSuite/)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.template_manager import TemplateManager

try:
    tm = TemplateManager()
    fabricantes = tm.get_fabricantes()
    print(f"Fabricantes encontrados: {len(fabricantes)}")
    print(f"Primeros 5 fabricantes: {fabricantes[:5]}")
    
    if fabricantes:
        modelos = tm.get_modelos_by_fabricante(fabricantes[0])
        print(f"Modelos de {fabricantes[0]}: {len(modelos)}")
        print(f"Primeros 3 modelos: {modelos[:3]}")
        
        if modelos:
            resumen = tm.get_template_summary(fabricantes[0], modelos[0])
            print(f"Categorías: {list(resumen['categorias'].keys())}")
    
    print("✅ TemplateManager funciona correctamente")
except Exception as e:
    print(f"❌ Error en TemplateManager: {e}")
    import traceback
    traceback.print_exc()
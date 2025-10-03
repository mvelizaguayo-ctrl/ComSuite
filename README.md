ComSuite / ComTools
===================

Breve guía para desarrollo y ejecución

- Ejecutar en modo desarrollo (preferido):

```powershell
# Ejecutar la aplicación como paquete
python -m src

# (Opcional) Instalar en editable para que los tests y scripts la importen como paquete
pip install -e .
```

- Si prefieres ejecutar el script raíz (compatibilidad):

```powershell
python main.py
```

Notas:
- Recomiendo usar `python -m src` para evitar problemas con rutas y imports.
- Para ejecutar tests con pytest, instala en editable o ejecuta pytest desde la raíz con PYTHONPATH apuntando a la carpeta raíz.


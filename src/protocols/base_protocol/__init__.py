# src/protocols/base_protocol/__init__.py
# Ruta completa: C:\Users\manue\ComSuite\src\protocols\base_protocol\__init__.py

"""
Paquete base_protocol - Interfaces comunes para todos los protocolos en ComSuite.

Este paquete define las interfaces abstractas que deben implementar todos los protocolos
de comunicación soportados por ComSuite, garantizando consistencia y compatibilidad.
"""

from .protocol_interface import ProtocolInterface
from .device_interface import DeviceInterface, DeviceStatus

__all__ = [
    'ProtocolInterface',
    'DeviceInterface', 
    'DeviceStatus'
]

# Versión de las interfaces
__version__ = "1.0.0"
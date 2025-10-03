import sys
import os
import traceback

# Asegurarse de que los imports del proyecto funcionen
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('src'))
sys.path.insert(0, os.path.abspath('src/protocols'))

print('PYTHONPATH:', sys.path[:3])

try:
    from src.core.device_manager import DeviceManager
    print('Imported DeviceManager')
except Exception as e:
    print('Failed importing DeviceManager:', e)
    traceback.print_exc()
    raise

# Config de ejemplo (similar a la que emite el wizard)
cfg = {
    'device_type': 'vfd',
    'device_id': 'test_vfd_1',
    'fabricante': 'Siemens',
    'modelo': 'SINAMICS S120',
    'parametros': ['Freq', 'Voltage'],
    'protocol': 'Modbus TCP',
    'config': {
        'ip': '127.0.0.1',
        'port': 502
    }
}

try:
    dm = DeviceManager()
    dev = dm.create_device_from_template(cfg)
    print('create_device_from_template returned:', dev)
    print('Registered devices:', list(dm.devices.keys()))
except Exception as e:
    print('Exception during device creation:', type(e).__name__, e)
    traceback.print_exc()
    raise

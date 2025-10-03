import sys, os
# Ensure imports work when running as a standalone script
root = os.path.abspath(os.path.dirname(__file__))
if root not in sys.path:
    sys.path.insert(0, root)
src_dir = os.path.join(root, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from src.core.device_manager import DeviceManager

print('Iniciando test: crear grupo de 3 registros vía DeviceManager')

dm = DeviceManager()
regs = [
    {'function': '3x', 'address': 100},
    {'function': '4x', 'address': 200},
    {'function': '1x', 'address': 10},
]
cfg = {'protocol': 'Modbus TCP', 'ip': '127.0.0.1', 'port': 502, 'device_name': 'test_regs'}

template = {
    'device_type': 'register_group',
    'device_id': cfg.get('device_name'),
    'protocol': cfg.get('protocol'),
    'config': {'ip': cfg.get('ip'), 'port': cfg.get('port')},
    'registers': regs
}

device = dm.create_device_from_template(template)

print('Device object:', device)
if device is not None:
    print('Device ID:', getattr(device, 'device_id', None))
    print('Protocol:', getattr(device, 'protocol_name', None))
    print('Status:', getattr(device, 'status', None))
    print('Registers stored on object:', getattr(device, 'registers', None))
    try:
        print('get_info():', device.get_info())
    except Exception as e:
        print('get_info() error:', e)

print('All devices in DeviceManager:', list(dm.get_all_devices().keys()))

from src.core.communication_engine import CommunicationEngine
from src.gui.modes.expert_mode import ExpertMode

print('Iniciando simulación UI: abrir wizard "Otros" y finalizar con 3 registros')

engine = CommunicationEngine()
mode = ExpertMode(engine)

regs = [
    {'function': '3x', 'address': 101},
    {'function': '4x', 'address': 202},
    {'function': '1x', 'address': 11},
]
cfg = {'protocol': 'Modbus TCP', 'ip': '127.0.0.1', 'port': 502, 'device_name': 'ui_test_regs'}

# Llamar directamente al handler como si la wizard hubiera emitido registers_created
mode._on_registers_created(regs, cfg)

# Verificar en el engine.device_manager
dm = engine.device_manager
print('Devices now:', list(dm.get_all_devices().keys()))
if 'ui_test_regs' in dm.get_all_devices():
    d = dm.get_all_devices()['ui_test_regs']
    print('Device registers:', getattr(d, 'registers', None))
else:
    print('ui_test_regs not found')

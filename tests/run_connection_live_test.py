import sys
import os
import socket
import threading
import time
import traceback

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('src'))

from src.core.device_manager import DeviceManager

HOST = '127.0.0.1'
PORT = 15002

# Simple TCP server that accepts one connection and keeps it open briefly
def tcp_server(host, port, ready_evt):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(1)
    ready_evt.set()
    try:
        conn, addr = s.accept()
        print('Server: connection from', addr)
        time.sleep(2)
        conn.close()
    finally:
        s.close()

if __name__ == '__main__':
    ready = threading.Event()
    t = threading.Thread(target=tcp_server, args=(HOST, PORT, ready), daemon=True)
    t.start()
    ready.wait(timeout=2)
    time.sleep(0.1)

    cfg = {
        'device_type': 'vfd',
        'device_id': 'live_test_vfd',
        'fabricante': 'Test',
        'modelo': 'T1',
        'parametros': [],
        'protocol': 'Modbus TCP',
        'config': {
            'ip': HOST,
            'port': PORT
        }
    }

    try:
        dm = DeviceManager()
        dev = dm.create_device_from_template(cfg)
        print('create_device_from_template returned:', dev)
        print('Registered devices:', list(dm.devices.keys()))

        # Try to connect explicitly
        ok = dm.connect_device('live_test_vfd')
        print('connect_device returned:', ok)
    except Exception as e:
        print('Exception:', e)
        traceback.print_exc()

    time.sleep(1)

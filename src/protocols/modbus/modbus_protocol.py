# src/protocols/modbus/modbus_protocol.py
# Ruta completa: C:\Users\manue\ComSuite\src\protocols\modbus\modbus_protocol.py

from typing import List, Dict, Any, Optional
from protocols.base_protocol.protocol_interface import ProtocolInterface
from protocols.base_protocol.device_interface import DeviceInterface, DeviceStatus
from .modbus_device import ModbusDevice

class ModbusProtocol(ProtocolInterface):
    """
    Implementación del protocolo Modbus que envuelve las clases existentes.
    Soporta TCP y RTU, modo Master y Slave.
    """
    
    def __init__(self):
        self._name = "Modbus"
        self._version = "1.0.0"
        self._connected = False
        self._config = {}
        self._devices: Dict[str, ModbusDevice] = {}
        self._mode = "master"  # "master" o "slave"
        self._protocol_type = "TCP"  # "TCP" o "RTU"
        
        # Referencias a tus clases existentes
        self._master_instance = None
        self._slave_instance = None
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def version(self) -> str:
        return self._version
    
    def connect(self, config: Dict[str, Any]) -> bool:
        """
        Conecta el protocolo Modbus usando la configuración proporcionada.
        
        Args:
            config: Configuración de conexión Modbus
            
        Returns:
            bool: True si la conexión fue exitosa
        """
        try:
            self._config = config
            self._mode = config.get('mode', 'master')
            self._protocol_type = config.get('protocol_type', 'TCP')
            
            print(f"Conectando Modbus {self._protocol_type} en modo {self._mode}...")
            
            if self._mode == 'master':
                return self._connect_master(config)
            elif self._mode == 'slave':
                return self._connect_slave(config)
            else:
                print(f"❌ Modo inválido: {self._mode}")
                return False
                
        except Exception as e:
            print(f"❌ Error al conectar Modbus: {e}")
            return False
    
    def _connect_master(self, config: Dict[str, Any]) -> bool:
        """Conecta en modo Master usando tus clases existentes"""
        try:
            if self._protocol_type == 'TCP':
                from .master_tcp import ModbusMasterTCP
                self._master_instance = ModbusMasterTCP(
                    ip=config.get('ip', '127.0.0.1'),
                    port=config.get('port', 502),
                    slave_id=config.get('slave_id', 1)
                )
            else:  # RTU
                from .master_rtu import ModbusMasterRTU
                self._master_instance = ModbusMasterRTU(
                    port=config.get('port', 'COM3'),
                    baudrate=config.get('baudrate', 9600),
                    parity=config.get('parity', 'N'),
                    stopbits=config.get('stopbits', 1),
                    bytesize=config.get('bytesize', 8),
                    slave_id=config.get('slave_id', 1)
                )
            
            # Configurar callbacks para logging
            self._master_instance.set_log_callback(self._log_callback)
            self._master_instance.set_frame_callback(self._frame_callback)
            
            # Conectar
            if self._master_instance.connect():
                self._connected = True
                print(f"✅ Modbus {self._protocol_type} Master conectado")
                
                # Crear dispositivo por defecto
                device_id = f"modbus_{self._protocol_type}_{self._mode}"
                self._devices[device_id] = ModbusDevice(
                    device_id=device_id,
                    protocol_name=self._name,
                    master_instance=self._master_instance
                )
                
                return True
            else:
                print(f"❌ No se pudo conectar Modbus {self._protocol_type} Master")
                return False
                
        except Exception as e:
            print(f"❌ Error al conectar Modbus Master: {e}")
            return False
    
    def _connect_slave(self, config: Dict[str, Any]) -> bool:
        """Conecta en modo Slave usando tus clases existentes"""
        try:
            if self._protocol_type == 'TCP':
                from .slave_tcp import ModbusSlaveTCP
                self._slave_instance = ModbusSlaveTCP(
                    ip=config.get('ip', '127.0.0.1'),
                    port=config.get('port', 502),
                    slave_id=config.get('slave_id', 1)
                )
            else:  # RTU
                from .slave_rtu import ModbusSlaveRTU
                self._slave_instance = ModbusSlaveRTU(
                    port=config.get('port', 'COM3'),
                    baudrate=config.get('baudrate', 9600),
                    parity=config.get('parity', 'N'),
                    stopbits=config.get('stopbits', 1),
                    bytesize=config.get('bytesize', 8),
                    slave_id=config.get('slave_id', 1)
                )
            
            # Configurar callbacks
            self._slave_instance.set_log_callback(self._log_callback)
            self._slave_instance.set_frame_callback(self._frame_callback)
            
            # Iniciar servidor slave
            if self._slave_instance.start():
                self._connected = True
                print(f"✅ Modbus {self._protocol_type} Slave iniciado")
                
                # Crear dispositivo por defecto
                device_id = f"modbus_{self._protocol_type}_{self._mode}"
                self._devices[device_id] = ModbusDevice(
                    device_id=device_id,
                    protocol_name=self._name,
                    slave_instance=self._slave_instance
                )
                
                return True
            else:
                print(f"❌ No se pudo iniciar Modbus {self._protocol_type} Slave")
                return False
                
        except Exception as e:
            print(f"❌ Error al conectar Modbus Slave: {e}")
            return False
    
    def disconnect(self) -> None:
        """Desconecta el protocolo Modbus"""
        try:
            if self._connected:
                if self._mode == 'master' and self._master_instance:
                    self._master_instance.disconnect()
                elif self._mode == 'slave' and self._slave_instance:
                    self._slave_instance.stop()
                
                self._connected = False
                print("✅ Modbus desconectado")
        except Exception as e:
            print(f"❌ Error al desconectar Modbus: {e}")
    
    def is_connected(self) -> bool:
        """Verifica si el protocolo está conectado"""
        return self._connected

    def get_status(self):
        """Obtener el estado del protocolo como DeviceStatus"""
        try:
            return DeviceStatus.CONNECTED if self._connected else DeviceStatus.DISCONNECTED
        except Exception:
            return DeviceStatus.UNKNOWN
    
    def read_data(self, device_id: str, address: int, count: int) -> List[int]:
        """
        Lee datos de un dispositivo Modbus.
        
        Args:
            device_id: ID del dispositivo
            address: Dirección de inicio
            count: Cantidad de datos a leer
        
        Returns:
            List[int]: Datos leídos o lista vacía si hay error
        """
        try:
            device = self._devices.get(device_id)
            if not device:
                print(f"❌ Dispositivo no encontrado: {device_id}")
                return []
            
            return device.read_holding_registers(address, count)
            
        except Exception as e:
            print(f"❌ Error al leer datos de {device_id}: {e}")
            return []
    
    def write_data(self, device_id: str, address: int, data: List[int]) -> bool:
        """
        Escribe datos en un dispositivo Modbus.
        
        Args:
            device_id: ID del dispositivo
            address: Dirección de inicio
            data: Datos a escribir
        
        Returns:
            bool: True si la escritura fue exitosa
        """
        try:
            device = self._devices.get(device_id)
            if not device:
                print(f"❌ Dispositivo no encontrado: {device_id}")
                return False
            
            return device.write_holding_registers(address, data)
            
        except Exception as e:
            print(f"❌ Error al escribir datos en {device_id}: {e}")
            return False
    
    def get_devices(self) -> List[str]:
        """
        Obtiene la lista de dispositivos Modbus disponibles.
        
        Returns:
            List[str]: Lista de device_id disponibles
        """
        return list(self._devices.keys())
    
    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de un dispositivo Modbus.
        
        Args:
            device_id: ID del dispositivo
        
        Returns:
            Optional[Dict]: Información del dispositivo o None
        """
        device = self._devices.get(device_id)
        if device:
            return device.get_info()
        return None
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Valida si la configuración Modbus es correcta.
        
        Args:
            config: Configuración a validar
        
        Returns:
            bool: True si la configuración es válida
        """
        required_params = ['mode', 'protocol_type']
        
        for param in required_params:
            if param not in config:
                print(f"❌ Parámetro requerido faltante: {param}")
                return False
        
        # Validar modo
        if config['mode'] not in ['master', 'slave']:
            print(f"❌ Modo inválido: {config['mode']}")
            return False
        
        # Validar protocolo
        if config['protocol_type'] not in ['TCP', 'RTU']:
            print(f"❌ Protocolo inválido: {config['protocol_type']}")
            return False
        
        # Validar parámetros específicos por protocolo
        if config['protocol_type'] == 'TCP':
            if 'ip' not in config or 'port' not in config:
                print("❌ TCP requiere 'ip' y 'port'")
                return False
        else:  # RTU
            if 'port' not in config:
                print("❌ RTU requiere 'port'")
                return False
        
        print("✅ Configuración Modbus válida")
        return True
    
    def _log_callback(self, message: str):
        """Callback para mensajes de log"""
        print(f"[Modbus] {message}")
    
    def _frame_callback(self, direction: str, frame: bytes):
        """Callback para tramas Modbus"""
        print(f"[Modbus] {direction}: {frame.hex()}")
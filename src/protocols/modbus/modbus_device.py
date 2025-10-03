# src/protocols/modbus/modbus_device.py
# Ruta completa: C:\Users\manue\ComSuite\src\protocols\modbus\modbus_device.py

from typing import List, Dict, Any, Optional
from protocols.base_protocol.device_interface import DeviceInterface, DeviceStatus

class ModbusDevice(DeviceInterface):
    """
    Adaptador que envuelve las clases Modbus existentes en la interfaz DeviceInterface.
    """
    
    def __init__(self, device_id: str, protocol_name: str, 
                 master_instance=None, slave_instance=None):
        self._device_id = device_id
        self._protocol_name = protocol_name
        self._status = DeviceStatus.CONNECTED
        self._master_instance = master_instance
        self._slave_instance = slave_instance
        self._last_error = None
    
    @property
    def device_id(self) -> str:
        return self._device_id
    
    @property
    def protocol_name(self) -> str:
        return self._protocol_name
    
    @property
    def status(self) -> DeviceStatus:
        return self._status
    
    def get_info(self) -> Dict[str, Any]:
        """
        Obtiene información completa del dispositivo Modbus.
        
        Returns:
            Dict[str, Any]: Información del dispositivo
        """
        return {
            'device_id': self._device_id,
            'protocol': self._protocol_name,
            'type': 'Modbus Device',
            'status': self._status.value,
            'mode': 'Master' if self._master_instance else 'Slave',
            'capabilities': [
                'read_holding_registers',
                'write_holding_registers',
                'read_coils',
                'write_coils',
                'read_discrete_inputs',
                'read_input_registers'
            ]
        }
    
    def read_registers(self, start_address: int, count: int) -> List[int]:
        """
        Lee registros del dispositivo Modbus.
        
        Args:
            start_address: Dirección de inicio
            count: Cantidad de registros a leer
        
        Returns:
            List[int]: Lista de valores leídos
        """
        try:
            if self._master_instance:
                return self._master_instance.read_holding_registers(start_address, count)
            else:
                self._last_error = "No se puede leer en modo Slave"
                return []
        except Exception as e:
            self._last_error = str(e)
            return []
    
    def write_registers(self, start_address: int, values: List[int]) -> bool:
        """
        Escribe registros en el dispositivo Modbus.
        
        Args:
            start_address: Dirección de inicio
            values: Lista de valores a escribir
        
        Returns:
            bool: True si la escritura fue exitosa
        """
        try:
            if self._master_instance:
                return self._master_instance.write_holding_registers(start_address, values)
            else:
                self._last_error = "No se puede escribir en modo Slave"
                return False
        except Exception as e:
            self._last_error = str(e)
            return False
    
    def read_coils(self, start_address: int, count: int) -> List[bool]:
        """
        Lee coils del dispositivo Modbus.
        
        Args:
            start_address: Dirección de inicio
            count: Cantidad de coils a leer
        
        Returns:
            List[bool]: Lista de valores booleanos leídos
        """
        try:
            if self._master_instance:
                return self._master_instance.read_coils(start_address, count)
            else:
                self._last_error = "No se puede leer coils en modo Slave"
                return []
        except Exception as e:
            self._last_error = str(e)
            return []
    
    def write_coils(self, start_address: int, values: List[bool]) -> bool:
        """
        Escribe coils en el dispositivo Modbus.
        
        Args:
            start_address: Dirección de inicio
            values: Lista de valores booleanos a escribir
        
        Returns:
            bool: True si la escritura fue exitosa
        """
        try:
            if self._master_instance:
                return self._master_instance.write_multiple_coils(start_address, values)
            else:
                self._last_error = "No se puede escribir coils en modo Slave"
                return False
        except Exception as e:
            self._last_error = str(e)
            return False
    
    def read_discrete_inputs(self, start_address: int, count: int) -> List[bool]:
        """
        Lee discrete inputs del dispositivo Modbus.
        
        Args:
            start_address: Dirección de inicio
            count: Cantidad de discrete inputs a leer
        
        Returns:
            List[bool]: Lista de valores booleanos leídos
        """
        try:
            if self._master_instance:
                return self._master_instance.read_discrete_inputs(start_address, count)
            else:
                self._last_error = "No se puede leer discrete inputs en modo Slave"
                return []
        except Exception as e:
            self._last_error = str(e)
            return []
    
    def read_input_registers(self, start_address: int, count: int) -> List[int]:
        """
        Lee input registers del dispositivo Modbus.
        
        Args:
            start_address: Dirección de inicio
            count: Cantidad de registros a leer
        
        Returns:
            List[int]: Lista de valores leídos
        """
        try:
            if self._master_instance:
                return self._master_instance.read_input_registers(start_address, count)
            else:
                self._last_error = "No se puede leer input registers en modo Slave"
                return []
        except Exception as e:
            self._last_error = str(e)
            return []
    
    def get_last_error(self) -> Optional[str]:
        """
        Obtiene el último error ocurrido.
        
        Returns:
            Optional[str]: Mensaje de error o None
        """
        return self._last_error
    
    def is_available(self) -> bool:
        """
        Verifica si el dispositivo está disponible.
        
        Returns:
            bool: True si está disponible
        """
        return self._status == DeviceStatus.CONNECTED

    # Compatibilidad: algunos paneles y código esperan is_connected()
    def is_connected(self) -> bool:
        return self.is_available()

    def connect(self) -> bool:
        """Intentar conectar el dispositivo usando la instancia master/slave asociada.

        Devuelve True si la conexión fue exitosa.
        """
        try:
            if self._master_instance and hasattr(self._master_instance, 'connect'):
                ok = self._master_instance.connect()
                if ok:
                    self._status = DeviceStatus.CONNECTED
                return ok

            if self._slave_instance and hasattr(self._slave_instance, 'start'):
                ok = self._slave_instance.start()
                if ok:
                    self._status = DeviceStatus.CONNECTED
                return ok

            # Si no hay instancias vinculadas, no se puede conectar
            self._last_error = "No hay instancia master/slave para conectar"
            return False
        except Exception as e:
            self._last_error = str(e)
            return False

    def disconnect(self) -> bool:
        """Intentar desconectar el dispositivo."""
        try:
            if self._master_instance and hasattr(self._master_instance, 'disconnect'):
                self._master_instance.disconnect()
                self._status = DeviceStatus.DISCONNECTED
                return True

            if self._slave_instance and hasattr(self._slave_instance, 'stop'):
                self._slave_instance.stop()
                self._status = DeviceStatus.DISCONNECTED
                return True

            self._last_error = "No hay instancia master/slave para desconectar"
            return False
        except Exception as e:
            self._last_error = str(e)
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """
        Obtiene la configuración actual del dispositivo.
        
        Returns:
            Dict[str, Any]: Configuración actual
        """
        return {
            'device_id': self._device_id,
            'protocol': self._protocol_name,
            'status': self._status.value
        }
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        """
        Actualiza la configuración del dispositivo.
        
        Args:
            config: Nueva configuración
        
        Returns:
            bool: True si la actualización fue exitosa
        """
        try:
            if 'device_id' in config:
                self._device_id = config['device_id']
            if 'status' in config:
                self._status = DeviceStatus(config['status'])
            return True
        except Exception as e:
            self._last_error = str(e)
            return False
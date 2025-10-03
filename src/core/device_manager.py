# src/core/device_manager.py
import logging
from typing import Dict, List, Optional, Any
from ..protocols.base_protocol.device_interface import DeviceInterface, DeviceStatus
from ..protocols.modbus.modbus_device import ModbusDevice
from ..protocols.modbus.modbus_protocol import ModbusProtocol

class DeviceManager:
    """Gestor de dispositivos VFD simplificado."""
    
    def __init__(self):
        self.devices: Dict[str, DeviceInterface] = {}
        self.logger = logging.getLogger(__name__)
        
    def register_device(self, device: DeviceInterface) -> bool:
        """Registrar un nuevo dispositivo."""
        if device.device_id in self.devices:
            self.logger.warning(f"Device {device.device_id} already registered")
            return False
        
        self.devices[device.device_id] = device
        self.logger.info(f"Device {device.device_id} registered successfully")
        return True
    
    def unregister_device(self, device_id: str) -> bool:
        """Eliminar un dispositivo registrado."""
        if device_id not in self.devices:
            self.logger.warning(f"Device {device_id} not found")
            return False
        
        del self.devices[device_id]
        self.logger.info(f"Device {device_id} unregistered successfully")
        return True
    
    def get_device(self, device_id: str) -> Optional[DeviceInterface]:
        """Obtener un dispositivo por su ID."""
        return self.devices.get(device_id)
    
    def get_all_devices(self) -> Dict[str, DeviceInterface]:
        """Obtener todos los dispositivos registrados (compatibilidad: devuelve dict).

        Muchas partes del UI esperan un diccionario {device_id: device}.
        """
        return self.devices.copy()
    
    def get_devices_by_protocol(self, protocol_name: str) -> List[DeviceInterface]:
        """Obtener dispositivos por protocolo."""
        return [device for device in self.devices.values() 
                if device.protocol_name == protocol_name]
    
    def get_devices_by_status(self, status: DeviceStatus) -> List[DeviceInterface]:
        """Obtener dispositivos por estado."""
        return [device for device in self.devices.values() 
                if device.status == status]

    def connect_device(self, device_id: str) -> bool:
        """Intentar conectar un dispositivo por su ID.

        Si el dispositivo tiene asociado un objeto protocolo con configuración,
        intenta reconectar el protocolo. Si el dispositivo es un ModbusDevice
        que tiene _master_instance/_slave_instance, intenta usar sus métodos.
        """
        device = self.get_device(device_id)
        if device is None:
            self.logger.error(f"connect_device: dispositivo {device_id} no encontrado")
            return False

        # Si ya está conectado, devolver True
        try:
            if device.status == DeviceStatus.CONNECTED:
                return True
        except Exception:
            pass

        # Intentar reconectar usando el protocolo asociado si existe
        protocol = getattr(device, '_protocol', None)
        protocol_config = getattr(device, '_protocol_config', None)

        if protocol and protocol_config:
            try:
                ok = protocol.connect(protocol_config)
                if ok:
                    try:
                        device._status = DeviceStatus.CONNECTED
                    except Exception:
                        pass
                    return True
            except Exception as e:
                self.logger.error(f"Error reconectando protocolo para {device_id}: {e}")

        # Intentar usar API del propio dispositivo
        try:
            if hasattr(device, 'connect'):
                return device.connect()
        except Exception as e:
            self.logger.error(f"Error llamando device.connect() para {device_id}: {e}")

        return False

    def disconnect_device(self, device_id: str) -> bool:
        """Intentar desconectar un dispositivo por su ID."""
        device = self.get_device(device_id)
        if device is None:
            self.logger.error(f"disconnect_device: dispositivo {device_id} no encontrado")
            return False

        try:
            if hasattr(device, 'disconnect'):
                ok = device.disconnect()
                try:
                    if ok:
                        device._status = DeviceStatus.DISCONNECTED
                except Exception:
                    pass
                return ok
        except Exception as e:
            self.logger.error(f"Error llamando device.disconnect() para {device_id}: {e}")

        # Si el protocolo asociado tiene método disconnect
        protocol = getattr(device, '_protocol', None)
        if protocol and hasattr(protocol, 'disconnect'):
            try:
                protocol.disconnect()
                try:
                    device._status = DeviceStatus.DISCONNECTED
                except Exception:
                    pass
                return True
            except Exception as e:
                self.logger.error(f"Error desconectando protocolo para {device_id}: {e}")

        return False
    
    def create_vfd_device(self, device_id: str, fabricante: str, modelo: str, 
                         parametros: List[str], config: Dict[str, Any]) -> Optional[DeviceInterface]:
        """
        Crear un dispositivo VFD con la información del wizard.
        
        Args:
            device_id: ID único del dispositivo
            fabricante: Fabricante del VFD
            modelo: Modelo del VFD
            parametros: Lista de parámetros a monitorear
            config: Configuración de comunicación
            
        Returns:
            DeviceInterface: El dispositivo creado o None si falla
        """
        try:
            self.logger.info(f"Creando dispositivo VFD con ID: {device_id}")
            self.logger.info(f"Fabricante: {fabricante}, Modelo: {modelo}")
            self.logger.info(f"Parámetros: {parametros}")
            
            # Extraer configuración del protocolo
            protocol_config = self._extract_protocol_config(config)

            # Crear el protocolo Modbus (firma sin parámetros) y conectar
            protocol = ModbusProtocol()
            try:
                connected = protocol.connect(protocol_config)
            except Exception as e:
                self.logger.error(f"Excepción al conectar protocolo Modbus: {e}")
                connected = False

            if not connected:
                # No se pudo conectar el protocolo ahora, pero permitimos crear el dispositivo
                # en estado desconectado para que la UI lo muestre y el usuario pueda intentar
                # conectarlo más tarde.
                self.logger.warning(f"No se pudo conectar el protocolo Modbus con config: {protocol_config} - creando dispositivo en modo desconectado")

            # Obtener instancias master/slave del protocolo (atributos internos)
            master_instance = getattr(protocol, '_master_instance', None)
            slave_instance = getattr(protocol, '_slave_instance', None)

            # Crear el dispositivo usando la firma actual de ModbusDevice
            device = ModbusDevice(
                device_id=device_id,
                protocol_name=getattr(protocol, 'name', 'Modbus'),
                master_instance=master_instance,
                slave_instance=slave_instance
            )

            # Si no hay conexión, marcar el dispositivo como desconectado
            if not connected:
                try:
                    device._status = DeviceStatus.DISCONNECTED
                except Exception:
                    pass

            # Guardar referencia al objeto protocolo y su configuración para permitir reconexiones
            try:
                device._protocol = protocol
                device._protocol_config = protocol_config
            except Exception:
                pass
            
            # Añadir información específica del VFD al dispositivo
            device.fabricante = fabricante
            device.modelo = modelo
            device.parametros_seleccionados = parametros
            
            # Registrar el dispositivo
            if self.register_device(device):
                self.logger.info(f"Dispositivo VFD creado exitosamente: {device_id}")
                return device
            else:
                self.logger.error(f"No se pudo registrar el dispositivo: {device_id}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creando dispositivo VFD: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    # Método de compatibilidad: algunas partes del código (o versiones antiguas) esperan
    # un método llamado `create_device_from_template`. Para mantener compatibilidad, lo
    # delegamos en `create_vfd_device` cuando el tipo de dispositivo sea 'vfd'.
    def create_device_from_template(self, template_config: Dict[str, Any]) -> Optional[DeviceInterface]:
        """
        Crear un dispositivo a partir de una plantilla (compatibilidad hacia atrás).
        Espera un diccionario con claves similares a las emitidas por el wizard.
        """
        try:
            device_type = template_config.get('device_type', 'vfd')

            # Normalize device_id
            device_id = template_config.get('device_id') or f"{device_type}_{len(self.devices)+1}"

            # If it's a VFD, delegate to the existing factory
            if device_type == 'vfd':
                fabricante = template_config.get('fabricante', template_config.get('manufacturer', 'Unknown'))
                modelo = template_config.get('modelo', template_config.get('model', 'Unknown'))
                parametros = template_config.get('parametros', template_config.get('parameters', []))
                # Pasar el template_config completo a create_vfd_device para que
                # _extract_protocol_config pueda encontrar la clave 'config' con ip/port.
                return self.create_vfd_device(device_id, fabricante, modelo, parametros, template_config)

            # Para otros tipos (sensor, plc, custom) creamos un dispositivo genérico
            self.logger.info(f"create_device_from_template: creando dispositivo genérico tipo '{device_type}' id '{device_id}'")

            # Extraer configuración del protocolo
            protocol_config = self._extract_protocol_config(template_config)

            # Intentar crear y conectar protocolo Modbus (si corresponde)
            protocol = ModbusProtocol()
            try:
                connected = protocol.connect(protocol_config)
            except Exception as e:
                self.logger.error(f"Excepción al conectar protocolo Modbus (genérico): {e}")
                connected = False

            if not connected:
                self.logger.warning(f"No se pudo conectar el protocolo Modbus con config: {protocol_config} - creando dispositivo en modo desconectado")

            master_instance = getattr(protocol, '_master_instance', None)
            slave_instance = getattr(protocol, '_slave_instance', None)

            device = ModbusDevice(
                device_id=device_id,
                protocol_name=getattr(protocol, 'name', 'Modbus'),
                master_instance=master_instance,
                slave_instance=slave_instance
            )

            if not connected:
                try:
                    device._status = DeviceStatus.DISCONNECTED
                except Exception:
                    pass

            # Guardar referencias para reconexión posterior
            try:
                device._protocol = protocol
                device._protocol_config = protocol_config
            except Exception:
                pass

            # Si el template incluye una lista de registros, adjuntarla al dispositivo
            try:
                regs = template_config.get('registers') if isinstance(template_config, dict) else None
                if regs is not None:
                    # normalizar a lista
                    device.registers = regs if isinstance(regs, list) else [regs]
            except Exception:
                pass

            # Metadata mínima
            try:
                device.device_type = device_type
            except Exception:
                pass

            # Registrar dispositivo
            if self.register_device(device):
                self.logger.info(f"Dispositivo genérico creado exitosamente: {device_id}")
                return device
            else:
                self.logger.error(f"No se pudo registrar el dispositivo genérico: {device_id}")
                return None

        except Exception as e:
            self.logger.error(f"Error en create_device_from_template: {e}")
            return None
    
    def _extract_protocol_config(self, device_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extraer la configuración del protocolo desde la configuración del dispositivo.
        
        Args:
            device_config: Configuración completa del dispositivo
            
        Returns:
            Dict[str, Any]: Configuración específica del protocolo
        """
        protocol_config = {
            'protocol': device_config.get('protocol', 'Modbus TCP')
        }
        
        # Añadir configuración específica según el protocolo
        if 'config' in device_config:
            config = device_config['config']
            
            if 'ip' in config and 'port' in config:
                # Configuración TCP
                protocol_config.update({
                    'connection_type': 'TCP',
                    'ip': config['ip'],
                    'port': config['port']
                })
            elif 'com_port' in config and 'baudrate' in config:
                # Configuración RTU
                protocol_config.update({
                    'connection_type': 'RTU',
                    'com_port': config['com_port'],
                    'baudrate': config['baudrate']
                })
        
        return protocol_config
import serial
import logging
import subprocess
import threading
import time

logger = logging.getLogger(__name__)

from ..utility.config import SystemConfig as HubConfig, T_LTE_CONFIG

class LTE:
    _instance = None
    apn = None
    config:T_LTE_CONFIG = None
    port = None
    baudrate = None
    serial_connection = None
    timeout = None
    thread = None
    stop_event = None
    gnss_lock = None
    gnss_data = None
    
    def __new__(cls):
        if cls._instance is None:
            try:
                logger.info("Creating LTE instance.")
                cls._instance = super(LTE, cls).__new__(cls)
                
                config = HubConfig()
                cls._instance.config = config.get_config('lte')
                
                cls._instance.port = f"/dev/{cls._instance.config['device_id']}"
                cls._instance.apn = cls._instance.config['apn']
                cls._instance.baudrate = 115200
                cls._instance.serial_connection = None
                cls._instance.timeout = 1
                
                cls._instance.gnss_lock = threading.Lock()
                cls._instance.gnss_data = ""
                
                command = ["systemctl", "stop", "ModemManager"]
                result = subprocess.run(command, capture_output=True, text=True)
                if result.returncode == 0:
                    logger.debug("ModemManager stopped.")
                else:
                    logger.error(f"Failed to stop ModemManager, {result.stderr}")
            except Exception as error:
                logger.error(f"Error creating LTE instance: {error}")
                raise Exception("LTE not created.")
        return cls._instance

            
    def __del__(self):
        self.stop_gnss()

    def _connect(self):
        self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        if self.serial_connection.is_open:
            logger.debug(f"Connected to {self.port} at {self.baudrate} baud.")
        else:
            raise Exception("Failed to open serial port.")

    def _disconnect(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            logger.debug("Disconnected from serial port.")

    def _send_at_command(self, command):
        try:
            if not self.serial_connection or not self.serial_connection.is_open:
                self._connect()

            self.serial_connection.write((command + '\r\n').encode())
            response = self.serial_connection.readlines()
            return ";".join([l.decode().strip() for l in response])
        except Exception as error:
            logger.error(f"Failed to send AT command '{command}': {error}")
            raise

    def configure_network(self):
        r = self._send_at_command('AT')
        if "OK" not in r:
            raise Exception("Module not ready.")
        
        # ECM mode
        r = self._send_at_command('AT#USBCFG?')
        if 'USBCFG: 3' not in r:
            self._send_at_command('AT#USBCFG=3')
            self._disconnect()
        
            connected = False
            for _ in range(60):
                try:
                    self._connect()
                    r = self._send_at_command('AT')
                    if "OK" in r:
                        connected = True
                    break
                except Exception as error:
                    logger.debug("Failed to connect to serial port. Retrying...")
                    time.sleep(1)
            if not connected:
                raise Exception("Failed to connect to serial port.")

        r = self._send_at_command(f'AT+CGDCONT=1, "ip", "{self.apn}"')        
        r = self._send_at_command('AT+COPS=0')
        r = self._send_at_command('AT+CGREG?')
        if '0,5' in r or '0,1' in r:
            logger.debug(f"LTE network, {r}")
        else:
            logger.debug(f"Failed to register to LTE network, {r}")
            raise Exception("Failed to configure network.")
        
        r = self._send_at_command('AT#ECM=1,0')
        r = self._send_at_command('AT#SGACT=1,1')
        
        cmd = ["udhcpc", "-q", "-f", "-i", "wwan0"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            logger.debug("dhcp client started.")
        else:
            logger.error(f"Failed to start dhcp, {result.stderr}")
            
    def configure_gnss(self):
        r = self._send_at_command('AT')
        if "OK" not in r:
            raise Exception("Module not ready.")
        
        r = self._send_at_command('AT$GPSP=1')

    def start_gnss(self):
        if self.serial_connection is None:
            raise Exception("Serial connection is not open.")
        
        if not self.serial_connection.is_open:
            self.serial_connection.open()
            
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._gnss_thread)
        self.thread.start()
        return True
    
    def get_gnss(self):
        with self.gnss_lock:
            return self.gnss_data
    
    def save_gnss(self, data):
        with self.gnss_lock:
            logger.debug(f"GNSS: {data}")
            self.gnss_data = data
    
    def _gnss_thread(self):
        count = 0
        while not self.stop_event.is_set():
            try:
                if count == 0:
                    r = self._send_at_command('AT$GPSACP')
                    self.save_gnss(r)
                count = 0 if count == 60 else count + 1
            except Exception as error:
                logger.error(f"Error reading GNSS: {error}")
                break
            time.sleep(1)
        pass
    
    def stop_gnss(self):
        logger.debug("Stopping GNSS")
        if self.stop_event:
            self.stop_event.set()
        if self.thread:
            self.thread.join()
        self._disconnect()
        logger.debug("GNSS stopped.")
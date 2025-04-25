import serial as Serial
import logging
import threading
import json

from ..utility.config import SystemConfig as HubConfig
from ..utility.config import T_BLE_CONFIG
from ..utility.cmd_interface import CMD_INTERFACE

logger = logging.getLogger(__name__)

class BLE:
    _instance = None
    port = None
    baudrate = None
    timeout = None
    serial_connection = None
    config:T_BLE_CONFIG = None
    thread = None
    stop_event = None

    def __new__(cls):
        if cls._instance is None:
            try:
                logger.info("Creating BLE instance.")
                cls._instance = super(BLE, cls).__new__(cls)

                config = HubConfig()
                cls._instance.config = config.get_config('ble')

                cls._instance.port = f"/dev/{cls._instance.config['uart']['device_id']}"
                cls._instance.baudrate = cls._instance.config["uart"]["baudrate"]
                cls._instance.timeout = 1

            except Exception as error:
                logger.error(f"Error creating BLE instance: {error}")
                raise Exception("BLE not created.")
        return cls._instance

    def __del__(self):
        self.stop()

    def _connect(self):
        self.serial_connection = Serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        if self.serial_connection.isOpen():
            logger.debug(f"Connected to {self.port} at {self.baudrate} baud.")
        else:
            raise Exception("Failed to open serial port.")

    def _disconnect(self):
        if self.serial_connection and self.serial_connection.isOpen():
            self.serial_connection.close()
            logger.debug("Disconnected from serial port.")

    def configure(self):
        if not self.serial_connection or not self.serial_connection.isOpen():
            self._connect()
        pass

    def start(self):
        if self.serial_connection is None:
            raise Exception("BLE UART not available")

        if not self.serial_connection.isOpen():
            self.serial_connection.open()

        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._read_thread)
        self.thread.start()
        return True

    def _read_thread(self):
        while not self.stop_event.is_set():
            try:
                line = self.serial_connection.readline()
                if line:
                    res = ""
                    l = line.split("-", 1)
                    if len(l) == 2:
                        cmd = l[0].lower()
                        data = l[1]

                        if cmd in CMD_INTERFACE:
                            res = CMD_INTERFACE[cmd](data)
                        else:
                            logger.error(f"Unknown cmd, {cmd}")
                            res = json.dumps({"error": "unknown cmd", "data": None})
                    else:
                        logger.error(f"Invalid data: f{line}")
                        res = json.dumps({"error": "invalid data", "data": None})
                    self._send_data(res)
            except Serial.SerialException:
                logger.error(f"Error reading BLE UART: {Serial.SerialException}")
                break
            except Exception as error:
                logger.error(f"Error reading BLE UART: {error}")
                break

    def _send_data(self, data):
        if self.serial_connection and self.serial_connection.isOpen():
            try:
                self.serial_connection.write(data.encode())
                logger.debug(f"Sent data to BLE: {data}")
            except Serial.SerialException:
                logger.error(f"Error sending data to BLE UART: {Serial.SerialException}")
            except Exception as error:
                logger.error(f"Error sending data to BLE UART: {error}")
        else:
            logger.error("BLE UART is not open")

    def stop(self):
        logger.debug("Stopping BLE")
        if self.stop_event:
            self.stop_event.set()
        if self.thread:
            self.thread.join()
        self._disconnect()
        logger.debug("BLE stopped")

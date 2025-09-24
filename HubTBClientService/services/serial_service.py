import threading
import serial
# pylint: disable= import-error, no-name-in-module
from tb_utils.constants import Constants
from n2kclient.util.settings_util import SettingsUtil

# Port for GNSS connection
SERIAL_PORT = SettingsUtil.get_setting(
    Constants.THINGSBOARD_SETTINGS_KEY,
    Constants.GNSS,
    Constants.SERIAL_PORT,
    default_value="/dev/ttyUSB1"
)

class SerialServiceSingleton:
    """
    Singleton class to manage serial communication with the telit modem.
    So we can have multiple services using the same serial connection.
    It uses a lock to ensure thread-safe access to the serial port and
    makes sure there is only one command being sent at a time.
    """
    _instance = None
    _lock = threading.Lock()
    _command_lock: threading.Lock

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(SerialServiceSingleton, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = False
        if self._initialized:
            return
        try:
            self._command_lock = threading.Lock()
            self.serial_connection = serial.Serial(SERIAL_PORT, baudrate=115200, timeout=1)
            self.turn_on_gps()
        except Exception as e:
            self.serial_connection = None
            print(f"Error initializing serial connection: {e}")
        self._initialized = True

    def turn_on_gps(self):
        with self._command_lock:
            try:
                self.serial_connection.flush()
                self.serial_connection.write(b'AT+CGPS=1\r')
                _ = self.serial_connection.read_until(b'OK\r\n')
            except Exception as e:
                print(f"Error turning on GPS: {e}")

    def write(self, at_command: str):
        with self._command_lock:
            try:
                self.serial_connection.write(at_command.encode())
                return self.serial_connection.read(self.serial_connection.in_waiting)
            except Exception as e:
                print(f"Error writing AT command: {e}")
                return b""

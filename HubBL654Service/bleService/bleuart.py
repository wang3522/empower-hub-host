import serial as Serial
import logging
import threading
import json
import hashlib
import time
import os
import zipfile
import shutil

from utility.cmd_interface import CMD_INTERFACE, CMD_INTERFACE_INSTANCE
from .uart_message_processor import load_key, decrypt_data

logger = logging.getLogger(__name__)

class BLE_UART:
    _instance = None
    port = None
    baudrate = None
    timeout = None
    serial_connection = None
    config = None
    thread = None
    is_authenticated = False
    stop_event = None

    def __new__(cls):
        if cls._instance is None:
            try:
                logger.info("Creating BLE uart instance.")
                cls._instance = super(BLE_UART, cls).__new__(cls)
                
                config_file_path = "/data/hub/config/bl654.conf"
                if os.path.exists(config_file_path):
                    with open(config_file_path, 'r') as file:
                        content = file.readlines()
                        if len(content) >= 2:
                            cls._instance.port = content[0].strip()
                            cls._instance.baudrate = int(content[1].strip())
                        else:
                            raise Exception(f"invalid config file {config_file_path}")
                else:
                    raise Exception(f"config file not found, at {config_file_path}")

                cls._instance.timeout = 1
                CMD_INTERFACE_INSTANCE.set_uart_authenticated_callback(cls._instance.set_is_authenticated)
            except Exception as error:
                logger.error(f"Error creating BLE uart instance: {error}")
                raise Exception("BLE uart not created.")
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

        load_key()

        if not self.serial_connection.isOpen():
            self.serial_connection.open()

        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._read_thread)
        self.thread.start()
        return True

    def handle_ota_transfer(self, zip_path: str):
        logger.debug("Starting OTA zip transfer: {}".format(zip_path))
        chunk_size = 1024

        extract_dir = "/tmp/ota_unpacked"
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        os.makedirs(extract_dir)

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        except Exception as e:
            logger.error("Failed to unzip OTA package: {}".format(e))
            return

        sorted_files = sorted(
            (os.path.join(root, f), os.path.relpath(os.path.join(root, f), extract_dir).replace("\\", "/"))
            for root, _, files in os.walk(extract_dir)
            for f in sorted(files)
        )

        session_hash = hashlib.sha256()
        for full_path, _ in sorted_files:
            try:
                with open(full_path, "rb") as f:
                    session_hash.update(f.read())
            except Exception as e:
                logger.error(f"Failed to read for checksum: {full_path}: {e}")
                return

        ota_checksum = session_hash.hexdigest()
        total_files = len(sorted_files)

        self._send_data(f"BL/OTA_UPDATE_METADATA/{total_files},{ota_checksum}\n")
        time.sleep(3)

        for full_path, rel_path in sorted_files:
            try:
                with open(full_path, "rb") as f:
                    content = f.read()
            except Exception as e:
                logger.error("Failed to read file {}: {}".format(rel_path, e))
                continue

            chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
            checksum = hashlib.sha256(content).hexdigest()
            header_cmd = "BL/OTA_HEADER/{},{},{},{}".format(rel_path, len(chunks), len(content), checksum)
            self._send_data(header_cmd + "\n")
            time.sleep(0.25)

            for idx, chunk in enumerate(chunks):
                hex_chunk = chunk.hex()
                data_cmd = "BL/OTA_DATA/{}/{}".format(idx, hex_chunk)
                self._send_data(data_cmd + "\n")
                time.sleep(0.2)
        return

    def _read_thread(self):
        while not self.stop_event.is_set():
            try:
                line = self.serial_connection.readline()
                if line:
                    decoded_line = line.decode("utf-8", errors="ignore").strip()
                    res = ""
                    l = decoded_line.split("/", 1)
                    if len(l) == 2:
                        cmd = l[0].lower()
                        data = l[1]
                        split_data = data.split("/")
                        data_cmd = split_data[0].lower()
                        cleaned_data = ""
                        if cmd in CMD_INTERFACE:
                            if len(split_data) > 1:
                                data_payload_hex = split_data[1].lower()
                                data_payload = bytes.fromhex(data_payload_hex)
                                if (self.is_authenticated and not data_cmd == "reset_grant_level"):
                                    cleaned_data = decrypt_data(data_payload).decode("utf-8", "ignore")
                                else:
                                    cleaned_data = data_payload.decode("utf-8", "ignore")
                            res = CMD_INTERFACE[cmd](data_cmd + "/" + cleaned_data)
                        else:
                            logger.error(f"Unknown cmd, {cmd}")
                    else:
                        logger.error(f"Invalid data: {line}")
                    if res.startswith("OTA_CONSENTED"):
                        try:
                            with open("/data/ota_consent.txt", "w") as f:
                                f.write("")
                        except Exception as e:
                            logger.error(f"Failed to write OTA consent file: {e}")
                        continue
                    if res.startswith("OTA_STATUS/"):
                        from ..dbusService.server import get_dbus_server_instance
                        dbus_obj = get_dbus_server_instance()
                        status = res.split("/")[1].strip()
                        if status == "success":
                            if dbus_obj:
                                dbus_obj.bl654_object.ota_complete("success")
                            else:
                                logger.warning("Dbus not set, could not signal ota_complete")
                        elif status == "error":
                            if dbus_obj:
                                dbus_obj.bl654_object.ota_error("error")
                            else:
                                logger.warning("DBus not set; could not signal ota_error")
                        continue
                    if res.startswith("NOTIFY_VERSION/"):
                        from ..dbusService.server import get_dbus_server_instance
                        dbus_obj = get_dbus_server_instance()
                        if dbus_obj:
                            dbus_obj.bl654_object.notify_version(res.split("/")[1].strip())
                        continue
                    if res.startswith("MX93/NOT_IMPLEMENTED"):
                        continue
                    if res.strip():
                        self._send_data(res)
            except Serial.SerialException:
                logger.error(f"Error reading BLE UART - serial exception: {Serial.SerialException}")
            except Exception as error:
                logger.error(f"Error reading BLE UART: {error}")

    def _send_data(self, data):
        if self.serial_connection and self.serial_connection.isOpen():
            try:
                logger.debug(f"Sending data to BLE UART: {data.encode()}")
                self.serial_connection.write(data.encode('utf-8'))
            except Serial.SerialException:
                logger.error(f"Error sending data to BLE UART: {Serial.SerialException}")
            except Exception as error:
                logger.error(f"Error sending data to BLE UART: {error}")
        else:
            logger.error("BLE UART is not open")

    def stop(self):
        logger.debug("Stopping BLE UART")
        if self.stop_event:
            self.stop_event.set()
        if self.thread:
            self.thread.join()
        self._disconnect()
        logger.debug("BLE UART stopped")

    def set_is_authenticated(self, authenticated: bool):
        self.is_authenticated = authenticated
        logger.debug(f"BLE UART authentication status set to {authenticated}")

    def request_application_version(self):
        self._send_data("MX93/VERSION\n")
        logger.debug("Requested application version from BL654")

    def get_cmd_interface(self):
        return CMD_INTERFACE_INSTANCE
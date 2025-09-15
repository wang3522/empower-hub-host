import serial as Serial
import logging
import threading
import json
import hashlib
import time
import os
import zipfile
import shutil
import subprocess

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
    _dbus_server = None

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

        self.handle_on_wake_up()
        return True

    def handle_on_wake_up(self):
        self._send_data("MX93/HELLO\n")
        logger.debug("Sent HELLO to BL654")

    def handle_ota_transfer(self, file_path: str):
        error_message = "MX93/OTA_TRANSFER_STATUS/error\n"
        success_message = "MX93/OTA_TRANSFER_STATUS/success\n"
        logger.debug("Starting OTA transfer: {}".format(file_path))
        chunk_size = 1024

        if file_path.endswith(".bin"):
            ota_type = "fw"
            packaged_name = os.path.basename(file_path)
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
            except Exception as e:
                logger.error("Failed to read OTA file {}: {}".format(file_path, e))
                self._send_data(error_message)
                return
        else:
            ota_type = "app"
            try:
                packaged_name = f"{os.path.basename(file_path)}_update.zip"
                packaged_path = os.path.join("/data", packaged_name)

                if os.path.exists(packaged_path):
                    logger.debug(f"Deleting old package at {packaged_path}")
                    os.remove(packaged_path)

                script_dir = os.path.dirname(os.path.abspath(__file__))
                packager = os.path.join(script_dir, "canvas_packager.py")
                subprocess.run([
                    "python3", packager,
                    "--version", "update",
                    file_path
                ], cwd="/data")

                input_files = sum(len(files) for _, _, files in os.walk(file_path))
                with zipfile.ZipFile(packaged_path, "r") as zf:
                    zipped_files = len(zf.namelist())

                if zipped_files != input_files:
                    logger.error(f"Sanity check failed: expected {input_files} files, got {zipped_files} in zip")
                    self._send_data(error_message)
                    return

                with open(packaged_path, "rb") as f:
                    content = f.read()
            except Exception as e:
                logger.error("Failed to read OTA file {}: {}".format(file_path, e))
                self._send_data(error_message)
                return

        ota_checksum = hashlib.sha256(content).hexdigest()
        total_size = len(content)
        chunks = [content[i:i+chunk_size] for i in range(0, total_size, chunk_size)]

        self._send_data(f"MX93/OTA_UPDATE_METADATA/{ota_type},{ota_checksum}\n")
        time.sleep(1)

        header_cmd = "MX93/OTA_HEADER/{},{},{}".format(
            packaged_name,
            len(chunks),
            total_size
        )
        
        self._send_data(header_cmd + "\n")
        time.sleep(0.25)

        for idx, chunk in enumerate(chunks):
            hex_chunk = chunk.hex()
            data_cmd = "MX93/OTA_DATA/{}/{}".format(idx, hex_chunk)
            self._send_data(data_cmd + "\n")
            time.sleep(0.2)

        self._send_data(success_message)
        return

    def handle_ble_connection_timeout(self):
        if self.is_authenticated:
            logger.debug("BLE connection authenticated within 10 seconds, ignoring disconnect")
        else:
            logger.debug("BLE connection not authenticated within 10 seconds, disconnecting client")
            self._send_data("MX93/BLE_DISCONNECT\n")

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
                        status = res.split("/")[1].strip()
                        if status == "success":
                            if self._dbus_server:
                                self._dbus_server.bl654_object.ota_complete("success")
                            else:
                                logger.warning("Dbus not set, could not signal ota_complete")
                        elif status == "error":
                            if self._dbus_server:
                                self._dbus_server.bl654_object.ota_error("error")
                            else:
                                logger.warning("Dbus not set; could not signal ota_error")
                        continue
                    if res.startswith("NOTIFY_VERSION/"):
                        if self._dbus_server:
                            self._dbus_server.bl654_object.notify_version(res.split("/")[1].strip())
                        else:
                            logger.warning("Dbus not set, could not signal notify_version")
                        continue
                    if res.startswith("CLIENT_CONNECTED"):
                        threading.Timer(10.0, self.handle_ble_connection_timeout).start()
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

    def set_dbus_server(self, dbus_server):
        self._dbus_server = dbus_server
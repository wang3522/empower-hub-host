import logging
import os
import json
import threading
import copy

from typing import TypedDict, Union
from typeguard import check_type

logger = logging.getLogger(__name__)


class T_WIFI_CONFIG(TypedDict):
    enable: bool
    device_id: str
    ssid: str
    password: str


class T_WAP_CONFIG(TypedDict):
    enable: bool
    device_id: str
    ssid: str
    password: str


class T_CAN_CONFIG(TypedDict):
    interface: str
    channel: str
    bitrate: int


class T_LTE_CONFIG(TypedDict):
    enable: bool
    device_id: str
    apn: str
    name: str


class T_BLE_CONFIG(TypedDict):
    class T_uart(TypedDict):
        enable: bool
        device_id: str
        baudrate: int

    uart: T_uart


class SystemConfig(object):
    _instance = None
    _configfile = None
    _lock = threading.Lock()
    _wifi: Union[T_WIFI_CONFIG, None] = None
    _wap: Union[T_WAP_CONFIG, None] = None
    _can: Union[T_CAN_CONFIG, None] = None
    _lte: Union[T_LTE_CONFIG, None] = None
    _ble: Union[T_BLE_CONFIG, None] = None

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    try:
                        logger.info("Creating Config instance.")
                        cls._instance = super(SystemConfig, cls).__new__(cls)

                        cls._instance._configfile = os.getenv("HUB_NET_CONFIG", None)
                        if cls._instance._configfile is None:
                            logger.warning("Environment variable HUB_NET_CONFIG not set, using default path.")
                            cls._instance._configfile = "/etc/hub/network-config.json"

                        if not os.path.exists(cls._instance._configfile):
                            cls._instance._configfile = None
                            raise Exception("Configuration file not found.")

                        cls._instance._load_config()
                    except Exception as error:
                        logger.error(f"Error creating Config instance: {error}")
                        cls._instance = None
                        raise error
        return cls._instance

    def __del__(self):
        logger.debug("Deleting Config instance.")
        self.save_config()
        pass

    def _load_config(self):
        logger.debug("Loading configuration.")
        config = None
        if self._configfile is None or not os.path.exists(self._configfile):
            raise Exception("Configuration file not found.")

        try:
            with open(self._configfile, "r") as file:
                config = json.load(file)

            self._wifi = check_type(config["wifi"], T_WIFI_CONFIG)
            self._wap = check_type(config["wap"], T_WAP_CONFIG)
            self._can = check_type(config["can"], T_CAN_CONFIG)
            self._lte = check_type(config["lte"], T_LTE_CONFIG)
            self._ble = check_type(config["ble"], T_BLE_CONFIG)

        except Exception as error:
            logger.error(f"Error loading configuration: {error}")
            raise error
        return

    def save_config(self):
        logger.debug("Saving configuration.")
        if self._configfile is None or not os.path.exists(self._configfile):
            raise Exception("Configuration file not found.")

        try:
            with open(self._configfile, "w") as file:
                config = {"wifi": self._wifi, "wap": self._wap, "can": self._can, "lte": self._lte, "ble": self._ble}
                json.dump(config, file)
        except Exception as error:
            logger.error(f"Error saving configuration: {error}")
            raise error
        return
    
    def get_config(self, key: str):
        with self._lock:
            internal_key = f"_{key}"
            if not hasattr(self, internal_key):
                raise KeyError(f"Configuration key '{key}' not found.")
            return copy.deepcopy(getattr(self, internal_key))

    def set_config(self, key: str, value):
        with self._lock:
            internal_key = f"_{key}"
            if not hasattr(self, internal_key):
                raise KeyError(f"Configuration key '{key}' not found.")
            setattr(self, internal_key, copy.deepcopy(value))

__all__ = ["SystemConfig", "T_WIFI_CONFIG", "T_WAP_CONFIG", "T_CAN_CONFIG", "T_LTE_CONFIG", "T_BLE_CONFIG"]

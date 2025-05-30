import logging
import threading
from typing import Any, List
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import dbus.proxies
import dbus.service
import reactivex as rx
import json
import copy

from N2KClient.models.devices import N2kDevice
from N2KClient.models.constants import Constants, JsonKeys, AttrNames
from reactivex import operators as ops
from gi.repository import GLib
from time import sleep
from N2KClient.util.settings_util import SettingsUtil
from N2KClient.models.common_enums import N2kDeviceType
from N2KClient.services.config_parser.config_parser import ConfigParser
from N2KClient.services.config_processor.config_processor import ConfigProcessor
from N2KClient.models.n2k_configuration.n2k_configuation import N2kConfiguration
from N2KClient.models.empower_system.empower_system import EmpowerSystem


class N2KClient(dbus.service.Object):
    _logger = logging.getLogger(Constants.DBUS_N2K_CLIENT)
    _disposable_list: List[rx.abc.DisposableBase]
    _latest_devices: dict[str, N2kDevice]
    _devices: rx.subject.BehaviorSubject
    _config: rx.subject.BehaviorSubject
    _empower_system: rx.subject.BehaviorSubject
    devices: rx.subject.BehaviorSubject
    config: rx.subject.BehaviorSubject
    bus: dbus.SystemBus
    n2k_dbus_interface: dbus.Interface
    n2k_dbus_object: dbus.proxies.ProxyObject
    getConfig: dbus.proxies._ProxyMethod
    getState: dbus.proxies._ProxyMethod
    getDevices: dbus.proxies._ProxyMethod
    _get_devices_thread: threading.Thread
    _get_state_thread: threading.Thread
    _latest_config: N2kConfiguration
    _latest_empower_system: EmpowerSystem
    _config_parser: ConfigParser
    _config_processor: ConfigProcessor
    _get_state_timeout = SettingsUtil.get_setting(
        Constants.WORKER_KEY, Constants.STATE_TIMEOUT_KEY, default_value=1
    )
    _get_devices_timeout = SettingsUtil.get_setting(
        Constants.WORKER_KEY, Constants.DEVICE_TIMEOUT_KEY, default_value=1
    )
    _latest_config: N2kConfiguration
    lock: threading.Lock

    def __init__(self):
        self._disposable_list = []

        self._latest_devices = {}

        self._devices = rx.subject.BehaviorSubject({})
        self._config = rx.subject.BehaviorSubject(N2kConfiguration())
        self._empower_system = rx.subject.BehaviorSubject(EmpowerSystem(None))

        # Pipes
        self.devices = self._devices.pipe(ops.publish(), ops.ref_count())
        self.config = self._config.pipe(ops.publish(), ops.ref_count())
        self.empower_system = self._empower_system.pipe(ops.publish(), ops.ref_count())

        # Initialize N2k dbus Interface
        self.bus = dbus.SystemBus()
        n2k_dbus_object = self.bus.get_object(
            Constants.N2K_SERVICE_NAME, Constants.N2K_OBJECT_PATH
        )
        self.n2k_dbus_interface = dbus.Interface(
            n2k_dbus_object, Constants.N2K_INTERFACE_NAME
        )

        # Initialize N2k dbus Service Methods
        self.getConfig = self.n2k_dbus_interface.get_dbus_method(
            Constants.GET_CONFIG_SERVICE_METHOD_NAME
        )
        self.getState = self.n2k_dbus_interface.get_dbus_method(
            Constants.GET_STATE_SERVICE_METHOD_NAME
        )
        self.getDevices = self.n2k_dbus_interface.get_dbus_method(
            Constants.GET_DEVICES_SERVICE_METHOD_NAME
        )

        # Threads
        self._get_devices_thread = threading.Thread(
            target=self._get_devices, name="__get_devices"
        )

        self._get_state_thread = threading.Thread(
            target=self._get_state, name="__get_state"
        )

        # Handler to update the latest device list internally
        def update_latest_devices(devices: dict[str, N2kDevice]):
            self._latest_devices = devices
            # Uncomment for demonstration purposes
            # devices_json = {
            #     device_id: device.to_dict() for device_id, device in devices.items()
            # }
            # self._logger.info(
            #     f"Latest devices: { json.dumps(devices_json, indent=2) }\n\n"
            # )

        self._config_parser = ConfigParser()
        self._config_processor = ConfigProcessor()

        # Handler to update the latest config internally
        def update_latest_config(config: N2kConfiguration):
            self._latest_config = config
            if config is not None:
                config_json = config.to_dict()
                self._logger.info(
                    f"Latest config: { json.dumps(config_json, indent=2) }\n\n"
                )

        def update_latest_empower_system(empower_system: EmpowerSystem):
            self._latest_empower_system = empower_system
            if empower_system is not None:
                empower_system_json = empower_system.to_config_dict()
                self._logger.info(
                    f"Latest empower system: { json.dumps(empower_system_json, indent=2) }\n\n"
                )

        self._disposable_list.append(self.devices.subscribe(update_latest_devices))
        self._disposable_list.append(self.config.subscribe(update_latest_config))
        self._disposable_list.append(
            self._empower_system.subscribe(update_latest_empower_system)
        )

        self.lock = threading.Lock()

    def start(self):
        # Raw Czone Config
        config_json = self.getConfig()
        raw_config = self._config_parser.parse_config(config_json)
        self._config.on_next(raw_config)

        # Empower System
        processed_config = self._config_processor.build_empower_system(raw_config)
        self._empower_system.on_next(processed_config)

        self._get_devices_thread.start()
        self._get_state_thread.start()

    def __merge_device_list(self, device_json):
        with self.lock:
            device_list_copy = copy.deepcopy(self._latest_devices)
        list_appended = False
        for device in device_json:
            device_id = device[JsonKeys.ID]
            if device_id not in device_list_copy:
                # Actually do JSON/ENUM mapping here here
                device_type = N2kDeviceType(device[JsonKeys.TYPE])
                device_list_copy[device_id] = N2kDevice(device_type)
                list_appended = True

        if list_appended:
            with self.lock:
                self._devices.on_next(device_list_copy)

    def _get_devices(self):
        self._logger.info("Starting Get Device thread")
        while True:
            try:
                devices = self.getDevices()
                devices_json = json.loads(devices)
                self.__merge_device_list(devices_json)
            except Exception as e:
                self._logger.error(f"Error reading dbus device response: {e}")
            sleep(self._get_devices_timeout)

    def _get_state(self):
        self._logger.info("Starting Get State thread")
        while True:
            keys = self._latest_devices.keys()
            state_update = {}
            try:
                for id in keys:
                    device_state = json.loads(self.getState(id))
                    state_update[id] = device_state
                self._merge_state_update(state_update)

            except Exception as e:
                self._logger.error(f"Error reading dbus state response: {e}")
            sleep(self._get_state_timeout)

    def _merge_state_update(self, state_updates: dict[str, dict[str, Any]]):
        with self.lock:
            device_list_copy = copy.deepcopy(self._latest_devices)
        for id, state_update in state_updates.items():
            for channel_id in state_update.keys():
                device_list_copy[id].channels[channel_id] = state_update[channel_id]
        with self.lock:
            self._devices.on_next(device_list_copy)

    def __del__(self):
        if self._disposable_list is not None:
            for disposable in self._disposable_list:
                disposable.dispose()
            self._disposable_list = []

    def get_devices(self):
        return self._latest_devices

    def get_devices_observable(self):
        return self.devices

    def get_config(self):
        return self._latest_config

    def get_config_observable(self):
        return self.config

    def get_empower_system(self):
        return self._latest_empower_system

    def get_empower_system_observable(self):
        return self.empower_system

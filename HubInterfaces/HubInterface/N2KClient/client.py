import logging
import threading
from typing import Any, List
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import dbus.service
import reactivex as rx
import json
import copy

from N2KClient.models.devices import N2kDevice
from N2KClient.models.constants import Constants
from reactivex import operators as ops
from gi.repository import GLib
from time import sleep
from N2KClient.util.settings_util import SettingsUtil
from N2KClient.models.common_enums import N2kDeviceType


class N2KClient(dbus.service.Object):
    _latest_devices: dict[str, N2kDevice]
    _disposable_list: List[rx.abc.DisposableBase]
    _get_state_timeout = SettingsUtil.get_setting(
        Constants.WORKER_KEY, Constants.STATE_TIMEOUT_KEY, default_value=15
    )
    _get_devices_timeout = SettingsUtil.get_setting(
        Constants.WORKER_KEY, Constants.DEVICE_TIMEOUT_KEY, default_value=15
    )

    def __init__(self):
        self._logger = logging.getLogger("N2KClient")
        self._disposable_list = []

        self._latest_devices = {}

        self._devices = rx.subject.BehaviorSubject({})

        # Pipes
        self.devices = self._devices.pipe(ops.publish(), ops.ref_count())

        # Initialize N2k dbus Interface
        self.bus = dbus.SystemBus()
        n2k_dbus_object = self.bus.get_object(
            Constants.n2k_service_name, Constants.n2k_object_path
        )
        self.n2k_dbus_interface = dbus.Interface(
            n2k_dbus_object, Constants.n2k_interface_name
        )

        # Initialize N2k dbus Service Methods
        self.getConfig = self.n2k_dbus_interface.get_dbus_method(
            Constants.get_config_service_method_name
        )
        self.getState = self.n2k_dbus_interface.get_dbus_method(
            Constants.get_state_service_method_name
        )
        self.getDevices = self.n2k_dbus_interface.get_dbus_method(
            Constants.get_devices_service_method_name
        )

        # Threads
        self._device_discovery_thread = threading.Thread(
            target=self._discover_devices, name="__discover_devices"
        )

        self._get_state_thread = threading.Thread(
            target=self._get_state, name="__get_state"
        )

        # Handler to update the latest device list internally
        def update_lastest_devices(devices: dict[str, N2kDevice]):
            self._latest_devices = devices

        self._disposable_list.append(self.devices.subscribe(update_lastest_devices))

        self.lock = threading.Lock()

    def start(self):
        config_json = self.getConfig()
        # parse config

        self._device_discovery_thread.start()
        self._get_state_thread.start()

    def __merge_device_list(self, device_json):
        with self.lock:
            device_list_copy = copy.deepcopy(self._latest_devices)
        list_appended = False
        for device in device_json:
            device_id = device["id"]
            if device_id not in device_list_copy:
                # Actually do JSON/ENUM mapping here here
                device_type = N2kDeviceType(device["type"])
                device_list_copy[device_id] = N2kDevice(device_type)
                list_appended = True

        if list_appended:
            with self.lock:
                self._devices.on_next(device_list_copy)

    def _discover_devices(self):
        while True:
            try:
                self._logger.debug("Discovering devices")
                x = self.getDevices()
                self._logger.debug(f"Devices: {x}")
                devices_json = json.loads(x)
                self.__merge_device_list(devices_json)
            except Exception as e:
                self._logger.error(f"Error heading dbus device response: {e}")
            sleep(1)

    def _get_state(self):
        while True:
            keys = self._latest_devices.keys()
            state_update = {}
            try:
                for id in keys:
                    device_state = json.loads(self.getState(id))
                    state_update[id] = device_state
                self._merge_state_update(state_update)

            except Exception as e:
                self._logger.error("Error heading dbus state response")
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

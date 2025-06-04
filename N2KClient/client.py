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
from N2KClient.models.n2k_configuration.engine_configuration import (
    EngineConfiguration,
)
from N2KClient.models.empower_system.engine_list import EngineList
from N2KClient.models.n2k_configuration.factory_metadata import FactoryMetadata


class N2KClient(dbus.service.Object):
    _logger = logging.getLogger(Constants.DBUS_N2K_CLIENT)
    _disposable_list: List[rx.abc.DisposableBase]
    _latest_devices: dict[str, N2kDevice]

    _devices: rx.subject.BehaviorSubject
    _config: rx.subject.BehaviorSubject
    _empower_system: rx.subject.BehaviorSubject
    _engine_config: rx.subject.BehaviorSubject
    _engine_list: rx.subject.BehaviorSubject
    _factory_metadata: rx.Subject

    devices: rx.subject.BehaviorSubject
    config: rx.subject.BehaviorSubject
    empower_system: rx.subject.BehaviorSubject
    engine_config: rx.subject.BehaviorSubject
    engine_list: rx.subject.BehaviorSubject
    factory_metadata: rx.Observable[FactoryMetadata]

    bus: dbus.SystemBus
    n2k_dbus_interface: dbus.Interface
    n2k_dbus_object: dbus.proxies.ProxyObject

    dbus_get_config: dbus.proxies._ProxyMethod
    dbus_get_config_all: dbus.proxies._ProxyMethod
    dbus_get_categories: dbus.proxies._ProxyMethod
    dbus_get_setting: dbus.proxies._ProxyMethod
    dbus_get_state: dbus.proxies._ProxyMethod
    dbus_get_devices: dbus.proxies._ProxyMethod

    _get_devices_thread: threading.Thread
    _get_state_thread: threading.Thread

    _latest_config: N2kConfiguration
    _latest_empower_system: EmpowerSystem
    _latest_engine_config: EngineConfiguration
    _latest_engine_list: EngineList
    _latest_factory_metadata: FactoryMetadata

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
        self._engine_config = rx.subject.BehaviorSubject(EngineConfiguration())
        self._engine_list = rx.subject.BehaviorSubject(EngineList(False))
        self._factory_metadata = rx.subject.Subject()

        # Pipes
        self.devices = self._devices.pipe(ops.publish(), ops.ref_count())
        self.config = self._config.pipe(ops.publish(), ops.ref_count())
        self.empower_system = self._empower_system.pipe(ops.publish(), ops.ref_count())
        self.engine_config = self._engine_config.pipe(ops.publish(), ops.ref_count())
        self.engine_list = self._engine_list.pipe(ops.publish(), ops.ref_count())
        self.factory_metadata = self._factory_metadata.pipe(
            ops.publish(), ops.ref_count()
        )

        # Initialize N2k dbus Interface
        self.bus = dbus.SystemBus()
        n2k_dbus_object = self.bus.get_object(
            Constants.N2K_SERVICE_NAME, Constants.N2K_OBJECT_PATH
        )
        self.n2k_dbus_interface = dbus.Interface(
            n2k_dbus_object, Constants.N2K_INTERFACE_NAME
        )

        # Initialize N2k dbus Service Methods
        self.dbus_get_config = self.n2k_dbus_interface.get_dbus_method(
            Constants.GET_CONFIG_SERVICE_METHOD_NAME
        )
        self.dbus_get_state = self.n2k_dbus_interface.get_dbus_method(
            Constants.GET_STATE_SERVICE_METHOD_NAME
        )
        self.dbus_get_devices = self.n2k_dbus_interface.get_dbus_method(
            Constants.GET_DEVICES_SERVICE_METHOD_NAME
        )
        self.dbus_get_config_all = self.n2k_dbus_interface.get_dbus_method(
            Constants.GET_CONFIG_ALL_SERVICE_METHOD_NAME
        )
        self.dbus_get_categories = self.n2k_dbus_interface.get_dbus_method(
            Constants.GET_CATEGORIES_SERVICE_METHOD_NAME
        )

        self.dbus_get_setting = self.n2k_dbus_interface.get_dbus_method(
            Constants.GET_SETTING_SERVICE_METHOD_NAME
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

        def update_latest_engine_config(config: EngineConfiguration):
            self._latest_engine_config = config
            if config is not None:
                config_json = config.to_dict()
                print(f"Latest engine config: {config_json}")

        def update_latest_engine_list(engine_list: EngineList):
            self._latest_engine_list = engine_list
            if engine_list is not None:
                engine_list_json = engine_list.to_config_dict()
                self._logger.info(
                    f"Latest engine list: { json.dumps(engine_list_json, indent=2) }\n\n"
                )

        def update_latest_factory_metadata(factory_metadata: FactoryMetadata):
            self._latest_factory_metadata = factory_metadata
            if factory_metadata is not None:
                factory_metadata_json = factory_metadata.to_dict()
                self._logger.info(
                    f"Latest factory metadata: { json.dumps(factory_metadata_json, indent=2) }\n\n"
                )

        self._disposable_list.append(self.devices.subscribe(update_latest_devices))
        self._disposable_list.append(self.config.subscribe(update_latest_config))
        self._disposable_list.append(
            self._empower_system.subscribe(update_latest_empower_system)
        )
        self._disposable_list.append(
            self.engine_config.subscribe(update_latest_engine_config)
        )
        self._disposable_list.append(
            self.engine_list.subscribe(update_latest_engine_list)
        )
        self._disposable_list.append(
            self.factory_metadata.subscribe(update_latest_factory_metadata)
        )

        self.lock = threading.Lock()

    # GETTERS

    # Devices
    def get_devices(self):
        return self._latest_devices

    def get_devices_observable(self):
        return self.devices

    # Config
    def get_config(self):
        return self._latest_config

    def get_config_observable(self):
        return self.config

    # Empower System
    def get_empower_system(self):
        return self._latest_empower_system

    def get_empower_system_observable(self):
        return self.empower_system

    # Factory Metadata
    def get_factory_metadata(self):
        return self._latest_factory_metadata

    def get_factory_metadata_observable(self):
        return self.factory_metadata

    def start(self):
        self._scan_factory_metadata()
        self._get_configuration()
        self._scan_marine_engine(should_reset=False)
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

    def _scan_marine_engine(self, should_reset: bool):
        self._logger.info(
            "Starting scan marine engine with should_reset = %r...", should_reset
        )
        self._scan_marine_engine_config(should_reset)

    def _scan_factory_metadata(self):
        try:
            self._logger.info("Loading factory metadata...")
            factory_metadata_response = self.dbus_get_setting(Constants.FactoryData)
            factory_metadata_json = json.loads(factory_metadata_response)
            factory_metadata = self._config_parser.parse_factory_metadata(
                factory_metadata_json
            )
            self._factory_metadata.on_next(factory_metadata)
        except Exception as e:
            self._logger.error(f"Error reading dbus Get Factory Metadata response: {e}")

    def _scan_config_metadata(self):
        try:
            self._logger.info("Loading config metadata...")
            config_metadata = self.dbus_get_setting(Constants.Config)
            return config_metadata
        except Exception as e:
            self._logger.error(f"Error reading dbus Get Config Metadata response: {e}")
            return {}

    def _get_configuration(self):
        # Raw Czone Config
        try:
            categories_json = self.dbus_get_categories()
            config_json = self.dbus_get_config_all()
            config_metadata_json = self._scan_config_metadata()
            raw_config = self._config_parser.parse_config(
                config_json, categories_json, config_metadata_json
            )
            self._config.on_next(raw_config)

            # Empower System
            processed_config = self._config_processor.build_empower_system(raw_config)
            self._empower_system.on_next(processed_config)
        except Exception as e:
            self._logger.error(f"Error reading dbus Get Config response: {e}")

    def _scan_marine_engine_config(self, should_reset: bool = False):
        """
        Scans the marine configuration and updates the engine configuration.

        This method retrieves the engine configuration from the data provider
        and updates the engine configuration in the `EngineConfiguration` object.

        Returns:
            None
        """
        engine_configuration: EngineConfiguration = copy.deepcopy(
            self._engine_config.value
        )
        self._logger.info(
            "Loading Engine configuration with should_reset = %r...", should_reset
        )

        # Engine Config
        try:
            engine_config_json = self.dbus_get_config(JsonKeys.ENGINES)
            raw_engine_config = self._config_parser.parse_engine_configuration(
                engine_config_json, engine_configuration
            )

            raw_engine_config.should_reset = should_reset

            self._engine_config.on_next(raw_engine_config)

            # Engine List
            engine_list = self._config_processor.build_engine_list(raw_engine_config)
            self._engine_list.on_next(engine_list)
        except Exception as e:
            self._logger.error(f"Error reading dbus Get Engine response: {e}")

    def _get_devices(self):
        self._logger.info("Starting Get Device thread")
        while True:
            try:
                devices = self.dbus_get_devices()
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
                    device_state = json.loads(self.dbus_get_state(id))
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

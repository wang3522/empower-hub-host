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
import platform

from .models.devices import N2kDevices
from .models.constants import Constants, JsonKeys
from reactivex import operators as ops
from gi.repository import GLib
from time import sleep
from .util.settings_util import SettingsUtil
from .models.common_enums import N2kDeviceType
from .services.config_parser.config_parser import ConfigParser
from .services.config_processor.config_processor import ConfigProcessor
from .models.n2k_configuration.n2k_configuation import N2kConfiguration
from .models.empower_system.empower_system import EmpowerSystem
from .models.n2k_configuration.engine_configuration import (
    EngineConfiguration,
)
from .models.empower_system.engine_list import EngineList
from .models.n2k_configuration.factory_metadata import FactoryMetadata
from .services.control_service.control_service import ControlService


class N2KClient(dbus.service.Object):

    _logger = logging.getLogger(Constants.DBUS_N2K_CLIENT)
    _disposable_list: List[rx.abc.DisposableBase]
    _latest_devices: N2kDevices

    _devices: rx.subject.BehaviorSubject
    _config: rx.subject.BehaviorSubject
    _empower_system: rx.subject.BehaviorSubject
    _engine_config: rx.subject.BehaviorSubject
    _engine_list: rx.subject.BehaviorSubject
    _factory_metadata: rx.subject.BehaviorSubject

    devices: rx.subject.BehaviorSubject
    config: rx.subject.BehaviorSubject
    empower_system: rx.subject.BehaviorSubject
    engine_config: rx.subject.BehaviorSubject
    engine_list: rx.subject.BehaviorSubject
    factory_metadata: rx.subject.BehaviorSubject

    bus: dbus.SystemBus
    n2k_dbus_interface: dbus.Interface
    n2k_dbus_object: dbus.proxies.ProxyObject

    _dbus_get_config: dbus.proxies._ProxyMethod
    _dbus_get_config_all: dbus.proxies._ProxyMethod
    _dbus_get_categories: dbus.proxies._ProxyMethod
    _dbus_get_setting: dbus.proxies._ProxyMethod
    _dbus_get_state: dbus.proxies._ProxyMethod
    _dbus_control: dbus.proxies._ProxyMethod

    _get_state_thread: threading.Thread

    _latest_config: N2kConfiguration
    _latest_empower_system: EmpowerSystem
    _latest_engine_config: EngineConfiguration
    _latest_engine_list: EngineList
    _latest_factory_metadata: FactoryMetadata

    _config_parser: ConfigParser
    _config_processor: ConfigProcessor
    control_service: ControlService

    _get_state_timeout = SettingsUtil.get_setting(
        Constants.WORKER_KEY, Constants.STATE_TIMEOUT_KEY, default_value=1
    )

    _dbus_retry_delay = SettingsUtil.get_setting(
        Constants.WORKER_KEY, Constants.DBUS_RETRY_DELAY_KEY, default_value=5
    )

    _control_dbus_max_attempts = SettingsUtil.get_setting(
        Constants.WORKER_KEY, Constants.CONTROL_DBUS_MAX_ATTEMPTS_KEY, default_value=3
    )

    lock: threading.Lock

    def __init__(self):
        self.lock = threading.Lock()
        self._disposable_list = []

        self._latest_devices = N2kDevices()

        self._devices = rx.subject.BehaviorSubject(N2kDevices())
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
        # Mac uses SessionBus, Linux uses SystemBus
        if platform.system() == "Darwin":
            self.bus = dbus.SessionBus()
        else:
            self.bus = dbus.SystemBus()

        n2k_dbus_object = self.bus.get_object(
            Constants.N2K_SERVICE_NAME, Constants.N2K_OBJECT_PATH
        )
        self.n2k_dbus_interface = dbus.Interface(
            n2k_dbus_object, Constants.N2K_INTERFACE_NAME
        )

        # Initialize N2k dbus Service Methods
        self._dbus_get_config = self.n2k_dbus_interface.get_dbus_method(
            Constants.GET_CONFIG_SERVICE_METHOD_NAME
        )
        self._dbus_get_state = self.n2k_dbus_interface.get_dbus_method(
            Constants.GET_STATE_SERVICE_METHOD_NAME
        )
        self._dbus_get_config_all = self.n2k_dbus_interface.get_dbus_method(
            Constants.GET_CONFIG_ALL_SERVICE_METHOD_NAME
        )
        self._dbus_get_categories = self.n2k_dbus_interface.get_dbus_method(
            Constants.GET_CATEGORIES_SERVICE_METHOD_NAME
        )

        self._dbus_get_setting = self.n2k_dbus_interface.get_dbus_method(
            Constants.GET_SETTING_SERVICE_METHOD_NAME
        )

        self._dbus_control = self.n2k_dbus_interface.get_dbus_method(Constants.Control)

        # Service initialization
        self._config_parser = ConfigParser()
        self._config_processor = ConfigProcessor()
        self.control_service = ControlService(
            get_config_func=self.get_config,
            get_devices_func=self.get_devices,
            send_control_func=self.dbus_control,
        )

        self._setup_subscriptions()

    def _setup_subscriptions(self):
        self._disposable_list.append(
            self.devices.subscribe(self._update_latest_devices)
        )
        self._disposable_list.append(self.config.subscribe(self._update_latest_config))
        self._disposable_list.append(
            self._empower_system.subscribe(self._update_latest_empower_system)
        )
        self._disposable_list.append(
            self.engine_config.subscribe(self._update_latest_engine_config)
        )
        self._disposable_list.append(
            self.engine_list.subscribe(self._update_latest_engine_list)
        )
        self._disposable_list.append(
            self.factory_metadata.subscribe(self._update_latest_factory_metadata)
        )

    def _update_latest_devices(self, devices: N2kDevices):
        self._latest_devices = devices
        self._logger.info(
            f"Latest devices: {json.dumps(devices.to_mobile_dict(), indent=None)}\n\n"
        )

    def _update_latest_config(self, config: N2kConfiguration):
        self._latest_config = config
        self._log_config_item("config", config)

    def _update_latest_empower_system(self, empower_system: EmpowerSystem):
        self._latest_empower_system = empower_system
        self._log_config_item("empower system", empower_system)

    def _update_latest_engine_config(self, config: EngineConfiguration):
        self._latest_engine_config = config
        self._log_config_item("engine config", config)

    def _update_latest_engine_list(self, engine_list: EngineList):
        self._latest_engine_list = engine_list
        self._log_config_item("engine list", engine_list)

    def _update_latest_factory_metadata(self, factory_metadata: FactoryMetadata):
        self._latest_factory_metadata = factory_metadata
        self._log_config_item("factory metadata", factory_metadata)

    def _retry_dbus_call(self, func, *args, delay=None, max_attempts=None, **kwargs):
        """
        Retry a DBus call indefinitely with a configurable delay.
        Logs the DBus method name, interface, and error on each failure.
        """
        if delay is None:
            delay = self._dbus_retry_delay
        attempt = 0
        # Try to extract DBus method name and interface if available
        method_name = (
            getattr(func, "_method_name", None)
            or getattr(func, "__name__", None)
            or str(func)
        )
        while True:
            try:
                return func(*args, **kwargs)
            except dbus.exceptions.DBusException as e:
                attempt += 1
                self._logger.warning(
                    f"DBus call '{method_name}' failed (attempt {attempt}): {e}"
                )
                if max_attempts and attempt >= max_attempts:
                    self._logger.error(
                        f"DBus call '{method_name}' failed after {attempt} attempts. Giving up."
                    )
                    raise
                sleep(delay)

    def dbus_get_config(self, *args, **kwargs) -> Any:
        """
        Call the DBus GetConfig method with retry.
        Returns the configuration for a given key.
        """
        return self._retry_dbus_call(self._dbus_get_config, *args, **kwargs)

    def dbus_get_state(self, *args, **kwargs) -> Any:
        """
        Call the DBus GetState method with retry.
        Returns the state for a given device key.
        """
        return self._retry_dbus_call(self._dbus_get_state, *args, **kwargs)

    def dbus_get_config_all(self, *args, **kwargs) -> Any:
        """
        Call the DBus GetConfigAll method with retry.
        Returns the full configuration.
        """
        return self._retry_dbus_call(self._dbus_get_config_all, *args, **kwargs)

    def dbus_get_categories(self, *args, **kwargs) -> Any:
        """
        Call the DBus GetCategories method with retry.
        Returns the categories configuration.
        """
        return self._retry_dbus_call(self._dbus_get_categories, *args, **kwargs)

    def dbus_get_setting(self, *args, **kwargs) -> Any:
        """
        Call the DBus GetSetting method with retry.
        Returns the requested setting.
        """
        return self._retry_dbus_call(self._dbus_get_setting, *args, **kwargs)

    def dbus_control(self, *args, **kwargs) -> Any:
        """
        Call the DBus Control method with retry.
        Sends a control request to the DBus service.
        """
        return self._retry_dbus_call(
            self._dbus_control,
            *args,
            **kwargs,
            max_attempts=self._control_dbus_max_attempts,
        )

    def _log_config_item(self, config_type: str, config_obj: Any):
        if config_obj is not None:
            # Prefer to_config_dict if available, else to_dict, else as-is
            if hasattr(config_obj, "to_config_dict"):
                config_dict = config_obj.to_config_dict()
            elif hasattr(config_obj, "to_dict"):
                config_dict = config_obj.to_dict()
            else:
                config_dict = config_obj
            self._logger.info(
                f"Latest {config_type}: { json.dumps(config_dict, indent=2) }\n\n"
            )

    # Public API methods
    def get_devices(self) -> N2kDevices:
        """
        Get the latest N2kDevices object.
        """
        return self._latest_devices

    def get_devices_observable(self) -> rx.Observable:
        """
        Get the observable for N2kDevices updates.
        """
        return self.devices

    def get_config(self) -> N2kConfiguration:
        """
        Get the latest N2kConfiguration object.
        """
        return self._latest_config

    def get_config_observable(self) -> rx.Observable:
        """
        Get the observable for N2kConfiguration updates.
        """
        return self.config

    def get_empower_system(self) -> EmpowerSystem:
        """
        Get the latest EmpowerSystem object.
        """
        return self._latest_empower_system

    def get_empower_system_observable(self) -> rx.Observable:
        """
        Get the observable for EmpowerSystem updates.
        """
        return self.empower_system

    def get_factory_metadata(self) -> FactoryMetadata:
        """
        Get the latest FactoryMetadata object.
        """
        return self._latest_factory_metadata

    def get_factory_metadata_observable(self) -> rx.Observable:
        """
        Get the observable for FactoryMetadata updates.
        """
        return self.factory_metadata

    def get_engine_list(self) -> EngineList:
        """
        Get the latest EngineList object.
        """
        return self._latest_engine_list

    def get_engine_list_observable(self) -> rx.Observable:
        """
        Get the observable for EngineList updates.
        """
        return self.engine_list

    def start(self):
        self._get_state_thread = threading.Thread(
            target=self._get_state, name="__get_state"
        )
        self._scan_factory_metadata()
        self._get_configuration()
        self._scan_marine_engine_config(should_reset=False)
        self._get_state_thread.start()

    def scan_marine_engines(self, should_clear: bool):
        self._logger.info(
            "Starting scan marine engines with should_clear = %r...", should_clear
        )
        self._scan_marine_engine_config(should_reset=should_clear)

    def _scan_marine_engine_congig(self, should_reset: bool):
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
            processed_config = self._config_processor.build_empower_system(
                raw_config, self._latest_devices
            )
            self._empower_system.on_next(processed_config)
        except Exception as e:
            self._logger.error(
                f"Error reading dbus Get Config response: {e}", exc_info=True
            )

    def _scan_marine_engine_config(self, should_reset: bool = False):
        """
        Scans the marine configuration and updates the engine configuration.

        This method retrieves the engine configuration from the data provider
        and updates the engine configuration in the `EngineConfiguration` object.

        Returns:
            None
        """
        engine_configuration: EngineConfiguration = self._engine_config.value

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
            engine_list = self._config_processor.build_engine_list(
                raw_engine_config, self._latest_devices
            )
            self._engine_list.on_next(engine_list)
        except Exception as e:
            self._logger.error(f"Error reading dbus Get Engine response: {e}")

    def _get_state(self):
        self._logger.info("Starting Get State thread")
        while True:
            devices = self._latest_devices.devices.items()
            state_update = {}
            try:
                for key, device in devices:
                    if device.type == N2kDeviceType.UNKNOWN:
                        continue
                    device_state = json.loads(self.dbus_get_state(key))
                    state_update[key] = device_state
                self._merge_state_update(state_update)

            except Exception as e:
                self._logger.error(
                    f"Error reading dbus state response: {e}", exc_info=True
                )
            sleep(self._get_state_timeout)

    def _merge_state_update(self, state_updates: dict[str, dict[str, Any]]):
        with self.lock:
            device_list_copy = self._latest_devices

        for id, state_update in state_updates.items():
            if id not in device_list_copy.devices:
                continue
            # Devices of type AC contain multiple AC Lines,
            # We want to keep ACLine data together within same device, but each lines data accessable by knowing the line ID
            # For this reason, we are creating channels within the AC device named as {channel_id}.{line_id}
            if device_list_copy.devices[id].type == N2kDeviceType.AC:
                lines: dict[int, dict[str, any]] = state_update.get("AClines", {})
                if lines is not None:
                    for line_id, line_value in lines.items():
                        for channel_id, value in line_value.items():
                            device_list_copy.update_channel(
                                id, f"{channel_id}.{int(line_id)}", value
                            )
            else:
                for channel_id, value in state_update.items():
                    device_list_copy.update_channel(id, channel_id, value)

        self._devices.on_next(device_list_copy)

    def __del__(self):
        if self._disposable_list is not None:
            for disposable in self._disposable_list:
                disposable.dispose()
            self._disposable_list = []

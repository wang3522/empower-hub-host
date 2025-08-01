import logging
import platform
import threading
from typing import Any, List, Union
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import dbus.proxies
import dbus.service
import reactivex as rx
import json

from .models.empower_system.engine_alarm_list import EngineAlarmList

from .models.devices import N2kDevices
from .models.constants import Constants, JsonKeys
from reactivex import operators as ops
from gi.repository import GLib
from time import sleep
from .util.settings_util import SettingsUtil
from .models.common_enums import N2kDeviceType, eEventType, ConnectionStatus
from .services.config_parser.config_parser import ConfigParser
from .services.config_processor.config_processor import ConfigProcessor
from .services.alarm_service.alarm_service import AlarmService
from .models.n2k_configuration.n2k_configuation import N2kConfiguration
from .models.empower_system.empower_system import EmpowerSystem
from .models.n2k_configuration.engine_configuration import EngineConfiguration
from .models.empower_system.engine_list import EngineList
from .models.n2k_configuration.factory_metadata import FactoryMetadata
from .services.control_service.control_service import ControlService
from .models.empower_system.alarm import Alarm
from .services.signal_parser.event_parser import EventParser
from .models.empower_system.alarm_list import AlarmList
from .models.dbus_connection_status import DBUSConnectionStatus
from .util.time_util import TimeUtil


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
    _n2k_dbus_connection_status: rx.subject.BehaviorSubject

    devices: rx.subject.BehaviorSubject
    config: rx.subject.BehaviorSubject
    empower_system: rx.subject.BehaviorSubject
    engine_config: rx.subject.BehaviorSubject
    engine_list: rx.subject.BehaviorSubject
    factory_metadata: rx.subject.BehaviorSubject
    n2k_dbus_connection_status: rx.subject.BehaviorSubject

    bus: Union[dbus.SystemBus, dbus.SessionBus]
    n2k_dbus_interface: dbus.Interface
    n2k_dbus_object: dbus.proxies.ProxyObject

    _dbus_get_config: dbus.proxies._ProxyMethod
    _dbus_get_config_all: dbus.proxies._ProxyMethod
    _dbus_get_categories: dbus.proxies._ProxyMethod
    _dbus_get_setting: dbus.proxies._ProxyMethod
    _dbus_control: dbus.proxies._ProxyMethod
    _dbus_alarm_acknowledge: dbus.proxies._ProxyMethod
    _dbus_alarm_list: dbus.proxies._ProxyMethod
    _dbus_single_snapshot: dbus.proxies._ProxyMethod

    _latest_config: N2kConfiguration
    _latest_empower_system: EmpowerSystem
    _latest_engine_config: EngineConfiguration
    _latest_engine_list: EngineList
    _latest_factory_metadata: FactoryMetadata
    _latest_alarms: AlarmList
    _latest_engine_alarms: EngineAlarmList

    _config_parser: ConfigParser
    _config_processor: ConfigProcessor
    control_service: ControlService
    _alarm_service: AlarmService

    _dbus_retry_delay = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY,
        Constants.WORKER_KEY,
        Constants.DBUS_RETRY_DELAY_KEY,
        default_value=5,
    )

    _control_dbus_max_attempts = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY,
        Constants.WORKER_KEY,
        Constants.CONTROL_DBUS_MAX_ATTEMPTS_KEY,
        default_value=3,
    )

    _snapshot_interval = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY,
        Constants.WORKER_KEY,
        Constants.SNAPSHOT_INTERVAL_KEY,
        default_value=60,
    )

    lock: threading.Lock

    def __init__(self):
        DBusGMainLoop(set_as_default=True)
        self.lock = threading.Lock()
        self._disposable_list = []

        self._latest_devices = N2kDevices()

        self._devices = rx.subject.BehaviorSubject(N2kDevices())
        self._config = rx.subject.BehaviorSubject(N2kConfiguration())
        self._empower_system = rx.subject.BehaviorSubject(EmpowerSystem(None))
        self._engine_config = rx.subject.BehaviorSubject(EngineConfiguration())
        self._engine_list = rx.subject.BehaviorSubject(EngineList(False))
        self._factory_metadata = rx.subject.Subject()

        self._n2k_dbus_connection_status = rx.subject.BehaviorSubject(
            DBUSConnectionStatus(
                connection_state=ConnectionStatus.IDLE,
                reason="",
                timestamp=TimeUtil.current_time(),
            )
        )
        self.previous_n2k_dbus_connection_status = DBUSConnectionStatus(
            connection_state=ConnectionStatus.IDLE,
            reason="",
            timestamp=TimeUtil.current_time(),
        )
        # Alarms
        self._active_alarms = rx.subject.BehaviorSubject(AlarmList())
        self._engine_alarms = rx.subject.BehaviorSubject(EngineAlarmList())

        self._latest_alarms = AlarmList()
        self._latest_engine_alarms = EngineAlarmList()
        # Pipes
        self.devices = self._devices.pipe(ops.publish(), ops.ref_count())
        self.config = self._config.pipe(ops.publish(), ops.ref_count())
        self.empower_system = self._empower_system.pipe(ops.publish(), ops.ref_count())
        self.engine_config = self._engine_config.pipe(ops.publish(), ops.ref_count())
        self.engine_list = self._engine_list.pipe(ops.publish(), ops.ref_count())
        self.factory_metadata = self._factory_metadata.pipe(
            ops.publish(), ops.ref_count()
        )
        self.active_alarms = self._active_alarms.pipe(ops.publish(), ops.ref_count())
        self.engine_alarms = self._engine_alarms.pipe(ops.publish(), ops.ref_count())
        self.n2k_dbus_connection_status = self._n2k_dbus_connection_status.pipe(
            ops.filter(lambda status: status is not None),
            ops.distinct_until_changed(
                lambda state: state.connection_state or state.reason
            ),
            ops.publish(),
            ops.ref_count(),
        )
        # Initialize N2k dbus Interface
        # Mac uses SessionBus, Linux uses SystemBus
        self.bus = dbus.SystemBus()
        if platform.system() == "Darwin":
            self.bus = dbus.SessionBus()

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

        self._dbus_get_config_all = self.n2k_dbus_interface.get_dbus_method(
            Constants.GET_CONFIG_ALL_SERVICE_METHOD_NAME
        )
        self._dbus_get_categories = self.n2k_dbus_interface.get_dbus_method(
            Constants.GET_CATEGORIES_SERVICE_METHOD_NAME
        )

        self._dbus_get_setting = self.n2k_dbus_interface.get_dbus_method(
            Constants.GET_SETTING_SERVICE_METHOD_NAME
        )

        self._dbus_control = self.n2k_dbus_interface.get_dbus_method(
            Constants.CONTROL_SERVICE_METHOD_NAME
        )

        self._dbus_alarm_acknowledge = self.n2k_dbus_interface.get_dbus_method(
            Constants.ALARM_ACKNOWLEDGE_SERVICE_METHOD_NAME
        )

        self._dbus_alarm_list = self.n2k_dbus_interface.get_dbus_method(
            Constants.ALARM_LIST_SERVICE_METHOD_NAME
        )

        self._dbus_single_snapshot = self.n2k_dbus_interface.get_dbus_method(
            Constants.SINGLE_SNAPSHOT_SERVICE_METHOD_NAME
        )

        # Service initialization
        self._config_parser = ConfigParser()
        self._config_processor = ConfigProcessor()
        self._event_parser = EventParser()
        self.control_service = ControlService(
            get_config_func=self.get_config,
            get_devices_func=self.get_devices,
            send_control_func=self.dbus_control,
        )
        self._alarm_service = AlarmService(
            alarm_list_func=self.dbus_alarm_list,
            get_latest_alarms_func=self.get_latest_alarms,
            get_config_func=self.get_config,
            get_engine_config_func=self.get_latest_engine_config,
            get_engine_alarms_func=self.get_engine_alarms,
            set_alarm_list=self._set_alarm_list,
            set_engine_alarms=self._set_engine_alarms,
            acknowledge_alarm_func=self.dbus_alarm_acknowledge,
        )

        self._setup_subscriptions()

        self.bus.add_signal_receiver(
            self.event_handler,
            dbus_interface=Constants.N2K_INTERFACE_NAME,
            signal_name=Constants.EVENT_SIGNAL_NAME,
            path=Constants.N2K_OBJECT_PATH,
        )

        self.bus.add_signal_receiver(
            self.snapshot_handler,
            dbus_interface=Constants.N2K_INTERFACE_NAME,
            signal_name=Constants.SNAPSHOT_SIGNAL_NAME,
            path=Constants.N2K_OBJECT_PATH,
        )

        self._set_periodic_snapshot_timer()

    def run_mainloop(self):
        """
        Run the GLib main loop to handle DBus signals and events.
        This method is typically called in a separate thread.
        """
        self._scan_factory_metadata()
        self._get_configuration()
        self._scan_marine_engine_config(should_reset=False)
        loop = GLib.MainLoop()
        loop.run()

    def _setup_subscriptions(self):
        self._disposable_list.append(
            self.devices.subscribe(self._update_latest_devices)
        )
        self._disposable_list.append(self.config.subscribe(self._update_latest_config))
        self._disposable_list.append(
            self.empower_system.subscribe(self._update_latest_empower_system)
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
        self._disposable_list.append(
            self.active_alarms.subscribe(self._update_latest_alarms)
        )
        self._disposable_list.append(
            self.engine_alarms.subscribe(self._update_latest_engine_alarms)
        )
        self._disposable_list.append(
            self.n2k_dbus_connection_status.subscribe(
                self._handle_dbus_connection_status_updated
            )
        )

    # === Update Handlers ===
    def _update_latest_engine_alarms(self, alarms: EngineAlarmList):
        self._latest_engine_alarms = alarms
        self._logger.debug(
            f"Latest engine alarms: {json.dumps(alarms.to_alarm_dict(), indent=None)}\n\n"
        )

    def _update_latest_alarms(self, alarms: AlarmList):
        self._latest_alarms = alarms
        self._logger.debug(
            f"Latest alarms: {json.dumps(alarms.to_alarm_dict(), indent=None)}\n\n"
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

    def _handle_dbus_connection_status_updated(self, status: DBUSConnectionStatus):
        """
        Refresh the active alarms and scan the marine engine config if the DBus status changes from "DISCONNECTED" to "CONNECTED".
        """
        self._logger.debug(
            f"DBus connection status updated: {status.connection_state}, reason: {status.reason}, timestamp: {status.timestamp}"
        )
        if (
            self.previous_n2k_dbus_connection_status is not None
            and self.previous_n2k_dbus_connection_status.connection_state
            == ConnectionStatus.DISCONNECTED
            and status.connection_state == ConnectionStatus.CONNECTED
        ):
            self._logger.info(
                f"Reconnected to DBus Service. Refreshing alarms and scanning marine engine config"
            )
            self._scan_marine_engine_config()
            self._alarm_service.load_active_alarms()
        self.previous_n2k_dbus_connection_status = status

    # === DBus Wrappers ===
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
                result = func(*args, **kwargs)
                self._n2k_dbus_connection_status.on_next(
                    DBUSConnectionStatus(
                        connection_state=ConnectionStatus.CONNECTED,
                        reason="",
                        timestamp=TimeUtil.current_time(),
                    )
                )
                return result
            except dbus.exceptions.DBusException as e:
                attempt += 1
                self._logger.warning(
                    f"DBus call '{method_name}' failed (attempt {attempt}): {e}"
                )
                self._n2k_dbus_connection_status.on_next(
                    DBUSConnectionStatus(
                        connection_state=ConnectionStatus.DISCONNECTED,
                        reason=str(e),
                        timestamp=TimeUtil.current_time(),
                    )
                )
                if max_attempts and attempt >= max_attempts:
                    self._logger.error(
                        f"DBus call '{method_name}' failed after {attempt} attempts. Giving up."
                    )
                    raise
                sleep(delay)

    def dbus_single_snapshot(self, *args, **kwargs) -> Any:
        """
        Call the DBus SingleSnapshot method with retry.
        Returns a single snapshot from the DBus service.
        """
        return self._retry_dbus_call(self._dbus_single_snapshot, *args, **kwargs)

    def dbus_get_config(self, *args, **kwargs) -> Any:
        """
        Call the DBus GetConfig method with retry.
        Returns the configuration for a given key.
        """
        return self._retry_dbus_call(self._dbus_get_config, *args, **kwargs)

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

    def dbus_alarm_acknowledge(self, *args, **kwargs) -> Any:
        """
        Call the DBus AlarmAcknowledge method with retry.
        Acknowledges an alarm in the DBus service.
        """
        return self._retry_dbus_call(
            self._dbus_alarm_acknowledge,
            *args,
            **kwargs,
            max_attempts=self._control_dbus_max_attempts,
        )

    def dbus_alarm_list(self, *args, **kwargs) -> Any:
        """
        Call the DBus AlarmList method with retry.
        Returns the list of alarms from the DBus service.
        """
        return self._retry_dbus_call(self._dbus_alarm_list, *args, **kwargs)

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

    # === Public API Methods ===
    def request_state_snapshot(self) -> None:
        # Grab all of the attributes and update the state
        self._logger.debug("Getting single snapshot")
        self._single_snapshot()

    def acknowledge_alarm(self, alarm_id: int) -> bool:
        self._logger.info(
            f"Acknowledge Alarm Command received for Alarm ID: {alarm_id}"
        )
        return self._alarm_service.acknowledge_alarm(alarm_id)

    def refresh_active_alarms(self) -> bool:
        self._logger.info("Refresh Alarm Command received. Scanning active alarms")
        return self._alarm_service.load_active_alarms(True)

    def scan_marine_engines(self, should_clear: bool = True) -> bool:
        self._logger.info(
            f"Scan Marine Engines Command received. should_clear = {should_clear}"
        )
        return self._scan_marine_engine_config(should_reset=should_clear)

    def set_circuit_power_state(self, runtime_id: int, target_on: bool) -> bool:
        """
        Set the power state of a circuit by its runtime ID.
        Returns True if the operation was successful, False otherwise.
        """
        try:
            result = self.control_service.set_circuit_power_state(
                runtime_id=runtime_id, target_on=target_on
            )
            return result
        except Exception as e:
            self._logger.error(
                f"Failed to set circuit power state for runtime_id {runtime_id} to {target_on}: {e}"
            )
            return False

    def set_circuit_level(self, runtime_id: int, level: float) -> bool:
        try:
            result = self.control_service.set_circuit_level(
                runtime_id=runtime_id, level=level
            )
            return result
        except Exception as e:
            self._logger.error(
                f"Failed to set circuit level for runtime_id {runtime_id} to {level}: {e}"
            )
            return False

    def _set_alarm_list(self, alarm_list: AlarmList):
        self._active_alarms.on_next(alarm_list)

    def _set_engine_alarms(self, engine_alarms: EngineAlarmList):
        self._engine_alarms.on_next(engine_alarms)

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

    def get_engine_alarms(self) -> EngineAlarmList:
        """
        Get the latest EngineAlarmList object.
        """
        return self._latest_engine_alarms

    def get_engine_list_observable(self) -> rx.Observable:
        """
        Get the observable for EngineList updates.
        """
        return self.engine_list

    def get_latest_alarms(self) -> dict[int, Alarm]:
        """
        Get the latest active alarms.
        Returns a dictionary of Alarm objects keyed by their unique ID.
        """
        return self._latest_alarms

    def get_latest_engine_config(self) -> EngineConfiguration:
        """
        Get the latest EngineConfiguration object.
        """
        return self._latest_engine_config

    def start(self):
        self._mainloop_thread = threading.Thread(target=self.run_mainloop, daemon=True)
        self._mainloop_thread.start()

    # === DBus Signal/Event Handlers ===
    def snapshot_handler(self, snapshot_json: str):
        try:
            self._logger.info(f"Received snapshot.")
            self._start_snapshot_timer()
            snapshot_dict: dict[str, dict[str, Any]] = json.loads(snapshot_json)

            if self._latest_engine_config is not None:
                self._alarm_service.process_engine_alarm_from_snapshot(snapshot_dict)

            state_update = self._process_state_from_snapshot(snapshot_dict)
            self._merge_state_update(state_update)
        except Exception as e:
            self._logger.error(
                f"Failed to parse DBus signal JSON: {e}, raw: {snapshot_json}"
            )
            return

    def event_handler(self, event_json: str):
        try:
            event_dict = json.loads(event_json)
            parsed_event = self._event_parser.parse_event(event_dict)
            if parsed_event.type is eEventType.EngineConfigChanged:
                self._logger.info("Received EngineConfigChanged event")
                self._scan_marine_engine_config()
            if parsed_event.type is eEventType.ConfigChange:
                self._logger.info("Received ConfigChange event")
                self._get_configuration()
            if parsed_event.type in [
                eEventType.AlarmAdded,
                eEventType.AlarmRemoved,
                eEventType.AlarmChanged,
                eEventType.AlarmActivated,
                eEventType.AlarmDeactivated,
            ]:
                self._logger.info("Received Alarm event")
                self._alarm_service.load_active_alarms()
            self._logger.debug("Event received and processed")

        except Exception as e:
            self._logger.error(
                f"Failed to parse DBus signal JSON: {e}, raw: {event_json}"
            )
            return

    # === Configuration and Metadata Scanning ===
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
            self._single_snapshot()
        except Exception as e:
            self._logger.error(
                f"Error reading dbus Get Config response: {e}", exc_info=True
            )

    def _scan_marine_engine_config(self, should_reset: bool = False) -> bool:
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
            self._single_snapshot()
            return True
        except Exception as e:
            self._logger.error(f"Error reading dbus Get Engine response: {e}")
            return False

    # === State Processing ===
    def _process_state_from_snapshot(self, snapshot_dict: dict[str, dict[str, Any]]):
        state_update = {}
        # Circuits
        if JsonKeys.CIRCUITS in snapshot_dict:
            for circuit_id, circuit_state in snapshot_dict[JsonKeys.CIRCUITS].items():
                state_update[circuit_id] = circuit_state

        # Tanks
        if JsonKeys.TANKS in snapshot_dict:
            for tank_id, tank_state in snapshot_dict[JsonKeys.TANKS].items():
                state_update[tank_id] = tank_state

        # Engines
        if JsonKeys.ENGINES in snapshot_dict:
            for engine_id, engine_state in snapshot_dict[JsonKeys.ENGINES].items():
                state_update[engine_id] = engine_state
        # AC
        if JsonKeys.AC in snapshot_dict:
            for ac_id, ac_state in snapshot_dict[JsonKeys.AC].items():
                state_update[ac_id] = ac_state

        # DC
        if JsonKeys.DC in snapshot_dict:
            for dc_id, dc_state in snapshot_dict[JsonKeys.DC].items():
                state_update[dc_id] = dc_state

        # Hvacs
        if JsonKeys.HVACS in snapshot_dict:
            for hvac_id, hvac_state in snapshot_dict[JsonKeys.HVACS].items():
                state_update[hvac_id] = hvac_state

        # InverterChargers
        if JsonKeys.INVERTER_CHARGERS in snapshot_dict:
            for inverter_charger_id, inverter_state in snapshot_dict[
                JsonKeys.INVERTER_CHARGERS
            ].items():
                state_update[inverter_charger_id] = inverter_state

        # GNSS
        if JsonKeys.GNSS in snapshot_dict:
            for gnss_id, gnss_state in snapshot_dict[JsonKeys.GNSS].items():
                state_update[gnss_id] = gnss_state

        # Binary Logic State
        if JsonKeys.BINARY_LOGIC_STATE in snapshot_dict:
            for bls_id, logic_state in snapshot_dict[
                JsonKeys.BINARY_LOGIC_STATE
            ].items():
                state_update[bls_id] = logic_state
        return state_update

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

    def _set_periodic_snapshot_timer(self):
        # Set up a periodic timer to call _single_snapshot every N seconds
        self._periodic_snapshot_timer = threading.Timer(
            self._snapshot_interval, self._single_snapshot
        )
        self._periodic_snapshot_timer.name = Constants.SNAPSHOT_TIMER_THREAD_NAME

    def _start_snapshot_timer(self):
        try:
            self._periodic_snapshot_timer.cancel()
            self._set_periodic_snapshot_timer()
            self._periodic_snapshot_timer.start()
        except:
            self._logger.warning("Failed to restart periodic snapshot timer")

    def _single_snapshot(self):
        try:
            snapshot = self.dbus_single_snapshot()
            self.snapshot_handler(snapshot)
        except Exception as e:
            self._logger.error(f"Error getting single snapshot: {e}")

    # === Destructor ===
    def __del__(self):
        if self._disposable_list is not None:
            for disposable in self._disposable_list:
                disposable.dispose()
            self._disposable_list = []

import logging
import threading
from typing import Any, List
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import dbus.service
import reactivex as rx
import json

from .models.empower_system.engine_alarm_list import EngineAlarmList

from .models.devices import N2kDevices
from .models.constants import Constants
from reactivex import operators as ops
from gi.repository import GLib
from .models.common_enums import ConnectionStatus
from .services.alarm_service.alarm_service import AlarmService
from .models.n2k_configuration.n2k_configuation import N2kConfiguration
from .models.empower_system.empower_system import EmpowerSystem
from .models.n2k_configuration.engine_configuration import EngineConfiguration
from .models.empower_system.engine_list import EngineList
from .models.n2k_configuration.factory_metadata import FactoryMetadata
from .services.control_service.control_service import ControlService
from .models.empower_system.alarm import Alarm
from .models.empower_system.alarm_list import AlarmList
from .models.dbus_connection_status import DBUSConnectionStatus
from .util.time_util import TimeUtil
from .services.dbus_proxy_service.dbus_proxy import DbusProxyService
from .services.config_service.config_service import ConfigService
from .services.snapshot_service.snapshot_service import SnapshotService
from .services.event_service.event_service import EventService


class N2KClient(dbus.service.Object):
    """
    Main class for the N2KClient, handling DBus connections and providing access to services.
    This class is responsible for managing the lifecycle of the client, including connecting to DBus, initializing managing services,
    subscribing to signals, and providing a unified interface for interacting with the various
    components of the N2K system.
    """

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

    _latest_config: N2kConfiguration
    _latest_empower_system: EmpowerSystem
    _latest_engine_config: EngineConfiguration
    _latest_engine_list: EngineList
    _latest_factory_metadata: FactoryMetadata
    _latest_alarms: AlarmList
    _latest_engine_alarms: EngineAlarmList

    _config_service: ConfigService
    _control_service: ControlService
    _alarm_service: AlarmService
    _snapshot_service: SnapshotService
    _event_service: EventService

    lock: threading.Lock

    def __init__(self):
        DBusGMainLoop(set_as_default=True)
        self.lock = threading.Lock()
        self._disposable_list = []

        self._latest_devices = N2kDevices()

        self._latest_engine_config = EngineConfiguration()

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
            ops.distinct_until_changed(lambda state: state.connection_state),
            ops.publish(),
            ops.ref_count(),
        )

        self._dbus_proxy = DbusProxyService(
            status_callback=self._n2k_dbus_connection_status.on_next,
        )

        self.control_service = ControlService(
            get_config_func=self.get_latest_config,
            get_devices_func=self.get_latest_devices,
            send_control_func=self._dbus_proxy.control,
        )
        self._alarm_service = AlarmService(
            alarm_list_func=self._dbus_proxy.alarm_list,
            get_latest_alarms_func=self.get_latest_alarms,
            get_config_func=self.get_latest_config,
            get_engine_config_func=self.get_latest_engine_config,
            get_engine_alarms_func=self.get_engine_alarms,
            set_alarm_list=self._set_alarm_list,
            set_engine_alarms=self._set_engine_alarms,
            acknowledge_alarm_func=self._dbus_proxy.alarm_acknowledge,
            get_latest_empower_system_func=self.get_latest_empower_system,
            get_latest_engine_list_func=self.get_latest_engine_list,
        )

        self._config_service = ConfigService(
            dbus_proxy=self._dbus_proxy,
            lock=self.lock,
            get_latest_devices=self.get_latest_devices,
            set_devices=self.set_devices,
            set_config=self.set_config,
            set_empower_system=self.set_empower_system,
            dispose_empower_system=self.dispose_empower_system,
            get_engine_config=self.get_latest_engine_config,
            get_engine_list=self.get_latest_engine_list,
            set_engine_config=self.set_engine_config,
            set_engine_list=self.set_engine_list,
            set_factory_metadata=self.set_factory_metadata,
            request_state_snapshot=self.request_state_snapshot,
        )
        self._snapshot_service = SnapshotService(
            dbus_proxy=self._dbus_proxy,
            lock=self.lock,
            get_latest_devices=self.get_latest_devices,
            set_devices=self.set_devices,
            get_latest_engine_config=self.get_latest_engine_config,
            process_engine_alarms_from_snapshot=self._alarm_service.process_engine_alarm_from_snapshots,
        )

        self._event_service = EventService(
            alarm_service=self._alarm_service,
            config_service=self._config_service,
        )

        self._dbus_proxy.snapshot_handler = self._snapshot_service.snapshot_handler
        self._dbus_proxy.event_handler = self._event_service.event_handler
        self._setup_subscriptions()

    def run_mainloop(self):
        """
        Run the GLib main loop to handle DBus signals and events.
        This method is typically called in a separate thread.
        """
        self._dbus_proxy.connect()
        self._config_service.scan_factory_metadata()
        self._config_service.get_configuration()
        self._config_service.scan_marine_engine_config(should_reset=False)
        loop = GLib.MainLoop()
        loop.run()

    def _setup_subscriptions(self):
        """
        Set up subscriptions to various observables to keep the latest state updated.
        This method subscribes to the latest devices, configuration, empower system,
        engine configuration, engine list, factory metadata, active alarms, and engine alarms.
        It also sets up handlers for DBus connection status updates.
        """
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
        """
        Set the latest engine alarms.
        This updates the internal state and notifies observers.
        """
        self._latest_engine_alarms = alarms
        self._logger.debug(
            f"Latest engine alarms: {json.dumps(alarms.to_alarm_dict(), indent=None)}\n\n"
        )

    def _update_latest_alarms(self, alarms: AlarmList):
        """
        Set the latest active alarms.
        This updates the internal state and notifies observers.
        """
        self._latest_alarms = alarms
        self._logger.debug(
            f"Latest alarms: {json.dumps(alarms.to_alarm_dict(), indent=None)}\n\n"
        )

    def _update_latest_devices(self, devices: N2kDevices):
        """
        Set the latest N2kDevices object.
        This updates the internal state and notifies observers."""
        self._latest_devices = devices
        self._logger.info(
            f"Latest devices: {json.dumps(devices.to_mobile_dict(), indent=None)}\n\n"
        )

    def _update_latest_config(self, config: N2kConfiguration):
        """
        Set the latest N2kConfiguration object.
        This updates the internal state and notifies observers.
        """
        self._latest_config = config
        self._log_config_item("config", config)

    def _update_latest_empower_system(self, empower_system: EmpowerSystem):
        """
        Set the latest EmpowerSystem object.
        This updates the internal state and notifies observers.
        """
        self._latest_empower_system = empower_system
        self._log_config_item("empower system", empower_system)

    def _update_latest_engine_config(self, config: EngineConfiguration):
        """
        Set the latest EngineConfiguration object.
        This updates the internal state and notifies observers.
        """
        self._latest_engine_config = config
        self._log_config_item("engine config", config)

    def _update_latest_engine_list(self, engine_list: EngineList):
        """
        Set the latest EngineList object.
        This updates the internal state and notifies observers.
        """
        self._latest_engine_list = engine_list
        self._log_config_item("engine list", engine_list)

    def _update_latest_factory_metadata(self, factory_metadata: FactoryMetadata):
        """
        Set the latest FactoryMetadata object.
        This updates the internal state and notifies observers.
        """
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
            self._config_service.scan_marine_engine_config()
            self._alarm_service.load_active_alarms()
        self.previous_n2k_dbus_connection_status = status

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
    def write_configuration(self, config_hex: str) -> None:
        """
        Write the configuration to the host.

        Args:
            config_hex: Configuration data encoded as hex.
        """
        self._logger.debug("Writing configuration to host")
        self._config_service.write_configuration(config_hex)

    def request_state_snapshot(self) -> None:
        """
        Request a snapshot of the current state.
        This will trigger the snapshot service to gather the latest state.
        """
        self._logger.debug("Getting single snapshot")
        self._snapshot_service._single_snapshot()

    def acknowledge_alarm(self, alarm_id: int) -> bool:
        """
        Acknowledge an alarm by its ID
        """
        self._logger.info(
            f"Acknowledge Alarm Command received for Alarm ID: {alarm_id}"
        )
        return self._alarm_service.acknowledge_alarm(alarm_id)

    def refresh_active_alarms(self) -> tuple[bool, str]:
        """
        Refresh the active alarms by requesting them from the DBus service.
        """
        self._logger.info("Refresh Alarm Command received. Scanning active alarms")
        success, message = self._alarm_service.load_active_alarms(True)
        if success:
            return True, message
        return False, message

    def scan_marine_engines(self, should_clear: bool = True) -> bool:
        """
        Scan for marine engines and update the engine list.
        If should_clear is True, it will clear the existing engine list
        """
        self._logger.info(
            f"Scan Marine Engines Command received. should_clear = {should_clear}"
        )
        return self._config_service.scan_marine_engine_config(should_reset=should_clear)

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
        """
        Set the dimming level of a circuit by its runtime ID.
        The level should be between 0 and 100.
        Returns True if the operation was successful, False otherwise.
        """
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

    # === Getters ===
    def get_latest_devices(self) -> N2kDevices:
        """
        Get the latest N2kDevices object.
        """
        return self._latest_devices

    def get_devices_observable(self) -> rx.Observable:
        """
        Get the observable for N2kDevices updates.
        """
        return self.devices

    def get_latest_config(self) -> N2kConfiguration:
        """
        Get the latest N2kConfiguration object.
        """
        return self._latest_config

    def get_config_observable(self) -> rx.Observable:
        """
        Get the observable for N2kConfiguration updates.
        """
        return self.config

    def get_latest_empower_system(self) -> EmpowerSystem:
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

    def get_latest_engine_list(self) -> EngineList:
        """
        Get the latest EngineList object.
        """
        return self._latest_engine_list

    def get_engine_list_observable(self) -> rx.Observable:
        """
        Get the observable for EngineList updates.
        """
        return self.engine_list

    def get_engine_alarms(self) -> EngineAlarmList:
        """
        Get the latest EngineAlarmList object.
        """
        return self._latest_engine_alarms

    def get_latest_alarms(self) -> dict[int, Alarm]:
        """
        Get the latest active alarms.
        Returns a dictionary of Alarm objects keyed by their unique ID.
        """
        return self._latest_alarms

    def get_alarms_observable(self) -> rx.subject.BehaviorSubject:
        """
        Get the observable for AlarmList updates.
        """
        return self._active_alarms

    def get_latest_engine_config(self) -> EngineConfiguration:
        """
        Get the latest EngineConfiguration object.
        """
        return self._latest_engine_config

    # === Setters ===
    def set_devices(self, devices: N2kDevices):
        """
        Set the latest N2kDevices object.
        """
        self._devices.on_next(devices)

    def set_config(self, config: N2kConfiguration):
        """
        Set the latest N2kConfiguration object.
        """
        self._config.on_next(config)

    def set_empower_system(self, empower_system: EmpowerSystem):
        """
        Set the latest EmpowerSystem object.
        """
        self._empower_system.on_next(empower_system)

    def set_engine_list(self, engine_list: EngineList):
        """
        Set the latest EngineList object.
        """
        self._engine_list.on_next(engine_list)

    def set_engine_config(self, engine_config: EngineConfiguration):
        """
        Set the latest EngineConfiguration object.
        """
        self._engine_config.on_next(engine_config)

    def set_factory_metadata(self, factory_metadata: FactoryMetadata):
        """
        Set the latest FactoryMetadata object.
        """
        self._factory_metadata.on_next(factory_metadata)

    def _set_alarm_list(self, alarm_list: AlarmList):
        """
        Set the latest active alarms.
        This updates the internal state and notifies observers.
        """
        self._active_alarms.on_next(alarm_list)

    def _set_engine_alarms(self, engine_alarms: EngineAlarmList):
        """
        Set the latest engine alarms.
        This updates the internal state and notifies observers.
        """
        self._engine_alarms.on_next(engine_alarms)

    # Lifecycle Methods
    def dispose_empower_system(self):
        """
        Dispose the current EmpowerSystem instance.
        This is useful for cleaning up resources when the system is no longer needed.
        """
        if self._latest_empower_system:
            self._latest_empower_system.dispose()

    def start(self):
        """
        Start the N2KClient by running the GLib main loop in a separate thread.
        This allows the client to handle DBus signals and events asynchronously, while not blocking the main thread.
        """
        self._mainloop_thread = threading.Thread(target=self.run_mainloop, daemon=True)
        self._mainloop_thread.start()

    # === Destructor ===
    def __del__(self):
        """
        Destructor to clean up resources when the N2KClient instance is deleted.
        """
        if self._disposable_list is not None:
            for disposable in self._disposable_list:
                disposable.dispose()
            self._disposable_list = []

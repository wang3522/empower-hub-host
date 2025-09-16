"""
Empower Service for handling telemetry, state, and alarms in a ThingsBoard environment.
This service sends the state that is received from the N2K client and publishes it
to the Thingsboard cloud.
"""
import os
import re
import json
import hashlib
from typing import Any, Dict, Optional, Union
import logging
import sys

import reactivex as rx
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
# pylint: disable=wrong-import-position,import-error,no-name-in-module
from mqtt_client import ThingsBoardClient
from services.sync_service import SyncService, AttributeType
from services.rpc_handler_service import RpcHandlerService
from services.config import (
    telemetry_filter_patterns,
    location_filter_pattern,
    bilge_pump_power_filter_pattern,
)
from tb_utils.constants import Constants
from n2kclient.models.empower_system.engine_list import EngineList
from n2kclient.models.empower_system.empower_system import EmpowerSystem
from n2kclient.client import N2KClient
from n2kclient.models.devices import N2kDevices
from n2kclient.models.dbus_connection_status import DBUSConnectionStatus
from n2kclient.models.empower_system.alarm import AlarmState, Alarm
from n2kclient.models.empower_system.alarm_list import AlarmList
from n2kclient.models.empower_system.engine_alarm_list import EngineAlarmList
from .location_service import LocationService

class EmpowerService:
    """
    EmpowerService class for handling telemetry, state, and alarms in a ThingsBoard environment.
    """
    _logger: logging.Logger = logging.getLogger("EmpowerService")

    thingsboard_client: ThingsBoardClient
    n2k_client: N2KClient = N2KClient()
    location_service: LocationService
    rpc_handler_service: RpcHandlerService = None
    telemetry_consent: bool = True

    _service_init_disposables: list[rx.abc.DisposableBase]

    _engine_list:dict[str, Any] = None
    _active_alarms:dict = None
    _engine_alarms:dict = None

    def __init__(self):
        self._logger = logging.getLogger("EmpowerService")
        self.thingsboard_client = ThingsBoardClient()
        self.n2k_client = N2KClient()
        self.rpc_handler_service = RpcHandlerService(self.n2k_client)
        self._service_init_disposables = []
        self._engine_list = {}
        self._active_alarms = {}
        self._engine_alarms = {}
        self.sync_service = SyncService()
        self.location_service = LocationService(self.n2k_client)

        self.__setup_subscriptions()

    def _publish_alarm_timeseries(self, alarms: list[Alarm]):
        telemetry_dict = {}
        for alarm in alarms:
            telemetry_dict[alarm.id] = alarm.to_dict()
        if telemetry_dict:
            self._logger.debug(
                "Publishing alarms timeseries data %s", json.dumps(telemetry_dict)
            )
            self.thingsboard_client.send_telemetry(
                telemetry_dict
            )

    def _reconcile_active_alarms(self, alarm_list: AlarmList):
        latest_cloud_alarms = self._active_alarms
        alarm_timeseries = []
        for [id, alarm] in alarm_list.alarm.items():
            if id in latest_cloud_alarms:
                cloud_state = latest_cloud_alarms[id][Constants.currentState]
                cloud_date_active = latest_cloud_alarms[id][Constants.dateActive]
                if alarm.current_state == AlarmState.ENABLED:
                    if cloud_state == AlarmState.ENABLED:
                        alarm.date_active = cloud_date_active
                    else:
                        alarm_timeseries.append(alarm)
                elif alarm.current_state == AlarmState.ACKNOWLEDGED:
                    alarm.date_active = cloud_date_active
                    if cloud_state != AlarmState.ACKNOWLEDGED:
                        alarm_timeseries.append(alarm)
            else:
                alarm_timeseries.append(alarm)
        self._publish_alarm_timeseries(alarm_timeseries)

    def _publish_active_alarms(self, alarm_list: AlarmList):
        if self.telemetry_consent is not None and self.telemetry_consent and alarm_list is not None:
            self.__print_active_alarms(alarm_list)
            alarm_dict = alarm_list.to_alarm_dict()
            # Convert all keys to strings for compatibility with ThingsBoard
            alarm_dict = {str(k): v for k, v in alarm_dict.items()}
            if self._active_alarms == alarm_dict:
                self._logger.debug("Cloud active_alarms attribute is up to date")
            else:
                self._logger.debug(
                    "Publishing updated active alarm list:\n%s", alarm_dict
                )
                self._reconcile_active_alarms(alarm_list)
                new_active_alarms = {Constants.ACTIVE_ALARMS_KEY: alarm_dict}
                self.thingsboard_client.update_attributes(
                    new_active_alarms
                )
                # Since this is a client attribute, we need to update the sync service
                # manually as tb client does not allow subscriptions to client attributes.
                # pylint: disable=protected-access
                self.sync_service._update_value(
                    new_active_alarms
                )

    def _reconcile_engine_alerts(self, engine_alerts: EngineAlarmList):
        if self.telemetry_consent is not None and self.telemetry_consent:
            engine_alert_list_dict = engine_alerts.to_alarm_dict()
            latest_cloud_engine_alerts = self._engine_alarms.copy() if self._engine_alarms else {}
            engine_alert_timeseries = []
            for [id, alarm] in engine_alerts.engine_alarms.items():
                if id in latest_cloud_engine_alerts:
                    alarm.date_active = latest_cloud_engine_alerts[id][
                        Constants.dateActive
                    ]
                else:
                    engine_alert_timeseries.append(alarm)
            self._publish_alarm_timeseries(engine_alert_timeseries)
            if self._engine_alarms != engine_alert_list_dict:
                self._engine_alarms = engine_alert_list_dict

    def __del__(self):
        if len(self._service_init_disposables) > 0:
            for disposable in self._service_init_disposables:
                disposable.dispose()
        if self.thingsboard_client is not None:
            self.thingsboard_client.__del__()

    def device_state_changes(self, devices: N2kDevices):
        """
        Handle state changes for the given devices.
        """
        if self.telemetry_consent is None or not self.telemetry_consent:
            self._logger.debug("Telemetry consent not granted, skipping device state changes.")
            return

        mobile_dict = devices.to_mobile_dict()

        telemetry_attrs = {
            key: value
            for key, value in mobile_dict.items()
            if any(re.match(pattern, key) for pattern in telemetry_filter_patterns)
        }

        state_attrs = {
            key: value
            for key, value in mobile_dict.items()
            if not any(re.match(pattern, key) for pattern in telemetry_filter_patterns)
               and not re.match(location_filter_pattern, key)
               and not re.match(bilge_pump_power_filter_pattern, key)
        }

        # Telemetry values that have state associated with them so
        # we can keep track and sync with cloud on startup and avoid
        # sending push notifications each time.
        telemetry_state_attrs = {
            key: value
            for key, value in mobile_dict.items()
            if re.match(bilge_pump_power_filter_pattern, key)
        }

        # TODO: Handle location attributes
        # elif re.match(location_filter_pattern, key):
        #     # Location-specific logic can be added here in the future.

        # Send telemetry updates
        if telemetry_attrs:
            print("Sending telemetry updates:", telemetry_attrs)
            self.thingsboard_client.send_telemetry(telemetry_attrs)

        # Send state updates
        if state_attrs:
            print("Sending state updates:", state_attrs)
            self.thingsboard_client.update_attributes(state_attrs)

        if telemetry_state_attrs:
            self.__handle_state_dependent_telemetry(telemetry_state_attrs)

    def __handle_state_dependent_telemetry(self, attrs: dict):
        """
        Handle state-dependent telemetry updates, which means state that lives in telemetry,
        but since device sdk cannot retreive telemetry attributes through mqtt, we need to also
        keep  copy of it in attributes so we can get the last known state when connected to thingsboard.
        """
        telemetry_to_send = {}
        timestamp = None
        for key, value in attrs.items():
            # We haven't seen this attribute before, or the sync service
            # file was cleared
            synced_value = self.sync_service.get_attribute_value(key)
            if synced_value is None:
                telemetry_to_send[key] = value
                timestamp = value.get(Constants.ts)
                # Start the sync service for the value
                self.sync_service.subscribe_to_attribute(key, AttributeType.CLIENT)
                # Since this is a client side update, we need to update the sync service
                self.sync_service._update_value({key: value})
            else:
                timestamp = synced_value[Constants.ts]
                synced_value[Constants.ts] = timestamp
                if synced_value[Constants.state] != value[Constants.state]:
                    telemetry_to_send[key] = value
                    # Since this is a client side update, we need to update the sync service
                    self.sync_service._update_value({key: value})

        if len(telemetry_to_send.keys()) > 0:
            print("Sending state dependent telemetry:", telemetry_to_send)
            self.thingsboard_client.send_telemetry(telemetry=telemetry_to_send, timestamp=timestamp)
            self.thingsboard_client.update_attributes(telemetry_to_send)

    def set_telemetry_consent(self, value: bool):
        if value is not None:
            self.telemetry_consent = value
            self._logger.info("Telemetry consent set to: %s", value)

    def update_active_alarms(self, alarms: dict):
        if alarms is not None:
            self._active_alarms = alarms
            self._logger.info("Active alarms updated: %s", alarms)

    def _set_engine_list(self, engine_list: dict[str, Any]):
        """
        Set the engine list with the provided engine_list.
        This method will send the engine list to ThingsBoard if it has changed.
        """
        if engine_list is not None:
            self._engine_list = engine_list
            self._logger.info("Engine list updated: %s", engine_list)

    def __setup_subscriptions(self):
        """
        Set up subscriptions for the EmpowerService.
        """
        # ======= ThingsBoard Client Subscriptions =======
        self.sync_service.subscribe_to_attribute(Constants.TELEMETRY_CONSENT_ENABLED_KEY)
        behavior_subject = self.sync_service.get_attribute_subject(
            key=Constants.TELEMETRY_CONSENT_ENABLED_KEY
        )
        if behavior_subject is not None:
            dispose = behavior_subject.subscribe(self.set_telemetry_consent)
            self._service_init_disposables.append(dispose)
        self.sync_service.subscribe_to_attribute(Constants.ACTIVE_ALARMS_KEY, AttributeType.CLIENT)
        behavior_subject = self.sync_service.get_attribute_subject(
            key=Constants.ACTIVE_ALARMS_KEY
        )
        if behavior_subject is not None:
            dispose = behavior_subject.subscribe(self.update_active_alarms)
            self._service_init_disposables.append(dispose)
        self.sync_service.subscribe_to_attribute(Constants.ENGINE_CONFIG_KEY, AttributeType.CLIENT)
        behavior_subject = self.sync_service.get_attribute_subject(
            key=Constants.ENGINE_CONFIG_KEY
        )
        if behavior_subject is not None:
            dispose = behavior_subject.subscribe(self._set_engine_list)
            self._service_init_disposables.append(dispose)
        # ======= N2K Client Subscriptions =======
        # Subscribe to mobile friendly engine configuration
        disposable = (self.n2k_client.get_engine_list_observable()
                      .subscribe(self._update_engine_configuration))
        self._service_init_disposables.append(disposable)
        # Subscribe to mobile friendly configuration
        disposable = (self.n2k_client.get_empower_system_observable()
                      .subscribe(self._update_cloud_configuration))
        self._service_init_disposables.append(disposable)
        # Subscribe to metadata updates
        disposable = (self.n2k_client.get_factory_metadata_observable()
                      .subscribe(self._update_metadata))
        self._service_init_disposables.append(disposable)
        # Subscribe to the state changes
        disposable = self.n2k_client.devices.subscribe(self.device_state_changes)
        self._service_init_disposables.append(disposable)
        # Subscribe to the alarm list updates
        disposable = self.n2k_client.get_alarms_observable().subscribe(self._publish_active_alarms)
        self._service_init_disposables.append(disposable)
        # Subscribe to the engine alarm list updates
        disposable = self.n2k_client.get_engine_alarms_observable().subscribe(self._reconcile_engine_alerts)
        self._service_init_disposables.append(disposable)
        # ======= N2K Client Connection Subscription =======
        # Need to get the value of the protected method since it is a behavior subject
        # and we want the latest value as soon as we subscribe in the event we miss
        # the initial connection status event.
        # pylint: disable=protected-access
        self._update_n2k_client_connection_status(
            self.n2k_client._n2k_dbus_connection_status.value
        )
        disposable = self.n2k_client.n2k_dbus_connection_status.subscribe(
            self._update_n2k_client_connection_status
        )
        self._service_init_disposables.append(disposable)

    def _update_n2k_client_connection_status(self, status: DBUSConnectionStatus):
        """
        Update the N2K client connection status.
        This method will send the connection status to ThingsBoard.
        """
        if status is None:
            self._logger.error("N2K client connection status is None")
            return

        if self.telemetry_consent is None or not self.telemetry_consent:
            self._logger.debug(
                "Telemetry consent not granted, skipping N2K client connection status update."
            )
            return

        self._logger.info("N2K client connection status updated: %s", status.to_json())
        self.thingsboard_client.update_attributes(
            {Constants.N2K_CONNECTION_STATUS_KEY: status.to_json()}
        )

    def _update_metadata(self, metadata: dict[str, Any]):
        """
        Update the metadata with the provided metadata.
        This method will send the metadata to ThingsBoard if it has changed.
        """
        if metadata is None:
            self._logger.error("Metadata is None, unable to update cloud configuration")
            return

        self._logger.debug("Attempting to update cloud metadata: %s",
            json.dumps(metadata)
        )
        self.thingsboard_client.update_attributes(metadata)

    def _update_cloud_configuration(self, config: EmpowerSystem):
        """
        Update the cloud configuration with the provided config.
        This method will send the configuration to ThingsBoard if it has changed.
        """
        if config is None:
            self._logger.error("Configuration is None, unable to update cloud configuration")
            return

        config_dict = config.to_config_dict()
        # Get the checksum of the config, don't attempt to udpate if the config
        # is the same
        hashed_string = hashlib.new("sha256")
        hashed_string.update(json.dumps(config.to_config_dict()).encode())
        checksum_value = hashed_string.hexdigest()

        prev_value = self.thingsboard_client.last_attributes.get(
            Constants.CONFIG_CHECKSUM_KEY, None
        )
        if prev_value != checksum_value:
            self._logger.debug("Attempting to update cloud configuration: %s",
                json.dumps(config_dict)
            )
            self.thingsboard_client.update_attributes(
                {Constants.CONFIG_KEY: config_dict,
                 Constants.CONFIG_CHECKSUM_KEY: checksum_value}
            )
            self.__print_cloud_config(config)
        else:
            self._logger.debug(
                "Cloud configuration is up to date, no changes detected."
            )


    def _update_engine_configuration(self, config: EngineList):
        """
        Update the cloud configuration with the provided config.
        This method will send the configuration to ThingsBoard if it has changed.
        """
        if config is None:
            self._logger.error("Configuration is None, unable to update cloud configuration")
            return

        try:
            config_dict = config.to_config_dict()
            # Get a copy of the current engine list so we can compare it later
            config_copy = self._engine_list.copy() if self._engine_list else {}
            # If should reset is True, clear the existing engine list
            # Otherwise, only update the existing engine list
            if config.should_reset is True:
                self._engine_list = {}

            # Append any new engines to the engine list
            for engine_id, engine in config_dict.items():
                self._engine_list[engine_id] = engine

            # If the engine list has changed, update the ThingsBoard client
            if config_copy != self._engine_list:
                new_engine_config = {Constants.ENGINE_CONFIG_KEY: self._engine_list}
                self.thingsboard_client.update_attributes(
                    new_engine_config
                )
                # Because engine config is a client attribute, the thingsboard subscribe does not
                # give us the latest value, so we need to manually update the sync service so its
                # available and can be used on startup when offline. If thingsboard didn't get the
                # change, then the sync service will update to the cloud copy when it connects.
                self.sync_service._update_value(new_engine_config)
            else:
                self._logger.debug("Engine configuration is up to date, no changes detected.")
            self.__print_engine_cloud_config(self._engine_list)
        except Exception as e:
            self._logger.error("Failed to update engine configuration: %s", e)

    def __print_cloud_config(self, system: dict):
        if system is None:
            self._logger.error(
                "print_cloud_config: System is None, unable to load configuration"
            )
            return

        self._logger.info("Configuration")

        self._logger.info("Things (%s found)", system.things.__len__())
        for [id_name, thing] in system.things.items():
            self._logger.info(
                "    ├╴ %s (ID=%s, Type=%s)", thing.name, thing.id, thing.type
            )

            for [channel_id, channel] in thing.channels.items():
                self._logger.info(
                    "        ├╴ %s (ID=%s, ReadOnly=%s)",
                    channel.name,
                    channel_id,
                    channel.read_only,
                )

    def __print_engine_cloud_config(self, config: dict[str, Any]):
        if config is None:
            self._logger.error(
                "print_engine_cloud_config: EngineList is None, unable to load engine configuration"
            )
            return
        self._logger.info("Engine Configuration")
        self._logger.info("Engines (%s found)", config.__len__())
        for engine_id in config:
            engine: dict[str, Any] = config[engine_id]
            self._logger.info(
                "    ├╴ %s (ID=%s, Type=%s)",
                engine.get("name"),
                engine.get("id"),
                engine.get("type"),
            )
            if "channels" in engine:
                for channel_id in engine["channels"]:
                    channel: dict[str, Any] = engine["channels"][channel_id]
                    self._logger.info(
                        "        ├╴ %s (ID=%s, ReadOnly=%s)",
                        channel.get("name"),
                        channel.get("id"),
                        channel.get("readOnly"),
                    )

    def __print_active_alarms(self, alarm_list: AlarmList):
        self._logger.info("Active Alarms (%s found)", alarm_list.alarm.__len__())
        for [alarm_id, alarm] in alarm_list.alarm.items():
            self._logger.info(
                "    ├╴ %s (ID=%s, Severity=%s, State=%s)",
                alarm.name,
                alarm_id,
                alarm.severity,
                alarm.current_state,
            )

    def run(self):
        self._logger.info("Starting Empower Service")
        self._logger.debug("Starting ThingsBoard client...")
        self.thingsboard_client.connect()
        self._logger.debug("Starting location service")
        self.location_service.start()
        self._logger.debug("Starting N2K Client")
        self.n2k_client.start()

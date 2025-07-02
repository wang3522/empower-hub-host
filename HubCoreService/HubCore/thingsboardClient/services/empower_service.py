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
import base64
import logging
import sys
import threading
import time

import reactivex as rx
from reactivex import operators as ops
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
# pylint: disable=wrong-import-position,import-error,no-name-in-module
from mqtt_client import ThingsBoardClient
from dict_diff import dict_diff
from tb_utils.constants import Constants
from services.config import (
    telemetry_filter_patterns,
    location_filter_pattern,
    bilge_pump_power_filter_pattern,
)
from n2kclient.models.empower_system.engine_list import EngineList
from n2kclient.models.empower_system.empower_system import EmpowerSystem
from n2kclient.client import N2KClient

class EmpowerService:
    """
    EmpowerService class for handling telemetry, state, and alarms in a ThingsBoard environment.
    """
    _logger: logging.Logger = logging.getLogger("EmpowerService")

    thingsboard_client: ThingsBoardClient
    n2k_client: N2KClient = N2KClient()
    # active_alarms: rx.Observable[AlarmList]
    # engine_alerts: rx.Observable[EngineAlertList]
    discovered_engines: rx.Observable[EngineList]
    telemetry_consent: rx.Observable[bool]
    _prev_system_subscription: rx.abc.DisposableBase = None
    _prev_engine_list_subscription: rx.abc.DisposableBase = None

    _service_init_disposables: list[rx.abc.DisposableBase]

    last_telemetry = {}
    last_state_attrs = {}

    def __init__(self):
        self.thingsboard_client = ThingsBoardClient()
        self._service_init_disposables = []
        self._prev_empower_system = None
        self._prev_engine_list = None

        #TODO: Callback for controlling value, is this needed here?
        # def callback(result, *args):
        #     self._logger.info("received attribute update kvp: %s", result)
        #     if not isinstance(result, dict):
        #         return
        #     key = list(result.keys())[0]
        #     state = result[key]

        #     for thing_id in self._latest_cloud_config.things:
        #         thing = self._latest_cloud_config.things[thing_id]
        #         for channel_id in thing.channels:
        #             if channel_id == key:
        #                 channel = thing.channels[channel_id]
        #                 self.__control_component(thing, channel, state)

        # consent = self.thingsboard_client.subscribe_all_attributes(None)
        # self._service_init_disposables.append(consent.subscribe(callback))

        # def __publish_state_changes(changes: list[ChannelStateChange]):
        def __publish_state_changes(changes: list):
            state_attrs = {}
            telemetry_attrs = {}
            telemetry_changes = []
            state_changes = []
            # Directly categorize changes into telemetry and state
            for change in changes:
                if any(
                    re.match(pattern, change.channel_id)
                    for pattern in telemetry_filter_patterns
                ):
                    telemetry_changes.append(change)
                elif re.match(location_filter_pattern, change.channel_id):
                    # Ignore gnss updates on connect1 so we don't modify last_known_location
                    # Keep it for non connect1 platforms to test gps from simulator.
                    if os.environ["RUNNING_PLATFORM"] != "CONNECT1":
                        # Give location service the telemetry object
                        pass
                else:
                    state_changes.append(change)

            def send_state_dependent_telemetry(state_dependent_changes: dict):
                state_dependent_telemetry_to_send = {}
                telemetry_timestamp = None
                for id_name, value in list(state_dependent_changes.items()):
                    if re.match(bilge_pump_power_filter_pattern, id_name):
                        state_dependent_telemetry_to_send[id_name] = value
                        # Confirm that entry is a dictionary and has the timestamp attribtue
                        if isinstance(value, dict) and Constants.ts in value:
                            # Set the telemetry timestamp to the value we got from state
                            telemetry_timestamp = value[Constants.ts]
                if len(state_dependent_telemetry_to_send) > 0:
                    # Pass in the telemetry timestamp if it is on an attribute
                    # we would like to override the server timestamp.
                    # If telemetry_timestamp is None, then it will use
                    # the time that server had received the telemetry message
                    self.thingsboard_client.send_telemetry(
                        state_dependent_telemetry_to_send,
                        telemetry_timestamp,
                    )

            def process_changes(
                # changes_group: list[ChannelStateChange],
                changes_group: list,
                attrs,
                last_attrs: dict[str],
                log_message,
            ):
                for change in changes_group:
                    attrs[change.channel_id] = change.state

                attrs_to_send = None
                if not last_attrs:
                    last_attrs.update(attrs)
                    attrs_to_send = attrs
                else:
                    diff_attrs = dict_diff(last_attrs, attrs)
                    if diff_attrs:
                        last_attrs.update(attrs)
                        attrs_to_send = diff_attrs

                if attrs_to_send:
                    self._logger.debug("%s %s", log_message, json.dumps(attrs_to_send))
                    return attrs_to_send
                return None

            # Process telemetry and state changes
            telemetry_to_send = process_changes(
                telemetry_changes,
                telemetry_attrs,
                self.last_telemetry,
                "Attempting to add telemetry",
            )
            if telemetry_to_send:
                self.thingsboard_client.send_telemetry(
                    telemetry_to_send
                )

            # Determine any state change and return the
            # new values to send to thingsboard
            state_to_send = process_changes(
                state_changes,
                state_attrs,
                self.last_state_attrs,
                "Attempting to update state",
            )
            # If this is not None, then device has updated values, need to send it to state
            # If it is None, then the device did not change since last cloud sync
            if state_to_send:
                send_state_dependent_telemetry(state_to_send)
                self.thingsboard_client.update_attributes(
                    state_to_send
                )

        #TODO: Subscribe to active alarms

        #TODO: Subscribe to engine alarms

        # def _publish_alarm_timeseries(alarms: list[Alarm]):
        def _publish_alarm_timeseries(alarms: list):
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

        # TODO: Handle alarm logic
        # def _reconcile_active_alarms(alarm_list: AlarmList):
        #     if Constants.ActiveAlarms not in self.last_state_attrs:
        #         self.last_state_attrs[Constants.ActiveAlarms] = {}
        #     latest_cloud_alarms = self.last_state_attrs[Constants.ActiveAlarms]
        #     alarm_timeseries = []
        #     for [id, alarm] in alarm_list.alarm.items():
        #         if id in latest_cloud_alarms:
        #             cloud_state = latest_cloud_alarms[id][Constants.currentState]
        #             cloud_date_active = latest_cloud_alarms[id][Constants.dateActive]
        #             if alarm.current_state == AlarmState.ENABLED:
        #                 if cloud_state == AlarmState.ENABLED:
        #                     alarm.date_active = cloud_date_active
        #                 else:
        #                     alarm_timeseries.append(alarm)
        #             elif alarm.current_state == AlarmState.ACKNOWLEDGED:
        #                 alarm.date_active = cloud_date_active
        #                 if cloud_state != AlarmState.ACKNOWLEDGED:
        #                     alarm_timeseries.append(alarm)
        #         else:
        #             alarm_timeseries.append(alarm)
        #     _publish_alarm_timeseries(alarm_timeseries)

        # def _verify_alarm_things(alarm_list: AlarmList):
        #     for id, alarm in list(alarm_list.alarm.items()):
        #         valid_things = []
        #         for thing in alarm.things:
        #             if thing in self._latest_cloud_config.things or (
        #                 TBConstants.ENGINE_CONFIG_KEY in self.last_state_attrs
        #                 and thing
        #                 in self.last_state_attrs[TBConstants.ENGINE_CONFIG_KEY]
        #             ):
        #                 valid_things.append(thing)
        #         alarm_list.alarm[id].things = valid_things
        #         if len(valid_things) == 0:
        #             del alarm_list.alarm[id]

        # def _publish_active_alarms(alarm_list: AlarmList):
        #     if self.current_telemetry_consent:
        #         _verify_alarm_things(alarm_list)
        #         _reconcile_active_alarms(alarm_list)
        #         alarm_dict = alarm_list.to_alarm_dict()
        #         self.__print_active_alarms(alarm_list=alarm_list)
        #         if self.last_state_attrs[Constants.ActiveAlarms] == alarm_dict:
        #             self._logger.debug(f"Cloud active_alarms attribute is up to date")
        #             self.thingsboard_client.handle_alarm_synced()
        #         else:
        #             self._logger.debug(
        #                 f"Publishing updated active alarm list:\n{alarm_dict}"
        #             )
        #             self.thingsboard_client.update_attributes(
        #                 {Constants.ActiveAlarms: alarm_dict},
        #                 client.AttributeDataType.ALARM,
        #             )
        #             self.last_state_attrs[Constants.ActiveAlarms] = alarm_dict

        # def _reconcile_engine_alerts(engine_alerts: EngineAlertList):
        #     if self.current_telemetry_consent:
        #         engine_alert_list_dict = engine_alerts.to_alarm_dict()
        #         if "EngineAlerts" not in self.last_state_attrs:
        #             self.last_state_attrs["EngineAlerts"] = {}
        #         latest_cloud_engine_alerts = self.last_state_attrs["EngineAlerts"]
        #         engine_alert_timeseries = []
        #         for [id, alarm] in engine_alerts.engine_alerts.items():
        #             if id in latest_cloud_engine_alerts:
        #                 alarm.date_active = latest_cloud_engine_alerts[id][
        #                     Constants.dateActive
        #                 ]
        #             else:
        #                 engine_alert_timeseries.append(alarm)
        #         _publish_alarm_timeseries(engine_alert_timeseries)
        #         if self.last_state_attrs["EngineAlerts"] != engine_alert_list_dict:
        #             self.last_state_attrs["EngineAlerts"] = engine_alert_list_dict

        #TODO: Subscribe to active alarms, engine alarms

        #TODO: Subscribe and handle engine config
        # def _publish_engine_config(config: EngineList):
        #     if config is None:
        #         return

        #     def __update_engine_config_attribute():
        #         if self.current_telemetry_consent:
        #             engine_dict = config.to_config_dict()
        #             updated_engine_dict: dict[str, any] = {}
        #             if config.should_reset:
        #                 self._logger.error("Latest Engine Configuration is cleared.")
        #                 updated_engine_dict = engine_dict
        #             else:
        #                 updated_engine_dict = copy.deepcopy(
        #                     self.last_state_attrs[TBConstants.ENGINE_CONFIG_KEY]
        #                 )
        #                 updated_engine_dict.update(engine_dict)
        #             if (
        #                 self.last_state_attrs[TBConstants.ENGINE_CONFIG_KEY]
        #                 == updated_engine_dict
        #             ):
        #                 self._logger.info(
        #                     f"Cloud Engine Configuration Attribute is up to date"
        #                 )
        #             else:
        #                 self._logger.info(
        #                     f"Publishing Updated Engine configuration:\n{updated_engine_dict}"
        #                 )
        #                 self.thingsboard_client.update_attributes(
        #                     {TBConstants.ENGINE_CONFIG_KEY: updated_engine_dict},
        #                     client.AttributeDataType.ENGINE_CLOUD_CONFIG,
        #                 )
        #                 self.last_state_attrs[TBConstants.ENGINE_CONFIG_KEY] = (
        #                     updated_engine_dict
        #                 )
        #             self.__print_engine_cloud_config(updated_engine_dict)
        #         if self._prev_engine_list_subscription is not None:
        #             self._prev_engine_list_subscription.dispose()
        #         if self._prev_engine_list is not None:
        #             self._prev_engine_list.__del__()
        #         self._prev_engine_list = config

        #         self._prev_engine_list_subscription = config.state_changes.pipe(
        #             ops.buffer_with_time(0.5),
        #             ops.filter(
        #                 lambda changes: len(changes) > 0
        #                 and self.current_telemetry_consent
        #             ),
        #         ).subscribe(__publish_state_changes)
        #         self.n2k_client.start_engine_state_sync()

        #     if TBConstants.ENGINE_CONFIG_KEY in self.last_state_attrs:
        #         __update_engine_config_attribute()
        #     else:
        #         fetch_engine_config = rx.Subject()

        #         def __fetch_and_update_engine_config(value):
        #             self.last_state_attrs[TBConstants.ENGINE_CONFIG_KEY] = {}
        #             if isinstance(value, dict):
        #                 if TBConstants.ENGINE_CONFIG_KEY in value and isinstance(
        #                     value[TBConstants.ENGINE_CONFIG_KEY], dict
        #                 ):
        #                     temp_engine_dict = value[TBConstants.ENGINE_CONFIG_KEY]
        #                 else:
        #                     if len(value) == 0:
        #                         self._logger.error(
        #                             "Engine Configuration Fetch returned an empty dict. Possible reasons include the fetch was unsuccessful or the attribute does not exist."
        #                         )
        #                     temp_engine_dict = value
        #                 for key, value in temp_engine_dict.items():
        #                     self.last_state_attrs[TBConstants.ENGINE_CONFIG_KEY][
        #                         key
        #                     ] = value
        #                 self._logger.info(
        #                     f"Successfully fetched engine config from cloud"
        #                 )
        #             else:
        #                 self._logger.error(
        #                     f"Invalid format when fetching engine config from cloud: {value}"
        #                 )
        #             __update_engine_config_attribute()

        #         fetch_engine_config.subscribe(__fetch_and_update_engine_config)
        #         self.thingsboard_client.request_attributes_state(
        #             client_attributes=[
        #                 TBConstants.ENGINE_CONFIG_KEY,
        #             ],
        #             subject=fetch_engine_config,
        #         )

        # TODO: Subscribe and publish factory metadata

        # def _publish_factory_metadata(factory_metadata: FactoryMetadata):
        #     if (
        #         factory_metadata.mender_artifact_info is None
        #         and factory_metadata.rt_firmware_version is None
        #         and factory_metadata.serial_number is None
        #     ):
        #         return
        #     factory_metadata_dict = factory_metadata.to_factory_metadata_dict()
        #     self._logger.debug(
        #         f"Publishing factory metadata as attributes:\n{factory_metadata_dict}"
        #     )
        #     self.thingsboard_client.update_attributes(
        #         factory_metadata_dict
        #     )

        self.n2k_client.engine_list.subscribe(self._update_engine_configuration)
        self.n2k_client.empower_system.subscribe(self._update_cloud_configuration)

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

    def __del__(self):
        if len(self._service_init_disposables) > 0:
            for disposable in self._service_init_disposables:
                disposable.dispose()
        if self._prev_system_subscription:
            self._prev_system_subscription.dispose()
        if self._prev_engine_list_subscription:
            self._prev_engine_list_subscription.dispose()
        if self.thingsboard_client is not None:
            self.thingsboard_client.__del__()

    # TODO: Set up some sort of n2k_server_connection state

    def _update_engine_configuration(self, config: EngineList):
        """
        Update the cloud configuration with the provided config.
        This method will send the configuration to ThingsBoard if it has changed.
        """
        if config is None:
            self._logger.error("Configuration is None, unable to update cloud configuration")
            return

        config_dict = config.to_config_dict()
        self._logger.debug(
            "Publishing engine configuration to cloud: %s", json.dumps(config_dict)
        )
        self.thingsboard_client.update_attributes(
            {Constants.ENGINE_CONFIG_KEY: config_dict}
        )
        self.__print_engine_cloud_config(config_dict)

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

    # def __print_active_alarms(self, alarm_list: AlarmList):
    def __print_active_alarms(self, alarm_list: dict):
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
        # TODO: Connect to thingsboard, start locaiton service, setup n2k connection status

        # TODO: Subscribe to active alarms
        # TODO: Subscribe to engine config attribute

        # TODO: Pull down active alarms, engine config

        # TODO: Get consents from sync service

        #TODO: Start n2k client
        self._logger.debug("Starting N2K Client")
        self.n2k_client.start()
        time.sleep(10)

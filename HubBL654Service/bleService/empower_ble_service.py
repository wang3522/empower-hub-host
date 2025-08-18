import re
import json
import logging
import time
import random
from utility.utils import ControlResult, dict_diff, telemetry_filter_patterns, location_filter_pattern, Constants
import reactivex as rx
from n2kclient.models.empower_system.empower_system import EmpowerSystem
from n2kclient.models.empower_system.circuit_thing import CircuitThing
from n2kclient.client import N2KClient
from n2kclient.models.devices import N2kDevice, N2kDevices
from n2kclient.models.empower_system.battery import Battery
from n2kclient.models.empower_system.charger import CombiCharger, ACMeterCharger
from n2kclient.models.empower_system.inverter import CombiInverter, AcMeterInverter
from bleService.uart_message_processor import encrypt_data

class EmpowerBleService:
    def __init__(self, ble_uart=None):
        self._logger = logging.getLogger("EmpowerBleService")
        self.ble_uart = ble_uart
        self.n2k_client = N2KClient()
        self._service_init_disposables = []
        self._prev_system_subscription = None
        self.last_telemetry = {}
        self.last_state_attrs = {}
        self.attribute_sub_set = set() #{attribute_ID, ...}
        self.attribute_dict = {} #{attribute_ID: (value, timestamp)}
        self.__setup_subscriptions()
        self._logger.debug("Starting empower ble service...")

    def start(self):
        self._logger.debug("Starting N2K Client in EmpowerBleService")
        self.n2k_client.start()

    def __del__(self):
        if len(self._service_init_disposables) > 0:
            for disposable in self._service_init_disposables:
                disposable.dispose()
        if self._prev_system_subscription:
            self._prev_system_subscription.dispose()

    def _handle_notify_client(self, key: str, value: str, timestamp: str):
        plaintext = f"attribute/{key}/{value}/{timestamp}"
        encrypted = encrypt_data(plaintext.encode('utf-8'))
        self.ble_uart._send_data(f"BL/SUB_UPDATE_NOTIFY/{encrypted.hex()}\n")
        self._logger.debug(f"Sent notify to client: {plaintext}")

    def _device_state_changes(self, devices: N2kDevices):
        """
        Handle state changes for the given devices.
        """
        mobile_dict = devices.to_mobile_dict()
        state_attrs = {
            key: value
            for key, value in mobile_dict.items()
            if not any(re.match(pattern, key) for pattern in telemetry_filter_patterns)
               and not re.match(location_filter_pattern, key)
        }

        diff_attrs = dict_diff(self.last_state_attrs, state_attrs)
        if diff_attrs:
            self.last_state_attrs.update(diff_attrs)
            for key, value in diff_attrs.items():
                timestamp = str(int(time.time() * 1000))
                self.attribute_dict[key] = (value, timestamp)
                if key in self.attribute_sub_set:
                    if self.ble_uart:
                        self._handle_notify_client(key, value, timestamp)

    def _update_attribute_dict(self, config: EmpowerSystem):
        """
        Make an attribute dict from the config.
        """
        self._logger.debug(f"Updating attribute dict with config: {config}")
        if config is None:
            self._logger.error("Configuration is None, unable to make attribute dict")
            return

        # Set empty state before parsing into dict to handle case where new config is uploaded
        self.attribute_dict = {}
        empower_dict = config.to_config_dict()
        self.attribute_dict = {
            channel_id: (None, 0)
            for thing in empower_dict.get("things", {}).values()
            for channel_id in thing.get("channels", {})
        }

    def __setup_subscriptions(self):
        try:
            self._logger.debug(f"Setup subscriptions for EmpowerBleService")
            disposable = (self.n2k_client.get_empower_system_observable().subscribe(self._update_attribute_dict))
            self._service_init_disposables.append(disposable)
            disposable = self.n2k_client.devices.subscribe(self._device_state_changes)
            self._service_init_disposables.append(disposable)
        except Exception as e:
            self._logger.error(f"Error setting up subscriptions: {e}")
            raise

    def update_attribute_subscription(self, attr_id: str, subscribe: bool):
        try:
            if subscribe:
                self.attribute_sub_set.add(attr_id)
                self._logger.debug(f"Subscribed to {attr_id}")
                attribute_tuple = self.attribute_dict.get(attr_id, None)
                if (attribute_tuple is not None):
                    if (attribute_tuple[0] is not None):
                        timestamp = str(int(time.time() * 1000))
                        self._handle_notify_client(attr_id, attribute_tuple[0], timestamp)
                    else:
                        self._logger.debug(f"Value for {attr_id} is None, not sending notification")
                else: 
                    self._logger.warning(f"Key does not exist in attribute_dict: {attr_id}")
            else:
                self.attribute_sub_set.discard(attr_id)
                self._logger.debug(f"Unsubscribed from {attr_id}")
        except Exception as e:
            self._logger.error(f"Error updating attribute subscriptions: {e}")
            raise
        
    def handle_control_component(self, attribute: str, state: str):
        try:
            thing_id = attribute.rsplit(".", 1)[0]
            latest_config = self.n2k_client.get_latest_empower_system()
            if latest_config is None:
                raise Exception("Config is not yet available")
            # Check if the thing exists in the configuration
            thing = latest_config.things.get(thing_id, None)
            if thing is None:
                raise Exception(f"Thing with ID {thing_id} not found")
            # Check if the channel exists in the thing
            target_attribute = thing.channels.get(attribute, None)
            if target_attribute is None:
                raise Exception(f"Attribute with ID {attribute} not found")

            if state == "true" or state == "True" or state == "1":
                desired_on = True
            elif state == "false" or state == "False" or state == "0":
                desired_on = False
            else:
                self._logger.error("Unknown state. Aborting control component")
                return ControlResult(False, "Invalid control Request")
            
            result = self._control_component(thing, target_attribute, desired_on)
            return result.to_json()
        except Exception as error:
            self._logger.error("Failed to process control command")
            self._logger.error(error)
            response = ControlResult(False, str(error))
            return response.to_json()

    def _control_component(self, thing: str, attribute: str, state: bool):
        try:
            if isinstance(thing, CircuitThing) and attribute.id == Constants.powerChannel:
                runtime_id = int(thing.id.split('.')[-1])
                successful = self.n2k_client.set_circuit_power_state(
                    runtime_id, state
                )
                return ControlResult(successful, None)
            
            elif isinstance(thing, Battery) and attribute.id == Constants.enabled:
                if thing.battery_circuit_id is not None:
                    successful = self.n2k_client.set_circuit_power_state(
                        thing.battery_circuit_id, state
                    )
                    return ControlResult(successful, None)
                else:
                    self._logger.error("No circuit found for Battery")
                    return ControlResult(False, "No circuit found for Battery")
            elif (
                isinstance(thing, CombiCharger) 
                or isinstance(thing, ACMeterCharger)
            ) and attribute.id == Constants.chargerEnable:
                if thing.charger_circuit_control_id is not None:
                    successful = self.n2k_client.set_circuit_power_state(
                        thing.charger_circuit_control_id, state
                    )
                    return ControlResult(successful, None)
                else:
                    self._logger.error("No circuit found for Charger")
                    return ControlResult(False, "No circuit found for Charger")
            elif (
                isinstance(thing, CombiInverter)
                or isinstance(thing, AcMeterInverter)
            ) and attribute.id == Constants.inverterEnable:
                if thing.inverter_circuit_control_id is not None:
                    successful = self.n2k_client.set_circuit_power_state(
                        thing.inverter_circuit_control_id, state
                    )
                    return ControlResult(successful, None)
                else:
                    self._logger.error("No circuit found for Inverter")
                    return ControlResult(False, "No circuit found for Inverter")

            self._logger.error("Failed to control component")
            return ControlResult(False, "Invalid control Request")

        except Exception as error:
            self._logger.error("Failed to control component")
            self._logger.error(error)
            return ControlResult(False, str(error))

    def reset_attribute_sub_set(self):
        self.attribute_sub_set.clear()
"""
RPC Handler Service for ThingsBoard Client
"""
import base64
import logging
import os
import sys
from typing import Any, Dict, Optional, Union
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
#pylint: disable=import-error, wrong-import-position
from mqtt_client import ThingsBoardClient
from tb_utils.constants import Constants
from n2kclient.client import N2KClient
from n2kclient.models.empower_system.thing import Thing
from n2kclient.models.empower_system.channel import Channel
from n2kclient.models.empower_system.circuit_thing import CircuitThing
from n2kclient.models.empower_system.battery import Battery
from n2kclient.models.empower_system.charger import CombiCharger, ACMeterCharger
from n2kclient.models.empower_system.inverter import CombiInverter, AcMeterInverter

class ControlResult:
    """
    Class to represent the result of a control operation.
    Its a convenience class to return the result of a control operation
    to the RPC handler.
    """
    successful: bool
    error: str

    def __init__(self, successful: bool, error: str):
        self.successful = successful
        self.error = error

    def to_json(self):
        """
        Convert the ControlResult to a JSON serializable dictionary.
        If successful, only the successful key is returned.
        """
        if self.successful:
            return {"successful": self.successful}
        else:
            return {
                "successful": self.successful,
                "error": self.error,
            }

class RpcHandlerService:
    """
    ThingsBoard Client class to handle RPC requests.
    This class is responsible for handling RPC the different commands available via RPC.
    """
    _logger = logging.getLogger(__name__)

    thingsboard_client: ThingsBoardClient
    n2k_client: N2KClient

    _stdout = ""
    _stdin = ""
    _stderr = ""

    def __init__(self, n2k_client):
        self.thingsboard_client = ThingsBoardClient()
        self.n2k_client = n2k_client
        self.register_rpc_callbacks()

    def __getCommandStatus_rpc_handler(self, body: dict[str, any]):
        self._logger.info("Received getCommandStatus command: %s", body)
        return {
            "data": [
                {
                    "stdout": self._stdout.read().decode(),
                    "stderr": self._stderr.read().decode(),
                }
            ],
            "done": True,
        }

    def register_rpc_callbacks(self):
        """
        Register the rpc related commands to the thingsboard client.
        """
        self.thingsboard_client.set_rpc_handler(
            "getCommandStatus", self.__getCommandStatus_rpc_handler
        )
        self.thingsboard_client.set_rpc_handler("control", self.__control_rpc_handler)
        self.thingsboard_client.set_rpc_handler(
            "writeConfig", self.__write_config_rpc_handler
        )
        self.thingsboard_client.set_rpc_handler(
            "refreshAlarms", self.__refreshAlarms_rpc_handler
        )
        self.thingsboard_client.set_rpc_handler(
            "clearEngineConfiguration", self.__clearEngineConfiguration_rpc_handler
        )
        self.thingsboard_client.set_rpc_handler(
            "acknowledgeAlarm", self.__acknowledge_alarm_handler
        )
        self.thingsboard_client.set_rpc_handler(
            "factoryReset", self.__factory_reset_rpc_handler
        )

    def __refreshAlarms_rpc_handler(self, body: dict[str, any]):
        self._logger.info("Received refreshAlarm command")
        result = self._refresh_alarms()
        return result.to_json()

    def _refresh_alarms(self):
        try:
            reason = None
            # TODO: Replace with actual refresh logic
            # successful, reason = self.n2k_client.refresh_active_alarms()
            successful = True
            return ControlResult(successful, reason)
        except Exception as error:
            self._logger.error("Failed to refresh alarms")
            self._logger.error(error)
            return ControlResult(
                False, reason if reason is not None else "Failed to refresh alarms"
            )

    def __clearEngineConfiguration_rpc_handler(self, body: dict[str, any]):
        self._logger.info("Received clearEngineConfiguration command")
        result = self._scan_engine_config(should_clear=True)
        return result.to_json()

    def _scan_engine_config(self, should_clear: bool):
        self._logger.info("Scanning Marine Engine Config")
        try:
            reason = None
            # TODO: Replace with actual scan logic
            # successful, reason = self.n2k_client.scan_marine_engines(
            #     should_clear=should_clear
            # )
            successful = True
            return ControlResult(successful, reason)
        except Exception as error:
            self._logger.error("Failed to scan engine config")
            self._logger.error(error)
            return ControlResult(
                False,
                (
                    reason
                    if reason is not None
                    else "Failed to clear engine configuration"
                ),
            )

    def __acknowledge_alarm_handler(self, body: dict[str, any]):
        self._logger.info("Received acknowledge alarm command: %s", body)
        try:
            if not "alarmId" in body:
                raise Exception("Invalid acknowledge command: alarmId is missing")

            alarm_id_segments = str(body["alarmId"]).split(".")

            if len(alarm_id_segments) < 2 or not (alarm_id_segments[1]).isdigit():
                raise Exception(
                    "Invalid acknowledge command: alarmId is not of the format alarm.###"
                )

            alarm_id = int(alarm_id_segments[1])
            # TODO: Get last state attributes from the n2k_client or similar
            # if alarm_id not in self.last_state_attrs[Constants.ActiveAlarms]:
            #     raise Exception(f"Active alarms with ID {alarm_id} not found")

            result = self._acknowledge_alarm(alarm_id)
            return result.to_json()

        except Exception as error:
            self._logger.error("Failed to acknowledge command")
            self._logger.error(error)
            response = ControlResult(False, str(error))
            return response.to_json()

    def _acknowledge_alarm(self, alarm_id: int) -> ControlResult:
        self._logger.info("Acknowledging alarm with id - (%d})", alarm_id)

        try:
            # TODO: Replace with actual acknowledge logic
            # successful = self.n2k_client.acknowledge_alarm(alarm_id)
            successful = True
            return ControlResult(successful, None)

        except Exception as error:
            self._logger.error("Failed to acknowledge alarm")
            self._logger.error(error)
            return ControlResult(False, "Failed to acknowledge alarm")

    def __control_rpc_handler(self, body: dict[str, any]):
        self._logger.info("Received control command: %s", body)
        try:
            thing_id = body.get("thingId", None)
            attribute_id = body.get("attributeId", None)
            state = body.get("state", None)

            # Check to make sure all required fields are present
            if thing_id is None:
                raise Exception("Invalid control command: thingId is missing")

            if attribute_id is None:
                raise Exception("Invalid control command: attributeId is missing")

            if state is None:
                raise Exception("Invalid control command: state is missing")

            # Get the latest configuration from the n2k_client
            latest_config = self.n2k_client.get_empower_system()
            if latest_config is None:
                raise Exception("Config is not yet available")

            # Check if the thing exists in the configuration
            thing = latest_config.things.get(thing_id, None)
            if thing is None:
                raise Exception(f"Thing with ID {thing_id} not found")

            # Check if the channel exists in the thing
            target_attribute = thing.channels.get(attribute_id, None)
            if target_attribute is None:
                raise Exception(f"Attribute with ID {attribute_id} not found")

            # Try to control the component
            result = self.__control_component(thing, target_attribute, state)
            return result.to_json()

        except Exception as error:
            self._logger.error("Failed to process control command")
            self._logger.error(error)
            response = ControlResult(False, str(error))
            return response.to_json()

    def __control_level_or_set_state(self,
            thing: Thing,
            state: Union[bool, float]
        ) -> ControlResult:
        """
        Control the level or set the state of a component.
        This function is a convenience function to control the level/set the state of a component.
        It will return a ControlResult object with the result of the operation.
        """
        runtime_id = int(thing.id.split('.')[-1])
        if isinstance(state, float):
            self._logger.debug("Setting level for circuit %s to %s", runtime_id, state)
            return self.n2k_client.set_circuit_level(runtime_id, float(state))
        else:
            if isinstance(state, int) or isinstance(state, bool):
                desired_on = False
                if state == 1 or state == True:
                    desired_on = True
                state = desired_on
            self._logger.debug("Setting state for circuit %s to %s", runtime_id, state)
            return self.n2k_client.set_circuit_power_state(runtime_id, bool(state))

    def __control_component(
        self,
        thing: Thing,
        attribute: Channel,
        state: Union[int, bool, float],
    ) -> ControlResult:
        self._logger.info(
            "Controlling %s (%s) attribute %s (%s) to %s",
            thing.name, thing.id, attribute.name, attribute.id, state
        )

        try:
            # Check to see if thing is a CircuitThing
            if (
                isinstance(thing, CircuitThing)
                and attribute.id == Constants.powerChannel
            ):
                # Circuit Things can be dimmable, so we can either set a level or state
                return ControlResult(self.__control_level_or_set_state(thing, state), None)
            # Check if thing is a Battery and the attribute is enabled
            elif isinstance(thing, Battery) and attribute.id == Constants.enabled:
                if thing.battery_circuit_id is not None:
                    # Try to set the state of the battery circuit
                    return ControlResult(
                        self.__control_level_or_set_state(
                            thing.battery_circuit_id, state),
                            None
                        )
                else:
                    self._logger.error("No circuit found for Battery")
                    return ControlResult(False, "No circuit found for Battery")
            # Check if thing is a Charger or Inverter and the attribute is enabled
            elif (
                isinstance(thing, CombiCharger)
                or isinstance(thing, ACMeterCharger)
            ) and attribute.id == Constants.chargerEnable:
                # Try to get the control ID for the charger circuit
                # and set the state if it exists
                if thing.charger_circuit_control_id is not None:
                    successful = self.n2k_client.set_circuit_power_state(
                        thing.charger_circuit_control_id,
                        state
                    )
                    return ControlResult(successful, None)
                else:
                    self._logger.error("No circuit found for Charger")
                    return ControlResult(False, "No circuit found for Charger")
            # Check if thing is a CombiInverter or AcMeterInverter and the attribute is enabled
            elif (
                isinstance(thing, CombiInverter)
                or isinstance(thing, AcMeterInverter)
            ) and attribute.id == Constants.inverterEnable:
                # Try to get the control ID for the inverter circuit
                # and set the state if it exists
                if thing.inverter_circuit_control_id is not None:
                    successful = self.n2k_client.set_circuit_power_state(
                        thing.inverter_circuit_control_id,
                        state
                    )
                    return ControlResult(successful, None)
                else:
                    self._logger.error("No circuit found for Inverter")
                    return ControlResult(False, "No circuit found for Inverter")
            # Not a valid component to control
            self._logger.error("Failed to control component")
            return ControlResult(False, "Invalid control Request")
        except Exception as error:
            self._logger.error("Failed to control component")
            self._logger.error(error)
            return ControlResult(False, "Failed to control Request")

    def __write_config_rpc_handler(self, body: dict[str, any]):
        self._logger.info("Received write config command: %s", body)
        try:
            if not "data" in body:
                raise Exception("Data is missing")

            data_as_base64 = body["data"]
            file_data = base64.b64decode(data_as_base64)

            # TODO: Write config file to the device
            # self.n2k_client.write_config(file_data)

            return {"successful": True}
        except Exception as error:
            self._logger.error("Failed to process write config command")
            self._logger.error(error)
            return {"successful": False, "error": error}

    def factory_reset_from_device(self):
        """
        Function to call the factory reset handler from local
        This will happen when user holds the reset button on the device
        Call the factory reset rpc handler function since TB flow
        should be the same
        """
        self.__factory_reset_rpc_handler(body={})

    def __factory_reset_rpc_handler(self, body: dict[str, any]):
        """
        Callback handler when the factory reset command comes through rpc
        The device will remove its ble auth key
        and delete the persistent data.
        """
        self._logger.info("Received reset command: %s", body)

        try:
            # Remove BT Access token if it exists
            if os.path.exists(Constants.BLE_SECRET_AUTH_KEY_PATH):
                self._logger.info("Removing BT ACCESS token file")
                os.remove(Constants.BLE_SECRET_AUTH_KEY_PATH)
            else:
                self._logger.info("No BT ACCESS token file found")
            return ControlResult(successful=True, error="").to_json()
        except Exception as error:
            self._logger.error("Encounted an error trying to do factory reset")
            self._logger.error(error)
            return ControlResult(successful=False, error=str(error)).to_json()

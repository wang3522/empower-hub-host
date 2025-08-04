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
            if not "thingId" in body:
                raise Exception("Invalid control command: thingId is missing")

            if not "attributeId" in body:
                raise Exception("Invalid control command: attributeId is missing")

            if not "state" in body:
                raise Exception("Invalid control command: state is missing")

            thing_id = body["thingId"]
            attribute_id = body["attributeId"]
            state = body["state"]

            print("desired state is a float:", isinstance(state, float))
            print("desired state is a bool:", isinstance(state, bool))
            print("desired state is an int:", isinstance(state, int))

            latest_config = self.n2k_client.get_empower_system()
            if latest_config is None:
                raise Exception("Config is not yet available")

            thing = latest_config.things.get(thing_id, None)
            if thing is None:
                raise Exception(f"Thing with ID {thing_id} not found")

            target_attribute = thing.channels.get(attribute_id, None)
            if target_attribute is None:
                raise Exception(f"Attribute with ID {attribute_id} not found")

            result = self.__control_component(thing, target_attribute, state)

            return result.to_json()

        except Exception as error:
            self._logger.error("Failed to process control command")
            self._logger.error(error)
            response = ControlResult(False, str(error))
            return response.to_json()

    def __control_component(
        self,
        thing: Thing,
        attribute: Channel,
        state: Union[int, bool, float],
    ) -> ControlResult:
        self._logger.info(
            f"Controlling {thing.name} ({thing.id}) attribute {attribute.name} ({attribute.id}) to {state}"
        )

        print(type(thing))
        print("attribute id: ", attribute.id)
        print(attribute.to_json())

        try:
            # TODO: Implement the control logic for the controlling components
            if (
                isinstance(thing, CircuitThing)
                and attribute.id == Constants.powerChannel
            ):
                print("CircuitThing found")
                desired_on = False
                if state == 1 or state == True:
                    desired_on = True

                # successful = self.n2k_client.set_circuit_state(
                #     thing.circuit_runtime_id, desired_on
                # )
                successful = True
                return ControlResult(successful, None)

            # elif isinstance(thing, Battery) and attribute.id == Constants.enabled:
            #     if thing.battery_circuit_id is not None:
            #         successful = self.n2k_client.set_circuit_state(
            #             thing.battery_circuit_id, state
            #         )
            #         return ControlResult(successful, None)
            #     else:
            #         self._logger.error("No circuit found for Battery")
            #         return ControlResult(False, "No circuit found for Battery")

            # elif (
            #     isinstance(thing, CombiMasterCharger)
            #     or isinstance(thing, AcMeterCharger)
            # ) and attribute.id == Constants.chargerEnable:
            #     if thing.charger_circuit_id is not None:
            #         successful = self.n2k_client.set_circuit_state(
            #             thing.charger_circuit_id, state
            #         )
            #         return ControlResult(successful, None)
            #     else:
            #         self._logger.error("No circuit found for Charger")
            #         return ControlResult(False, "No circuit found for Charger")

            # elif (
            #     isinstance(thing, CombiMasterInverter)
            #     or isinstance(thing, AcMeterInverter)
            # ) and attribute.id == Constants.inverterEnable:
            #     if thing.inverter_circuit_id is not None:
            #         successful = self.n2k_client.set_circuit_state(
            #             thing.inverter_circuit_id, state
            #         )
            #         return ControlResult(successful, None)
            #     else:
            #         self._logger.error("No circuit found for Inverter")
            #         return ControlResult(False, "No circuit found for Inverter")

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

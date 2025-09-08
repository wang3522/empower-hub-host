"""
Helper functions for the Thingsboard client.
This module contains utility functions to manage the connection to Thingsboard,
provisioning, and other helper functions.
"""
import enum
import os
import logging
#pylint: disable=import-error
from tb_utils.constants import Constants
from provisioning_client import EmpowerProvisionClient


logger = logging.getLogger("Utility")

class ConnectionStatus(str, enum.Enum):
    """
    Enum for the connection status of the device.
    """
    UNKNOWN = "Unknown"
    DISCONNECTED = "Disconnected"
    CONNECTED = "Connected"
    LOW_POWER = "LowPower"
    IDLE = "Idle"

class MessageType(str, enum.Enum):
    """
    Enum for the message type.
    """
    ATTRIBUTE = "Attribute"
    TELEMETRY = "Telemetry"

class ControlResult:
    """
    Class to represent the result of a control operation.
    """
    successful: bool
    error: str

    def __init__(self, successful: bool, error: str):
        self.successful = successful
        self.error = error

    def to_json(self):
        """
        Convert the ControlResult to a JSON object."""
        if self.successful:
            return {"successful": self.successful}
        else:
            return {
                "successful": self.successful,
                "error": self.error,
            }

def get_tb_host():
    """
    Get the host for the Thingsboard server.
    """
    if (
        "TB_HOST" in os.environ
        and os.environ["TB_HOST"] != ""
        and os.environ["TB_HOST"] != "{YOUR TB HOST ENDPOINT}"
    ):
        return os.environ["TB_HOST"]
    else:
        return "mqtt.empower-czone.com"


def get_tb_port():
    """
    Get the port for the Thingsboard server.
    """
    if (
        "TB_PORT" in os.environ
        and os.environ["TB_PORT"] != ""
        and os.environ["TB_PORT"] != "[TB_PORT]"
        and os.environ["TB_PORT"] != "{YOUR TB HOST PORT}"
    ):
        try:
            return int(os.environ["TB_PORT"])
        except ValueError as e:
            logger.error(e)
            logger.info("returning default port 8883")
            return 8883
    else:
        return 8883

def get_access_token():
    """
    Get the access token for the device.
    """
    # Case 1: TB_ACCESS_TOKEN exists in env (Testing with device already provisioned manually)
    logger.info("getting access token")
    if (
        "TB_ACCESS_TOKEN" in os.environ
        and os.environ["TB_ACCESS_TOKEN"] != ""
        and os.environ["TB_ACCESS_TOKEN"] != "{YOUR ACCESS TOKEN}"
    ):
        logger.info("Found TB_ACCES_TOKEN in env. Overriding local access token")
        return os.environ["TB_ACCESS_TOKEN"]
    else:
        if os.path.exists(Constants.TB_ACCESS_TOKEN_PATH):
            with open(Constants.TB_ACCESS_TOKEN_PATH, "r", encoding="utf-8") as file:
                tb_access_token = file.read().rstrip()
                # Case 2: TB_ACCESS_TOKEN doesn't exist in env but we have the access token stored
                # (Device provisioned by itself previously)
                logger.info("Found TB_ACCES_TOKEN in local file")
                return tb_access_token
        else:
            logger.warning("tb_access_token file not found")
            # Case 3: TB_ACCESS_TOKEN doesn't exist in env and no access token stored
            # but we have TB_PROV_KEY and TB_PROV_SECRET in env (Device ready for provisioning)
            if "TB_PROV_KEY" in os.environ and "TB_PROV_SECRET" in os.environ:
                if os.path.exists(Constants.SN_PATH):
                    with open(Constants.SN_PATH, "r", encoding="utf-8") as file:
                        logger.info(
                            "Found PROV_KEY, PROV_SECRET, and SN. Ready to provision"
                        )
                        serial_number = file.read().rstrip()
                        provision_request = {
                            "provisionDeviceKey": os.environ["TB_PROV_KEY"],
                            "provisionDeviceSecret": os.environ["TB_PROV_SECRET"],
                        }
                        provision_request["deviceName"] = serial_number
                        prov_client = EmpowerProvisionClient(
                            get_tb_host(), get_tb_port(), provision_request
                        )
                        prov_client.provision()
                        credentials = prov_client.get_credentials()
                        if (
                            credentials is not None
                            and credentials.get("status") == "SUCCESS"
                        ):
                            if credentials["credentialsType"] == "ACCESS_TOKEN":
                                tb_access_token = credentials["credentialsValue"]
                                try:
                                    with open(
                                        Constants.TB_ACCESS_TOKEN_PATH, "w", encoding="utf-8"
                                    ) as file:
                                        file.write(tb_access_token)
                                except Exception as e:
                                    logger.error("Error writing access token to file: %s", e)
                                return tb_access_token
                            else:
                                logger.error("credentials type doesn't match")
                        else:
                            logger.error("provisioning failed")
                        return None
                else:
                    # Case 4: Not provisioned and can't provision itself because
                    # there is no serial number
                    logger.error("serial_number file not found, can't provision")
                    return None
            # Case 5: Not provisioned and can't provision itself because
            # there is no PROV_KEY and PROV_SECRET
            logger.error("TB_PROV_KEY and/or SECRET not found, can't provision")
            return None

import os
import sys
import json
import hmac
import hashlib
import string
import logging
import secrets 
import time
from bleService.uart_message_processor import get_key

logger = logging.getLogger(__name__)

class CmdInterface:
    def __init__(self):
        self._device_info = {
            "serial_number": "undefined",
            "model_number": "undefined",
            "hardware_rev": "undefined",
            "firmware_rev": "undefined",
        }
        self._auth_state = {
            "expected_hash_2": None
        }
        self._uart_authenticated_cb = None
        self._empower_ble_service = None

    def handle_hello(self,data: str):
        logger.debug(f"handle_hello {data}")
        return f"MX93/HELLO"

    def handle_get_device_information(self, data: str):
        logger.debug(f"handle_get_device_information {data}")
        device_info_json = json.dumps(self._device_info, separators=(',', ':'))
        return f"MX93/DEVICE_INFO/{device_info_json.encode().hex()}"

    def handle_notify_version(self, data: str):
        logger.debug(f"handle_notify_version {data}")
        return f"NOTIFY_VERSION/{data.strip().encode().hex()}"

    def handle_auth_chal(self, data: str):
        logger.debug("handle_auth_chal {}".format(data))

        key = get_key()

        challenge_1 = data.strip()
        response_for_app = hmac.new(key.encode("utf-8"), challenge_1.encode("utf-8"), hashlib.sha256).hexdigest()
        challenge_2 = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(8))

        self._auth_state["expected_hash_2"] = hmac.new(key.encode("utf-8"), challenge_2.encode("utf-8"), hashlib.sha256).hexdigest()

        combined = response_for_app + challenge_2
        return f"MX93/AUTH_RESP_SERVER/{combined.encode().hex()}"

    def handle_auth_resp_client(self,data: str):
        logger.debug(f"handle_auth_resp_client {data}")
        if data.strip() == self._auth_state["expected_hash_2"]:
            if (self._uart_authenticated_cb is not None):
                self._uart_authenticated_cb(True)
            grant_level = "01"
        else:
            grant_level = "00"
        return f"MX93/GRANT_LVL/{grant_level.encode().hex()}"

    def handle_get_enc_type(self, data: str):
        logger.debug(f"handle_get_enc_type {data}")
        return f"MX93/NOT_IMPLEMENTED"

    def handle_sub(self, data: str):
        logger.debug(f"handle_sub {data}")
        if self._empower_ble_service is not None:
            self._empower_ble_service.update_attribute_subscription(data.split("/")[1], True)
            return f""
        logger.error("handle_sub called but empower_ble_service is None")
        return f""

    def handle_pub(self, data: str):
        logger.debug(f"handle_pub {data}")
        if self._empower_ble_service is not None:
            split_data = data.split("/")
            attribute, value = split_data[0], split_data[1]
            self._empower_ble_service.handle_control_component(attribute, value)
            return f""
        logger.error("handle_pub called but empower_ble_service is None")
        return f""

    def handle_unsub(self, data: str):
        logger.debug(f"handle_unsub {data}")
        if self._empower_ble_service is not None:
            self._empower_ble_service.update_attribute_subscription(data.split("/")[1], False)
            return f""
        logger.error("handle_unsub called but empower_ble_service is None")
        return f""

    def handle_get_fw_dl_status(self, data: str):
        logger.debug(f"handle_get_fw_dl_status {data}")
        return f"MX93/NOT_IMPLEMENTED"

    # handle_notify_fw_dl_status does not return as hex since it's not sent to the BL654 and is handled in bleuart
    def handle_notify_fw_dl_status(self, data: str):
        logger.debug(f"handle_notify_fw_dl_status {data}")
        return f"OTA_STATUS/{data.strip()}"

    # handle_go_fw_update does not return as hex since it's not sent to the BL654 and is handled in bleuart
    def handle_go_fw_update(self, data: str):
        logger.debug(f"handle_go_fw_update {data}")
        return f"OTA_CONSENTED"

    def handle_set_ssid(self, data: str):
        logger.debug(f"handle_set_ssid {data}")
        return f"MX93/NOT_IMPLEMENTED"

    def handle_set_pw(self, data: str):
        logger.debug(f"handle_set_pw {data}")
        return f"MX93/NOT_IMPLEMENTED"

    def handle_get_ssid(self, data: str):
        logger.debug(f"handle_get_ssid {data}")
        return f"MX93/NOT_IMPLEMENTED"

    def handle_get_attr_list(self, data: str):
        logger.debug(f"handle_get_attr_list {data}")
        return f"MX93/NOT_IMPLEMENTED"

    def handle_update_adc_value(self, data: str):
        logger.debug(f"handle_update_adc_value {data}")
        return f"MX93/NOT_IMPLEMENTED"

    def handle_version(self, data: str):
        logger.debug(f"handle_version {data}")
        return f"MX93/NOT_IMPLEMENTED"

    def handle_set_name(self, data: str):
        logger.debug(f"handle_set_name {data}")
        return f"MX93/NOT_IMPLEMENTED"

    def handle_get_names(self, data: str):
        logger.debug(f"handle_get_names {data}")
        return f"MX93/NOT_IMPLEMENTED"

    def handle_set_range(self, data: str):
        logger.debug(f"handle_set_range {data}")
        return f"MX93/NOT_IMPLEMENTED"

    def handle_get_range(self, data: str):
        logger.debug(f"handle_get_range {data}")
        return f"MX93/NOT_IMPLEMENTED"

    def handle_set_alarm_rule(self, data: str):
        logger.debug(f"handle_set_alarm_rule {data}")
        return f"MX93/NOT_IMPLEMENTED"

    def handle_reset_grant_level(self, data: str):
        logger.debug(f"handle_reset_grant_level {data}")
        if self._uart_authenticated_cb is not None:
            self._uart_authenticated_cb(False)
        if self._empower_ble_service is not None:
            self._empower_ble_service.reset_attribute_sub_set()
        return f""

    def handle_get_time(self, data: str):
        now = time.gmtime()
        rtc_tuple = (now[0], now[1], now[2], now[6], now[3], now[4], now[5], 0)
        payload = ",".join(str(x) for x in rtc_tuple)
        logger.debug(f"handle_get_time: Set time {payload}")
        return f"MX93/SET_TIME/{payload.encode().hex()}"

    def _bl_cmd_interface(self, data: str):
        try:
            response = None

            handlers = {
                "HELLO": self.handle_hello,
                "GET_DEVICE_INFORMATION": self.handle_get_device_information,
                "NOTIFY_VERSION": self.handle_notify_version,
                "AUTH_CHAL": self.handle_auth_chal,
                "AUTH_RESP_CLIENT": self.handle_auth_resp_client,
                "GET_ENC_TYPE": self.handle_get_enc_type,
                "SUB": self.handle_sub,
                "PUB": self.handle_pub,
                "UNSUB": self.handle_unsub,
                "GET_FW_DL_STATUS": self.handle_get_fw_dl_status,
                "NOTIFY_FW_DL_STATUS": self.handle_notify_fw_dl_status,
                "GO_FW_UPDATE": self.handle_go_fw_update,
                "SET_SSID": self.handle_set_ssid,
                "SET_PW": self.handle_set_pw,
                "GET_SSID": self.handle_get_ssid,
                "GET_ATTR_LIST": self.handle_get_attr_list,
                "UPDATE_ADC_VALUE": self.handle_update_adc_value,
                "SET_NAME": self.handle_set_name,
                "GET_NAMES": self.handle_get_names,
                "SET_RANGE": self.handle_set_range,
                "GET_RANGE": self.handle_get_range,
                "SET_ALARM_RULE": self.handle_set_alarm_rule,
                "RESET_GRANT_LEVEL": self.handle_reset_grant_level,
                "GET_TIME": self.handle_get_time,
            }

            split_data = data.split("/", 1)
            cmd = split_data[0].upper()

            payload = split_data[1] if len(split_data) > 1 else ""

            handler = handlers.get(cmd)
            if handler:
                return handler(payload) + "\n"
            else:
                logger.error(f"Unknown BL command: {cmd}")
                return ""

        except Exception as e:
            logger.error(f"BL command handler failed: {e}")
            return ""

    def set_uart_authenticated_callback(self, callback):
        self._uart_authenticated_cb = callback

    def set_empower_ble_service(self, empower_ble_service):
        self._empower_ble_service = empower_ble_service

_cmd_interface_instance = CmdInterface()

CMD_INTERFACE_INSTANCE = _cmd_interface_instance
CMD_INTERFACE = {"bl": _cmd_interface_instance._bl_cmd_interface}

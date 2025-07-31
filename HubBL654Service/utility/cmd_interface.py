import os
import sys
import json
import hmac
import hashlib
import string
import logging
import secrets 

from ..bleService.uart_message_processor import encrypt_data, decrypt_data, get_key

logger = logging.getLogger(__name__)

_device_info = {
    "serial_number": "undefined",
    "model_number": "undefined",
    "hardware_rev": "undefined",
    "firmware_rev": "undefined",
}

_auth_state = {
    "expected_hash_2": None
}

def handle_hello(data: str):
    logger.debug(f"handle_hello {data}")
    return f"MX93/HELLO"

def handle_get_sn(data: str):
    logger.debug(f"handle_get_sn {data}")
    return f"MX93/SN/{_device_info['serial_number']}"

def handle_get_mn(data: str):
    logger.debug(f"handle_get_mn {data}")
    return f"MX93/MN/{_device_info['model_number']}"

def handle_get_fr(data: str):
    logger.debug(f"handle_get_fr {data}")
    return f"MX93/FR/{_device_info['firmware_rev']}"

def handle_get_hr(data: str):
    logger.debug(f"handle_get_hr {data}")
    return f"MX93/HR/{_device_info['hardware_rev']}"

def handle_notify_ar(data: str):
    logger.debug(f"handle_notify_ar {data}")
    return f"NOTIFY_AR/{data.strip()}"

def handle_auth_chal(data: str):
    logger.debug("handle_auth_chal {}".format(data))

    key = get_key()

    challenge_1 = data.strip()
    response_for_app = hmac.new(key.encode("utf-8"), challenge_1.encode("utf-8"), hashlib.sha256).hexdigest()
    challenge_2 = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(8))

    _auth_state["expected_hash_2"] = hmac.new(key.encode("utf-8"), challenge_2.encode("utf-8"), hashlib.sha256).hexdigest()

    combined = response_for_app + challenge_2
    return f"MX93/AUTH_RESP_SERVER/{combined}"

def handle_auth_resp_client(data: str):
    logger.debug(f"handle_auth_resp_client {data}")
    if data.strip() == _auth_state["expected_hash_2"]:
        grant_level = "01"
    else:
        grant_level = "00"
    return f"MX93/GRANT_LVL/{grant_level}"

def handle_get_enc_type(data: str):
    logger.debug(f"handle_get_enc_type {data}")
    return f"MX93/NOT_IMPLEMENTED"

def handle_sub(data: str):
    logger.debug(f"handle_sub {data}")
    return f"MX93/NOT_IMPLEMENTED"

def handle_pub(data: str):
    logger.debug(f"handle_pub {data}")
    return f"MX93/NOT_IMPLEMENTED"

def handle_unsub(data: str):
    logger.debug(f"handle_unsub {data}")
    return f"MX93/NOT_IMPLEMENTED"

def handle_get_fw_dl_status(data: str):
    logger.debug(f"handle_get_fw_dl_status {data}")
    return f"MX93/NOT_IMPLEMENTED"

def handle_notify_fw_dl_status(data: str):
    logger.debug(f"handle_notify_fw_dl_status {data}")
    return f"OTA_STATUS/{data.strip()}"

def handle_go_fw_update(data: str):
    logger.debug(f"handle_go_fw_update {data}")
    return f"OTA_CONSENTED"

def handle_set_ssid(data: str):
    logger.debug(f"handle_set_ssid {data}")
    return f"MX93/NOT_IMPLEMENTED"

def handle_set_pw(data: str):
    logger.debug(f"handle_set_pw {data}")
    return f"MX93/NOT_IMPLEMENTED"

def handle_get_ssid(data: str):
    logger.debug(f"handle_get_ssid {data}")
    return f"MX93/NOT_IMPLEMENTED"

def handle_get_attr_list(data: str):
    logger.debug(f"handle_get_attr_list {data}")
    return f"MX93/NOT_IMPLEMENTED"

def handle_update_adc_value(data: str):
    logger.debug(f"handle_update_adc_value {data}")
    return f"MX93/NOT_IMPLEMENTED"

def handle_version(data: str):
    logger.debug(f"handle_version {data}")
    return f"MX93/NOT_IMPLEMENTED"

def handle_set_name(data: str):
    logger.debug(f"handle_set_name {data}")
    return f"MX93/NOT_IMPLEMENTED"

def handle_get_names(data: str):
    logger.debug(f"handle_get_names {data}")
    return f"MX93/NOT_IMPLEMENTED"

def handle_set_range(data: str):
    logger.debug(f"handle_set_range {data}")
    return f"MX93/NOT_IMPLEMENTED"

def handle_get_range(data: str):
    logger.debug(f"handle_get_range {data}")
    return f"MX93/NOT_IMPLEMENTED"

def handle_set_alarm_rule(data: str):
    logger.debug(f"handle_set_alarm_rule {data}")
    return f"MX93/NOT_IMPLEMENTED"

def _bl_cmd_interface(data: str):
    try:
        logger.debug(f"Received BL message: {data}")
        response = None

        handlers = {
            "HELLO": handle_hello,
            "GET_SN": handle_get_sn,
            "GET_MN": handle_get_mn,
            "GET_FR": handle_get_fr,
            "GET_HR": handle_get_hr,
            "NOTIFY_AR": handle_notify_ar,
            "AUTH_CHAL": handle_auth_chal,
            "AUTH_RESP_CLIENT": handle_auth_resp_client,
            "GET_ENC_TYPE": handle_get_enc_type,
            "SUB": handle_sub,
            "PUB": handle_pub,
            "UNSUB": handle_unsub,
            "GET_FW_DL_STATUS": handle_get_fw_dl_status,
            "NOTIFY_FW_DL_STATUS": handle_notify_fw_dl_status,
            "GO_FW_UPDATE": handle_go_fw_update,
            "SET_SSID": handle_set_ssid,
            "SET_PW": handle_set_pw,
            "GET_SSID": handle_get_ssid,
            "GET_ATTR_LIST": handle_get_attr_list,
            "UPDATE_ADC_VALUE": handle_update_adc_value,
            "VERSION": handle_version,
            "SET_NAME": handle_set_name,
            "GET_NAMES": handle_get_names,
            "SET_RANGE": handle_set_range,
            "GET_RANGE": handle_get_range,
            "SET_ALARM_RULE": handle_set_alarm_rule,
        }

        split_data = data.split("/")
        cmd = split_data[0].upper()
        payload = split_data[1] if len(split_data) > 1 else ""
        
        handler = handlers.get(cmd)
        if handler:
            return handler(payload) + "\n"
        else:
            return json.dumps({"error": f"unknown BL command '{cmd}'", "data": None})

    except Exception as e:
        logger.error(f"BL command handler failed: {e}")
        return json.dumps({"error": str(e)})



CMD_INTERFACE = {"bl": _bl_cmd_interface}

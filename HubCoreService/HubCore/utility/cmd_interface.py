import logging
import json
import base64

from .config import SystemConfig as HubConfig, T_WIFI_CONFIG
from ..network.wifi import configure_wifi_settings, WIFI
from .gpio import GPIO, E_LED

logger = logging.getLogger(__name__)


def _wifi_cmd_interface(data: str):
    config = HubConfig()
    wifi_config: T_WIFI_CONFIG = config.get_config("wifi")
    ret = {"data": None, "error": None}

    if data.lower() == "enable":
        if wifi_config["enable"] == False:
            wifi_config["enable"] = True
            config.set_config("wifi", wifi_config)
            config.save_config()
            wifi = configure_wifi_settings()

            gpio = GPIO()
            gpio.update_led(E_LED.WIFI, wifi)
        ret["data"] = "ok"

    elif data.lower() == "disable":
        if wifi_config["enable"] == True:
            wifi_config["enable"] = False
            config.set_config("wifi", wifi_config)
            config.save_config()
            wifi = configure_wifi_settings()

            gpio = GPIO()
            gpio.update_led(E_LED.WIFI, wifi)
        ret["data"] = "ok"

    elif data.lower() == "list":
        ret["data"] = WIFI.scan_list()

    elif data.lower() == "status":
        wifi = WIFI()
        ret["data"] = wifi.status()

    elif data.lower() == "restart":
        wifi = configure_wifi_settings()
        gpio = GPIO()
        gpio.update_led(E_LED.WIFI, wifi)
        ret["data"] = wifi

    else:
        logger.error(f"unknown data: {data}")
        ret["error"] = "unknown data"

    return json.dumps(ret)


def _wifi_config(ssid, pwd):
    config = HubConfig()
    wifi_config: T_WIFI_CONFIG = config.get_config("wifi")
    wifi_config["ssid"] = ssid
    wifi_config["password"] = base64.b64encode(pwd.encode("utf-8")).decode("utf-8")
    config.set_config("wifi", wifi_config)
    config.save_config()
    wifi = configure_wifi_settings()
    gpio = GPIO()
    gpio.update_led(E_LED.WIFI, wifi)
    ret = {"data": wifi, "error": None}

    return json.dumps(ret)


def _ap_cmd_interface(data: str):
    ret = {"data": None, "error": None}

    return json.dumps(ret)


CMD_INTERFACE = {"wifi": _wifi_cmd_interface, "ap": _ap_cmd_interface, "wificonfig": _wifi_config}

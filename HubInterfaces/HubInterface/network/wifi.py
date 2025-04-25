import subprocess
import base64
import logging
import dbus
import time

from ..utility.config import SystemConfig as HubConfig, T_WIFI_CONFIG

logger = logging.getLogger(__name__)


class WIFI:
    device_id = None
    ssid = None
    password = None
    config: T_WIFI_CONFIG = None

    def __init__(self):
        c = HubConfig()
        config = c.get_config("wifi")
        self.config = config

        if config is None:
            raise ValueError("Invalid configuration")

        self.device_id = config["device_id"]
        self.ssid = config["ssid"]
        self.password = base64.b64decode(config["password"]).decode("utf-8")

        if "\n" in self.password or "\n" in self.ssid or not self.ssid:
            raise ValueError("Invalid wifi password or ssid")

    @staticmethod
    def subprocess_run(cmd):
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.stdout, result.stderr

    @classmethod
    def check_driver(cls):
        logger.debug("Checking if drive is mounted")
        # check if drive is mounted
        out, err = WIFI.subprocess_run("lsmod")
        if err:
            logger.error(f"Unable to check if drive is mounted, {err}")
            return False
        if "moal" not in out:
            logger.error("Drive is not mounted")
            return False
        return True

    def create(self):
        logger.debug("Creating wifi connection")
        out, err = WIFI.subprocess_run(f"nmcli con show")
        if err:
            logger.error(f"Unable to check network, {err}")
            raise ValueError("Unable to check network")
        if self.ssid in out:
            logger.debug("Wifi already exists")
            return

        logger.debug("Adding wifi connection")
        out, err = WIFI.subprocess_run(f"nmcli dev wifi connect {self.ssid} password {self.password} ifname {self.device_id}")
        if err:
            logger.error(f"Unable to add wifi point, {err}")
            raise ValueError("Unable to add wifi point")

        for _ in range(5):
            out, err = WIFI.subprocess_run(f"nmcli con modify {self.ssid} +ipv4.dns 8.8.8.8")
            if err:
                logger.debug(f"Unable to add DNS to wifi, {err}")
                time.sleep(1)
            else:
                break

        return

    def get_device_list(self):
        bus = dbus.SystemBus()
        nm_obj = bus.get_object("org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager")
        nm_iface = dbus.Interface(nm_obj, "org.freedesktop.NetworkManager")

        devices = nm_iface.GetDevices()
        device_list = []
        for device in devices:
            device_obj = bus.get_object("org.freedesktop.NetworkManager", device)
            device_interface = dbus.Interface(device_obj, "org.freedesktop.DBus.Properties")

            d_type = device_interface.Get("org.freedesktop.NetworkManager.Device", "DeviceType")
            if d_type == 2:
                device_list.append(device_interface.Get("org.freedesktop.NetworkManager.Device", "Interface"))
        return device_list

    def configure(self):
        logger.debug("Configuring wifi connection")

        if not WIFI.check_driver():
            raise ValueError("Driver not mounted")

        available_devices = self.get_device_list()

        if self.device_id not in available_devices:
            logger.error("Invalid device id")
            raise ValueError("Invalid device id")

        self.create()
        self.stop()

        return

    def start(self):
        logger.debug("Starting wifi connection")
        out, err = WIFI.subprocess_run(f"nmcli con show --active")
        if err:
            logger.error(f"Unable to check active network, {err}")
            return False
        if self.ssid in out:
            logger.debug(f"Wifi already active")
            return True

        out, err = WIFI.subprocess_run(f"nmcli con up {self.ssid}")
        if err:
            logger.error(f"Unable to start wifi, {err}")
            return False
        return True

    def stop(self):
        logger.debug("Stopping wifi connection")
        out, err = WIFI.subprocess_run(f"nmcli con show --active")
        if err:
            logger.error(f"Unable to check active network, {err}")
            return False
        if self.ssid in out:
            out, err = WIFI.subprocess_run(f"nmcli con down {self.ssid}")
            if err:
                logger.error(f"Unable to stop wifi, {err}")
                return False
        return True

    def status(self):
        logger.debug("Checking active network")
        out, err = WIFI.subprocess_run("nmcli con show --active")
        if err:
            logger.error(f"Unable to check active network, {err}")
            return False
        if self.ssid in out:
            return True
        return False

    @staticmethod
    def scan_list():
        try:
            logger.debug("Wifi Scan List")
            out, err = WIFI.subprocess_run(f"nmcli -t -f ssid dev wifi list")
            if err:
                logger.error(f"unable to get list of wifi, {err}")
                return []
            wifi_list = list(set(filter(None, out.splitlines())))
            return wifi_list
        except Exception as error:
            logger.error(f"unable to get list of wifi, {error}")
            return []


def configure_wifi_settings():
    config = HubConfig()
    wifi_config = config.get_config("wifi")

    try:
        HS = WIFI()

        for _ in range(3):
            try:
                HS.configure()
                break
            except Exception as error:
                logger.error(f"Error configuring wifi settings: {error}")
                time.sleep(1)

        if wifi_config["enable"]:
            HS.start()
        else:
            HS.stop()

        for _ in range(60):
            time.sleep(1)
            if HS.status() == wifi_config["enable"]:
                return wifi_config["enable"]

        raise ValueError("Unable to start wifi")
    except Exception as error:
        logger.error(f"Error configuring wifi settings: {error}")
    return False

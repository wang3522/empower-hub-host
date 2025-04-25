import subprocess
import base64
import logging
import logging.handlers
import dbus
import time

from ..utility.config import SystemConfig as HubConfig

logger = logging.getLogger(__name__)

class WAP:
    device_id = None
    ssid = None
    password = None
        
    def __init__(self):
        c = HubConfig()
        config = c.wap
        self.config = config
                        
        if config is None:
            raise ValueError("Invalid configuration")
        
        self.device_id = config["device_id"]
        self.ssid = config["ssid"]
        self.pwd = base64.b64decode(config["password"]).decode("utf-8")
        
        if "\n" in self.pwd or "\n" in self.ssid or not self.ssid:
            raise ValueError("Invalid wifi access point password or ssid")
                
    @staticmethod
    def subprocess_run(cmd):
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.stdout, result.stderr
        
    @classmethod
    def check_driver(cls):
        logger.debug("Checking if drive is mounted")
        # check if drive is mounted
        out, err = WAP.subprocess_run("lsmod")
        if err:
            logger.error(f"Unable to check if drive is mounted, {err}")
            return False
        if "moal" not in out:
            logger.error("Drive is not mounted")
            return False
        return True
    
    def create(self):
        logger.debug("Creating wifi access point")
        out, err = WAP.subprocess_run(f"nmcli con show")
        if err:
            logger.error(f"Unable to check network, {err}")
            raise ValueError("Unable to check network")
        if self.ssid in out:
            logger.debug("Wifi access point already exists")
            return
        
        logger.debug("Adding wifi access point")
        out, err = WAP.subprocess_run(f"nmcli con add type wifi ifname {self.device_id} con-name {self.ssid} autoconnect yes ssid {self.ssid}")
        if err:
            logger.error(f"Unable to add wifi access point, {err}")
            raise ValueError("Unable to add wifi access point")
        
        out, err = WAP.subprocess_run(f"nmcli con modify {self.ssid} 802-11-wireless.mode ap 802-11-wireless.band bg ipv4.method shared")
        if err:
            logger.error(f"Unable to modify wifi access point mode, {err}")
            raise ValueError("Unable to modify wifi access point mode")
        
        out, err = WAP.subprocess_run(f"nmcli con modify {self.ssid} 802-11-wireless-security.key-mgmt wpa-psk 802-11-wireless-security.psk {self.pwd}")
        if err:
            logger.error(f"Unable to modify wifi access point security, {err}")
            raise ValueError("Unable to modify wifi access point security")
        
        return
    
    def get_device_list(self):
        bus = dbus.SystemBus()
        nm_obj = bus.get_object("org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager")
        nm_iface = dbus.Interface(nm_obj, "org.freedesktop.NetworkManager")
        
        devices = nm_iface.GetDevices()
        device_list = []
        for device in devices:
            device_obj = bus.get_object('org.freedesktop.NetworkManager', device)
            device_interface = dbus.Interface(device_obj, 'org.freedesktop.DBus.Properties')
            
            d_type = device_interface.Get('org.freedesktop.NetworkManager.Device', 'DeviceType')
            if d_type == 2:
                device_list.append(device_interface.Get('org.freedesktop.NetworkManager.Device', 'Interface'))
        return device_list

    def configure(self):
        logger.debug("Configuring wifi access point")
        
        if not WAP.check_driver():
            raise ValueError("Driver not loaded")
        
        available_devices = self.get_device_list()
                
        if self.device_id not in available_devices:
            logger.error("Invalid device id")
            raise ValueError("Invalid device id")
        
        return self.create()
    
    def start(self):
        logger.debug("Starting wifi access point")
        out, err = WAP.subprocess_run(f"nmcli con show --active")
        if err:
            logger.error(f"Unable to check active network, {err}")
            return False
        if self.ssid in out:
            logger.debug("Wifi access point already active")
            return True
        
        out, err = WAP.subprocess_run(f"nmcli con up {self.ssid}")
        if err:
            logger.error(f"Unable to start wifi access point, {err}")
            return False
        return True

    def stop(self):
        logger.debug("Stopping wifi access point")
        out, err = WAP.subprocess_run(f"nmcli con show --active")
        if err:
            logger.error(f"Unable to check active network, {err}")
            return False
        if self.ssid in out:
            out, err = WAP.subprocess_run(f"nmcli con down {self.ssid}")
            if err:
                logger.error(f"Unable to stop wifi access point, {err}")
                return False
        return True

    def status(self):
        logger.debug("Checking active network")
        out, err = WAP.subprocess_run("nmcli con show --active")
        if err:
            logger.error(f"Unable to check active network, {err}")
            return False
        if self.ssid in out:
            return True
        return False

def configure_wap_settings():
    config = HubConfig()
    wap_config = config.wap
    
    try:
        HS = WAP()
        
        for _ in range(3):
            try:
                HS.configure()
                break
            except Exception as error:
                logger.error(f"Error configuring wifi access point: {error}")
        
        if wap_config["enable"]:
            HS.start()
        else:
            HS.stop()
            
        for _ in range(60):
            time.sleep(1)
            if HS.status() == wap_config["enable"]:
                return wap_config["enable"]
        
        raise ValueError("Unable to start hotspot")
    except Exception as error:
        logger.error(f"Error configuring wifi access point: {error}")
    return False

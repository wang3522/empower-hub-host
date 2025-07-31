import os
import logging
import dbus
import dbus.service
import threading
import time
from bleService.bleuart import BLE_UART

logger = logging.getLogger(__name__)

class DBusBl654(dbus.service.Object):
    DBUS_OBJECT = "/org/navico/HubUtility/bl654"
    DBUS_INTERFACE = "org.navico.HubUtility.bl654"

    def __init__(self, bus):
        bus_name = dbus.service.BusName(self.DBUS_INTERFACE, bus=bus)
        super().__init__(bus_name, self.DBUS_OBJECT)

    @dbus.service.signal(DBUS_INTERFACE, signature='s')
    def ota_error(self, message): pass

    @dbus.service.signal(DBUS_INTERFACE, signature='s')
    def ota_complete(self, message): pass

    @dbus.service.signal(DBUS_INTERFACE, signature='s')
    def notify_version(self, message): pass

    @dbus.service.method(DBUS_INTERFACE, in_signature="", out_signature="s")
    def get_version(self):
        BLE_UART().request_application_version()
        return "Requesting version from BL654..."

    @dbus.service.method(DBUS_INTERFACE, in_signature="s", out_signature="s")
    def initiate_ota(self, filepath):
        logger.info(f"DBusBl654.transfer called with: {filepath}")
        if os.path.exists("/data/ota_consent.txt"):
            threading.Thread(target=BLE_UART().handle_ota_transfer, args=(filepath,)).start()
            return "Starting OTA transfer..."
        else:
            logger.error("OTA consent file not found.")
            return "Consent file not found, not starting OTA transfer..."
import logging
import dbus
import dbus.service
import threading
import time

# from ..utility.cmd_interface import CMD_INTERFACE

logger = logging.getLogger(__name__)

class DBusBl654(dbus.service.Object):
    DBUS_OBJECT = "/org/navico/HubUtility/bl654"
    DBUS_INTERFACE = "org.navico.HubUtility.bl654"

    def __init__(self, bus):
        bus_name = dbus.service.BusName(self.DBUS_INTERFACE, bus=bus)
        super().__init__(bus_name, self.DBUS_OBJECT)

    @dbus.service.signal(DBUS_INTERFACE, signature='s')
    def ota_progress(self, message): pass

    @dbus.service.signal(DBUS_INTERFACE, signature='s')
    def ota_error(self, message): pass

    @dbus.service.signal(DBUS_INTERFACE, signature='s')
    def ota_complete(self, message): pass

    @dbus.service.method(DBUS_INTERFACE, in_signature="", out_signature="s")
    def version(self):
        return "v1"

    @dbus.service.method(DBUS_INTERFACE, in_signature="s", out_signature="s")
    def initiate_ota(self, filepath):
        logger.info(f"DBusBl654.transfer called with: {filepath}")
        threading.Thread(target=self._handle_ota_transfer, args=(filepath,)).start()
        return "Starting OTA transfer..."

    def _handle_ota_transfer(self, filepath):
        try:
            # return CMD_INTERFACE["bl"](f"OTA_TRANSFER/{filepath}")
            self.ota_progress("OTA transfer started...")
            time.sleep(3)
            self.ota_progress("1/4 files transferred")
            time.sleep(3)
            self.ota_progress("2/4 files transferred")
            time.sleep(3)
            self.ota_progress("3/4 files transferred")
            time.sleep(3)
            self.ota_progress("4/4 files transferred")
            time.sleep(3)
            self.ota_complete("OTA transfer completed successfully")
        except Exception as e:
            logger.error(f"OTA transfer failed: {e}")
            self.ota_error(f"OTA error: {e}")
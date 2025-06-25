import logging
import dbus
import dbus.service

# from ..utility.cmd_interface import CMD_INTERFACE

logger = logging.getLogger(__name__)

class DBusBl654(dbus.service.Object):
    DBUS_OBJECT = "/org/navico/HubUtility/bl654"
    DBUS_INTERFACE = "org.navico.HubUtility.bl654"

    def __init__(self, bus):
        bus_name = dbus.service.BusName(self.DBUS_INTERFACE, bus=bus)
        super().__init__(bus_name, self.DBUS_OBJECT)

    @dbus.service.method(DBUS_INTERFACE, in_signature="", out_signature="s")
    def version(self):
        return "v1"

    @dbus.service.method(DBUS_INTERFACE, in_signature="s", out_signature="s")
    def ota_transfer(self, filepath):
        logger.info(f"DBusBl654.transfer called with: {filepath}")
        # return CMD_INTERFACE["bl"](f"OTA_TRANSFER/{filepath}")
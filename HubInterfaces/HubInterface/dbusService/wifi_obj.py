import logging
import dbus
import dbus.service

from ..utility.cmd_interface import CMD_INTERFACE

logger = logging.getLogger(__name__)

class DBusWiFi(dbus.service.Object):
    DBUS_OBJECT = "/org/navico/HubInterface/wifi"
    DBUS_INTERFACE = "org.navico.HubInterface.wifi"

    def __init__(self, bus):
        bus_name = dbus.service.BusName(self.DBUS_INTERFACE, bus=bus)
        super().__init__(bus_name, self.DBUS_OBJECT)

    @dbus.service.method(DBUS_INTERFACE, in_signature="", out_signature="s")
    def status(self):
        return CMD_INTERFACE["wifi"]("status")

    @dbus.service.method(DBUS_INTERFACE, in_signature="", out_signature="s")
    def enable(self):
        return CMD_INTERFACE["wifi"]("enable")

    @dbus.service.method(DBUS_INTERFACE, in_signature="", out_signature="s")
    def disable(self):
        return CMD_INTERFACE["wifi"]("disable")

    @dbus.service.method(DBUS_INTERFACE, in_signature="", out_signature="s")
    def list(self):
        return CMD_INTERFACE["wifi"]("list")

    @dbus.service.method(DBUS_INTERFACE, in_signature="", out_signature="s")
    def restart(self):
        return CMD_INTERFACE["wifi"]("restart")

    @dbus.service.method(DBUS_INTERFACE, in_signature="", out_signature="s")
    def version(self):
        return "Hello"

    @dbus.service.method(DBUS_INTERFACE, in_signature="ss", out_signature="s")
    def configure(self, ssid, password):
        logger.debug(f"configure_wifi called with SSID: {ssid}, Password: {password}")
        return CMD_INTERFACE["wificonfig"](ssid, password)

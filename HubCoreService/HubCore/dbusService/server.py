import logging
import dbus
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib

from .wifi_obj import DBusWiFi
from .bl654_obj import DBusBl654

logger = logging.getLogger(__name__)

class DBusServer(dbus.service.Object):
    bus = None
    loop = None
    DBUS_OBJECT = "/org/navico/HubUtility"
    DBUS_INTERFACE = "org.navico.HubUtility"
    DBUS_SERVER_VERSION = "1.0.0"

    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()
        bus_name = dbus.service.BusName(self.DBUS_INTERFACE, bus=self.bus)
        super().__init__(bus_name, self.DBUS_OBJECT)
        self.wifi_object = DBusWiFi(self.bus)
        self.bl654_object = DBusBl654(self.bus)

        self.loop = GLib.MainLoop()

    def start(self):
        self.loop.run()

    def stop(self):
        if self.loop:
            self.loop.quit()
            self.loop = None

    def __del__(self):
        self.stop()

    @dbus.service.method(DBUS_INTERFACE, in_signature="", out_signature="s")
    def version(self):
        return self.DBUS_SERVER_VERSION

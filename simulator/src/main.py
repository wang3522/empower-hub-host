import logging
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

DBusGMainLoop(set_as_default=True)

OPATH = "/org/navico/CzoneCpp"
IFACE = "org.navico.CzoneCpp"
BUS_NAME = "org.navico.CzoneCpp"


class N2KDBusSimulator(dbus.service.Object):
    logger: logging.Logger

    def __init__(self):
        bus = dbus.SystemBus()
        bus.request_name(BUS_NAME)
        bus_name = dbus.service.BusName(BUS_NAME, bus=bus)
        dbus.service.Object.__init__(self, bus_name, OPATH)

    @dbus.service.method(dbus_interface=IFACE, in_signature="", out_signature="s")
    def GetDevices(self):
        return '[{"id": "dc.1", "type": "dc"}, {"id": "ac.12", "type": "dc"}]'

    @dbus.service.method(dbus_interface=IFACE, in_signature="", out_signature="s")
    def GetConfig(self):
        return "[]"

    @dbus.service.method(dbus_interface=IFACE, in_signature="s", out_signature="s")
    def GetState(self, state: str):
        return '{"voltage": 12, "current": 2, "stateOfCharge": 75, "temperature": 23, "capacityRemaining": 1000}'


class Main:
    logger = logging.getLogger("DBUS N2k Simulator")

    def __init__(self):
        self.logger.setLevel(logging.INFO)
        log_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        log_handler.setFormatter(formatter)
        self.logger.addHandler(log_handler)

    def run(self):
        service = N2KDBusSimulator()
        loop = GLib.MainLoop()
        self.logger.info("Service started. Press Ctrl+C to exit.")
        try:
            loop.run()
        except KeyboardInterrupt:
            self.logger.info("Service stopped.")


def main():
    main = Main()
    main.run()


if __name__ == "__main__":
    main()

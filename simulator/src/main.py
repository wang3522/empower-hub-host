import json
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
    get_devices_count: int
    get_state_count: int
    device_list: list

    def __init__(self):
        self.get_devices_count = 0
        self.get_state_count = 0
        self.device_list = [
            {"id": "dc.1", "type": "dc"},
            {"id": "tank.1", "type": "tank"},
            {"id": "engine.1", "type": "engine"},
        ]
        bus = dbus.SystemBus()
        bus.request_name(BUS_NAME)
        bus_name = dbus.service.BusName(BUS_NAME, bus=bus)
        dbus.service.Object.__init__(self, bus_name, OPATH)

    @dbus.service.method(dbus_interface=IFACE, in_signature="", out_signature="s")
    def GetDevices(self):
        self.get_devices_count += 1
        if self.get_devices_count == 5:
            self.device_list.append({"id": "ac.1", "type": "ac"})
        return json.dumps(self.device_list)

    @dbus.service.method(dbus_interface=IFACE, in_signature="", out_signature="s")
    def GetConfig(self):
        return "[]"

    @dbus.service.method(dbus_interface=IFACE, in_signature="s", out_signature="s")
    def GetState(self, id: str):
        self.get_state_count += 1
        if self.get_state_count < 10:
            if id == "dc.1":
                return '{"voltage": 12, "current": 2, "stateOfCharge": 75, "temperature": 23, "capacityRemaining": 1000}'
            elif id == "ac.1":
                return '{"voltage": 11.32, "current": 3.4, "power": 38.48, "frequency": 40}'
            elif id == "tank.1":
                return '{"level": 200, "levelPercent": 87}'
            elif id == "engine.1":
                return '{"engineState": "dead", "speed": 0, "oilPressure": 50, "oilTemperature": 80, "coolantTemperature": 90, "fuelLevel": 50, "engineHours": 1000}'
        elif self.get_state_count < 20:
            if id == "dc.1":
                return '{"voltage": 13.5, "current": 4.1, "stateOfCharge": 62, "temperature": 27, "capacityRemaining": 850}'
            elif id == "ac.1":
                return '{"voltage": 10.95, "current": 2.8, "power": 30.66, "frequency": 50}'
            elif id == "tank.1":
                return '{"level": 150, "levelPercent": 65}'
            elif id == "engine.1":
                return '{"engineState": "running", "speed": 3200, "oilPressure": 45, "oilTemperature": 75, "coolantTemperature": 85, "fuelLevel": 40, "engineHours": 1200}'
        else:
            if id == "dc.1":
                return '{"voltage": 14.2, "current": 5.0, "stateOfCharge": 55, "temperature": 29, "capacityRemaining": 700}'
            elif id == "ac.1":
                return '{"voltage": 12.10, "current": 3.1, "power": 37.51, "frequency": 60}'
            elif id == "tank.1":
                return '{"level": 100, "levelPercent": 43}'
            elif id == "engine.1":
                return '{"engineState": "idle", "speed": 900, "oilPressure": 40, "oilTemperature": 70, "coolantTemperature": 80, "fuelLevel": 30, "engineHours": 1400}'


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

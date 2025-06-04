import json
import logging
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from simulator.models.config import CONFIG_JSON_STRING

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
            {"Id": "dc.1", "Type": "dc"},
            {"Id": "tank.1", "Type": "tank"},
            {"Id": "ac.1", "Type": "ac"},
        ]
        bus = dbus.SystemBus()
        bus.request_name(BUS_NAME)
        bus_name = dbus.service.BusName(BUS_NAME, bus=bus)
        dbus.service.Object.__init__(self, bus_name, OPATH)

    @dbus.service.method(dbus_interface=IFACE, in_signature="", out_signature="s")
    def GetDevices(self):
        self.get_devices_count += 1
        if self.get_devices_count == 15:
            self.device_list.append({"Id": "engine.1", "Type": "engine"})
        return json.dumps(self.device_list)

    @dbus.service.method(dbus_interface=IFACE, in_signature="", out_signature="s")
    def GetConfigAll(self):
        return CONFIG_JSON_STRING

    @dbus.service.method(dbus_interface=IFACE, in_signature="s", out_signature="s")
    def GetState(self, id: str):
        self.get_state_count += 1
        if self.get_state_count < 80:
            if id == "dc.1":
                return '{"voltage": 12, "current": 2, "stateOfCharge": 75, "temperature": 23, "capacityRemaining": 1000}'
            elif id == "ac.1":
                return '{"voltage": 11.32, "current": 3.4, "power": 38.48, "frequency": 40}'
            elif id == "tank.1":
                return '{"level": 200, "levelPercent": 87}'
            elif id == "engine.1":
                return '{"engineState": "dead", "speed": 0, "oilPressure": 50, "oilTemperature": 80, "coolantTemperature": 90, "fuelLevel": 50, "engineHours": 1000}'
        elif self.get_state_count < 120:
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
                return '{"engineState": "crank", "speed": 900, "oilPressure": 40, "oilTemperature": 70, "coolantTemperature": 80, "fuelLevel": 30, "engineHours": 1400}'

    @dbus.service.method(dbus_interface=IFACE, in_signature="s", out_signature="s")
    def GetConfig(self, type: str):
        if type == "Engines":
            return '{"Engines":[{"DisplayType":41,"Id":0,"NameUTF8":"Starboard Engine","Instance":{"Enabled":true,"Instance":0},"SoftwareId":"Software_Id_0","CalibrationId":"CalibrationId_0","SerialNumber":"","ECUSerialNumber":"","EngineType":1}]}'

    @dbus.service.method(dbus_interface=IFACE, in_signature="s", out_signature="s")
    def GetSetting(self, type: str):
        if type == "FactoryData":
            return '{"FactoryDataSettings":{"SerialNumber":"1234567890","RTFirmwareVersion":"1.0.0","MenderArtifactInfo":"1.2.3"}}'

        elif type == "Config":
            return '{"ConfigId":726930,"ConfigVersion":0,"ConfigFileVersion":6,"ConfigName":"test-bench-qa-ui-rel"}'

    @dbus.service.method(dbus_interface=IFACE, in_signature="", out_signature="s")
    def GetCategories(self):
        # Fill in below with categories
        return '{"Items":[{"NameUTF8":"Pumps","Index":12},{"NameUTF8":"Lighting","Index":10},{"NameUTF8":"Vessel Critical","Index":1},{"NameUTF8":"Electronics","Index":3},{"NameUTF8":"Power","Index":14},{"NameUTF8":"Navigation","Index":2},{"NameUTF8":"Communications","Index":5},{"NameUTF8":"Refrigeration","Index":15},{"NameUTF8":"Entertainment","Index":16},{"NameUTF8":"Accessories","Index":6},{"NameUTF8":"Fans/Ventilation","Index":9},{"NameUTF8":"House/Habitat"},{"NameUTF8":"Engine Management","Index":8},{"NameUTF8":"Vessel Management","Index":11},{"NameUTF8":"Propulsion Management","Index":13},{"NameUTF8":"24-Hour Circuits","Index":4},{"NameUTF8":"Indicators and Alarms","Index":7},{"NameUTF8":"Climate","Index":17},{"NameUTF8":"Appliances","Index":18},{"NameUTF8":"Shore Fuse","Index":28},{"NameUTF8":"Bilge Pumps","Index":29},{"NameUTF8":"Audio","Index":23},{"NameUTF8":"Fuel","Index":24},{"NameUTF8":"Water Tanks","Index":25},{"Index":26},{"Index":27},{"NameUTF8":"Other","Index":19}]}'


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

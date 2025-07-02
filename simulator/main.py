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
            {"Id": "DC.6", "Type": "dc"},
            {"Id": "Tank.17", "Type": "tank"},
            {"Id": "Circuit.77", "Type": "circuit"},
            {"Id": "Tank.81", "Type": "tank"},
            {"Id": "Engine.0", "Type": "engine"},
            {"Id": "Circuit.43", "Type": "circuit"},
            {"Id": "GNSS.128", "Type": "gnss"},
            {"Id": "InverterCharger.0", "Type": "inverter_charger"},
            {"Id": "AC.1", "Type": "ac"},
        ]
        bus = dbus.SystemBus()
        bus.request_name(BUS_NAME)
        bus_name = dbus.service.BusName(BUS_NAME, bus=bus)
        dbus.service.Object.__init__(self, bus_name, OPATH)

    @dbus.service.method(dbus_interface=IFACE, in_signature="", out_signature="s")
    def GetDevices(self):

        return json.dumps(self.device_list)

    @dbus.service.method(dbus_interface=IFACE, in_signature="", out_signature="s")
    def GetConfigAll(self):
        return CONFIG_JSON_STRING

    @dbus.service.method(dbus_interface=IFACE, in_signature="s", out_signature="s")
    def GetState(self, id: str):
        self.get_state_count += 1
        if self.get_state_count < 160:
            if id == "DC.6":
                return '{"ComponentStatus": "Connected", "Voltage": 12, "Current": 2, "StateOfCharge": 75, "Temperature": 23, "CapacityRemaining": 1000, "TimeRemaining": 120, "TimeToCharge": 60}'
            elif id == "Tank.17":
                return (
                    '{"ComponentStatus": "Connected", "Level": 200, "LevelPercent": 87}'
                )
            elif id == "AC.1":
                return '{"Instance": 1, "AClines": {"1": {"Instance": 1, "Line": 1, "ComponentStatus": "Connected", "Voltage": 230.0, "Current": 10.5, "Frequency": 50.0, "Power": 2400.0}, "2": {"Instance": 2, "Line": 2, "ComponentStatus": "Connected", "Voltage": 230.0, "Current": 9.8, "Frequency": 50.0, "Power": 2250.0}}}'
            elif id == "Tank.81":
                return (
                    '{"ComponentStatus": "Connected", "Level": 300, "LevelPercent": 92}'
                )
            elif id == "Engine.0":
                return '{"ComponentStatus": "Connected", "EngineState": 1, "Speed": 0, "OilPressure": 50, "OilTemperature": 80, "FuelLevel": 50, "EngineHours": 1000}'
            elif id == "Circuit.77":
                return '{"ComponentStatus": "Connected", "Current": 1.5, "Voltage": 12.5, "Level": 100}'
            elif id == "Circuit.43":
                return '{"ComponentStatus": "Disconnected", "Current": 2.5, "Voltage": 8.5, "Level": 100}'
            elif id == "GNSS.128":
                return '{"ComponentStatus": "Connected", "FixType": "2D Fix", "LatitudeDeg": 8.5, "LongitudeDeg": 100, "Sog": 5.5}'
            elif id == "InverterCharger.0":
                return '{"ComponentStatus": "Connected", "InverterState": "Inverting"}'
        elif self.get_state_count < 320:
            if id == "DC.6":
                return '{"ComponentStatus": "Connected", "Voltage": 13.5, "Current": 4.1, "StateOfCharge": 62, "Temperature": 27, "CapacityRemaining": 850, "TimeRemaining": 150, "TimeToCharge": 30}'
            elif id == "Tank.17":
                return (
                    '{"ComponentStatus": "Connected", "Level": 150, "LevelPercent": 65}'
                )
            elif id == "Tank.81":
                return (
                    '{"ComponentStatus": "Connected", "Level": 250, "LevelPercent": 78}'
                )
            elif id == "Engine.0":
                return '{"ComponentStatus": "Connected", "EngineState": 3, "Speed": 3200, "OilPressure": 45, "CoolantTemperature": 85, "FuelLevel": 40, "EngineHours": 1200}'
            elif id == "Circuit.77":
                return '{"ComponentStatus": "Connected", "Current": 2.5, "Voltage": 9.5, "Level": 0}'
            elif id == "Circuit.43":
                return '{"ComponentStatus": "Connected", "Current": 2.5, "Voltage": 8.5, "Level": 100}'
            elif id == "GNSS.128":
                return '{"ComponentStatus": "Connected", "FixType": "3D Fix", "LatitudeDeg": 10, "LongitudeDeg": 500, "Sog": 10}'
            elif id == "InverterCharger.0":
                return '{"ComponentStatus": "Connected","InverterState": "Charging"}'
            elif id == "AC.1":
                return '{"Instance": 1, "AClines": {"1": {"Instance": 1, "Line": 1, "ComponentStatus": "Connected", "Voltage": 230.0, "Current": 10.5, "Frequency": 50.0, "Power": 2400.0}, "2": {"Instance": 2, "Line": 2, "ComponentStatus": "Connected", "Voltage": 230.0, "Current": 9.8, "Frequency": 50.0, "Power": 2250.0}}}'
        elif self.get_state_count < 480:
            if id == "DC.6":
                return '{"ComponentStatus": "Connected", "Voltage": 14.2, "Current": 5.0, "StateOfCharge": 55, "Temperature": 29, "CapacityRemaining": 700, "TimeRemaining": 200, "TimeToCharge": 40}'
            elif id == "Tank.17":
                return '{"ComponentStatus": "Connected", "Level": 100.1, "LevelPercent": 43}'
            elif id == "Tank.81":
                return (
                    '{"ComponentStatus": "Connected", "Level": 200, "LevelPercent": 65}'
                )
            elif id == "Engine.0":
                return '{"ComponentStatus": "Connected", "EngineState": 1, "Speed": 900, "OilPressure": 40, "CoolantTemperature": 80, "FuelLevel": 30, "EngineHours": 1400}'
            elif id == "Circuit.77":
                return '{"ComponentStatus": "Connected", "Current": 3.5, "Voltage": 13.5, "Level": 100}'
            elif id == "Circuit.43":
                return '{"ComponentStatus": "Disconnected", "Current": 1.8, "Voltage": 10.5, "Level": 0}'
            elif id == "GNSS.128":
                return '{"ComponentStatus": "Connected", "FixType": "3D Fix", "LatitudeDeg": 100, "LongitudeDeg": 10, "Sog": 20}'
            elif id == "InverterCharger.0":
                return (
                    '{"ComponentStatus": "Connected", "InverterState": "EnergySaving"}'
                )
            elif id == "AC.1":
                return '{"Instance": 1, "AClines": {"1": {"Instance": 1, "Line": 1, "ComponentStatus": "Connected", "Voltage": 230.0, "Current": 10.5, "Frequency": 50.0, "Power": 2400.0}, "2": {"Instance": 2, "Line": 2, "ComponentStatus": "Connected", "Voltage": 230.0, "Current": 9.8, "Frequency": 50.0, "Power": 2250.0}}}'
        else:
            if id == "DC.6":
                return '{"ComponentStatus": "Disconnected", "Voltage": 14.5, "Current": 6, "StateOfCharge": 55, "Temperature": 29.5, "CapacityRemaining": 700.5555, "TimeRemaining": 200, "TimeToCharge": 40}'
            elif id == "Tank.17":
                return '{"ComponentStatus": "Disconnected", "Level": 100.000002, "LevelPercent": 43}'
            elif id == "Tank.81":
                return '{"ComponentStatus": "Disconnected", "Level": 200.09, "LevelPercent": 65}'
            elif id == "Engine.0":
                return '{"ComponentStatus": "Disconnected", "EngineState": 1, "Speed": 800, "OilPressure": 40000, "CoolantPressure": 44444, "CoolantTemperature": 300, "FuelLevel": 3000, "EngineHours": 2000}'
            elif id == "Circuit.77":
                return '{"ComponentStatus": "Disconnected", "Current": 9.5666666, "Voltage": 13.5, "Level": 100}'
            elif id == "Circuit.43":
                return '{"ComponentStatus": "Disconnected", "Current": 5.8256326, "Voltage": 10.5, "Level": 0}'
            elif id == "GNSS.128":
                return '{"ComponentStatus": "Disconnected", "FixType": "3D Fix", "LatitudeDeg": 100.44444444444444444, "LongitudeDeg": 10.44444444444, "Sog": 20}'
            elif id == "InverterCharger.0":
                return '{"ComponentStatus": "Disconnected", "InverterState": "EnergySaving"}'
            elif id == "AC.1":
                return '{"Instance": 1, "AClines": {"1": {"Instance": 1, "Line": 1, "ComponentStatus": "Connected", "Voltage": 230.0, "Current": 10.5, "Frequency": 50.0, "Power": 2400.0}, "2": {"Instance": 2, "Line": 2, "ComponentStatus": "Connected", "Voltage": 230.0, "Current": 9.8, "Frequency": 50.0, "Power": 2250.0}}}'
        return "{}"

    @dbus.service.method(dbus_interface=IFACE, in_signature="s", out_signature="s")
    def GetConfig(self, type: str):
        if type == "Engines":
            return '{"Engines":[{"DisplayType":41,"Id":0,"NameUTF8":"Starboard Engine","Instance":{"Enabled":true,"Instance":0},"SoftwareId":"Software_Id_0","CalibrationId":"CalibrationId_0","SerialNumber":"","ECUSerialNumber":"","EngineType":1}]}'
        return ""

    @dbus.service.method(dbus_interface=IFACE, in_signature="s", out_signature="s")
    def GetSetting(self, type: str):
        if type == "FactoryData":
            return '{"FactoryDataSettings":{"SerialNumber":"1234567890","RTFirmwareVersion":"1.0.0","MenderArtifactInfo":"1.2.3"}}'

        elif type == "Config":
            return '{"ConfigId":726930,"ConfigVersion":0,"ConfigFileVersion":6,"ConfigName":"test-bench-qa-ui-rel"}'
        return ""

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

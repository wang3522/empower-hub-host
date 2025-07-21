import json
import logging
import dbus
import dbus.service
import platform
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from models.config import CONFIG_JSON_STRING

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
            {"Id": "Circuit.141", "Type": "circuit"},
            {"Id": "Tank.81", "Type": "tank"},
            {"Id": "Engine.0", "Type": "engine"},
            {"Id": "Circuit.114", "Type": "circuit"},
            {"Id": "GNSS.128", "Type": "gnss"},
            {"Id": "InverterCharger.0", "Type": "inverter_charger"},
            {"Id": "AC.5", "Type": "ac"},
            {"Id": "AC.1", "Type": "ac"},
            {"Id": "DC.7", "Type": "dc"},
            {"Id": "Circuit.135", "Type": "circuit"},
            {"Id": "Circuit.138", "Type": "circuit"},
        ]
        # bus = dbus.SystemBus()
        bus = dbus.SessionBus() if platform.system() == "Darwin" else dbus.SystemBus()
        bus.request_name(BUS_NAME)
        bus_name = dbus.service.BusName(BUS_NAME, bus=bus)
        dbus.service.Object.__init__(self, bus_name, OPATH)
        self.get_config_fail_count = 0
        self.control_fail_count = 0

    @dbus.service.method(dbus_interface=IFACE, in_signature="", out_signature="s")
    def GetDevices(self):

        return json.dumps(self.device_list)

    @dbus.service.method(dbus_interface=IFACE, in_signature="", out_signature="s")
    def GetConfigAll(self):
        if self.get_config_fail_count < 5:
            self.get_config_fail_count += 1
            raise dbus.exceptions.DBusException("DBus call failed")
        return CONFIG_JSON_STRING

    @dbus.service.method(dbus_interface=IFACE, in_signature="s", out_signature="s")
    def GetState(self, id: str):
        self.get_state_count += 1
        if self.get_state_count < 80:
            if id == "DC.6":
                return '{"ComponentStatus": "Disconnected", "Voltage": 12.0, "Current": 2.0, "StateOfCharge": 75, "Temperature": 23.11, "CapacityRemaining": 1000.0, "TimeRemaining": 120, "TimeToCharge": 60}'
            elif id == "DC.7":
                return '{"ComponentStatus": "Connected", "Voltage": 11.0, "Current": 12.0, "StateOfCharge": 13, "Temperature": 14.11, "CapacityRemaining": 15555.0, "TimeRemaining": 1444, "TimeToCharge": 124}'
            elif id == "Tank.17":
                return (
                    '{"ComponentStatus": "Connected", "Level": 200, "LevelPercent": 87}'
                )
            elif id == "AC.1":
                return '{"Instance": 1, "AClines": {"1": {"Instance": 1, "Line": 1, "ComponentStatus": "Connected", "Voltage": 11.0, "Current": 10.5, "Frequency": 50.0, "Power": 2400.0}, "2": {"Instance": 2, "Line": 2, "ComponentStatus": "Disconnected", "Voltage": 11.0, "Current": 59.8, "Frequency": 50.0, "Power": 5555.0}}}'
            elif id == "Tank.81":
                return (
                    '{"ComponentStatus": "Connected", "Level": 300, "LevelPercent": 92}'
                )
            elif id == "Engine.0":
                return '{"ComponentStatus": "Connected", "EngineState": 1, "Speed": 0, "CoolantPressure": 50, "CoolantTemperature": 80.0, "FuelLevel": 50, "EngineHours": 1000}'
            elif id == "Circuit.141":
                return '{"IsOffline": false, "Current": 1.5, "Voltage": 12.5, "Level": 100}'
            elif id == "Circuit.114":
                return (
                    '{"IsOffline": true, "Current": 2.5, "Voltage": 8.5, "Level": 100}'
                )
            elif id == "GNSS.128":
                return '{"ComponentStatus": "Connected", "FixType": "2D Fix", "LatitudeDeg": 8.5, "LongitudeDeg": 100.0, "Sog": 5.5}'
            elif id == "InverterCharger.0":
                return '{"ComponentStatus": "Connected", "InverterEnable": 0, "ChargerEnable": 0, "InverterState": "Inverting", "ChargerState": "Float"}'
            elif id == "AC.5":
                return '{"Instance": 1, "AClines": {"1": {"Instance": 1, "Line": 1, "ComponentStatus": "Connected", "Voltage": 1110.0, "Current": 11.5, "Frequency": 11.0, "Power": 1111.0}, "2": {"Instance": 2, "Line": 2, "ComponentStatus": "Connected", "Voltage": 111.0, "Current": 11.8, "Frequency": 111.0, "Power": 111.0}}}'

        if self.get_state_count >= 80:
            if id == "DC.6":
                return '{"ComponentStatus": "Connected", "Voltage": 12.0, "Current": 2.0, "StateOfCharge": 75, "Temperature": 23, "CapacityRemaining": 1000, "TimeRemaining": 120, "TimeToCharge": 60}'
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
                return '{"ComponentStatus": "Connected", "EngineState": 1, "Speed": 0, "OilPressure": 50, "CoolantTemperature": 80.0, "FuelLevel": 50, "EngineHours": 1000}'
            elif id == "Circuit.141":
                return '{"ComponentStatus": "Connected", "Current": 1234.1, "Voltage": 12.5, "Level": 0}'
            elif id == "Circuit.114":
                return '{"ComponentStatus": "Disconnected", "Current": 1234.1, "Voltage": 12.5, "Level": 100}'
            elif id == "Circuit.135":
                return '{"ComponentStatus": "Disconnected", "Current": 2.5, "Voltage": 8.5, "Level": 100}'
            elif id == "Circuit.138":
                return '{"ComponentStatus": "Disconnected", "Current": 2.5, "Voltage": 8.5, "Level": 100}'
            elif id == "GNSS.128":
                return '{"ComponentStatus": "Connected", "FixType": "2D Fix", "LatitudeDeg": 8.5, "LongitudeDeg": 100.0, "Sog": 5.5}'
            elif id == "InverterCharger.0":
                return '{"ComponentStatus": "Connected", "InverterState": "Inverting"}'

        return "{}"

    @dbus.service.method(dbus_interface=IFACE, in_signature="s", out_signature="s")
    def GetConfig(self, type: str):
        if type == "Engines":
            return '{"Engines":[{"DisplayType":41,"Id":0,"NameUTF8":"Starboard Engine","Instance":{"Enabled":true,"Instance":0},"SoftwareId":"Software_Id_0","CalibrationId":"CalibrationId_0","SerialNumber":"TESTSERIAL","ECUSerialNumber":"TESTECU","EngineType":1}]}'
        elif type == "NonVisibleCircuits":
            return (
                '{"Circuits":['
                '{"DisplayType":1,"Id":{"Valid":true,"Value":200},"NameUTF8":"","SingleThrowId":{"Enabled":true,"Id":143},'
                '"SequentialNamesUTF8":[{"Name":""},{"Name":""},{"Name":""},{"Name":""},{"Name":""},{"Name":""},{"Name":""},{"Name":""},{"Name":""},{"Name":""},{"Name":""},{"Name":""},{"Name":""},{"Name":""},{"Name":""},{"Name":""}],'
                '"HasComplement":true,"DisplayCategories":2101248,"ConfirmDialog":0,"VoltageSource":{"Enabled":true,"Instance":253},"CircuitType":0,"SwitchType":1,"MinLevel":0,"MaxLevel":1000,"NonVisibleCircuit":false,'
                '"Dimstep":25,"Step":0,"Dimmable":false,"LoadSmoothStart":0,"SequentialStates":1,"ControlId":65,'
                '"CircuitLoads":[{"DisplayType":38,"Id":167,"NameUTF8":"Fresh Water Pump","ChannelAddress":16437,"FuseLevel":0,"RunningCurrent":0,"SystemOnCurrent":0,"ForceAcknowledgeOn":false,"Level":1000,"ControlType":0,"IsSwitchedModule":false}],'
                '"Categories":[{"NameUTF8":"Pumps","Enabled":true,"Index":0},{"NameUTF8":"Lighting","Enabled":false,"Index":0},{"NameUTF8":"Vessel Critical","Enabled":false,"Index":0},{"NameUTF8":"Electronics","Enabled":false,"Index":0},{"NameUTF8":"Power","Enabled":false,"Index":0},{"NameUTF8":"Navigation","Enabled":false,"Index":0},{"NameUTF8":"Communications","Enabled":false,"Index":0},{"NameUTF8":"Refrigeration","Enabled":false,"Index":0},{"NameUTF8":"Entertainment","Enabled":false,"Index":0},{"NameUTF8":"Accessories","Enabled":false,"Index":0},{"NameUTF8":"Fans/Ventilation","Enabled":false,"Index":0},{"NameUTF8":"House/Habitat","Enabled":false,"Index":0},{"NameUTF8":"Engine Management","Enabled":false,"Index":0},{"NameUTF8":"Vessel Management","Enabled":false,"Index":0},{"NameUTF8":"Propulsion Management","Enabled":false,"Index":0},{"NameUTF8":"24-Hour Circuits","Enabled":false,"Index":0},{"NameUTF8":"Indicators and Alarms","Enabled":false,"Index":0},{"NameUTF8":"Climate","Enabled":false,"Index":0},{"NameUTF8":"Appliances","Enabled":false,"Index":0},{"NameUTF8":"Shore Fuse","Enabled":false,"Index":0},{"NameUTF8":"Bilge Pumps","Enabled":false,"Index":0},{"NameUTF8":"Audio","Enabled":false,"Index":0},{"NameUTF8":"Fuel","Enabled":false,"Index":0},{"NameUTF8":"Water Tanks","Enabled":false,"Index":0},{"NameUTF8":"","Enabled":false,"Index":0},{"NameUTF8":"","Enabled":false,"Index":0},{"NameUTF8":"Other","Enabled":false,"Index":0}],'
                '"DCCircuit":true,"HasDCCircuit":true,"ACCircuit":false,"HasACCircuit":true,"ModeIcon":0,"HasModeIcon":false,"PrimaryCircuitId":65535,"HasPrimaryCircuitId":true,"RemoteVisibility":1,"HasRemoteVisibility":true,"SwitchString":"","HasSwitchString":true,"SystemsOnAnd":false,"HasSystemsOnAnd":true},'
                '{"DisplayType":1,"Id":{"Valid":true,"Value":203},"NameUTF8":"","SingleThrowId":{"Enabled":true,"Id":143},'
                '"SequentialNamesUTF8":[{"Name":""},{"Name":""},{"Name":""},{"Name":""},{"Name":""},{"Name":""},{"Name":""},{"Name":""},{"Name":""},{"Name":""},{"Name":""},{"Name":""},{"Name":""},{"Name":""},{"Name":""},{"Name":""}],'
                '"HasComplement":true,"DisplayCategories":2101248,"ConfirmDialog":0,"VoltageSource":{"Enabled":true,"Instance":253},"CircuitType":0,"SwitchType":1,"MinLevel":0,"MaxLevel":1000,"NonVisibleCircuit":false,'
                '"Dimstep":25,"Step":0,"Dimmable":false,"LoadSmoothStart":0,"SequentialStates":1,"ControlId":67,'
                '"CircuitLoads":[{"DisplayType":38,"Id":167,"NameUTF8":"Fresh Water Pump","ChannelAddress":16437,"FuseLevel":0,"RunningCurrent":0,"SystemOnCurrent":0,"ForceAcknowledgeOn":false,"Level":1000,"ControlType":0,"IsSwitchedModule":false}],'
                '"Categories":[{"NameUTF8":"Pumps","Enabled":true,"Index":0},{"NameUTF8":"Lighting","Enabled":false,"Index":0},{"NameUTF8":"Vessel Critical","Enabled":false,"Index":0},{"NameUTF8":"Electronics","Enabled":false,"Index":0},{"NameUTF8":"Power","Enabled":false,"Index":0},{"NameUTF8":"Navigation","Enabled":false,"Index":0},{"NameUTF8":"Communications","Enabled":false,"Index":0},{"NameUTF8":"Refrigeration","Enabled":false,"Index":0},{"NameUTF8":"Entertainment","Enabled":false,"Index":0},{"NameUTF8":"Accessories","Enabled":false,"Index":0},{"NameUTF8":"Fans/Ventilation","Enabled":false,"Index":0},{"NameUTF8":"House/Habitat","Enabled":false,"Index":0},{"NameUTF8":"Engine Management","Enabled":false,"Index":0},{"NameUTF8":"Vessel Management","Enabled":false,"Index":0},{"NameUTF8":"Propulsion Management","Enabled":false,"Index":0},{"NameUTF8":"24-Hour Circuits","Enabled":false,"Index":0},{"NameUTF8":"Indicators and Alarms","Enabled":false,"Index":0},{"NameUTF8":"Climate","Enabled":false,"Index":0},{"NameUTF8":"Appliances","Enabled":false,"Index":0},{"NameUTF8":"Shore Fuse","Enabled":false,"Index":0},{"NameUTF8":"Bilge Pumps","Enabled":false,"Index":0},{"NameUTF8":"Audio","Enabled":false,"Index":0},{"NameUTF8":"Fuel","Enabled":false,"Index":0},{"NameUTF8":"Water Tanks","Enabled":false,"Index":0},{"NameUTF8":"","Enabled":false,"Index":0},{"NameUTF8":"","Enabled":false,"Index":0},{"NameUTF8":"Other","Enabled":false,"Index":0}],'
                '"DCCircuit":true,"HasDCCircuit":true,"ACCircuit":false,"HasACCircuit":true,"ModeIcon":0,"HasModeIcon":false,"PrimaryCircuitId":65535,"HasPrimaryCircuitId":true,"RemoteVisibility":1,"HasRemoteVisibility":true,"SwitchString":"","HasSwitchString":true,"SystemsOnAnd":false,"HasSystemsOnAnd":true}'
                "]}"
            )
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

    @dbus.service.method(dbus_interface=IFACE, in_signature="s", out_signature="s")
    def Control(self, control_request: str):
        if self.control_fail_count < 11:
            self.control_fail_count += 1
            raise dbus.exceptions.DBusException("DBus call failed")
        try:
            control_json = json.loads(control_request)
            if "Type" in control_json and control_json["Type"] in (
                "Activate",
                "Release",
                "SetLevel",
            ):
                return '{"Result": "Ok"}'
            else:
                return '{"Result": "Error", "Message": "Unknown Type"}'
        except Exception as e:
            return '{"Result": "Error", "Message": "Invalid JSON"}'


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

import json
import logging
import time
import dbus
import dbus.service
import platform
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from models.config import CONFIG_JSON_STRING

DBusGMainLoop(set_as_default=True)

OPATH = "/org/navico/HubN2K"
IFACE = "org.navico.HubN2K.czone"
BUS_NAME = "org.navico.HubN2K"


class N2KDBusSimulator(dbus.service.Object):
    logger: logging.Logger
    get_devices_count: int
    get_state_count: int
    device_list: list

    def __init__(self):

        self.get_devices_count = 0
        self.get_state_count = 0
        self.initial = True
        self.circuit_state_1 = json.dumps(
            {"IsOffline": True, "Current": 2.5, "Voltage": 8.5, "Level": 0}
        )

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

        # Retry loop for DBus bus and service registration
        while True:
            try:
                if platform.system() == "Darwin":
                    bus = dbus.SessionBus()
                else:
                    bus = dbus.SystemBus()
                bus.request_name(BUS_NAME)
                bus_name = dbus.service.BusName(BUS_NAME, bus=bus)
                dbus.service.Object.__init__(self, bus_name, OPATH)
                break
            except Exception as e:
                print(
                    f"[Simulator] Failed to connect/register on DBus: {e}. Retrying in 5 seconds..."
                )
                time.sleep(5)

        self.get_config_fail_count = 0
        self.control_fail_count = 0

    @dbus.service.signal(dbus_interface=IFACE, signature="s")
    def Event(self, message: str):
        """
        Mock DBus signal for demonstration/testing purposes.
        Args:
            message (str): The message to emit with the signal.
        """
        pass

    @dbus.service.signal(dbus_interface=IFACE, signature="s")
    def Snapshot(self, message: str):
        """
        Mock DBus signal for demonstration/testing purposes.
        Args:
            message (str): The message to emit with the signal.
        """

        pass

    @dbus.service.method(dbus_interface=IFACE, in_signature="", out_signature="s")
    def AlarmList(self):
        return json.dumps(
            {
                "Alarms": [
                    {
                        "AlarmType": 0,
                        "Severity": 1,
                        "CurrentState": 1,
                        "ChannelId": 16404,
                        "ExternalAlarmId": 6,
                        "UniqueId": 29,
                        "Valid": True,
                        "Name": "DC High Voltage",
                        "Channel": "Port Battery",
                        "Device": "COI 1",
                        "Title": "Port Battery",
                        "Description": "",
                    },
                    {
                        "AlarmType": 0,
                        "Severity": 1,
                        "CurrentState": 1,
                        "ChannelId": 1283,
                        "ExternalAlarmId": 6,
                        "UniqueId": 260,
                        "Valid": True,
                        "Name": "DC High Voltage",
                        "Channel": "House Battery",
                        "Device": "MI 3",
                        "Title": "House Battery",
                        "Description": "",
                    },
                ]
            }
        )

    @dbus.service.method(dbus_interface=IFACE, in_signature="", out_signature="s")
    def GetDevices(self):

        return json.dumps(self.device_list)

    @dbus.service.method(dbus_interface=IFACE, in_signature="", out_signature="s")
    def GetConfigAll(self):
        return CONFIG_JSON_STRING

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
    def AlarmAcknowledge(self, acknowledge_request: str) -> str:
        try:
            acknowledge_json = json.loads(acknowledge_request)
            if "Id" in acknowledge_json and "Accepted" in acknowledge_json:
                alarm_id = acknowledge_json["Id"]
                accepted = acknowledge_json["Accepted"]
                print(f"Acknowledge Request: Id={alarm_id}, Accepted={accepted}")

                return '{"Result": "Ok"}'
            else:
                self.logger.error(
                    "Invalid acknowledge request format: %s", acknowledge_request
                )
                return '{"Result": "Error", "Message": "Invalid Format"}'
        except Exception as e:
            self.logger.error("Failed to acknowledge alarm %s: %s", alarm_id, e)
            return False

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
        try:
            control_json = json.loads(control_request)
            if "Type" in control_json and control_json["Type"] in (
                "Activate",
                "Release",
                "SetAbsolute",
            ):
                print(f"Control Request: {control_json}")
                self.circuit_state_1 = json.dumps(
                    {"IsOffline": False, "Current": 2.5, "Voltage": 8.5, "Level": 100}
                )
                return '{"Result": "Ok"}'
            else:
                return '{"Result": "Error", "Message": "Unknown Type"}'
        except Exception as e:
            return '{"Result": "Error", "Message": "Invalid JSON"}'

    @dbus.service.method(dbus_interface=IFACE, in_signature="s", out_signature="s")
    def PutFile(self, request: str):
        try:
            request_json = json.loads(request)
            if "Content" in request_json:
                print(f"PutFile Request: {request_json['Content']}")
                return '{"Result": "Ok"}'
            else:
                return '{"Result": "Error", "Message": "Invalid Content"}'
        except Exception as e:
            return '{"Result": "Error", "Message": "Invalid JSON"}'

    @dbus.service.method(dbus_interface=IFACE, in_signature="s", out_signature="s")
    def Operation(self, operation_request: str):
        try:
            operation_json = json.loads(operation_request)
            if "type" in operation_json and operation_json["type"] == 1:
                return '{"Result": "Ok"}'
            else:
                return '{"Result": "Error", "Message": "Unknown Operation"}'
        except Exception as e:
            return '{"Result": "Error", "Message": "Invalid JSON"}'

    @dbus.service.method(dbus_interface=IFACE, in_signature="", out_signature="s")
    def SingleSnapshot(self):
        snapshot = {
            "DC": {
                "DC.6": {
                    "ComponentStatus": "Disconnected",
                    "Voltage": 12.0,
                    "Current": 2.0,
                    "StateOfCharge": 75,
                    "Temperature": 23.11,
                    "CapacityRemaining": 1000.0,
                    "TimeRemaining": 120,
                    "TimeToCharge": 60,
                },
                "DC.7": {
                    "ComponentStatus": "Connected",
                    "Voltage": 11.0,
                    "Current": 12.0,
                    "StateOfCharge": 13,
                    "Temperature": 14.11,
                    "CapacityRemaining": 15555.0,
                    "TimeRemaining": 1444,
                    "TimeToCharge": 124,
                },
            },
            "Tanks": {
                "Tanks.17": {
                    "ComponentStatus": "Connected",
                    "Level": 200,
                    "LevelPercent": 87,
                },
                "Tanks.81": {
                    "ComponentStatus": "Connected",
                    "Level": 300,
                    "LevelPercent": 92,
                },
            },
            "AC": {
                "AC.1": {
                    "Instance": 1,
                    "AClines": {
                        "1": {
                            "Instance": 1,
                            "Line": 1,
                            "ComponentStatus": "Connected",
                            "Voltage": 11.0,
                            "Current": 10.5,
                            "Frequency": 50.0,
                            "Power": 2400.0,
                        },
                        "2": {
                            "Instance": 2,
                            "Line": 2,
                            "ComponentStatus": "Disconnected",
                            "Voltage": 11.0,
                            "Current": 59.8,
                            "Frequency": 50.0,
                            "Power": 5555.0,
                        },
                    },
                },
                "AC.5": {
                    "Instance": 1,
                    "AClines": {
                        "1": {
                            "Instance": 1,
                            "Line": 1,
                            "ComponentStatus": "Connected",
                            "Voltage": 1110.0,
                            "Current": 11.5,
                            "Frequency": 11.0,
                            "Power": 1111.0,
                        },
                        "2": {
                            "Instance": 2,
                            "Line": 2,
                            "ComponentStatus": "Connected",
                            "Voltage": 111.0,
                            "Current": 11.8,
                            "Frequency": 111.0,
                            "Power": 111.0,
                        },
                    },
                },
            },
            "Engines": {
                "Engines.0": {
                    "ComponentStatus": "Connected",
                    "EngineState": 1,
                    "Speed": 0,
                    "CoolantPressure": 50,
                    "CoolantTemperature": 80.0,
                    "FuelLevel": 50,
                    "EngineHours": 1000,
                    "DiscreteStatus1": 1,
                    "DiscreteStatus2": 1,
                }
            },
            "Circuits": {
                "Circuits.0": {
                    "IsOffline": False,
                    "Current": 1.5,
                    "Voltage": 12.5,
                    "Level": 100,
                },
                "Circuits.114": {
                    "IsOffline": True,
                    "Current": 2.5,
                    "Voltage": 8.5,
                    "Level": 0,
                },
                "Circuits.135": {
                    "IsOffline": True,
                    "Current": 2.5,
                    "Voltage": 8.5,
                    "Level": 0,
                },
                "Circuits.138": {
                    "IsOffline": True,
                    "Current": 2.5,
                    "Voltage": 8.5,
                    "Level": 0,
                },
                "Circuits.141": {
                    "IsOffline": False,
                    "Current": 2.5,
                    "Voltage": 8.5,
                    "Level": 100,
                },
            },
            "GNSS": {
                "GNSS.128": {
                    "ComponentStatus": "Connected",
                    "FixType": "2D Fix",
                    "LatitudeDeg": 8.5,
                    "LongitudeDeg": 100.0,
                    "Sog": 5.5,
                },
            },
            "InverterChargers": {
                "InverterChargers.0": {
                    "ComponentStatus": "Connected",
                    "InverterEnable": 0,
                    "ChargerEnable": 0,
                    "InverterState": "Inverting",
                    "ChargerState": "Float",
                },
            },
        }
        return json.dumps(snapshot)


class Main:
    logger = logging.getLogger("DBUS N2k Simulator")

    def __init__(self):
        self.logger.setLevel(logging.DEBUG)
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

        def emit_event():
            service.Event('{"Type": 1}')
            return True  # Repeat every interval

        def emit_snapshot():
            self.logger.debug("Emitting snapshot")
            snapshot = {
                "DC": {
                    "DC.6": {
                        "ComponentStatus": "Disconnected",
                        "Voltage": 12.0,
                        "Current": 2.0,
                        "StateOfCharge": 75,
                        "Temperature": 23.11,
                        "CapacityRemaining": 1000.0,
                        "TimeRemaining": 120,
                        "TimeToCharge": 60,
                    },
                    "DC.7": {
                        "ComponentStatus": "Connected",
                        "Voltage": 11.0,
                        "Current": 12.0,
                        "StateOfCharge": 13,
                        "Temperature": 14.11,
                        "CapacityRemaining": 15555.0,
                        "TimeRemaining": 1444,
                        "TimeToCharge": 124,
                    },
                },
                "Tanks": {
                    "Tanks.17": {
                        "ComponentStatus": "Connected",
                        "Level": 200,
                        "LevelPercent": 87,
                    },
                    "Tanks.81": {
                        "ComponentStatus": "Connected",
                        "Level": 300,
                        "LevelPercent": 92,
                    },
                },
                "AC": {
                    "AC.1": {
                        "Instance": 1,
                        "AClines": {
                            "1": {
                                "Instance": 1,
                                "Line": 1,
                                "ComponentStatus": "Connected",
                                "Voltage": 11.0,
                                "Current": 10.5,
                                "Frequency": 50.0,
                                "Power": 2400.0,
                            },
                            "2": {
                                "Instance": 2,
                                "Line": 2,
                                "ComponentStatus": "Disconnected",
                                "Voltage": 11.0,
                                "Current": 59.8,
                                "Frequency": 50.0,
                                "Power": 5555.0,
                            },
                        },
                    },
                    "AC.5": {
                        "Instance": 1,
                        "AClines": {
                            "1": {
                                "Instance": 1,
                                "Line": 1,
                                "ComponentStatus": "Connected",
                                "Voltage": 1110.0,
                                "Current": 11.5,
                                "Frequency": 11.0,
                                "Power": 1111.0,
                            },
                            "2": {
                                "Instance": 2,
                                "Line": 2,
                                "ComponentStatus": "Connected",
                                "Voltage": 111.0,
                                "Current": 11.8,
                                "Frequency": 111.0,
                                "Power": 111.0,
                            },
                        },
                    },
                },
                "Engines": {
                    "Engines.0": {
                        "ComponentStatus": "Connected",
                        "EngineState": 1,
                        "Speed": 0,
                        "CoolantPressure": 50,
                        "CoolantTemperature": 80.0,
                        "FuelLevel": 50,
                        "EngineHours": 1000,
                        "DiscreteStatus1": 1,
                        "DiscreteStatus2": 1,
                    }
                },
                "Circuits": {
                    "Circuits.0": {
                        "IsOffline": False,
                        "Current": 1.5,
                        "Voltage": 12.5,
                        "Level": 100,
                    },
                    "Circuits.114": {
                        "IsOffline": True,
                        "Current": 2.5,
                        "Voltage": 8.5,
                        "Level": 0,
                    },
                    "Circuits.135": {
                        "IsOffline": True,
                        "Current": 2.5,
                        "Voltage": 8.5,
                        "Level": 0,
                    },
                    "Circuits.138": {
                        "IsOffline": True,
                        "Current": 2.5,
                        "Voltage": 8.5,
                        "Level": 0,
                    },
                    "Circuits.141": {
                        "IsOffline": False,
                        "Current": 2.5,
                        "Voltage": 8.5,
                        "Level": 100,
                    },
                },
                "GNSS": {
                    "GNSS.128": {
                        "ComponentStatus": "Connected",
                        "FixType": "2D Fix",
                        "LatitudeDeg": 8.5,
                        "LongitudeDeg": 100.0,
                        "Sog": 5.5,
                    },
                },
                "InverterChargers": {
                    "InverterChargers.0": {
                        "ComponentStatus": "Connected",
                        "InverterEnable": 0,
                        "ChargerEnable": 0,
                        "InverterState": "Inverting",
                        "ChargerState": "Float",
                    },
                },
            }
            service.Snapshot(json.dumps(snapshot))
            return True

        GLib.timeout_add_seconds(2, emit_snapshot)  # Emit every 2 second

        try:
            loop.run()
        except KeyboardInterrupt:
            self.logger.info("Service stopped.")


def main():
    main = Main()
    main.run()


if __name__ == "__main__":
    main()

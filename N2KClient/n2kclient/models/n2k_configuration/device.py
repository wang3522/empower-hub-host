import json
from typing import Optional
from enum import Enum
from ..constants import AttrNames


class DeviceType(Enum):
    NotSet = 0x00
    OutputInterface = 0x0F
    MeterInterface = 0x0E
    SignalInterface = 0x0D
    MotorControlInterface = 0x0C
    SwitchInterface = 0x0B
    ACOutputInterface = 0x0A
    ACMainsInterface = 0x09
    MasterbusInterface = 0x08
    Contact6 = 0x07
    SwitchPad = 0x03
    WirelessInterface = 0x11
    DisplayInterface = 0x10
    SmartBatteryHub = 0x1B
    Control1 = 0x1C
    Keypad = 0x1D
    Contact6Plus = 0x1E
    CombinationOutputInterface = 0x1F
    M2VSM = 0x20
    CZoneDDS = 0x21
    RV1 = 0x30
    ControlX = 0x36
    Europa = 0x40
    Shunt = 0x80
    Charger = 0x81
    InverterCharger = 0x82
    Battery = 0x83


class Device:
    name_utf8: str
    source_address: int
    conflict: bool
    device_type: DeviceType
    valid: bool
    transient: bool
    version: Optional[str]
    dipswitch: str

    def __init__(
        self,
        name_utf8: str = "",
        source_address: int = 0,
        conflict: bool = False,
        device_type: DeviceType = DeviceType.NotSet,
        valid: bool = False,
        transient: bool = False,
        version: Optional[str] = None,
        dipswitch: str = "",
    ):
        self.name_utf8 = name_utf8
        self.source_address = source_address
        self.conflict = conflict
        self.device_type = device_type
        self.valid = valid
        self.transient = transient
        self.version = version
        self.dipswitch = dipswitch

    def to_dict(self) -> dict[str, str]:
        try:
            fields = {
                AttrNames.NAMEUTF8: self.name_utf8,
                AttrNames.SOURCE_ADDRESS: self.source_address,
                AttrNames.CONFLICT: self.conflict,
                AttrNames.DEVICE_TYPE: self.device_type.value,
                AttrNames.VALID: self.valid,
                AttrNames.TRANSIENT: self.transient,
                AttrNames.DIPSWITCH: self.dipswitch,
            }
            if self.version is not None:
                fields[AttrNames.VERSION] = self.version
            return {
                **fields,
            }
        except Exception as e:
            print(f"Error serializing Device to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing Device to JSON: {e}")
            return "{}"

from typing import Optional
from enum import Enum


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

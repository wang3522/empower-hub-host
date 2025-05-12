from typing import Optional
from enum import Enum

class DeviceType(Enum):
    None = 0x00
    OutputInterface = 0x0f
    MeterInterface = 0x0e
    SignalInterface = 0x0d
    MotorControlInterface = 0x0c
    SwitchInterface = 0x0b
    ACOutputInterface = 0x0a
    ACMainsInterface = 0x09
    MasterbusInterface = 0x08
    Contact6 = 0x07
    SwitchPad = 0x03
    WirelessInterface = 0x11
    DisplayInterface = 0x10
    SmartBatteryHub = 0x1b
    Control1 = 0x1c
    Keypad = 0x1d
    Contact6Plus = 0x1e
    CombinationOutputInterface = 0x1f
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
    dipswitch: int
    source_address: int
    conflict: bool
    device_type: DeviceType
    valid: bool
    transient: bool
    version: Optional[str]

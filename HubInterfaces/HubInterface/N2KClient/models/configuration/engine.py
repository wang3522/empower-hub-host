from .config_item import ConfigItem
from .instance import Instance
from enum import Enum


class EngineType(Enum):
    SmartCraft: 0
    NMEA2000: 1


class EnginesDevice(ConfigItem):
    instance: Instance
    software_id: str
    calibration_id: str
    serial_number: str
    ecu_serial_number: str
    engine_type: EngineType

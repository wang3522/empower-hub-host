from .monitoring_device import MonitoringDevice
from enum import Enum


class TemperatureType(Enum):
    Sea = 0
    Outside = 1
    Inside = 2
    EngineRoom = 3
    MainCabin = 4
    LiveWell1 = 5
    BaitWell = 6
    Refrigeration = 7
    HeatingSystem = 8
    DewPoint = 9
    WindChillApparent = 10
    WindChillTheoretical = 11
    HeadIndex = 12
    Freezer = 13
    ExhaustGas = 14


class Temperature(MonitoringDevice):
    high_temperature: bool
    temperature_type: TemperatureType

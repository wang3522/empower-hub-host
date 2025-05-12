from .monitoring_device import MonitoringDevice
from enum import Enum


class PressureType(Enum):
    Atmospheric = 0
    Water = 1
    Steam = 2
    CompressedAir = 3
    Hydraulic = 4


class Pressure(MonitoringDevice):
    pressure_type: PressureType
    atmospheric_pressure: bool

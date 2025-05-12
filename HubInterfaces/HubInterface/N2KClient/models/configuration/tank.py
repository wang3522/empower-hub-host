from .monitoring_device import MonitoringDevice
from enum import Enum


class TankType(Enum):
    Fuel = 0
    FreshWater = 1
    WasteWater = 2
    LiveWell = 3
    Oil = 4
    BlackWater = 5


class Tank(MonitoringDevice):
    tank_type: TankType
    tank_capacity: float

import json
from .monitoring_device import MonitoringDevice
from enum import Enum
from ..constants import AttrNames


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

    def to_dict(self) -> dict[str, str]:
        return {
            **super().to_dict(),
            AttrNames.TANK_TYPE: self.tank_type.value,
            AttrNames.TANK_CAPACITY: self.tank_capacity,
        }

    def to_json_string(self) -> str:
        return json.dumps(self.to_dict())

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

    def __init__(self, tank_type=TankType.Fuel, tank_capacity=0.0, **kwargs):
        super().__init__(**kwargs)
        self.tank_type = tank_type
        self.tank_capacity = tank_capacity

    def to_dict(self) -> dict[str, str]:
        try:
            return {
                **super().to_dict(),
                AttrNames.TANK_TYPE: self.tank_type.value,
                AttrNames.TANK_CAPACITY: self.tank_capacity,
            }
        except Exception as e:
            print(f"Error serializing Tank to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing Tank to JSON: {e}")
            return "{}"

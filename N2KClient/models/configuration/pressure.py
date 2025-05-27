import json
from .monitoring_device import MonitoringDevice
from enum import Enum
from ..constants import AttrNames


class PressureType(Enum):
    Atmospheric = 0
    Water = 1
    Steam = 2
    CompressedAir = 3
    Hydraulic = 4


class Pressure(MonitoringDevice):
    pressure_type: PressureType
    atmospheric_pressure: bool

    def to_dict(self) -> dict[str, str]:
        try:
            return {
                **super().to_dict(),
                AttrNames.PRESSURE_TYPE: self.pressure_type.value,
                AttrNames.ATMOSPHERIC_PRESSURE: self.atmospheric_pressure,
            }
        except Exception as e:
            print(f"Error serializing Pressure to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing Pressure to JSON: {e}")
            return "{}"

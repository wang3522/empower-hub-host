import json
from .monitoring_device import MonitoringDevice
from enum import Enum
from ..constants import AttrNames


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

    def to_dict(self) -> dict[str, str]:
        try:
            return {
                **super().to_dict(),
                AttrNames.HIGH_TEMPERATURE: self.high_temperature,
                AttrNames.TEMPERATURE_TYPE: self.temperature_type.value,
            }
        except Exception as e:
            print(f"Error serializing Temperature to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing Temperature to JSON: {e}")
            return "{}"

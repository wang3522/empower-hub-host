from enum import Enum
import json
from N2KClient.models.configuration.metering_device import MeteringDevice
from ..constants import AttrNames


class ACLine(Enum):
    Line1 = 0
    Line2 = 1
    Line3 = 2


class ACType(Enum):
    Unknown = 0
    Generator = 1
    ShorePower = 2
    Inverter = 3
    Parallel = 4
    Charger = 5
    Outlet = 6


class AC(MeteringDevice):
    line: ACLine
    output: bool

    nominal_frequency: int

    ac_type: ACType

    def to_dict(self) -> dict[str, str]:
        try:
            return {
                **super().to_dict(),
                AttrNames.LINE: self.line.value,
                AttrNames.OUTPUT: self.output,
                AttrNames.NOMINAL_FREQUENCY: self.nominal_frequency,
                AttrNames.AC_TYPE: self.ac_type.value,
            }
        except Exception as e:
            print(f"Error serializing AC to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing AC to JSON: {e}")
            return "{}"

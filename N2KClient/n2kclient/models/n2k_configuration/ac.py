from enum import Enum
import json
from .metering_device import MeteringDevice
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

    def __init__(
        self,
        line=ACLine.Line1,
        output=False,
        nominal_frequency=0,
        ac_type=ACType.Unknown,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.line = line
        self.output = output
        self.nominal_frequency = nominal_frequency
        self.ac_type = ac_type

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

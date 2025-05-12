from ..common_enums import ACLine, ACType
from enum import Enum
from .metering_device import MeteringDevice


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

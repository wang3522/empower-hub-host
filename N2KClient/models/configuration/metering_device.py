from .config_item import ConfigItem
from .instance import Instance


class MeteringDevice(ConfigItem):
    instance: Instance

    output: bool
    nominal_voltage: int
    address: int

    warning_low: float
    warning_high: float

    show_voltage: bool
    show_current: bool

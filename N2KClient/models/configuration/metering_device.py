import json
from .config_item import ConfigItem
from .instance import Instance
from ..constants import AttrNames


class MeteringDevice(ConfigItem):
    instance: Instance

    output: bool
    nominal_voltage: int
    address: int

    show_voltage: bool
    show_current: bool

    def to_dict(self):
        return {
            **super().to_dict(),
            AttrNames.INSTANCE_: self.instance.to_dict(),
            AttrNames.OUTPUT: self.output,
            AttrNames.NOMINAL_VOLTAGE: self.nominal_voltage,
            AttrNames.ADDRESS: self.address,
            AttrNames.SHOW_VOLTAGE: self.show_voltage,
            AttrNames.SHOW_CURRENT: self.show_current,
        }

    def to_json_string(self):
        return json.dumps(self.to_dict())

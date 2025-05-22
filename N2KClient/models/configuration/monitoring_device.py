import json
from typing import Optional
from .config_item import ConfigItem
from .instance import Instance
from .data_id import DataId

from ..common_enums import SwitchType
from ..constants import AttrNames


class MonitoringDevice(ConfigItem):
    instance: Instance
    circuit_id: Optional[DataId]
    switch_type: SwitchType
    circuit_name: Optional[str]
    address: int

    def to_dict(self):
        fields = {
            **super().to_dict(),
            AttrNames.INSTANCE_: self.instance.to_dict(),
            AttrNames.SWITCH_TYPE: self.switch_type.value,
            AttrNames.ADDRESS: self.address,
        }
        if self.circuit_id:
            fields["circuit_id"] = self.circuit_id.to_dict()
        if self.circuit_name:
            fields["circuit_name"] = self.circuit_name

    def to_json_string(self):
        return json.dumps(self.to_dict())

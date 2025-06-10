import json
from typing import Optional
from .config_item import ConfigItem
from .instance import Instance
from .data_id import DataId

from ..common_enums import SwitchType
from ..constants import AttrNames


class MonitoringDevice(ConfigItem):
    instance: Instance
    switch_type: SwitchType
    address: int

    circuit_id: Optional[DataId]
    circuit_name_utf8: Optional[str]

    def __init__(self):
        super().__init__()
        self.circuit_id = None
        self.circuit_name_utf8 = None

    def to_dict(self):
        try:
            fields = {
                **super().to_dict(),
                AttrNames.INSTANCE: self.instance.to_dict(),
                AttrNames.SWITCH_TYPE: self.switch_type.value,
                AttrNames.ADDRESS: self.address,
            }
            if self.circuit_id:
                fields["circuit_id"] = self.circuit_id.to_dict()
            if self.circuit_name_utf8:
                fields["circuit_name_utf8"] = self.circuit_name_utf8
            return fields
        except Exception as e:
            print(f"Error serializing MonitoringDevice to dict: {e}")
            return {}

    def to_json_string(self):
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing MonitoringDevice to JSON: {e}")
            return "{}"

import json
from typing import Optional
from .config_item import ConfigItem
from .instance import Instance
from .data_id import DataId

from ..common_enums import SwitchType
from ..constants import AttrNames
from .alarm_limit import AlarmLimit


class MonitoringDevice(ConfigItem):
    instance: Instance
    switch_type: SwitchType
    address: int

    circuit_id: Optional[DataId]
    circuit_name_utf8: Optional[str]

    very_low_limit: Optional[AlarmLimit]
    low_limit: Optional[AlarmLimit]
    high_limit: Optional[AlarmLimit]
    very_high_limit: Optional[AlarmLimit]

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
            circuit_id: Optional[DataId] = getattr(self, "circuit_id", None)
            if circuit_id:
                fields["circuit_id"] = circuit_id.to_dict()
            circuit_name_utf8: Optional[str] = getattr(self, "circuit_name_utf8", None)
            if circuit_name_utf8:
                fields["circuit_name_utf8"] = circuit_name_utf8
            very_low_limit: Optional[AlarmLimit] = getattr(self, "very_low_limit", None)
            if very_low_limit:
                fields[AttrNames.VERY_LOW_LIMIT] = very_low_limit.to_dict()
            low_limit: Optional[AlarmLimit] = getattr(self, "low_limit", None)
            if low_limit:
                fields[AttrNames.LOW_LIMIT] = low_limit.to_dict()
            high_limit: Optional[AlarmLimit] = getattr(self, "high_limit", None)
            if high_limit:
                fields[AttrNames.HIGH_LIMIT] = high_limit.to_dict()
            very_high_limit: Optional[AlarmLimit] = getattr(
                self, "very_high_limit", None
            )
            if very_high_limit:
                fields[AttrNames.VERY_HIGH_LIMIT] = very_high_limit.to_dict()
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

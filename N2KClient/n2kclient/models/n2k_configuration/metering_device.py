import json
from typing import Optional
from .config_item import ConfigItem
from .instance import Instance
from ..constants import AttrNames
from .alarm_limit import AlarmLimit


class MeteringDevice(ConfigItem):
    instance: Instance

    output: bool
    nominal_voltage: int
    address: int

    show_voltage: bool
    show_current: bool

    low_limit: Optional[AlarmLimit]
    very_low_limit: Optional[AlarmLimit]
    high_limit: Optional[AlarmLimit]
    very_high_limit: Optional[AlarmLimit]
    frequency: Optional[AlarmLimit]
    low_voltage: Optional[AlarmLimit]
    very_low_voltage: Optional[AlarmLimit]
    high_voltage: Optional[AlarmLimit]

    def to_dict(self):
        try:
            fields = {
                **super().to_dict(),
                AttrNames.INSTANCE: self.instance.to_dict(),
                AttrNames.OUTPUT: self.output,
                AttrNames.NOMINAL_VOLTAGE: self.nominal_voltage,
                AttrNames.ADDRESS: self.address,
                AttrNames.SHOW_VOLTAGE: self.show_voltage,
                AttrNames.SHOW_CURRENT: self.show_current,
            }
            low_limit: Optional[AlarmLimit] = getattr(self, "low_limit", None)
            if low_limit:
                fields[AttrNames.LOW_LIMIT] = low_limit.to_dict()
            very_low_limit: Optional[AlarmLimit] = getattr(self, "very_low_limit", None)
            if very_low_limit:
                fields[AttrNames.VERY_LOW_LIMIT] = very_low_limit.to_dict()
            high_limit: Optional[AlarmLimit] = getattr(self, "high_limit", None)
            if high_limit:
                fields[AttrNames.HIGH_LIMIT] = high_limit.to_dict()
            very_high_limit: Optional[AlarmLimit] = getattr(
                self, "very_high_limit", None
            )
            if very_high_limit:
                fields[AttrNames.VERY_HIGH_LIMIT] = very_high_limit.to_dict()
            frequency: Optional[AlarmLimit] = getattr(self, "frequency", None)
            if frequency:
                fields[AttrNames.FREQUENCY] = frequency.to_dict()
            low_voltage: Optional[AlarmLimit] = getattr(self, "low_voltage", None)
            if low_voltage:
                fields[AttrNames.LOW_VOLTAGE] = low_voltage.to_dict()
            very_low_voltage: Optional[AlarmLimit] = getattr(
                self, "very_low_voltage", None
            )
            if very_low_voltage:
                fields[AttrNames.VERY_LOW_VOLTAGE] = very_low_voltage.to_dict()
            high_voltage: Optional[AlarmLimit] = getattr(self, "high_voltage", None)
            if high_voltage:
                fields[AttrNames.HIGH_VOLTAGE] = high_voltage.to_dict()

            return fields
        except Exception as e:
            print(f"Error serializing MeteringDevice to dict: {e}")
            return {}

    def to_json_string(self):
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing MeteringDevice to JSON: {e}")
            return "{}"

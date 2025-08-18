from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .constants import Constants
from .common_enums import ChannelType, Unit


class AlarmSettingType(Enum):
    TANK = 1
    BATTERY = 2


class AlarmSettingLimit(str, Enum):
    VeryLowLimit = "very_low_limit"
    LowLimit = "low_limit"
    HighLimit = "high_limit"
    VeryHighLimit = "very_high_limit"
    HighVoltage = "high_voltage"
    LowVoltage = "low_voltage"
    VeryLowVoltage = "very_low_voltage"


@dataclass
class AlarmSetting:
    """Represents a generic alarm setting with common attributes.
    Attributes:
        name (str): Name of the alarm setting.
        type (ChannelType): Type of the channel.
        unit (Unit): Unit of measurement for the alarm setting.
        metadata (Dict[str, Any]): Metadata associated with the alarm setting.
        read_only (bool): Indicates if the alarm setting is read-only.
        tags (List[str]): Tags associated with the alarm setting.
        value (float): Value of the alarm setting.
    Methods:
        to_json: Converts the AlarmSetting object to a JSON-serializable dictionary."""

    name: str = ""
    type: ChannelType = ChannelType.NUMBER
    unit: Unit = Unit.PERCENT
    metadata: Dict[str, Any] = field(default_factory=dict)
    read_only: bool = True
    tags: List[str] = field(default_factory=list)
    value: float = 0.0

    def __init__(
        self,
        limit: AlarmSettingLimit,
        alarm_id: int,
        value: float,
        is_on: bool,
        limit_mappings: dict[AlarmSettingLimit, List[str]],
    ):
        onoff = Constants.On if is_on else Constants.Off
        self.name = f"{limit_mappings[limit][0]} ({onoff})"
        self.tags = [
            f"{Constants.empower}:{Constants.threshold}.{limit_mappings[limit][1]}.{onoff}"
        ]
        self.metadata = {f"{Constants.europa}:{Constants.alarmId}": alarm_id}
        if is_on:
            self.metadata[
                f"{Constants.empower}:{Constants.notification}.{Constants.userPreference}"
            ] = f"{Constants.empower}:{Constants.threshold}.{limit_mappings[limit][2]}"
        self.value = value

    def to_json(self):
        """Converts the AlarmSetting object to a JSON-serializable dictionary."""
        return {
            "name": self.name,
            "type": self.type.value,
            "unit": self.unit.value,
            "readOnly": self.read_only,
            "metadata": self.metadata,
            "tags": self.tags,
            "value": self.value,
        }


class TankAlarmSetting(AlarmSetting):
    """
    Alarm setting specific to tank parameters.
    Attributes:
        limit_mappings (dict): Mappings for tank alarm limits to names and tags.
    Methods:
        __init__: Initializes a TankAlarmSetting instance.
    """

    limit_mappings = {
        AlarmSettingLimit.VeryLowLimit: [
            "Very Low Level",
            "veryLowLevel",
            "veryLowSignal",
        ],
        AlarmSettingLimit.LowLimit: ["Low Level", "lowLevel", "lowSignal"],
        AlarmSettingLimit.HighLimit: ["High Level", "highLevel", "highSignal"],
        AlarmSettingLimit.VeryHighLimit: [
            "Very High Level",
            "veryHighLevel",
            "veryHighSignal",
        ],
    }

    def __init__(
        self, limit: AlarmSettingLimit, alarm_id: int, value: float, is_on: bool
    ):
        super().__init__(limit, alarm_id, value, is_on, self.limit_mappings)
        self.unit = Unit.PERCENT


class BatteryAlarmSetting(AlarmSetting):
    """
    Alarm setting specific to battery parameters.
    Attributes:
        limit_mappings (dict): Mappings for battery alarm limits to names and tags.
    Methods:
        __init__: Initializes a BatteryAlarmSetting instance.
    """

    limit_mappings = {
        AlarmSettingLimit.VeryLowLimit: [
            "Very Low Capacity",
            "veryLowCapacity",
            "veryLowCapacity",
        ],
        AlarmSettingLimit.LowLimit: ["Low Capacity", "lowCapacity", "lowCapacity"],
        AlarmSettingLimit.HighLimit: [
            "Battery Full",
            "batteryFull",
            "highCapacity",
        ],
        AlarmSettingLimit.VeryHighLimit: [
            "Very High Capacity",
            "veryHighCapacity",
            "veryHighCapacity",
        ],
        AlarmSettingLimit.HighVoltage: [
            "High Voltage",
            "highVoltage",
            "highVoltage",
        ],
        AlarmSettingLimit.LowVoltage: ["Low Voltage", "lowVoltage", "lowVoltage"],
        AlarmSettingLimit.VeryLowVoltage: [
            "Very Low Voltage",
            "veryLowVoltage",
            "veryLowVoltage",
        ],
    }

    def __init__(
        self,
        limit: AlarmSettingLimit,
        alarm_id: int,
        value: float,
        is_on: bool,
        name: Optional[str] = None,
    ):
        """Initializes a BatteryAlarmSetting instance."""
        super().__init__(limit, alarm_id, value, is_on, self.limit_mappings)
        if name:
            self.metadata[
                f"{Constants.empower}:{Constants.notification}.{Constants.userPreference}.{Constants.name}"
            ] = name
        self.unit = (
            Unit.ENERGY_VOLT
            if Constants.voltage in limit.value.lower()
            else Unit.PERCENT
        )
        self.value = value


class AlarmSettingFactory:
    @staticmethod
    def get_alarm_setting(
        type: AlarmSettingLimit,
        limit: AlarmSettingLimit,
        alarm_id: int,
        value: float,
        is_on: bool,
        name: Optional[str] = None,
    ):
        """Factory method to create appropriate AlarmSetting instance."""
        value = round(value, 1)
        if type == AlarmSettingType.TANK:
            return TankAlarmSetting(limit, alarm_id, value, is_on)
        elif type == AlarmSettingType.BATTERY:
            return BatteryAlarmSetting(limit, alarm_id, value, is_on, name)

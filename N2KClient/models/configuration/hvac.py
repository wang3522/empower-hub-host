import json
from .instance import Instance
from .data_id import DataId
from .config_item import ConfigItem
from ..constants import AttrNames


class HVACDevice(ConfigItem):
    instance: Instance
    operating_mode_id: DataId
    fan_mode_id: DataId
    fan_speed_id: DataId
    setpoint_temperature_id: DataId
    operating_mode_toggle_id: DataId
    fan_mode_toggle_id: DataId
    fan_speed_toggle_id: DataId
    setpoint_temperature_toggle_id: DataId

    temperature_monitoring_id: DataId
    fan_speed_count: int

    # 1 << NoChange = 0U
    # 1 << ModeOff = 1U
    # 1 << Moisture = 2U
    # 1 << Auto = 3U
    # 1 << Heat = 4U
    # 1 << Cool = 5U
    # 1 << AutoAux = 6U
    # 1 << Aux = 7U
    # 1 << FanOnly = 8U
    # 1 << Pet = 9U
    operating_modes_mask: int

    model: int

    temperature_instance: Instance
    setpoint_temperature_min: float
    setpoint_temperature_max: float

    fan_speed_off_modes_mask: int
    fan_speed_auto_modes_mask: int
    fan_speed_manual_modes_mask: int

    def to_dict(self) -> dict[str, str]:
        try:
            return {
                **super().to_dict(),
                AttrNames.INSTANCE: self.instance.to_dict(),
                AttrNames.OPERATING_MODE_ID: self.operating_mode_id.to_dict(),
                AttrNames.FAN_MODE_ID: self.fan_mode_id.to_dict(),
                AttrNames.FAN_SPEED_ID: self.fan_speed_id.to_dict(),
                AttrNames.SETPOINT_TEPERATURE_ID: self.setpoint_temperature_id.to_dict(),
                AttrNames.OPERATING_MODE_TOGGLE_ID: self.operating_mode_toggle_id.to_dict(),
                AttrNames.FAN_MODE_TOGGLE_ID: self.fan_mode_toggle_id.to_dict(),
                AttrNames.FAN_SPEED_TOGGLE_ID: self.fan_speed_toggle_id.to_dict(),
                AttrNames.SET_POINT_TEMPERATURE_TOGGLE_ID: self.setpoint_temperature_toggle_id.to_dict(),
                AttrNames.TEMPERATURE_MONITORING_ID: self.temperature_monitoring_id.to_dict(),
                AttrNames.FAN_SPEED_COUNT: self.fan_speed_count,
                AttrNames.OPERATING_MODES_MASK: self.operating_modes_mask,
                AttrNames.MODEL: self.model,
                AttrNames.TEMPERATURE_INSTANCE: self.temperature_instance.to_dict(),
                AttrNames.SETPOINT_TEMPERATURE_MIN: self.setpoint_temperature_min,
                AttrNames.SETPOINT_TEMPERATURE_MAX: self.setpoint_temperature_max,
                AttrNames.FAN_SPEED_OFF_MODES_MASK: self.fan_speed_off_modes_mask,
                AttrNames.FAN_SPEED_AUTO_MODES_MASK: self.fan_speed_auto_modes_mask,
                AttrNames.FAN_SPEED_MANUAL_MODES_MASK: self.fan_speed_manual_modes_mask,
            }
        except Exception as e:
            print(f"Error serializing HVACDevice to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing HVACDevice to JSON: {e}")
            return "{}"

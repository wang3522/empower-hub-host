from .instance import Instance
from .data_id import DataId
from .config_item import ConfigItem


class HVACDevice(ConfigItem):
    instance: Instance
    operating_mode_id: DataId
    fan_mode_id: DataId
    fan_speed_id: DataId
    setpoint_temperature_id: DataId
    operating_mode_temperature_id: DataId
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

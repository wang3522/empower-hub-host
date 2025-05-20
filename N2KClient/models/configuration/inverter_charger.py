from .instance import Instance
from .data_id import DataId
from .config_item import ConfigItem


class InverterChargerDevice(ConfigItem):
    model: int
    type: int
    sub_type: int
    inverter_instance: Instance
    inverter_ac_id: DataId
    inverter_circuit_id: DataId
    inverter_toggle_circuit_id: DataId
    charger_instance: Instance
    charger_ac_id: DataId
    charger_circuit_id: DataId
    charger_toggle_circuit_id: DataId
    battery_bank_1_id: DataId
    battery_bank_2_id: DataId
    battery_bank_3_id: DataId
    position_column: int
    position_row: int
    clustered: bool
    primary: bool
    primary_phase: int
    device_instance: int
    dipswitch: int
    channel_index: int

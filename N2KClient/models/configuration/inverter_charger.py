import json
from .instance import Instance
from .data_id import DataId
from .config_item import ConfigItem
from ..constants import AttrNames


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

    def to_dict(self) -> dict[str, str]:
        return {
            **super().to_dict(),
            AttrNames.MODEL: self.model,
            AttrNames.TYPE: self.type,
            AttrNames.SUB_TYPE: self.sub_type,
            AttrNames.INVERTER_INSTANCE: self.inverter_instance.to_dict(),
            AttrNames.INVERTER_AC_ID: self.inverter_ac_id.to_dict(),
            AttrNames.INVERTER_CIRCUIT_ID: self.inverter_circuit_id.to_dict(),
            AttrNames.INVERTER_TOGGLE_CIRCUIT_ID: self.inverter_toggle_circuit_id.to_dict(),
            AttrNames.CHARGER_INSTANCE: self.charger_instance.to_dict(),
            AttrNames.CHARGER_AC_ID: self.charger_ac_id.to_dict(),
            AttrNames.CHARGER_CIRCUIT_ID: self.charger_circuit_id.to_dict(),
            AttrNames.CHARGER_TOGGLE_CIRCUIT_ID: self.charger_toggle_circuit_id.to_dict(),
            AttrNames.BATTERY_BANK_1_ID: self.battery_bank_1_id.to_dict(),
            AttrNames.BATTERY_BANK_2_ID: self.battery_bank_2_id.to_dict(),
            AttrNames.BATTERY_BANK_3_ID: self.battery_bank_3_id.to_dict(),
            AttrNames.POSITION_COLUMN: self.position_column,
            AttrNames.POSITION_ROW: self.position_row,
            AttrNames.CLUSTERED: self.clustered,
            AttrNames.PRIMARY: self.primary,
            AttrNames.PRIMARY_PHASE: self.primary_phase,
            AttrNames.DEVICE_INSTANCE: self.device_instance,
        }

    def to_json_string(self) -> str:
        return json.dumps(self.to_dict())

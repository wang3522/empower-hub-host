import json
from typing import Optional
from .instance import Instance
from .data_id import DataId
from .config_item import ConfigItem
from ..constants import AttrNames


class InverterChargerDevice(ConfigItem):
    """
    Represents an unprocessed inverter charger device configuration item.
    """

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
    dipswitch: Optional[int]
    channel_index: Optional[int]

    def __init__(
        self,
        model=0,
        type=0,
        sub_type=0,
        inverter_instance=None,
        inverter_ac_id=None,
        inverter_circuit_id=None,
        inverter_toggle_circuit_id=None,
        charger_instance=None,
        charger_ac_id=None,
        charger_circuit_id=None,
        charger_toggle_circuit_id=None,
        battery_bank_1_id=None,
        battery_bank_2_id=None,
        battery_bank_3_id=None,
        position_column=0,
        position_row=0,
        clustered=False,
        primary=False,
        primary_phase=0,
        device_instance=0,
        dipswitch=None,
        channel_index=None,
    ):
        self.model = model
        self.type = type
        self.sub_type = sub_type
        self.inverter_instance = (
            inverter_instance if inverter_instance is not None else Instance()
        )
        self.inverter_ac_id = inverter_ac_id
        self.inverter_circuit_id = inverter_circuit_id
        self.inverter_toggle_circuit_id = inverter_toggle_circuit_id
        self.charger_instance = (
            charger_instance if charger_instance is not None else Instance()
        )
        self.charger_ac_id = charger_ac_id
        self.charger_circuit_id = charger_circuit_id
        self.charger_toggle_circuit_id = charger_toggle_circuit_id
        self.battery_bank_1_id = battery_bank_1_id
        self.battery_bank_2_id = battery_bank_2_id
        self.battery_bank_3_id = battery_bank_3_id
        self.position_column = position_column
        self.position_row = position_row
        self.clustered = clustered
        self.primary = primary
        self.primary_phase = primary_phase
        self.device_instance = device_instance
        self.dipswitch = dipswitch
        self.channel_index = channel_index

    def to_dict(self) -> dict[str, str]:
        try:
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
                AttrNames.DIPSWITCH: self.dipswitch,
                AttrNames.CHANNEL_INDEX: self.channel_index,
            }
        except Exception as e:
            print(f"Error serializing InverterChargerDevice to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing InverterChargerDevice to JSON: {e}")
            return "{}"

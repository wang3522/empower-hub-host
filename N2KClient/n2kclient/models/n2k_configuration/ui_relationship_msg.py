from enum import Enum
import json
from ..constants import AttrNames


class ItemType(Enum):
    NotSet = 0
    FluidLevel = 1
    Pressure = 2
    Temperature = 3
    DcMeter = 4
    AcMeter = 5
    BinaryLogicState = 6
    Circuit = 7
    Category = 8
    InverterCharger = 9


class RelationshipType(Enum):
    Normal = 0
    Duplicates = 1


class UiRelationShipMsg:
    primary_type: ItemType
    secondary_type: ItemType
    primary_id: int
    secondary_id: int
    relationship_type: RelationshipType

    primary_config_address: int
    secondary_config_address: int

    primary_channel_index: int
    secondary_channel_index: int

    def to_dict(self) -> dict[str, str]:
        try:
            return {
                AttrNames.PRIMARY_TYPE: self.primary_type.value,
                AttrNames.SECONDARY_TYPE: self.secondary_type.value,
                AttrNames.PRIMARY_ID: self.primary_id,
                AttrNames.SECONDARY_ID: self.secondary_id,
                AttrNames.RELATIONSHIP_TYPE: self.relationship_type.value,
                AttrNames.PRIMARY_CONFIG_ADDRESS: self.primary_config_address,
                AttrNames.SECONDARY_CONFIG_ADDRESS: self.secondary_config_address,
                AttrNames.PRIMARY_CHANNEL_INDEX: self.primary_channel_index,
                AttrNames.SECONDARY_CHANNEL_INDEX: self.secondary_channel_index,
            }
        except Exception as e:
            print(f"Error serializing UiRelationShipMsg to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing UiRelationShipMsg to JSON: {e}")
            return "{}"

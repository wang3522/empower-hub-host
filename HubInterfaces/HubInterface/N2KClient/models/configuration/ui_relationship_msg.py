from enum import Enum


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

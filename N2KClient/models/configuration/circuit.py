import json
from .config_item import ConfigItem
from .data_id import DataId
from .instance import Instance
from ..common_enums import SwitchType
from .sequential_name import SequentialName

from typing import Optional
from enum import Enum
from ..constants import AttrNames


class CircuitType(Enum):
    Circuit = 0
    ModeGroup1 = 1
    ModeGroup2 = 2
    ModeGroup3 = 3
    ModeGroupExclusive = 4


class ControlType(Enum):
    SetOutput = 0
    LimitOneDirection = 1
    LimitBothDirections = 2
    SetandLimit = 3


class CategoryItem:
    name_utf8: str
    enabled: bool
    index: int

    def to_dict(self) -> dict[str, str]:
        try:
            return {
                AttrNames.NAMEUTF8: self.name_utf8,
                AttrNames.ENABLED: self.enabled,
                AttrNames.INDEX: self.index,
            }
        except Exception as e:
            print(f"Error serializing CategoryItem to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing CategoryItem to JSON: {e}")
            return "{}"


class CircuitLoad(ConfigItem):
    channel_address: int
    fuse_level: float
    running_current: float
    system_on_current: float
    force_acknowledge_on: bool
    level: int
    control_type: ControlType
    is_switched_module: bool

    def to_dict(self) -> dict[str, str]:
        try:
            return {
                **super().to_dict(),
                AttrNames.CHANNEL_ADDRESS: self.channel_address,
                AttrNames.FUSE_LEVEL: self.fuse_level,
                AttrNames.RUNNING_CURRENT: self.running_current,
                AttrNames.SYSTEM_ON_CURRENT: self.system_on_current,
                AttrNames.FORCE_ACKNOWLEDGE_ON: self.force_acknowledge_on,
                AttrNames.LEVEL: self.level,
                AttrNames.CONTROL_TYPE: self.control_type.value,
                AttrNames.IS_SWITCHED_MODULE: self.is_switched_module,
            }
        except Exception as e:
            print(f"Error serializing CircuitLoad to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing CircuitLoad to JSON: {e}")
            return "{}"


class Circuit(ConfigItem):
    single_throw_id: DataId
    sequential_names_utf8: list[SequentialName]
    has_complement: bool
    display_categories: int
    circuit_type: CircuitType
    switch_type: SwitchType
    min_level: int
    max_level: int

    dimstep: int
    step: int
    dimmable: bool
    load_smooth_start: int
    sequential_states: int
    control_id: int

    circuit_loads: list[CircuitLoad]
    categories: list[CategoryItem]

    non_visible_circuit: Optional[bool]
    voltage_source: Optional[Instance]
    dc_circuit: Optional[bool]
    ac_circuit: Optional[bool]
    primary_circuit_id: Optional[int]
    remote_visibility: Optional[int]
    switch_string: Optional[str]
    systems_on_and: Optional[bool]

    def __init__(self):
        super().__init__()
        self.non_visible_circuit = None
        self.voltage_source = None
        self.dc_circuit = None
        self.ac_circuit = None
        self.primary_circuit_id = None
        self.remote_visibility = None
        self.switch_string = None
        self.systems_on_and = None

    def to_dict(self) -> dict[str, str]:
        try:
            fields = {
                AttrNames.SINGLE_THROW_ID: self.single_throw_id.to_dict(),
                AttrNames.SEQUENTIAL_NAMES_UTF8: [
                    name.to_dict() for name in self.sequential_names_utf8
                ],
                AttrNames.HAS_COMPLEMENT: self.has_complement,
                AttrNames.DISPLAY_CATEGORIES: self.display_categories,
                AttrNames.CIRCUIT_TYPE: self.circuit_type.value,
                AttrNames.SWITCH_TYPE: self.switch_type.value,
                AttrNames.MIN_LEVEL: self.min_level,
                AttrNames.MAX_LEVEL: self.max_level,
                AttrNames.NONVISIBLE_CIRCUIT: self.non_visible_circuit,
                AttrNames.DIMSTEP: self.dimstep,
                AttrNames.STEP: self.step,
                AttrNames.DIMMABLE: self.dimmable,
                AttrNames.LOAD_SMOOTH_START: self.load_smooth_start,
                AttrNames.SEQUENTIAL_STATES: self.sequential_states,
                AttrNames.CONTROL_ID: self.control_id,
            }

            if self.voltage_source:
                fields[AttrNames.VOLTAGE_SOURCE] = self.voltage_source.to_dict()
            if self.circuit_loads:
                fields[AttrNames.CIRCUIT_LOADS] = [
                    load.to_dict() for load in self.circuit_loads
                ]
            if self.categories:
                fields[AttrNames.CATEGORIES] = [
                    category.to_dict() for category in self.categories
                ]
            if self.dc_circuit is not None:
                fields[AttrNames.DC_CIRCUIT] = self.dc_circuit
            if self.ac_circuit is not None:
                fields[AttrNames.AC_CIRCUIT] = self.ac_circuit
            if self.primary_circuit_id is not None:
                fields[AttrNames.PRIMARY_CIRCUIT_ID] = self.primary_circuit_id
            if self.remote_visibility is not None:
                fields[AttrNames.REMOTE_VISIBILITY] = self.remote_visibility
            if self.switch_string is not None:
                fields[AttrNames.SWITCH_STRING] = self.switch_string
            if self.systems_on_and is not None:
                fields[AttrNames.SYSTEMS_ON_AND] = self.systems_on_and

            return {
                **super().to_dict(),
                **fields,
            }
        except Exception as e:
            print(f"Error serializing Circuit to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing Circuit to JSON: {e}")
            return "{}"

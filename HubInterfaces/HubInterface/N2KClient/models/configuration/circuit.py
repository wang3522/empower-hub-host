from .config_item import ConfigItem
from .data_id import DataId
from .instance import Instance
from ..common_enums import SwitchType

from typing import Optional
from enum import Enum


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


class CircuitLoad:
    channel_address: int
    fuse_level: float
    running_current: float
    systems_on_current: float
    force_acknowledge: bool
    level: int
    control_type: ControlType
    is_switched_module: bool


class Circuit(ConfigItem):
    single_throw_id: DataId
    sequential_names_utf8: list[str]
    has_complement: bool
    display_categories: int
    voltage_source: Optional[Instance]
    circuit_type: CircuitType
    switch_type: SwitchType
    min_level: int
    max_level: int
    nonvisibile_circuit: bool
    dimstep: int
    step: int
    dimmable: bool
    load_smooth_start: int
    sequential_states: int
    control_id: int

    circuit_loads: list[CircuitLoad]
    categories: list[CategoryItem]
    dc_circuit: Optional[bool]
    ac_circuit: Optional[bool]
    primary_circuit_id: Optional[int]
    remote_visibility: Optional[int]
    switch_string: Optional[str]
    system_on_and: Optional[bool]

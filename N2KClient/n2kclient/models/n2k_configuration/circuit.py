import json
from .config_item import ConfigItem
from .value_u32 import ValueU32
from .data_id import DataId
from .instance import Instance
from ..common_enums import SwitchType
from .sequential_name import SequentialName

from typing import Optional
from enum import Enum
from .category_item import CategoryItem
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


class CircuitLoad(ConfigItem):
    channel_address: int
    fuse_level: float
    running_current: float
    system_on_current: float
    force_acknowledge_on: bool
    level: int
    control_type: ControlType
    is_switched_module: bool

    def __init__(
        self,
        channel_address=0,
        fuse_level=0.0,
        running_current=0.0,
        system_on_current=0.0,
        force_acknowledge_on=False,
        level=0,
        control_type=None,
        is_switched_module=False,
    ):
        self.channel_address = channel_address
        self.fuse_level = fuse_level
        self.running_current = running_current
        self.system_on_current = system_on_current
        self.force_acknowledge_on = force_acknowledge_on
        self.level = level
        self.control_type = control_type
        self.is_switched_module = is_switched_module

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


class Circuit:
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

    id: ValueU32
    name_utf8: str

    non_visible_circuit: Optional[bool]
    voltage_source: Optional[Instance]
    dc_circuit: Optional[bool]
    ac_circuit: Optional[bool]
    primary_circuit_id: Optional[int]
    remote_visibility: Optional[int]
    switch_string: Optional[str]
    systems_on_and: Optional[bool]

    def __init__(
        self,
        name_utf8: str = "",
        control_id: int = 0,
        dimmable: bool = False,
        categories: list = None,
        circuit_loads: list = None,
        id=None,
        single_throw_id=None,
        sequential_names_utf8=None,
        has_complement=False,
        display_categories=0,
        circuit_type=None,
        switch_type=None,
        min_level=0,
        max_level=0,
        dimstep=0,
        step=0,
        load_smooth_start=0,
        sequential_states=0,
        non_visible_circuit=None,
        voltage_source=None,
        dc_circuit=None,
        ac_circuit=None,
        primary_circuit_id=None,
        remote_visibility=None,
        switch_string=None,
        systems_on_and=None,
    ):
        self.name_utf8 = name_utf8
        self.control_id = control_id
        self.dimmable = dimmable
        self.categories = categories if categories is not None else []
        self.circuit_loads = circuit_loads if circuit_loads is not None else []
        self.id = id
        self.single_throw_id = single_throw_id
        self.sequential_names_utf8 = (
            sequential_names_utf8 if sequential_names_utf8 is not None else []
        )
        self.has_complement = has_complement
        self.display_categories = display_categories
        self.circuit_type = circuit_type
        self.switch_type = switch_type
        self.min_level = min_level
        self.max_level = max_level
        self.dimstep = dimstep
        self.step = step
        self.load_smooth_start = load_smooth_start
        self.sequential_states = sequential_states
        self.non_visible_circuit = non_visible_circuit
        self.voltage_source = voltage_source
        self.dc_circuit = dc_circuit
        self.ac_circuit = ac_circuit
        self.primary_circuit_id = primary_circuit_id
        self.remote_visibility = remote_visibility
        self.switch_string = switch_string
        self.systems_on_and = systems_on_and

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
                AttrNames.ID: self.id.to_dict(),
                AttrNames.NAMEUTF8: self.name_utf8,
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

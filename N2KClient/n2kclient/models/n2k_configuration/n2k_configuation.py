import json
from typing import Any

from ..n2k_configuration.bls_alarm_mapping import (
    BLSAlarmMapping,
)
from .dc import DC
from .pressure import Pressure
from .tank import Tank
from .inverter_charger import InverterChargerDevice
from .hvac import HVACDevice
from .audio_stereo import AudioStereoDevice
from .circuit import Circuit
from .device import Device
from .gnss import GNSSDevice
from .binary_logic_state import BinaryLogicState
from .ui_relationship_msg import UiRelationShipMsg
from ..constants import AttrNames
from .category_item import CategoryItem
from .ac_meter import ACMeter
from .config_metadata import ConfigMetadata


class N2kConfiguration:
    metadata: ConfigMetadata
    gnss: dict[int, GNSSDevice]
    circuit: dict[int, Circuit]
    hidden_circuit: dict[str, Circuit]
    dc: dict[int, DC]
    ac: dict[int, ACMeter]
    tank: dict[int, Tank]
    inverter_charger: dict[int, InverterChargerDevice]
    device: dict[int, Device]
    hvac: dict[int, HVACDevice]
    audio_stereo: dict[int, AudioStereoDevice]
    binary_logic_state: dict[int, BinaryLogicState]
    ui_relationships: list[UiRelationShipMsg]
    category: list[CategoryItem]

    pressure: dict[int, Pressure]
    mode: dict[int, Circuit]
    bls_alarm_mappings: dict[int, BLSAlarmMapping]

    config_metadata: ConfigMetadata

    def __init__(self):
        self.gnss = {}
        self.circuit = {}
        self.hidden_circuit = {}
        self.dc = {}
        self.ac = {}
        self.tank = {}
        self.inverter_charger = {}
        self.device = {}
        self.hvac = {}
        self.audio_stereo = {}
        self.binary_logic_state = {}
        self.ui_relationships = []

        self.pressure = {}
        self.mode = {}
        self.category = []
        self.config_metadata = ConfigMetadata()
        self.bls_alarm_mappings = {}

    def __del__(self):
        self.gnss.clear()
        self.circuit.clear()
        self.hidden_circuit.clear()
        self.dc.clear()
        self.ac.clear()
        self.tank.clear()
        self.inverter_charger.clear()
        self.device.clear()
        self.hvac.clear()
        self.audio_stereo.clear()
        self.binary_logic_state.clear()
        self.ui_relationships = []

        self.pressure.clear()
        self.mode.clear()
        self.category = []
        self.config_metadata = ConfigMetadata()
        self.bls_alarm_mappings.clear()

    def to_dict(self) -> dict[str, Any]:
        try:
            return {
                AttrNames.GNSS: [gnss.to_dict() for gnss in self.gnss.values()],
                AttrNames.CIRCUIT: [
                    circuit.to_dict() for circuit in self.circuit.values()
                ],
                AttrNames.HIDDEN_CIRCUIT: [
                    circuit.to_dict() for circuit in self.hidden_circuit.values()
                ],
                AttrNames.DC: [dc.to_dict() for dc in self.dc.values()],
                AttrNames.AC: [ac.to_dict() for ac in self.ac.values()],
                AttrNames.TANK: [tank.to_dict() for tank in self.tank.values()],
                AttrNames.INVERTER_CHARGER: [
                    inverter_charger.to_dict()
                    for inverter_charger in self.inverter_charger.values()
                ],
                AttrNames.DEVICE: [device.to_dict() for device in self.device.values()],
                AttrNames.HVAC: [hvac.to_dict() for hvac in self.hvac.values()],
                AttrNames.AUDIO_STEREO: [
                    audio_stereo.to_dict()
                    for audio_stereo in self.audio_stereo.values()
                ],
                AttrNames.BINARY_LOGIC_STATE: [
                    binary_logic_state.to_dict()
                    for binary_logic_state in self.binary_logic_state.values()
                ],
                AttrNames.UI_RELATIONSHIP: [
                    ui_relationship.to_dict()
                    for ui_relationship in self.ui_relationships
                ],
                AttrNames.PRESSURE: [
                    pressure.to_dict() for pressure in self.pressure.values()
                ],
                AttrNames.MODE: [mode.to_dict() for mode in self.mode.values()],
                AttrNames.CATEGORY: [category.to_dict() for category in self.category],
                AttrNames.CONFIG_METADATA: self.config_metadata.to_dict(),
            }
        except Exception as e:
            print(f"Error serializing HostConfiguration: to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing HostConfiguration: to JSON: {e}")
            return "{}"

    def __eq__(self, other):
        if not isinstance(other, N2kConfiguration):
            return False
        return self.to_dict() == other.to_dict()

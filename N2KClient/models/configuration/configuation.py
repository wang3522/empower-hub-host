from typing import Any
from .dc import DC
from .ac import AC
from .pressure import Pressure
from .tank import Tank
from .inverter_charger import InverterChargerDevice
from .hvac import HVACDevice
from .audio_stereo import AudioStereoDevice
from .circuit import Circuit
from .device import Device
from .gnss import GNSSDevice
from .engine import EnginesDevice
from .binary_logic_state import BinaryLogicStates
from .ui_relationship_msg import UiRelationShipMsg
from ..constants import AttrNames


class N2KConfiguration:
    gnss: dict[str, GNSSDevice]
    circuit: dict[str, Circuit]
    dc: dict[str, DC]
    ac: dict[str, AC]
    tank: dict[str, Tank]
    inverter_charger: dict[str, InverterChargerDevice]
    device: dict[str, Device]
    hvac: dict[str, HVACDevice]
    audio_stereo: dict[str, AudioStereoDevice]
    binary_logic_state: dict[str, BinaryLogicStates]
    ui_relationships: list[UiRelationShipMsg]

    pressure: dict[str, Pressure]
    mode: dict[str, Circuit]
    engine: dict[str, EnginesDevice]

    def __init__(self):
        self.gnss = {}
        self.circuit = {}
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
        self.engine = {}

    def __del__(self):
        self.gnss.clear()
        self.circuit.clear()
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
        self.engine.clear()

    def to_dict(self) -> dict[str, Any]:
        return {
            AttrNames.GNSS: self.gnss,
            AttrNames.CIRCUIT: self.circuit,
            AttrNames.DC: self.dc,
            AttrNames.AC: self.ac,
            AttrNames.TANK: self.tank,
            AttrNames.INVERTER_CHARGER: self.inverter_charger,
            AttrNames.DEVICE: self.device,
            AttrNames.HVAC: self.hvac,
            AttrNames.AUDIO_STEREO: self.audio_stereo,
            AttrNames.BINARY_LOGIC_STATE: self.binary_logic_state,
            AttrNames.UI_RELATIONSHIP: self.ui_relationships,
            AttrNames.PRESSURE: self.pressure,
            AttrNames.MODE: self.mode,
            AttrNames.ENGINE: self.engine,
        }

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


class N2KConfiguration:
    gnss: dict[int, GNSSDevice]
    circuit: dict[int, Circuit]
    dc: dict[int, DC]
    ac: dict[int, AC]
    tank: dict[int, Tank]
    inverter_charger: dict[int, InverterChargerDevice]
    device: dict[int, Device]
    hvac: dict[int, HVACDevice]
    audio_stereo: dict[int, AudioStereoDevice]
    binary_logic_state: dict[int, BinaryLogicStates]
    ui_relationships: list[UiRelationShipMsg]

    pressure: dict[int, Pressure]
    mode: dict[int, Circuit]
    engine: dict[int, EnginesDevice]

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
            "gnss": self.gnss,
            "circuit": self.circuit,
            "dc": self.dc,
            "ac": self.ac,
            "tank": self.tank,
            "inverter_charger": self.inverter_charger,
            "device": self.device,
            "hvac": self.hvac,
            "audio_stereo": self.audio_stereo,
            "binary_logic_state": self.binary_logic_state,
            "ui_relationships": self.ui_relationships,
            "pressure": self.pressure,
            "mode": self.mode,
            "engine": self.engine,
        }

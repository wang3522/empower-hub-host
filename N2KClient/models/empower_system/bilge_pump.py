from N2KClient.models.empower_system.circuit_thing import CircuitThing
from typing import Optional
from .thing import Thing
from N2KClient.models.n2k_configuration.inverter_charger import InverterChargerDevice
from N2KClient.models.n2k_configuration.ac import AC
from N2KClient.models.n2k_configuration.dc import DC
from N2KClient.models.n2k_configuration.circuit import Circuit
from ..common_enums import ThingType
from ..constants import Constants
from .channel import Channel
from N2KClient.models.empower_system.ac_meter import ACMeterThingBase
from .link import Link
from N2KClient.models.n2k_configuration.binary_logic_state import BinaryLogicState
from N2KClient.models.n2k_configuration.category_item import CategoryItem


class CircuitBilgePump(CircuitThing):

    def __init__(
        self, circuit: Circuit, links: list[Link], bls: BinaryLogicState = None
    ):
        CircuitThing.__init__(self, ThingType.BILGE_PUMP, circuit, links, bls)

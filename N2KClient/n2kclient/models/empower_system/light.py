from .circuit_thing import CircuitThing
from ..n2k_configuration.circuit import Circuit
from ..common_enums import ThingType
from .link import Link
from ..n2k_configuration.binary_logic_state import BinaryLogicState


class CircuitLight(CircuitThing):

    def __init__(self, circuit: Circuit, links: list[Link], bls: BinaryLogicState):
        CircuitThing.__init__(self, ThingType.LIGHT, circuit, links, bls)

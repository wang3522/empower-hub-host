from .circuit_thing import CircuitThing
from ..n2k_configuration.circuit import Circuit
from ..common_enums import ThingType
from .link import Link
from ..n2k_configuration.binary_logic_state import BinaryLogicState


class CircuitWaterPump(CircuitThing):

    def __init__(
        self, circuit: Circuit, links: list[Link], bls: BinaryLogicState = None
    ):
        CircuitThing.__init__(self, ThingType.PUMP, circuit, links, bls)

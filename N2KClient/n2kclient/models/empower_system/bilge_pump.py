from ..devices import N2kDevices
from .circuit_thing import CircuitThing
from ..n2k_configuration.circuit import Circuit
from ..common_enums import ThingType
from .link import Link
from ..n2k_configuration.binary_logic_state import BinaryLogicState


class CircuitBilgePump(CircuitThing):
    """
    Representation of a bilge pump circuit in the Empower system.
    Inherits from CircuitThing to utilize common circuit functionalities.

    Methods:
        __init__: Initializes the CircuitBilgePump with a Circuit configuration, links, N2kDevices, and an optional BinaryLogicState.
    """

    def __init__(
        self,
        circuit: Circuit,
        links: list[Link],
        n2k_devices: N2kDevices,
        bls: BinaryLogicState = None,
    ):
        CircuitThing.__init__(
            self, ThingType.BILGE_PUMP, circuit, links, n2k_devices, bls
        )

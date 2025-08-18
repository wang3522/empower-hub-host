from ..devices import N2kDevices
from .circuit_thing import CircuitThing
from ..n2k_configuration.circuit import Circuit
from ..common_enums import ThingType
from .link import Link
from ..n2k_configuration.binary_logic_state import BinaryLogicState


class CircuitPowerSwitch(CircuitThing):
    """
    Representation of a generic power switch circuit in the Empower system.
    Inherits from CircuitThing to utilize common circuit functionalities.
    Methods:
        __init__: Initializes the CircuitPowerSwitch with the provided circuit, links, N2k
    """

    def __init__(
        self,
        circuit: Circuit,
        links: list[Link],
        n2k_devices: N2kDevices,
        bls: BinaryLogicState = None,
    ):
        CircuitThing.__init__(
            self, ThingType.GENERIC_CIRCUIT, circuit, links, n2k_devices, bls
        )

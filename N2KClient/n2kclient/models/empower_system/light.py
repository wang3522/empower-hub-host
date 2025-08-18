from ..devices import N2kDevices
from .circuit_thing import CircuitThing
from ..n2k_configuration.circuit import Circuit
from ..common_enums import ThingType
from .link import Link
from ..n2k_configuration.binary_logic_state import BinaryLogicState


class CircuitLight(CircuitThing):
    """
    This class extends CircuitThing to handle specific properties and behaviors of light circuits,
    including the association with a Binary Logic State (BLS) and links to other components.

    Methods:
        __init__: Initializes the CircuitLight instance with the provided circuit, links, BLS, and N2kDevices.
        to_json: Converts the CircuitLight instance to a JSON-compatible dictionary.
    """

    def __init__(
        self,
        circuit: Circuit,
        links: list[Link],
        bls: BinaryLogicState,
        n2k_devices: N2kDevices,
    ):
        CircuitThing.__init__(self, ThingType.LIGHT, circuit, links, n2k_devices, bls)

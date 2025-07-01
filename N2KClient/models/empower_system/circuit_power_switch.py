from N2KClient.models.devices import N2kDevices
from N2KClient.models.empower_system.circuit_thing import CircuitThing
from N2KClient.models.n2k_configuration.circuit import Circuit
from ..common_enums import ThingType
from .link import Link
from N2KClient.models.n2k_configuration.binary_logic_state import BinaryLogicState


class CircuitPowerSwitch(CircuitThing):

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

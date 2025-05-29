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


def get_enabled_categories(categories: list[CategoryItem]):
    return [category.name_utf8 for category in categories if category.enabled == True]


class CircuitThing(Thing):
    circuit: Circuit

    def __init__(
        self,
        type: ThingType,
        circuit: Circuit,
        links: list[Link],
        bls: BinaryLogicState = None,
    ):
        Thing.__init__(
            self,
            type,
            circuit.control_id,
            circuit.name_utf8,
            get_enabled_categories(circuit.categories),
            links=links,
        )
        self.circuit = circuit
        self.circuit_runtime_id = circuit.control_id

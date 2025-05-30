from typing import Optional
from .thing import Thing
from N2KClient.models.n2k_configuration.inverter_charger import InverterChargerDevice
from N2KClient.models.n2k_configuration.ac import AC
from N2KClient.models.n2k_configuration.dc import DC
from N2KClient.models.n2k_configuration.circuit import Circuit
from ..common_enums import ChannelType, ThingType, Unit
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

        channels = []
        channels.extend(
            [
                Channel(
                    id="cs",
                    name="Component Status",
                    type=ChannelType.STRING,
                    unit=Unit.NONE,
                    read_only=False,
                    tags=[
                        f"{Constants.empower}:{type.value}.{Constants.componentStatus}"
                    ],
                ),
                Channel(
                    id="c",
                    name="Current",
                    type=ChannelType.NUMBER,
                    unit=Unit.ENERGY_AMP,
                    read_only=True,
                    tags=[f"{Constants.empower}:{type.value}.current"],
                ),
            ]
        )
        if circuit.dimmable:
            channels.append(
                Channel(
                    id="lvl",
                    name="Level",
                    type=ChannelType.NUMBER,
                    unit=Unit.NONE,
                    read_only=False,
                    tags=[f"{Constants.empower}:{type.value}.level"],
                )
            )
        else:
            channels.append(
                Channel(
                    id="p",
                    name="Power",
                    type=ChannelType.BOOLEAN,
                    unit=Unit.NONE,
                    read_only=circuit.switch_type == 0,
                    tags=[f"{Constants.empower}:{type.value}.power"],
                )
            )
        for channel in channels:
            self._define_channel(channel)

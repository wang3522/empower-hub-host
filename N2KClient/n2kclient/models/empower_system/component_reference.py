from typing import Union
from ..common_enums import ComponentType
from ...models.n2k_configuration.metering_device import MeteringDevice
from ...models.n2k_configuration.tank import Tank
from ...models.n2k_configuration.circuit import Circuit
from ...models.n2k_configuration.binary_logic_state import BinaryLogicState
from ...models.n2k_configuration.engine import EngineDevice
from ...models.n2k_configuration.inverter_charger import InverterChargerDevice
from ...models.n2k_configuration.dc import DC
from ...models.n2k_configuration.ac import AC


class ComponentReference:
    """
    Reference to a component in the Empower system, encapsulating its type and associated object. Used for handling of alarm association to components.
    This class allows for the association of a component type with its corresponding thing, enabling easy identification and management of components within the system.
    Attributes:
        component_type: The type of the component, represented as a ComponentType enum.
        thing: The actual component instance, which can be of various types such as DC, AC, MeteringDevice, Tank, Circuit, BinaryLogicState, EngineDevice, or InverterChargerDevice.
    Methods:
        __init__: Initializes the ComponentReference with a specific component type and thing.
    """

    component_type: ComponentType
    thing: Union[
        DC,
        AC,
        Tank,
        Circuit,
        BinaryLogicState,
        EngineDevice,
        InverterChargerDevice,
    ]

    def __init__(
        self,
        component_type: ComponentType,
        thing: Union[
            DC,
            AC,
            MeteringDevice,
            Tank,
            Circuit,
            BinaryLogicState,
            EngineDevice,
            InverterChargerDevice,
        ],
    ):
        self.component_type = component_type
        self.thing = thing

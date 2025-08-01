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

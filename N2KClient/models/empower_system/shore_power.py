from typing import Optional
from .thing import Thing
from N2KClient.models.common_enums import ThingType
from N2KClient.models.n2k_configuration.ac import AC
from N2KClient.models.n2k_configuration.circuit import Circuit
from ..constants import Constants
from .channel import Channel
from ..common_enums import ChannelType, Unit
from N2KClient.models.n2k_configuration.binary_logic_state import BinaryLogicState


class ShorePower(Thing):
    def __init__(
        self,
        ac_line1: AC,
        ac_line2: AC,
        ac_line3: AC,
        categories: list[str] = [],
        circuit: Optional[Circuit] = None,
        ic_associated_line: Optional[int] = None,
        bls: BinaryLogicState = None,
    ):
        Thing.__init__(
            self,
            ThingType.SHORE_POWER,
            ac_line1,
            ac_line2,
            ac_line3,
            categories,
            ic_associated_line,
        )

        if circuit is not None:
            # Enabled channel defined here
            pass

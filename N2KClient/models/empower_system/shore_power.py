from typing import Optional
from .thing import Thing
from N2KClient.models.common_enums import ThingType
from N2KClient.models.n2k_configuration.ac import AC
from N2KClient.models.n2k_configuration.circuit import Circuit
from ..constants import Constants
from .channel import Channel
from ..common_enums import ChannelType, Unit
from N2KClient.models.n2k_configuration.binary_logic_state import BinaryLogicState
from N2KClient.models.empower_system.ac_meter import ACMeterThingBase


class ShorePower(ACMeterThingBase):
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
        ACMeterThingBase.__init__(
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
                        f"{Constants.empower}:{Constants.shorepower}.{Constants.componentStatus}"
                    ],
                ),
                Channel(
                    id="connected",
                    name="Connected",
                    read_only=True,
                    type=ChannelType.BOOLEAN,
                    unit=Unit.NONE,
                    tags=[f"{Constants.empower}:{Constants.shorepower}.connected"],
                ),
            ]
        )

        if circuit is not None:
            channels.append(
                Channel(
                    id="enabled",
                    name="Enabled",
                    type=ChannelType.BOOLEAN,
                    unit=Unit.NONE,
                    read_only=circuit.switch_type == 0,
                    tags=[
                        f"{Constants.empower}:{Constants.shorepower}.{Constants.enabled}"
                    ],
                )
            )
        for channel in channels:
            self._define_channel(channel)

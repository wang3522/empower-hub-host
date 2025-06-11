from typing import Optional
from N2KClient.models.common_enums import ThingType
from N2KClient.models.devices import ChannelSource, MobileChannelMapping, N2kDevices
from N2KClient.models.empower_system.mapping_utility import (
    MappingUtils,
    RegisterMappingUtility,
)
from N2KClient.models.n2k_configuration.ac import AC
from N2KClient.models.n2k_configuration.circuit import Circuit
from ..constants import Constants, JsonKeys
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
        n2k_devices: N2kDevices,
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
        channels = []

        channels.extend(
            Channel(
                id="connected",
                name="Connected",
                read_only=True,
                type=ChannelType.BOOLEAN,
                unit=Unit.NONE,
                tags=[f"{Constants.empower}:{Constants.shorepower}.connected"],
            ),
        )

        RegisterMappingUtility.register_shorepower_connected_mappings(
            n2k_devices,
            self.id,
            bls,
            ac_line1,
            ac_line2,
            ac_line3,
            ic_associated_line,
        )

        if circuit is not None:
            self.circuit = circuit
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

            RegisterMappingUtility.register_enable_mapping(
                n2k_devices=n2k_devices,
                thing_id=self.id,
                circuit_id=self.circuit.control_id,
                device_key_prefix=JsonKeys.AC,
                channel_key="Level",
            )

        for channel in channels:
            self._define_channel(channel)

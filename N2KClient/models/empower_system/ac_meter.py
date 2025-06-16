from typing import Optional

from N2KClient.models.devices import ChannelSource, MobileChannelMapping, N2kDevices
from N2KClient.models.empower_system.mapping_utility import (
    RegisterMappingUtility,
)
from .thing import Thing
from N2KClient.models.common_enums import ThingType
from N2KClient.models.n2k_configuration.ac import AC
from ..constants import Constants, JsonKeys
from .channel import Channel
from ..common_enums import ChannelType, Unit


class ACMeterThingBase(Thing):
    def __init__(
        self,
        type: ThingType,
        ac_line1: AC,
        ac_line2: AC,
        ac_line3: AC,
        n2k_devices: N2kDevices,
        categories: list[str],
        ic_associated_line: Optional[int],
    ):
        Thing.__init__(
            self,
            type,
            ac_line1.instance.instance,
            ac_line1.name_utf8,
            categories=categories,
            links=[],
        )
        channels = [
            Channel(
                id="cs",
                name="Component Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=[f"{Constants.empower}:{type.value}.{Constants.componentStatus}"],
            ),
        ]

        if ac_line1 is not None:
            channels.extend(
                [
                    Channel(
                        id="l1cs",
                        name="Line 1 Component Status",
                        type=ChannelType.STRING,
                        unit=Unit.NONE,
                        read_only=False,
                        tags=[
                            f"{Constants.empower}:{type.value}.{Constants.line1}.{Constants.componentStatus}"
                        ],
                    ),
                    Channel(
                        id="l1v",
                        name="Line 1 Voltage",
                        type=ChannelType.NUMBER,
                        unit=Unit.ENERGY_VOLT,
                        read_only=True,
                        tags=[
                            f"{Constants.empower}:{type.value}.{Constants.line1}.{Constants.voltage}"
                        ],
                    ),
                    Channel(
                        id="l1c",
                        name="Line 1 Current",
                        type=ChannelType.NUMBER,
                        unit=Unit.ENERGY_AMP,
                        read_only=True,
                        tags=[
                            f"{Constants.empower}:{type.value}.{Constants.line1}.{Constants.current}"
                        ],
                    ),
                    Channel(
                        id="l1f",
                        name="Line 1 Frequency",
                        type=ChannelType.NUMBER,
                        unit=Unit.FREQUENCY_HERTZ,
                        read_only=True,
                        tags=[
                            f"{Constants.empower}:{type.value}.{Constants.line1}.{Constants.frequency}"
                        ],
                    ),
                    Channel(
                        id="l1p",
                        name="Line 1 Power",
                        type=ChannelType.NUMBER,
                        unit=Unit.ENERGY_VOLT,
                        read_only=True,
                        tags=[
                            f"{Constants.empower}:{type.value}.{Constants.line1}.{Constants.power}"
                        ],
                    ),
                ]
            )
            RegisterMappingUtility.register_ac_line_mappings(
                n2k_devices=n2k_devices,
                ac=ac_line1,
                line=1,
                mobile_key_prefix=self.id,
                ic_associated_line=ic_associated_line,
            )

        if ac_line2 is not None:
            channels.extend(
                [
                    Channel(
                        id="l2cs",
                        name="Line 2 Component Status",
                        type=ChannelType.STRING,
                        unit=Unit.NONE,
                        read_only=False,
                        tags=[
                            f"{Constants.empower}:{type.value}.{Constants.line2}.{Constants.componentStatus}"
                        ],
                    ),
                    Channel(
                        id="l2v",
                        name="Line 2 Voltage",
                        type=ChannelType.NUMBER,
                        unit=Unit.ENERGY_VOLT,
                        read_only=True,
                        tags=[
                            f"{Constants.empower}:{type.value}.{Constants.line2}.{Constants.voltage}"
                        ],
                    ),
                    Channel(
                        id="l2c",
                        name="Line 2 Current",
                        type=ChannelType.NUMBER,
                        unit=Unit.ENERGY_AMP,
                        read_only=True,
                        tags=[
                            f"{Constants.empower}:{type.value}.{Constants.line2}.{Constants.current}"
                        ],
                    ),
                    Channel(
                        id="l2f",
                        name="Line 2 Frequency",
                        type=ChannelType.NUMBER,
                        unit=Unit.FREQUENCY_HERTZ,
                        read_only=True,
                        tags=[
                            f"{Constants.empower}:{type.value}.{Constants.line2}.{Constants.frequency}"
                        ],
                    ),
                    Channel(
                        id="l2p",
                        name="Line 2 Power",
                        type=ChannelType.NUMBER,
                        unit=Unit.ENERGY_WATT,
                        read_only=True,
                        tags=[
                            f"{Constants.empower}:{type.value}.{Constants.line2}.{Constants.power}"
                        ],
                    ),
                ]
            )
            RegisterMappingUtility.register_ac_line_mappings(
                n2k_devices=n2k_devices,
                ac=ac_line2,
                line=2,
                mobile_key_prefix=self.id,
                ic_associated_line=ic_associated_line,
            )

        if ac_line3 is not None:
            channels.extend(
                [
                    Channel(
                        id="l3cs",
                        name="Line 3 Component Status",
                        type=ChannelType.STRING,
                        unit=Unit.NONE,
                        read_only=False,
                        tags=[
                            f"{Constants.empower}:{type.value}.{Constants.line3}.{Constants.componentStatus}"
                        ],
                    ),
                    Channel(
                        id="l3v",
                        name="Line 3 Voltage",
                        type=ChannelType.NUMBER,
                        unit=Unit.ENERGY_VOLT,
                        read_only=True,
                        tags=[
                            f"{Constants.empower}:{type.value}.{Constants.line3}.{Constants.voltage}"
                        ],
                    ),
                    Channel(
                        id="l3c",
                        name="Line 3 Current",
                        type=ChannelType.NUMBER,
                        unit=Unit.ENERGY_AMP,
                        read_only=True,
                        tags=[
                            f"{Constants.empower}:{type.value}.{Constants.line3}.{Constants.current}"
                        ],
                    ),
                    Channel(
                        id="l3f",
                        name="Line 3 Frequency",
                        type=ChannelType.NUMBER,
                        unit=Unit.FREQUENCY_HERTZ,
                        read_only=True,
                        tags=[
                            f"{Constants.empower}:{type.value}.{Constants.line3}.{Constants.frequency}"
                        ],
                    ),
                    Channel(
                        id="l3p",
                        name="Line 3 Power",
                        type=ChannelType.NUMBER,
                        unit=Unit.ENERGY_WATT,
                        read_only=True,
                        tags=[
                            f"{Constants.empower}:{type.value}.{Constants.line3}.{Constants.power}"
                        ],
                    ),
                ]
            )
            RegisterMappingUtility.register_ac_line_mappings(
                n2k_devices=n2k_devices,
                ac=ac_line3,
                line=3,
                mobile_key_prefix=self.id,
                ic_associated_line=ic_associated_line,
            )
            # Register component status mapping for the AC meter

        for channel in channels:
            self._define_channel(channel)

        RegisterMappingUtility.register_ac_meter_component_status_mapping(
            n2k_devices=n2k_devices,
            mobile_key_prefix=self.id,
            ac_instance=ac_line1.instance.instance,
            ic_associated_line=ic_associated_line,
        )

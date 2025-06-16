from N2KClient.models.devices import N2kDevices
from .thing import Thing
from ..common_enums import ChannelType, ThingType, Unit
from ..constants import Constants
from .channel import Channel
from N2KClient.models.n2k_configuration.hvac import HVACDevice
from N2KClient.models.empower_system.mapping_utility import (
    RegisterMappingUtility,
)


class Climate(Thing):
    def __init__(
        self,
        hvac: HVACDevice,
        n2k_devices: N2kDevices,
        categories: list[str] = [],
    ):
        Thing.__init__(
            self,
            type=ThingType.CLIMATE,
            id=hvac.instance.instance,
            name=hvac.name_utf8,
            categories=categories,
        )

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
                        f"{Constants.empower}:{Constants.hvac}.{Constants.componentStatus}"
                    ],
                ),
                Channel(
                    id="mode",
                    name="Mode",
                    type=ChannelType.STRING,
                    unit=Unit.NONE,
                    read_only=True,
                    tags=[f"{Constants.empower}:{Constants.hvac}.{Constants.mode}"],
                ),
                Channel(
                    id="sp",
                    name="Set Point",
                    read_only=False,
                    type=ChannelType.NUMBER,
                    unit=Unit.TEMPERATURE_CELSIUS,
                    tags=[f"{Constants.empower}:{Constants.hvac}.{Constants.setPoint}"],
                ),
                Channel(
                    id="at",
                    name="Ambient Temperature",
                    read_only=True,
                    type=ChannelType.NUMBER,
                    unit=Unit.TEMPERATURE_CELSIUS,
                    tags=[
                        f"{Constants.empower}:{Constants.hvac}.{Constants.ambientTemperature}"
                    ],
                ),
                Channel(
                    id="fs",
                    name="Fan Speed",
                    read_only=False,
                    type=ChannelType.STRING,
                    unit=Unit.NONE,
                    tags=[f"{Constants.empower}:{Constants.hvac}.{Constants.fanSpeed}"],
                ),
                Channel(
                    id="fm",
                    name="Fan Mode",
                    read_only=False,
                    type=ChannelType.STRING,
                    unit=Unit.NONE,
                    tags=[f"{Constants.empower}:{Constants.hvac}.{Constants.fanMode}"],
                ),
            ]
        )
        for channel in channels:
            self._define_channel(channel)

        RegisterMappingUtility.register_climate_mappings(
            n2k_devices=n2k_devices,
            thing_id=self.id,
            instance=hvac.instance.instance,
        )

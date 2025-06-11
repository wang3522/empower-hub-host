from N2KClient.models.constants import Constants, JsonKeys
from N2KClient.models.devices import ChannelSource, MobileChannelMapping, N2kDevices
from N2KClient.models.empower_system.channel import Channel
from N2KClient.models.empower_system.mapping_utility import (
    MappingUtils,
    RegisterMappingUtility,
)
from .thing import Thing
from N2KClient.models.common_enums import ChannelType, ThingType, Unit
from N2KClient.models.n2k_configuration.gnss import GNSSDevice
from N2KClient.models.empower_system.location_state import LocationState


class GNSS(Thing):
    def __init__(
        self,
        gnss: GNSSDevice,
        n2k_devices: N2kDevices,
        categories: list[str] = [],
    ):
        Thing.__init__(
            self,
            ThingType.GNSS,
            gnss.instance.instance,
            gnss.name_utf8,
            categories,
        )
        self.instance = gnss.instance.instance

        self.metadata[
            f"{Constants.empower}:{Constants.location}.{Constants.external}"
        ] = gnss.is_external

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
                        f"{Constants.empower}:{Constants.location}.{Constants.componentStatus}"
                    ],
                ),
                Channel(
                    id="ft",
                    name="Fix Type",
                    read_only=True,
                    type=ChannelType.STRING,
                    unit=Unit.NONE,
                    tags=[f"{Constants.empower}:{Constants.location}.fixType"],
                ),
                Channel(
                    id="loc",
                    name="Location",
                    read_only=True,
                    type=ChannelType.POINT,
                    unit=Unit.GEOJSON_POINT,
                    tags=[f"{Constants.empower}:{Constants.location}.position"],
                ),
            ]
        )
        for channel in channels:
            self._define_channel(channel)

        self._register_mobile_channel_mappings(n2k_devices)

    def _register_mobile_channel_mappings(self, n2k_devices: N2kDevices):
        """
        Register mappings for GNSS channels.
        """
        gnss_device = n2k_devices.devices.get(f"{JsonKeys.GNSS}.{self.instance}")
        if not gnss_device:
            return

        # Register fix type mapping using the centralized utility
        RegisterMappingUtility.register_simple_mapping(
            n2k_devices=n2k_devices,
            mobile_key=f"{self.id}.ft",
            device_key=f"{JsonKeys.GNSS}.{self.instance}",
            channel_key="FixType",
            label="Fix Type",
        )

        # Register location mapping using the centralized utility
        RegisterMappingUtility.register_location_mapping(
            n2k_devices=n2k_devices,
            thing_id=self.id,
            device_key=f"{JsonKeys.GNSS}.{self.instance}",
            location_state_class=LocationState,
        )

from N2KClient.models.constants import Constants, JsonKeys
from N2KClient.models.devices import ChannelSource, MobileChannelMapping, N2kDevices
from N2KClient.models.empower_system.channel import Channel
from N2KClient.models.empower_system.inverter import MappingUtils
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
        self._register_fix_type_mapping(n2k_devices)
        self._register_location_mapping(n2k_devices)

    def _register_fix_type_mapping(self, n2k_devices: N2kDevices):

        def fix_type_transform(values: dict, last_updated: dict):
            fix_type_value = MappingUtils.get_value_or_default(values, "ft", None)
            return fix_type_value

        mapping = MobileChannelMapping(
            mobile_key=f"{self.id}.ft",
            channel_sources=[
                ChannelSource(
                    label="fix_type",
                    device_key=f"{JsonKeys.GNSS}.{self.instance}",
                    channel_key="FixType",
                )
            ],
            transform=fix_type_transform,
        )
        n2k_devices.add_mobile_channel_mapping(mapping)

    def _register_location_mapping(self, n2k_devices: N2kDevices):
        def location_transform(values: dict, last_updated: dict):
            lat_value = MappingUtils.get_value_or_default(values, "lat", None)
            long_value = MappingUtils.get_value_or_default(values, "long", None)
            sog_value = MappingUtils.get_value_or_default(values, "sog", None)
            return LocationState(lat_value, long_value, sog_value)

        mapping = MobileChannelMapping(
            mobile_key=f"{self.id}.loc",
            channel_sources=[
                ChannelSource(
                    label="lat",
                    device_key=f"{JsonKeys.GNSS}.{self.instance}",
                    channel_key="LatitudeDeg",
                ),
                ChannelSource(
                    label="long",
                    device_key=f"{JsonKeys.GNSS}.{self.instance}",
                    channel_key="LongitudeDeg",
                ),
                ChannelSource(
                    label="sog",
                    device_key=f"{JsonKeys.GNSS}.{self.instance}",
                    channel_key="SOG",
                ),
            ],
            transform=location_transform,
        )
        n2k_devices.add_mobile_channel_mapping(mapping)

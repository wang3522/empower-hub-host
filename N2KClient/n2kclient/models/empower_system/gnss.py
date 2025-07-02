from ..constants import Constants
from .channel import Channel
from .thing import Thing
from ..common_enums import ChannelType, ThingType, Unit
from ..n2k_configuration.gnss import GNSSDevice


class GNSS(Thing):
    def __init__(
        self,
        gnss: GNSSDevice,
        categories: list[str] = [Constants.location],
    ):
        Thing.__init__(
            self,
            ThingType.GNSS,
            gnss.instance.instance,
            gnss.name_utf8,
            categories,
        )

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
